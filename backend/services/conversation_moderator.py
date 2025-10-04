"""
Conversation Moderator Service
Handles the turn-by-turn simulation of conversations between agent and debtor
Implements the "Moderator" logic as defined in the PRD
"""

from typing import List, Tuple, Optional
from models.evaluation import TranscriptMessage
from core.gemini_client import generate_next_turn_with_proper_history
from google.genai import types


# Termination keywords that indicate a conversation should end
HANGUP_KEYWORDS = [
    "don't call me again",
    "i'm hanging up",
    "stop calling",
    "goodbye",
    "hanging up now",
    "leave me alone",
    "don't contact me",
    "end this call"
]

# Maximum number of turn pairs (agent + debtor = 1 pair)
MAX_TURN_PAIRS = 10


def replace_variables_in_prompt(prompt: str, name: str = None, amount: float = None) -> str:
    """
    Replace variables in the prompt with actual values
    
    Args:
        prompt: The prompt containing variables like {name} and {amount}
        name: The actual name to replace {name} with
        amount: The actual amount to replace {amount} with
    
    Returns:
        str: Prompt with variables replaced
    """
    result = prompt
    if name:
        result = result.replace("{name}", name)
    if amount is not None:
        # Format amount as Indian Rupees
        result = result.replace("{amount}", f"₹{amount:,.2f}")
    return result


def check_should_terminate(last_message: str, turn_count: int) -> bool:
    """
    Check if the conversation should terminate based on termination conditions
    
    Args:
        last_message: The last message in the conversation
        turn_count: Current number of turn pairs (agent + debtor = 1 pair)
    
    Returns:
        bool: True if conversation should end, False otherwise
    """
    # Check turn limit
    if turn_count >= MAX_TURN_PAIRS:
        return True
    
    # Check for hangup keywords
    message_lower = last_message.lower()
    for keyword in HANGUP_KEYWORDS:
        if keyword in message_lower:
            return True
    
    return False


async def run_conversation_simulation(
    agent_system_prompt: str,
    personality_system_prompt: str,
    scenario_objective: str,
    debtor_name: str = "Customer",
    debtor_amount: Optional[float] = None,
    model_name: str = "gemini-2.5-flash",
    agent_temperature: float = 0.7,
    debtor_temperature: float = 0.7
) -> List[TranscriptMessage]:
    """
    Run a complete conversation simulation between an agent and a debtor
    
    This function implements the Moderator logic with proper context separation:
    1. Maintains conversation history as a Contents array (Google Genai SDK pattern)
    2. Keeps system prompts separate for each speaker
    3. Replaces variables {name} and {amount} with actual values
    4. Alternates turns between agent and debtor
    5. Checks termination conditions after each turn
    6. Returns the full transcript
    
    Args:
        agent_system_prompt: The system prompt for the debt collection agent
        personality_system_prompt: The system prompt defining the debtor's personality
        scenario_objective: The debtor's objective in this specific scenario
        debtor_name: The name of the debtor (replaces {name} variable)
        debtor_amount: The amount owed (replaces {amount} variable)
        model_name: The Gemini model to use 
        agent_temperature: Temperature for agent responses (default: 0.7)
        debtor_temperature: Temperature for debtor responses (default: 0.7)
    
    Returns:
        List[TranscriptMessage]: The complete conversation transcript
    
    Raises:
        Exception: If there's an error during conversation generation
    """
    transcript: List[TranscriptMessage] = []
    turn_count = 0
    
    # Replace variables in both system prompts
    agent_prompt_filled = replace_variables_in_prompt(
        agent_system_prompt, 
        name=debtor_name, 
        amount=debtor_amount
    )
    personality_prompt_filled = replace_variables_in_prompt(
        personality_system_prompt,
        name=debtor_name,
        amount=debtor_amount
    )
    
    # Enhanced debtor system prompt with scenario objective
    enhanced_debtor_prompt = f"""{personality_prompt_filled}

YOUR OBJECTIVE IN THIS CALL: {scenario_objective}

You are receiving a call from a debt collection agent. Stay in character and pursue your objective naturally through the conversation."""

    print(f"\n{'='*80}")
    print(f"🎭 STARTING CONVERSATION SIMULATION")
    print(f"{'='*80}")
    print(f"👤 Debtor Name: {debtor_name}")
    print(f"💰 Debtor Amount: ₹{debtor_amount:,.2f}" if debtor_amount else "💰 Debtor Amount: Not specified")
    print(f"🤖 Model: {model_name}")
    print(f"🌡️  Agent Temperature: {agent_temperature}")
    print(f"🌡️  Debtor Temperature: {debtor_temperature}")
    print(f"🎯 Scenario Objective: {scenario_objective[:100]}...")
    print(f"{'='*80}\n")
    
    try:
        # Agent starts the conversation
        while turn_count < MAX_TURN_PAIRS:
            # ============================================================
            # AGENT'S TURN
            # ============================================================
            print(f"\n{'='*60}")
            print(f"🤖 AGENT'S TURN (Turn {turn_count + 1})")
            print(f"{'='*60}")
            
            # For agent's turn, we treat the conversation from agent's perspective:
            # - Previous debtor messages are "user" inputs (what the agent is responding to)
            # - Previous agent messages are "model" outputs (what the agent said)
            # But since we're alternating speakers, we need to build history correctly
            
            # Build agent's perspective history
            agent_history = []
            for i, msg in enumerate(transcript):
                if msg.speaker == "debtor":
                    # Debtor's message is "user" input to the agent
                    agent_history.append(
                        types.Content(
                            role="user",
                            parts=[types.Part.from_text(text=msg.message)]
                        )
                    )
                else:  # agent
                    # Agent's previous message is "model" output
                    agent_history.append(
                        types.Content(
                            role="model",
                            parts=[types.Part.from_text(text=msg.message)]
                        )
                    )
            
            # Generate agent response with proper history and separate system prompt
            agent_response = await generate_next_turn_with_proper_history(
                contents_history=agent_history,
                system_prompt=agent_prompt_filled,
                model_name=model_name,
                temperature=agent_temperature
            )
            
            print(f"✅ Agent response generated: {agent_response[:200]}...")
            
            agent_message = TranscriptMessage(
                speaker="agent",
                message=agent_response.strip()
            )
            transcript.append(agent_message)
            
            # Check termination after agent's turn
            if check_should_terminate(agent_message.message, turn_count):
                print(f"🛑 Termination condition met after agent's turn")
                break
            
            # ============================================================
            # DEBTOR'S TURN
            # ============================================================
            print(f"\n{'='*60}")
            print(f"👤 DEBTOR'S TURN (Turn {turn_count + 1})")
            print(f"{'='*60}")
            
            # Build debtor's perspective history
            debtor_history = []
            for i, msg in enumerate(transcript):
                if msg.speaker == "agent":
                    # Agent's message is "user" input to the debtor
                    debtor_history.append(
                        types.Content(
                            role="user",
                            parts=[types.Part.from_text(text=msg.message)]
                        )
                    )
                else:  # debtor
                    # Debtor's previous message is "model" output
                    debtor_history.append(
                        types.Content(
                            role="model",
                            parts=[types.Part.from_text(text=msg.message)]
                        )
                    )
            
            # Generate debtor response with proper history and separate system prompt
            debtor_response = await generate_next_turn_with_proper_history(
                contents_history=debtor_history,
                system_prompt=enhanced_debtor_prompt,
                model_name=model_name,
                temperature=debtor_temperature
            )
            
            print(f"✅ Debtor response generated: {debtor_response[:200]}...")
            
            debtor_message = TranscriptMessage(
                speaker="debtor",
                message=debtor_response.strip()
            )
            transcript.append(debtor_message)
            
            # Increment turn count (one full pair: agent + debtor)
            turn_count += 1
            
            print(f"\n✅ Turn {turn_count} completed")
            print(f"📊 Total messages in transcript: {len(transcript)}")
            
            # Check termination after debtor's turn
            if check_should_terminate(debtor_message.message, turn_count):
                print(f"🛑 Termination condition met after debtor's turn")
                break
        
        print(f"\n{'='*80}")
        print(f"✅ CONVERSATION SIMULATION COMPLETE")
        print(f"{'='*80}")
        print(f"📊 Total turns: {turn_count}")
        print(f"📊 Total messages: {len(transcript)}")
        print(f"{'='*80}\n")
        
        return transcript
    
    except Exception as e:
        # Log the error and raise it for the caller to handle
        print(f"\n{'='*80}")
        print(f"❌ ERROR DURING CONVERSATION SIMULATION")
        print(f"{'='*80}")
        print(f"Error: {str(e)}")
        print(f"Turn count: {turn_count}")
        print(f"Messages in transcript: {len(transcript)}")
        import traceback
        print(f"Traceback:\n{traceback.format_exc()}")
        print(f"{'='*80}\n")
        raise Exception(f"Conversation simulation failed: {str(e)}")


def format_transcript_for_evaluation(transcript: List[TranscriptMessage]) -> str:
    """
    Format the transcript into a readable text format for evaluation
    
    Args:
        transcript: List of TranscriptMessage objects
    
    Returns:
        str: Formatted transcript text
    
    Example:
        AGENT: Hello, I'm calling regarding an outstanding balance.
        DEBTOR: I don't have the money right now.
        AGENT: I understand. Can we discuss a payment plan?
    """
    formatted_lines = []
    for msg in transcript:
        speaker_label = msg.speaker.upper()
        formatted_lines.append(f"{speaker_label}: {msg.message}")
    
    return "\n".join(formatted_lines)
