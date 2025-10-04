"""
Unit Tests for Conversation Moderator Service
Tests the turn-by-turn conversation simulation logic with mocked Gemini API calls
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from services.conversation_moderator import (
    run_conversation_simulation,
    check_should_terminate,
    format_transcript_for_evaluation,
    replace_variables_in_prompt,
    HANGUP_KEYWORDS,
    MAX_TURN_PAIRS
)
from models.evaluation import TranscriptMessage


class TestVariableReplacement:
    """Test variable replacement in prompts"""
    
    def test_replace_name_only(self):
        """Test replacing {name} variable"""
        prompt = "Hello {name}, how are you?"
        result = replace_variables_in_prompt(prompt, name="John Doe")
        assert result == "Hello John Doe, how are you?"
    
    def test_replace_amount_only(self):
        """Test replacing {amount} variable"""
        prompt = "You owe {amount} to the bank."
        result = replace_variables_in_prompt(prompt, amount=5000.0)
        assert result == "You owe ₹5,000.00 to the bank."
    
    def test_replace_both_variables(self):
        """Test replacing both {name} and {amount}"""
        prompt = "Hello {name}, you owe {amount}."
        result = replace_variables_in_prompt(prompt, name="Jane Smith", amount=12500.50)
        assert result == "Hello Jane Smith, you owe ₹12,500.50."
    
    def test_replace_no_variables(self):
        """Test prompt without variables"""
        prompt = "This is a generic message."
        result = replace_variables_in_prompt(prompt)
        assert result == "This is a generic message."
    
    def test_replace_multiple_occurrences(self):
        """Test replacing multiple occurrences of same variable"""
        prompt = "Dear {name}, I'm calling {name} to discuss your debt."
        result = replace_variables_in_prompt(prompt, name="Bob")
        assert result == "Dear Bob, I'm calling Bob to discuss your debt."


class TestTerminationLogic:
    """Test conversation termination conditions"""
    
    def test_check_should_terminate_turn_limit(self):
        """Test that conversation terminates at max turn limit"""
        # Should terminate at MAX_TURN_PAIRS
        assert check_should_terminate("Hello", MAX_TURN_PAIRS) == True
        
        # Should not terminate before limit
        assert check_should_terminate("Hello", MAX_TURN_PAIRS - 1) == False
        assert check_should_terminate("Hello", 0) == False
    
    def test_check_should_terminate_hangup_keywords(self):
        """Test that conversation terminates on hangup keywords"""
        # Test each hangup keyword
        for keyword in HANGUP_KEYWORDS:
            assert check_should_terminate(keyword, 0) == True
            assert check_should_terminate(keyword.upper(), 0) == True
            assert check_should_terminate(f"I think {keyword} now", 0) == True
    
    def test_check_should_terminate_normal_messages(self):
        """Test that normal messages don't trigger termination"""
        normal_messages = [
            "Hello, how are you?",
            "I want to pay my debt",
            "Can you help me?",
            "Thank you for calling"
        ]
        
        for msg in normal_messages:
            assert check_should_terminate(msg, 5) == False


class TestTranscriptFormatting:
    """Test transcript formatting utilities"""
    
    def test_format_transcript_for_evaluation(self):
        """Test transcript is formatted correctly for evaluation"""
        transcript = [
            TranscriptMessage(speaker="agent", message="Hello, I'm calling about your account."),
            TranscriptMessage(speaker="debtor", message="I don't have the money right now."),
            TranscriptMessage(speaker="agent", message="I understand. Can we discuss a payment plan?")
        ]
        
        formatted = format_transcript_for_evaluation(transcript)
        
        # Check format
        lines = formatted.split("\n")
        assert len(lines) == 3
        assert lines[0].startswith("AGENT:")
        assert lines[1].startswith("DEBTOR:")
        assert lines[2].startswith("AGENT:")
        
        # Check content
        assert "Hello, I'm calling about your account." in formatted
        assert "I don't have the money right now." in formatted
        assert "Can we discuss a payment plan?" in formatted
    
    def test_format_empty_transcript(self):
        """Test formatting empty transcript"""
        formatted = format_transcript_for_evaluation([])
        assert formatted == ""


class TestConversationSimulation:
    """Test the full conversation simulation with mocked Gemini API"""
    
    @pytest.mark.asyncio
    async def test_conversation_basic_flow(self):
        """Test basic conversation flow with mocked responses"""
        # Mock the Gemini API function
        with patch('services.conversation_moderator.generate_next_turn_with_proper_history') as mock_generate:
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
                scenario_objective="Avoid payment",
                debtor_name="John Doe",
                debtor_amount=5000.0
            )
            
            # Verify conversation structure
            assert len(transcript) == 4  # Should stop after "I'm hanging up"
            assert transcript[0].speaker == "agent"
            assert transcript[1].speaker == "debtor"
            assert transcript[2].speaker == "agent"
            assert transcript[3].speaker == "debtor"
            
            # Verify messages
            assert "outstanding balance" in transcript[0].message.lower()
            assert "hanging up" in transcript[3].message.lower()
            
            # Verify mock was called correctly
            assert mock_generate.call_count == 4
    
    @pytest.mark.asyncio
    async def test_conversation_max_turns(self):
        """Test conversation stops at max turn limit"""
        with patch('services.conversation_moderator.generate_next_turn_with_proper_history') as mock_generate:
            # Mock returns responses that never trigger hangup
            mock_generate.return_value = "Let's continue talking."
            
            # Run simulation
            transcript = await run_conversation_simulation(
                agent_system_prompt="Agent prompt",
                personality_system_prompt="Debtor prompt",
                scenario_objective="Keep talking",
                debtor_name="Test User"
            )
            
            # Should have exactly MAX_TURN_PAIRS * 2 messages (agent + debtor per turn)
            # Actually, it may be MAX_TURN_PAIRS * 2 or MAX_TURN_PAIRS * 2 - 1 depending on termination check
            assert len(transcript) <= MAX_TURN_PAIRS * 2
            assert len(transcript) >= MAX_TURN_PAIRS * 2 - 1
    
    @pytest.mark.asyncio
    async def test_conversation_immediate_hangup(self):
        """Test conversation stops immediately on first hangup"""
        with patch('services.conversation_moderator.generate_next_turn_with_proper_history') as mock_generate:
            # First response (agent) triggers hangup
            mock_generate.return_value = "I'm hanging up now"
            
            transcript = await run_conversation_simulation(
                agent_system_prompt="Agent prompt",
                personality_system_prompt="Debtor prompt",
                scenario_objective="Hang up immediately",
                debtor_name="Test User"
            )
            
            # Should have only 1 message (agent hangs up immediately)
            assert len(transcript) == 1
            assert transcript[0].speaker == "agent"
    
    @pytest.mark.asyncio
    async def test_conversation_error_handling(self):
        """Test that errors are properly propagated"""
        with patch('services.conversation_moderator.generate_next_turn_with_proper_history') as mock_generate:
            # Simulate API error
            mock_generate.side_effect = Exception("Gemini API error")
            
            # Should raise exception
            with pytest.raises(Exception) as exc_info:
                await run_conversation_simulation(
                    agent_system_prompt="Agent prompt",
                    personality_system_prompt="Debtor prompt",
                    scenario_objective="Test error",
                    debtor_name="Test User"
                )
            
            assert "Conversation simulation failed" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_conversation_history_passed_correctly(self):
        """Test that conversation history is accumulated and passed correctly"""
        with patch('services.conversation_moderator.generate_next_turn_with_proper_history') as mock_generate:
            # Track history passed to mock
            call_histories = []
            
            def track_history(contents_history, system_prompt, model_name, temperature):
                call_histories.append(len(contents_history))
                if len(call_histories) == 1:
                    return "Agent message 1"
                elif len(call_histories) == 2:
                    return "Debtor message 1"
                elif len(call_histories) == 3:
                    return "I'm hanging up"
                return "Continue"
            
            mock_generate.side_effect = track_history
            
            await run_conversation_simulation(
                agent_system_prompt="Agent prompt",
                personality_system_prompt="Debtor prompt",
                scenario_objective="Test history",
                debtor_name="Test User"
            )
            
            # Verify history grows: 0 → 1 → 2
            assert call_histories[0] == 0  # First call has empty history
            assert call_histories[1] == 1  # Second call has 1 message
            assert call_histories[2] == 2  # Third call has 2 messages
    
    @pytest.mark.asyncio
    async def test_conversation_objective_injection(self):
        """Test that scenario objective is injected into debtor prompt"""
        with patch('services.conversation_moderator.generate_conversational_response_with_history') as mock_generate:
            mock_generate.return_value = "I'm hanging up"
            
            objective = "Get a payment plan without revealing income"
            
            await run_conversation_simulation(
                agent_system_prompt="Agent prompt",
                personality_system_prompt="Debtor personality",
                scenario_objective=objective
            )
            
            # Check that one of the calls included the objective
            found_objective = False
            for call in mock_generate.call_args_list:
                system_prompt = call[1]['system_prompt']
                if objective in system_prompt:
                    found_objective = True
                    break
            
            assert found_objective, "Scenario objective should be injected into debtor system prompt"


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
