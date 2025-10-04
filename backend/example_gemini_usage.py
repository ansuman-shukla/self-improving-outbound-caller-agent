"""
Example Usage of Gemini Client
This file demonstrates how to use the gemini_client module for various tasks
"""

import asyncio
from google import genai
from core.gemini_client import (
    configure_gemini,
    generate_structured_content,
    generate_conversational_response,
    generate_conversational_response_with_history,
    generate_conversational_response_stream,
    create_schema
)


async def example_1_simple_conversation():
    """Example: Simple conversational response"""
    print("\n" + "="*60)
    print("Example 1: Simple Conversation")
    print("="*60)
    
    response = await generate_conversational_response(
        prompt="What is the capital of France?",
        system_instruction="You are a helpful geography teacher."
    )
    
    print(f"Response: {response}")


async def example_2_structured_output():
    """Example: Generate structured JSON output"""
    print("\n" + "="*60)
    print("Example 2: Structured JSON Output")
    print("="*60)
    
    # Define schema for a person object
    person_schema = genai.types.Schema(
        type=genai.types.Type.OBJECT,
        required=["name", "age", "occupation"],
        properties={
            "name": genai.types.Schema(type=genai.types.Type.STRING),
            "age": genai.types.Schema(type=genai.types.Type.INTEGER),
            "occupation": genai.types.Schema(type=genai.types.Type.STRING),
            "skills": genai.types.Schema(
                type=genai.types.Type.ARRAY,
                items=genai.types.Schema(type=genai.types.Type.STRING)
            )
        }
    )
    
    prompt = "Generate a profile for a software engineer named Alice who is 30 years old."
    
    response = await generate_structured_content(
        prompt=prompt,
        response_schema=person_schema,
        system_instruction="You are a helpful assistant that generates realistic profiles."
    )
    
    print(f"Structured Response:\n{response}")


async def example_3_scenario_generation():
    """Example: Generate a debt collection scenario (from PRD)"""
    print("\n" + "="*60)
    print("Example 3: Scenario Generation (PRD Use Case)")
    print("="*60)
    
    # This is the schema from the PRD for scenario generation
    scenario_schema = genai.types.Schema(
        type=genai.types.Type.OBJECT,
        required=["title", "backstory", "objective"],
        properties={
            "title": genai.types.Schema(type=genai.types.Type.STRING),
            "backstory": genai.types.Schema(type=genai.types.Type.STRING),
            "objective": genai.types.Schema(type=genai.types.Type.STRING),
        }
    )
    
    personality = {
        "name": "Anxious First-Time Debtor",
        "description": "A person who is nervous about debt collection",
        "system_prompt": "You are anxious, worried, and unfamiliar with debt processes."
    }
    
    brief = "They just received their first-ever debt notice and are scared."
    
    prompt = f"""Based on the following debtor personality and situation, generate a scenario for a debt collection call.

PERSONALITY NAME: {personality['name']}
PERSONALITY DESCRIPTION: {personality['description']}
PERSONALITY SYSTEM PROMPT: {personality['system_prompt']}

SITUATION BRIEF: {brief}

Generate a title, a detailed backstory for the debtor, and a clear objective for them in the upcoming call."""
    
    response = await generate_structured_content(
        prompt=prompt,
        response_schema=scenario_schema,
        temperature=0.7
    )
    
    print(f"Generated Scenario:\n{response}")


async def example_4_conversation_with_history():
    """Example: Multi-turn conversation with history"""
    print("\n" + "="*60)
    print("Example 4: Conversation with History")
    print("="*60)
    
    history = [
        {"speaker": "user", "message": "Hi, I'm calling about my debt."},
        {"speaker": "agent", "message": "Hello! I'm here to help. Can you tell me more about your situation?"},
        {"speaker": "user", "message": "I lost my job last month and can't pay right now."}
    ]
    
    system_prompt = "You are an empathetic debt collection agent. Be understanding and help find solutions."
    
    response = await generate_conversational_response_with_history(
        history=history,
        system_prompt=system_prompt
    )
    
    print(f"Agent Response: {response}")


async def example_5_streaming_response():
    """Example: Streaming response for real-time output"""
    print("\n" + "="*60)
    print("Example 5: Streaming Response")
    print("="*60)
    
    print("Streaming response: ", end="", flush=True)
    
    async for chunk in generate_conversational_response_stream(
        prompt="Tell me a very short story about a helpful robot.",
        system_instruction="You are a creative storyteller. Keep it under 50 words.",
        temperature=0.9
    ):
        print(chunk, end="", flush=True)
    
    print("\n")


async def example_6_evaluation_scoring():
    """Example: Evaluate a conversation transcript (from PRD)"""
    print("\n" + "="*60)
    print("Example 6: Conversation Evaluation (PRD Use Case)")
    print("="*60)
    
    # Schema for evaluation scores
    evaluation_schema = genai.types.Schema(
        type=genai.types.Type.OBJECT,
        required=["scores", "evaluator_analysis"],
        properties={
            "scores": genai.types.Schema(
                type=genai.types.Type.OBJECT,
                required=["task_completion", "conversation_efficiency"],
                properties={
                    "task_completion": genai.types.Schema(type=genai.types.Type.INTEGER),
                    "conversation_efficiency": genai.types.Schema(type=genai.types.Type.INTEGER),
                }
            ),
            "evaluator_analysis": genai.types.Schema(type=genai.types.Type.STRING),
        }
    )
    
    transcript = """
agent: Hello, this is regarding your outstanding balance. How can I help you today?
debtor: I can't pay right now, I lost my job.
agent: I understand. Let's discuss a payment plan that works for you.
debtor: That sounds good, thank you.
"""
    
    prompt = f"""You are a conversation analyst. Your task is to evaluate the following debt collection call transcript.

DEBTOR'S OBJECTIVE: Express inability to pay due to job loss
AGENT'S GOAL: To collect the debt or arrange a payment plan in a compliant and efficient manner.

TRANSCRIPT:
{transcript}

Analyze the transcript and provide scores (0-100) for Task Completion (how well the agent moved towards their goal) and Conversation Efficiency (how relevant and non-repetitive the agent was). Also provide a brief analysis."""
    
    response = await generate_structured_content(
        prompt=prompt,
        response_schema=evaluation_schema,
        temperature=0.2
    )
    
    print(f"Evaluation Result:\n{response}")


async def main():
    """Run all examples"""
    print("\n🚀 Gemini Client Usage Examples")
    print("="*60)
    
    # Configure Gemini (make sure GEMINI_API_KEY is set in .env.local)
    configure_gemini()
    
    # Run examples
    await example_1_simple_conversation()
    await example_2_structured_output()
    await example_3_scenario_generation()
    await example_4_conversation_with_history()
    await example_5_streaming_response()
    await example_6_evaluation_scoring()
    
    print("\n✅ All examples completed!")


if __name__ == "__main__":
    asyncio.run(main())
