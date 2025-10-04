"""
Test script to verify the improved conversation simulation
This demonstrates:
1. Variable replacement ({name} and {amount})
2. Proper context separation between agent and debtor
3. Correct system prompt usage
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import asyncio
from services.conversation_moderator import run_conversation_simulation, replace_variables_in_prompt


# Test agent prompt with variables
AGENT_PROMPT = """You are "Ana" an assistant working for SBI BANK India. Your job is to call customers with overdue credit card bills. The customer's name is {name}, and the overdue amount is ₹{amount}. Start by confirming the customer's identity.

Begin the call by greeting {name} politely. Then, remind {name} about the outstanding credit card bill of ₹{amount}. Urge {name} to settle this debt as quickly as possible, while remaining professional and courteous throughout the conversation. Allow user to end the conversation."""


# Test debtor personality
DEBTOR_PROMPT = """You are a struggling parent named {name}. You have a daughter named Priya who is in school. You recently paid her school fees and are now completely out of money. You owe ₹{amount} on your credit card.

You are:
- Anxious and stressed about money
- Prioritizing your daughter's education above all else
- Honest about your financial situation
- Hoping for understanding and a payment plan

Stay in character throughout the conversation."""


# Test scenario objective
SCENARIO_OBJECTIVE = "Try to negotiate a payment plan while explaining that you just paid your daughter's school fees and have no money right now."


async def test_variable_replacement():
    """Test that variables are replaced correctly"""
    print("\n" + "="*80)
    print("TEST 1: Variable Replacement")
    print("="*80)
    
    # Test replacement
    test_name = "Priya Sharma"
    test_amount = 5000.0
    
    replaced = replace_variables_in_prompt(AGENT_PROMPT, name=test_name, amount=test_amount)
    
    print(f"\nOriginal prompt contains: {{name}} and {{amount}}")
    print(f"After replacement:")
    print(f"  - Name should be: {test_name}")
    print(f"  - Amount should be: ₹{test_amount:,.2f}")
    
    if "{name}" in replaced:
        print("  ❌ FAILED: {name} variable not replaced")
    else:
        print(f"  ✅ PASSED: {{name}} replaced with '{test_name}'")
    
    if "{amount}" in replaced:
        print("  ❌ FAILED: {amount} variable not replaced")
    else:
        print(f"  ✅ PASSED: {{amount}} replaced with '₹{test_amount:,.2f}'")


async def test_conversation_simulation():
    """Test actual conversation simulation with proper context separation"""
    print("\n" + "="*80)
    print("TEST 2: Conversation Simulation with Proper Context")
    print("="*80)
    print("\nThis test will run a SHORT conversation simulation (limited to 3 turns)")
    print("to verify that:")
    print("  1. Variables are replaced in both agent and debtor prompts")
    print("  2. Agent and debtor messages stay separate")
    print("  3. Proper context is maintained throughout")
    print("\nStarting simulation...\n")
    
    try:
        transcript = await run_conversation_simulation(
            agent_system_prompt=AGENT_PROMPT,
            personality_system_prompt=DEBTOR_PROMPT,
            scenario_objective=SCENARIO_OBJECTIVE,
            debtor_name="Priya Sharma",
            debtor_amount=5000.0,
            model_name="gemini-2.0-flash-exp",  # Use the latest model
            agent_temperature=0.7,
            debtor_temperature=0.7
        )
        
        print("="*80)
        print("CONVERSATION TRANSCRIPT")
        print("="*80)
        
        for i, msg in enumerate(transcript, 1):
            speaker_label = "AGENT" if msg.speaker == "agent" else "DEBTOR"
            print(f"\n{speaker_label} (Message {i}):")
            print(f"{msg.message}")
            print("-" * 80)
        
        # Verify results
        print("\n" + "="*80)
        print("VERIFICATION")
        print("="*80)
        
        # Check if messages alternate correctly
        speakers = [msg.speaker for msg in transcript]
        alternates_correctly = all(
            speakers[i] != speakers[i+1] 
            for i in range(len(speakers)-1)
        )
        
        if alternates_correctly:
            print("✅ PASSED: Messages alternate correctly between agent and debtor")
        else:
            print("❌ FAILED: Message speakers don't alternate correctly")
        
        # Check if any message contains unreplaced variables
        all_messages = " ".join([msg.message for msg in transcript])
        has_unreplaced = "{name}" in all_messages or "{amount}" in all_messages
        
        if has_unreplaced:
            print("❌ FAILED: Some variables were not replaced")
        else:
            print("✅ PASSED: All variables were replaced correctly")
        
        # Check for the combined message issue
        # In the old implementation, sometimes both agent and debtor messages
        # were combined in a single message
        suspicious_patterns = [
            "debtor:",
            "agent:",
            "**(I",  # Stage directions like **(I answer the phone
        ]
        
        has_mixed_speakers = False
        for msg in transcript:
            msg_lower = msg.message.lower()
            if msg.speaker == "agent" and any(pattern in msg_lower for pattern in ["debtor:", "**(i answer", "**(i sigh"]):
                has_mixed_speakers = True
                break
            elif msg.speaker == "debtor" and "agent:" in msg_lower:
                has_mixed_speakers = True
                break
        
        if has_mixed_speakers:
            print("❌ WARNING: Possible mixed speaker context detected in messages")
        else:
            print("✅ PASSED: No mixed speaker context detected")
        
        print(f"\nTotal messages: {len(transcript)}")
        print(f"Agent messages: {sum(1 for msg in transcript if msg.speaker == 'agent')}")
        print(f"Debtor messages: {sum(1 for msg in transcript if msg.speaker == 'debtor')}")
        
    except Exception as e:
        print(f"\n❌ ERROR: Conversation simulation failed")
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()


async def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("IMPROVED CONVERSATION SIMULATION TEST SUITE")
    print("="*80)
    print("\nThis test suite verifies the improvements made to conversation simulation:")
    print("  1. Variable replacement in prompts")
    print("  2. Proper context separation using Google Genai SDK")
    print("  3. Prevention of message mixing between speakers")
    
    # Test 1: Variable replacement
    await test_variable_replacement()
    
    # Test 2: Full conversation simulation
    await test_conversation_simulation()
    
    print("\n" + "="*80)
    print("TEST SUITE COMPLETE")
    print("="*80)


if __name__ == "__main__":
    asyncio.run(main())
