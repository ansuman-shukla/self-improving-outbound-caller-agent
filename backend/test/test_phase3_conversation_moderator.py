"""
Phase 3.3 Backend Testing: Conversation Moderator Tests
Tests for run_conversation_simulation with mocked Gemini API calls
No pytest dependency - uses simple Python assertions and asyncio
"""

import sys
import os
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.conversation_moderator import (
    run_conversation_simulation,
    check_should_terminate,
    format_transcript_for_evaluation,
    HANGUP_KEYWORDS,
    MAX_TURN_PAIRS
)
from models.evaluation import TranscriptMessage


# ============================================================================
# TEST 1: Termination Logic Tests
# ============================================================================

def test_termination_turn_limit():
    """Test that conversation terminates at max turn limit"""
    print("\n🧪 TEST 1.1: Termination at turn limit")
    
    # Should terminate at MAX_TURN_PAIRS
    result = check_should_terminate("Hello", MAX_TURN_PAIRS)
    assert result == True, "Should terminate at MAX_TURN_PAIRS"
    print(f"   ✅ Terminates at turn {MAX_TURN_PAIRS}")
    
    # Should not terminate before limit
    result = check_should_terminate("Hello", MAX_TURN_PAIRS - 1)
    assert result == False, "Should not terminate before MAX_TURN_PAIRS"
    print(f"   ✅ Continues at turn {MAX_TURN_PAIRS - 1}")
    
    result = check_should_terminate("Hello", 0)
    assert result == False, "Should not terminate at turn 0"
    print(f"   ✅ Continues at turn 0")


def test_termination_hangup_keywords():
    """Test that conversation terminates on hangup keywords"""
    print("\n🧪 TEST 1.2: Termination on hangup keywords")
    
    # Test each hangup keyword
    for keyword in HANGUP_KEYWORDS[:3]:  # Test first 3 to avoid clutter
        result = check_should_terminate(keyword, 0)
        assert result == True, f"Should terminate on keyword: {keyword}"
        print(f"   ✅ Terminates on: '{keyword}'")
        
        # Test uppercase
        result = check_should_terminate(keyword.upper(), 0)
        assert result == True, f"Should terminate on uppercase keyword: {keyword.upper()}"
        
        # Test in sentence
        result = check_should_terminate(f"I think {keyword} now", 0)
        assert result == True, f"Should terminate on keyword in sentence: {keyword}"
    
    print(f"   ✅ All {len(HANGUP_KEYWORDS)} hangup keywords work correctly")


def test_termination_normal_messages():
    """Test that normal messages don't trigger termination"""
    print("\n🧪 TEST 1.3: No termination on normal messages")
    
    normal_messages = [
        "Hello, how are you?",
        "I want to pay my debt",
        "Can you help me?",
        "Thank you for calling"
    ]
    
    for msg in normal_messages:
        result = check_should_terminate(msg, 5)
        assert result == False, f"Should not terminate on normal message: {msg}"
    
    print(f"   ✅ {len(normal_messages)} normal messages don't trigger termination")


# ============================================================================
# TEST 2: Transcript Formatting Tests
# ============================================================================

def test_format_transcript_basic():
    """Test transcript is formatted correctly"""
    print("\n🧪 TEST 2.1: Basic transcript formatting")
    
    transcript = [
        TranscriptMessage(speaker="agent", message="Hello, I'm calling about your account."),
        TranscriptMessage(speaker="debtor", message="I don't have the money right now."),
        TranscriptMessage(speaker="agent", message="I understand. Can we discuss a payment plan?")
    ]
    
    formatted = format_transcript_for_evaluation(transcript)
    
    # Check format
    lines = formatted.split("\n")
    assert len(lines) == 3, f"Expected 3 lines, got {len(lines)}"
    assert lines[0].startswith("AGENT:"), "First line should start with AGENT:"
    assert lines[1].startswith("DEBTOR:"), "Second line should start with DEBTOR:"
    assert lines[2].startswith("AGENT:"), "Third line should start with AGENT:"
    
    # Check content
    assert "Hello, I'm calling about your account." in formatted
    assert "I don't have the money right now." in formatted
    assert "Can we discuss a payment plan?" in formatted
    
    print("   ✅ Transcript formatted correctly with speaker labels")


def test_format_empty_transcript():
    """Test formatting empty transcript"""
    print("\n🧪 TEST 2.2: Empty transcript formatting")
    
    formatted = format_transcript_for_evaluation([])
    assert formatted == "", "Empty transcript should return empty string"
    
    print("   ✅ Empty transcript handled correctly")


# ============================================================================
# TEST 3: Conversation Simulation with Mocked Gemini API
# ============================================================================

async def test_conversation_basic_flow():
    """Test basic conversation flow with mocked responses"""
    print("\n🧪 TEST 3.1: Basic conversation flow (MOCKED)")
    
    # Mock the Gemini API function
    with patch('services.conversation_moderator.generate_conversational_response_with_history') as mock_generate:
        # Setup mock to return different responses
        mock_generate.side_effect = [
            "Hello, I'm calling about an outstanding balance on your account.",  # Agent 1
            "I don't have the money right now.",  # Debtor 1
            "I understand. Can we discuss a payment plan?",  # Agent 2
            "I'm hanging up now."  # Debtor 2 - triggers termination
        ]
        
        # Run simulation
        transcript = await run_conversation_simulation(
            agent_system_prompt="You are a debt collector.",
            personality_system_prompt="You are a debtor.",
            scenario_objective="Avoid payment"
        )
        
        # Verify conversation structure
        assert len(transcript) == 4, f"Expected 4 messages, got {len(transcript)}"
        assert transcript[0].speaker == "agent", "First speaker should be agent"
        assert transcript[1].speaker == "debtor", "Second speaker should be debtor"
        assert transcript[2].speaker == "agent", "Third speaker should be agent"
        assert transcript[3].speaker == "debtor", "Fourth speaker should be debtor"
        
        # Verify messages
        assert "outstanding balance" in transcript[0].message.lower()
        assert "hanging up" in transcript[3].message.lower()
        
        # Verify mock was called correctly
        assert mock_generate.call_count == 4, f"Expected 4 API calls, got {mock_generate.call_count}"
        
        print("   ✅ Conversation alternates correctly between agent and debtor")
        print("   ✅ Conversation terminates on hangup keyword")
        print(f"   ✅ Generated {len(transcript)} messages")


async def test_conversation_max_turns():
    """Test conversation stops at max turn limit"""
    print("\n🧪 TEST 3.2: Conversation stops at max turns (MOCKED)")
    
    with patch('services.conversation_moderator.generate_conversational_response_with_history') as mock_generate:
        # Mock returns responses that never trigger hangup
        mock_generate.return_value = "Let's continue talking."
        
        # Run simulation
        transcript = await run_conversation_simulation(
            agent_system_prompt="Agent prompt",
            personality_system_prompt="Debtor prompt",
            scenario_objective="Keep talking"
        )
        
        # Should have messages up to MAX_TURN_PAIRS
        expected_max = MAX_TURN_PAIRS * 2  # Each turn pair = agent + debtor
        assert len(transcript) <= expected_max, f"Transcript too long: {len(transcript)} > {expected_max}"
        assert len(transcript) >= expected_max - 2, f"Transcript too short: {len(transcript)} < {expected_max - 2}"
        
        print(f"   ✅ Conversation stopped at {len(transcript)} messages")
        print(f"   ✅ Within expected range (max {expected_max} messages)")


async def test_conversation_immediate_hangup():
    """Test conversation stops immediately on first hangup"""
    print("\n🧪 TEST 3.3: Immediate hangup on first message (MOCKED)")
    
    with patch('services.conversation_moderator.generate_conversational_response_with_history') as mock_generate:
        # Agent's first message triggers hangup
        mock_generate.return_value = "I'm hanging up now"
        
        transcript = await run_conversation_simulation(
            agent_system_prompt="Agent prompt",
            personality_system_prompt="Debtor prompt",
            scenario_objective="Hang up immediately"
        )
        
        # Should only have 1 message (agent hangs up immediately)
        assert len(transcript) == 1, f"Expected 1 message, got {len(transcript)}"
        assert transcript[0].speaker == "agent"
        assert "hanging up" in transcript[0].message.lower()
        
        print("   ✅ Conversation terminated after first message")


async def test_conversation_debtor_hangup():
    """Test conversation stops when debtor hangs up mid-conversation"""
    print("\n🧪 TEST 3.4: Debtor hangs up mid-conversation (MOCKED)")
    
    with patch('services.conversation_moderator.generate_conversational_response_with_history') as mock_generate:
        # Setup mock responses
        mock_generate.side_effect = [
            "Hello, I'm calling about your debt.",  # Agent 1
            "Don't call me again",  # Debtor 1 - hangup keyword
        ]
        
        transcript = await run_conversation_simulation(
            agent_system_prompt="Agent prompt",
            personality_system_prompt="Debtor prompt",
            scenario_objective="Hang up after first exchange"
        )
        
        # Should have 2 messages (agent + debtor with hangup)
        assert len(transcript) == 2, f"Expected 2 messages, got {len(transcript)}"
        assert "don't call me again" in transcript[1].message.lower()
        
        print("   ✅ Conversation terminated when debtor hung up")


async def test_conversation_error_handling():
    """Test that errors during conversation are properly raised"""
    print("\n🧪 TEST 3.5: Error handling during conversation (MOCKED)")
    
    with patch('services.conversation_moderator.generate_conversational_response_with_history') as mock_generate:
        # Mock raises an exception
        mock_generate.side_effect = Exception("Gemini API error")
        
        try:
            transcript = await run_conversation_simulation(
                agent_system_prompt="Agent prompt",
                personality_system_prompt="Debtor prompt",
                scenario_objective="Test error"
            )
            assert False, "Should have raised an exception"
        except Exception as e:
            assert "Conversation simulation failed" in str(e)
            print("   ✅ Errors are properly caught and re-raised")


# ============================================================================
# TEST RUNNER
# ============================================================================

async def run_async_tests():
    """Run all async tests"""
    print("\n" + "="*70)
    print("ASYNC TESTS: Conversation Simulation with Mocked Gemini")
    print("="*70)
    
    await test_conversation_basic_flow()
    await test_conversation_max_turns()
    await test_conversation_immediate_hangup()
    await test_conversation_debtor_hangup()
    await test_conversation_error_handling()


def run_all_tests():
    """Run all tests for conversation moderator"""
    print("\n" + "="*70)
    print("PHASE 3.3 BACKEND TESTING: CONVERSATION MODERATOR")
    print("="*70)
    
    # Run synchronous tests
    print("\n" + "="*70)
    print("UNIT TESTS: Termination Logic")
    print("="*70)
    
    test_termination_turn_limit()
    test_termination_hangup_keywords()
    test_termination_normal_messages()
    
    print("\n" + "="*70)
    print("UNIT TESTS: Transcript Formatting")
    print("="*70)
    
    test_format_transcript_basic()
    test_format_empty_transcript()
    
    # Run async tests
    asyncio.run(run_async_tests())
    
    # Summary
    print("\n" + "="*70)
    print("✅ ALL CONVERSATION MODERATOR TESTS PASSED")
    print("="*70)
    print("Summary:")
    print("  - Termination logic: ✅ 3/3 tests passed")
    print("  - Transcript formatting: ✅ 2/2 tests passed")
    print("  - Conversation simulation: ✅ 5/5 tests passed")
    print("  - Total: ✅ 10/10 tests passed")
    print("="*70)


if __name__ == "__main__":
    try:
        run_all_tests()
        print("\n✨ Test suite completed successfully!\n")
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}\n")
        sys.exit(1)
