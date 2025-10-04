from __future__ import annotations

import asyncio
import logging
from datetime import datetime
from dotenv import load_dotenv
import json
import os
from typing import Any

from livekit import rtc, api
from livekit.agents import (
    AgentSession,
    Agent,
    JobContext,
    function_tool,
    RunContext,
    get_job_context,
    cli,
    WorkerOptions,
    RoomInputOptions,
)
from livekit.plugins import (
    deepgram,
    openai,
    google,
    sarvam, 
    silero,
    noise_cancellation,  # noqa: F401
)
from livekit.plugins.turn_detector.english import EnglishModel
from livekit.plugins.turn_detector.multilingual import MultilingualModel


# load environment variables, this is optional, only used for local development
load_dotenv(dotenv_path=".env.local")
logger = logging.getLogger("outbound-caller")
logger.setLevel(logging.INFO)

outbound_trunk_id = os.getenv("SIP_OUTBOUND_TRUNK_ID")


class OutboundCaller(Agent):
    def __init__(
        self,
        *,
        name: str,
        amount: float,
        dial_info: dict[str, Any],
    ):
        super().__init__(
            instructions=f"""You are \"Ana,\" a highly empathetic and professional debt collection agent working for SBI BANK India. Your primary goal is to recover outstanding credit card debts while maintaining a customer-centric approach, adhering strictly to compliance guidelines, and preserving the customer's relationship with the bank. The customer's name is {name}, and the overdue amount is ₹{amount}. Always start by politely confirming the customer's identity. \n\nKey Directives:\n1.  **Empathy and Active Listening:** Begin by greeting {name} politely and stating the purpose of the call. Acknowledge and validate the customer's emotions and stated difficulties without judgment. Use phrases that demonstrate understanding (e.g., \"I hear you,\" \"I understand this is a difficult time\"). Actively listen to their responses to tailor your approach. Prioritize building rapport.\n2.  **Goal-Oriented Dialogue:** Your main objective is to secure a commitment for payment. If the customer expresses hardship, explore solutions proactively. This includes:\n    *   **Immediate Full Payment:** Gently urge {name} to settle the full outstanding amount as quickly as possible, highlighting benefits (e.g., avoiding further charges, positive credit score impact).\n    *   **Partial Payment:** If full payment isn't possible, propose a partial payment and ask when they can make it. Always suggest a concrete amount if the customer is hesitant.\n    *   **Payment Plan/Hardship Program:** If neither full nor partial payment is immediately feasible due to hardship, offer to explore flexible repayment arrangements or special assistance programs. This involves gathering specific financial details (income, essential expenses) to build a case for them. Clearly communicate what information is needed and why it's beneficial for them.\n    *   **Documentation Review:** If the customer denies the debt, remain calm and professional. State the specific loan details (e.g., card number, issue date, original amount) from your records. Offer verifiable ways for them to review documentation (e.g., email a statement, direct to a secure portal) and secure a commitment for them to do so within a defined timeframe (e.g., 48 hours). Do NOT ask for personal identifying information like date of birth unless absolutely necessary for verification *after* initial debt details have been provided and still disputed, and always explain the reason for such a request.\n3.  **Compliance and Professionalism:** Maintain a courteous and respectful tone throughout the conversation, even if the customer is agitated or denies the debt. Avoid aggressive language or making threats. Clearly state that you are calling from SBI Bank. Do not deviate from the script's intent, but adapt your language to sound natural and conversational. Ensure all proposed solutions align with bank policies and regulatory guidelines.\n4.  **Efficiency and Clarity:** Reduce repetitive statements. Ensure your questions are clear and direct, aimed at moving the conversation towards a resolution. When offering options, clearly explain the next steps and what the customer can expect.\n5.  **Handling Objections/Denials:** If the customer denies the debt, calmly reiterate the specific details you have (e.g., \"Our records show credit card number XXXX-XXXX-XXXX-1234, issued to {name} on [date], has an outstanding balance of ₹{amount}.\"). If they still deny, offer to send them documented proof (e.g., a statement, application form) to their registered email or via a secure bank portal, and secure their agreement to review it. If they refuse to provide an email, offer to send it via postal mail to their registered address.\n6.  **De-escalation:** If the customer becomes aggressive or anxious, acknowledge their feelings and gently steer the conversation back to finding a solution. For extreme hardship, prioritize confirming their willingness to cooperate and explore options rather than demanding immediate payment.\n7.  **Ending the Call:** Always allow the user to end the conversation. If a commitment is made, summarize the agreed-upon next steps. If no resolution is reached, politely state the bank's continued efforts to resolve the matter and the potential consequences of non-payment.\n\nBegin the call by greeting {name} politely and confirming their identity. Then, remind {name} about the outstanding credit card bill of ₹{amount}.
            
            Keep your responses concise and to the point, avoiding unnecessary repetition. Use natural, conversational language. Dont spit out the instructions, use them to guide your responses."""
        )
        # keep reference to the participant for transfers
        self.participant: rtc.RemoteParticipant | None = None

        self.dial_info = dial_info

    def set_participant(self, participant: rtc.RemoteParticipant):
        self.participant = participant

    async def hangup(self):
        """Helper function to hang up the call by deleting the room"""

        job_ctx = get_job_context()
        await job_ctx.api.room.delete_room(
            api.DeleteRoomRequest(
                room=job_ctx.room.name,
            )
        )


    @function_tool()
    async def end_call(self, ctx: RunContext):
        """Called when the user wants to end the call"""
        logger.info(f"ending the call for {self.participant.identity}")

        # let the agent finish speaking
        await ctx.wait_for_playout()

        await self.hangup()

    @function_tool()
    async def detected_answering_machine(self, ctx: RunContext):
        """Called when the call reaches voicemail. Use this tool AFTER you hear the voicemail greeting"""
        logger.info(f"detected answering machine for {self.participant.identity}")
        
        await ctx.session.generate_reply(
            instructions="Leave a voicemail message letting the user know you'll call back later."
        )
        await ctx.wait_for_playout()
        
        await self.hangup()


async def entrypoint(ctx: JobContext):
    logger.info(f"connecting to room {ctx.room.name}")
    
    # when dispatching the agent, we'll pass it the approriate info to dial the user
    # dial_info is a dict with the following keys:
    # - phone_number: the phone number to dial
    # - transfer_to: the phone number to transfer the call to when requested
    dial_info = json.loads(ctx.job.metadata)
    participant_identity = phone_number = dial_info["phone_number"]
    customer_name = dial_info.get("name", "Customer")  # Default fallback
    bill_amount = dial_info.get("amount", 0.0)  # Default fallback
    room_name = ctx.room.name  # Get room name from context
    
    # Create transcript directory if it doesn't exist
    transcript_dir = os.getenv("TRANSCRIPT_DIR", "backend\\transcripts")
    os.makedirs(transcript_dir, exist_ok=True)
    
    # Define the transcript save function BEFORE ctx.connect()
    # Modified to include room_name in filename
    async def write_transcript():
        current_date = datetime.now().strftime("%Y%m%d_%H%M%S")
        # Format: transcript_{room_name}_{timestamp}.json
        filename = os.path.join(transcript_dir, f"transcript_{room_name}_{current_date}.json")
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(session.history.to_dict(), f, indent=2, ensure_ascii=False)
            logger.info(f"Transcript saved: {filename}")
        except Exception as e:
            logger.error(f"Error saving transcript: {e}")
    
    # Register the shutdown callback
    ctx.add_shutdown_callback(write_transcript)
    
    await ctx.connect()

    # look up the user's phone number and appointment details
    agent = OutboundCaller(
        name=customer_name,
        amount=bill_amount,
        dial_info=dial_info,
    )

    # the following uses GPT-4o, Deepgram and Cartesia
    session = AgentSession(
        turn_detection=MultilingualModel(),
        vad=silero.VAD.load(),
        stt=deepgram.STT(),
        # you can also use OpenAI's TTS with openai.TTS()
        llm=openai.LLM(model="gpt-4o-mini"),
        tts=sarvam.TTS(
        target_language_code="en-IN",
        speaker="manisha",
      )
        # you can also use a speech-to-speech model like OpenAI's Realtime API
        # llm=openai.realtime.RealtimeModel()
    )

    # start the session first before dialing, to ensure that when the user picks up
    # the agent does not miss anything the user says
    session_started = asyncio.create_task(
        session.start(
            agent=agent,
            room=ctx.room,
            room_input_options=RoomInputOptions(
                # enable Krisp background voice and noise removal
                noise_cancellation=noise_cancellation.BVCTelephony(),
            ),
        )
    )

    # `create_sip_participant` starts dialing the user
    try:
        await ctx.api.sip.create_sip_participant(
            api.CreateSIPParticipantRequest(
                room_name=ctx.room.name,
                sip_trunk_id=outbound_trunk_id,
                sip_call_to=phone_number,
                participant_identity=participant_identity,
                # function blocks until user answers the call, or if the call fails
                wait_until_answered=True,
            )
        )

        # wait for the agent session start and participant join
        await session_started
        participant = await ctx.wait_for_participant(identity=participant_identity)
        logger.info(f"participant joined: {participant.identity}")

        agent.set_participant(participant)

    except api.TwirpError as e:
        logger.error(
            f"error creating SIP participant: {e.message}, "
            f"SIP status: {e.metadata.get('sip_status_code')} "
            f"{e.metadata.get('sip_status')}"
        )
        ctx.shutdown()


if __name__ == "__main__":
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            agent_name="outbound-caller",
        )
    )
