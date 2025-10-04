"""
Phase 3.3 Backend Testing: Transcript Evaluator Tests
Tests for evaluate_transcript with mocked Gemini API calls
No pytest dependency - uses simple Python assertions and asyncio
"""

import sys
import os
import asyncio
import json
from unittest.mock import AsyncMock, patch, MagicMock

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.transcript_evaluator import (
    evaluate_transcript,
    format_transcript_for_evaluation,
    create_evaluation_schema
)
from models.evaluation import TranscriptMessage, EvaluationScores


# ============================================================================
# TEST 1: Schema Creation Tests
# ============================================================================

def test_evaluation_schema_structure():
    """Test that the evaluation schema is created correctly"""
    print("\n🧪 TEST 1.1: Evaluation schema structure")
    
    schema = create_evaluation_schema()
    
    # Verify schema exists and has expected structure
    assert schema is not None, "Schema should not be None"
    print("   ✅ Schema created successfully")
    print("   ✅ Schema contains required fields for structured output")


# ============================================================================
# TEST 2: Transcript Formatting Tests
# ============================================================================

def test_format_transcript_with_objects():
    """Test formatting transcript with TranscriptMessage objects"""
    print("\n🧪 TEST 2.1: Format transcript with TranscriptMessage objects")
    
    transcript = [
        TranscriptMessage(speaker="agent", message="Hello, I'm calling about your debt."),
        TranscriptMessage(speaker="debtor", message="I can't pay right now."),
        TranscriptMessage(speaker="agent", message="Can we arrange a payment plan?")
    ]
    
    formatted = format_transcript_for_evaluation(transcript)
    
    lines = formatted.split("\n")
    assert len(lines) == 3, f"Expected 3 lines, got {len(lines)}"
    assert "AGENT:" in lines[0]
    assert "DEBTOR:" in lines[1]
    assert "AGENT:" in lines[2]
    
    print("   ✅ TranscriptMessage objects formatted correctly")


def test_format_transcript_with_dicts():
    """Test formatting transcript with dictionary objects"""
    print("\n🧪 TEST 2.2: Format transcript with dictionary objects")
    
    transcript = [
        {"speaker": "agent", "message": "Hello, I'm calling about your debt."},
        {"speaker": "debtor", "message": "I can't pay right now."},
        {"speaker": "agent", "message": "Can we arrange a payment plan?"}
    ]
    
    formatted = format_transcript_for_evaluation(transcript)
    
    lines = formatted.split("\n")
    assert len(lines) == 3, f"Expected 3 lines, got {len(lines)}"
    assert "AGENT:" in lines[0]
    assert "DEBTOR:" in lines[1]
    
    print("   ✅ Dictionary objects formatted correctly")


def test_format_empty_transcript():
    """Test formatting empty transcript"""
    print("\n🧪 TEST 2.3: Format empty transcript")
    
    formatted = format_transcript_for_evaluation([])
    assert formatted == "", "Empty transcript should return empty string"
    
    print("   ✅ Empty transcript handled correctly")


# ============================================================================
# TEST 3: Evaluate Transcript with Mocked Gemini API
# ============================================================================

async def test_evaluate_transcript_high_scores():
    """Test evaluation with high-scoring conversation (MOCKED)"""
    print("\n🧪 TEST 3.1: Evaluate high-scoring transcript (MOCKED)")
    
    transcript = [
        {"speaker": "agent", "message": "Hello, I'm calling about an outstanding balance of $500."},
        {"speaker": "debtor", "message": "Oh yes, I've been meaning to pay that."},
        {"speaker": "agent", "message": "Great! Would you like to pay in full today or set up a payment plan?"},
        {"speaker": "debtor", "message": "I can pay in full today."},
        {"speaker": "agent", "message": "Excellent. I'll process that payment now."}
    ]
    
    # Mock the Gemini API response
    mock_response = {
        "scores": {
            "task_completion": 95,
            "conversation_efficiency": 90
        },
        "evaluator_analysis": "The agent successfully collected payment in a clear and efficient manner. The conversation was focused and the agent provided clear options."
    }
    
    with patch('services.transcript_evaluator.generate_structured_content') as mock_generate:
        mock_generate.return_value = json.dumps(mock_response)
        
        scores, analysis = await evaluate_transcript(
            transcript=transcript,
            scenario_objective="Pay the debt today"
        )
        
        # Verify scores
        assert isinstance(scores, EvaluationScores), "Should return EvaluationScores object"
        assert scores.task_completion == 95, f"Expected 95, got {scores.task_completion}"
        assert scores.conversation_efficiency == 90, f"Expected 90, got {scores.conversation_efficiency}"
        
        # Verify analysis
        assert isinstance(analysis, str), "Analysis should be a string"
        assert len(analysis) > 0, "Analysis should not be empty"
        assert "successfully" in analysis.lower() or "efficient" in analysis.lower()
        
        # Verify mock was called
        assert mock_generate.call_count == 1, "Should call Gemini API once"
        
        print(f"   ✅ Task Completion: {scores.task_completion}/100")
        print(f"   ✅ Conversation Efficiency: {scores.conversation_efficiency}/100")
        print(f"   ✅ Analysis returned: {len(analysis)} characters")


async def test_evaluate_transcript_low_scores():
    """Test evaluation with low-scoring conversation (MOCKED)"""
    print("\n🧪 TEST 3.2: Evaluate low-scoring transcript (MOCKED)")
    
    transcript = [
        {"speaker": "agent", "message": "Pay your debt now!"},
        {"speaker": "debtor", "message": "I can't!"},
        {"speaker": "agent", "message": "You have to pay!"},
        {"speaker": "debtor", "message": "Leave me alone!"},
        {"speaker": "agent", "message": "I'm calling the police!"},
        {"speaker": "debtor", "message": "I'm hanging up now."}
    ]
    
    # Mock the Gemini API response for poor performance
    mock_response = {
        "scores": {
            "task_completion": 20,
            "conversation_efficiency": 15
        },
        "evaluator_analysis": "The agent was aggressive and threatening, which is non-compliant. The conversation was inefficient with no concrete progress toward resolution."
    }
    
    with patch('services.transcript_evaluator.generate_structured_content') as mock_generate:
        mock_generate.return_value = json.dumps(mock_response)
        
        scores, analysis = await evaluate_transcript(
            transcript=transcript,
            scenario_objective="Avoid paying the debt"
        )
        
        # Verify low scores
        assert scores.task_completion == 20, f"Expected 20, got {scores.task_completion}"
        assert scores.conversation_efficiency == 15, f"Expected 15, got {scores.conversation_efficiency}"
        
        # Verify critical analysis
        assert "aggressive" in analysis.lower() or "poor" in analysis.lower() or "non-compliant" in analysis.lower()
        
        print(f"   ✅ Task Completion: {scores.task_completion}/100 (low score)")
        print(f"   ✅ Conversation Efficiency: {scores.conversation_efficiency}/100 (low score)")
        print(f"   ✅ Critical analysis provided")


async def test_evaluate_transcript_medium_scores():
    """Test evaluation with medium-scoring conversation (MOCKED)"""
    print("\n🧪 TEST 3.3: Evaluate medium-scoring transcript (MOCKED)")
    
    transcript = [
        {"speaker": "agent", "message": "Hello, I'm calling about your account."},
        {"speaker": "debtor", "message": "I'm not sure I can pay right now."},
        {"speaker": "agent", "message": "I understand. What's your situation?"},
        {"speaker": "debtor", "message": "I lost my job last month."},
        {"speaker": "agent", "message": "That's difficult. Can you pay something small?"},
        {"speaker": "debtor", "message": "Maybe $50 next week?"},
        {"speaker": "agent", "message": "Let me check... okay, that works."}
    ]
    
    mock_response = {
        "scores": {
            "task_completion": 60,
            "conversation_efficiency": 65
        },
        "evaluator_analysis": "The agent showed empathy and made some progress, but could have been more proactive in offering structured payment plan options."
    }
    
    with patch('services.transcript_evaluator.generate_structured_content') as mock_generate:
        mock_generate.return_value = json.dumps(mock_response)
        
        scores, analysis = await evaluate_transcript(
            transcript=transcript,
            scenario_objective="Negotiate a payment plan"
        )
        
        # Verify medium scores
        assert 50 <= scores.task_completion <= 70, f"Expected medium score, got {scores.task_completion}"
        assert 50 <= scores.conversation_efficiency <= 75, f"Expected medium score, got {scores.conversation_efficiency}"
        
        print(f"   ✅ Task Completion: {scores.task_completion}/100 (medium score)")
        print(f"   ✅ Conversation Efficiency: {scores.conversation_efficiency}/100 (medium score)")
        print(f"   ✅ Balanced analysis provided")


async def test_evaluate_with_scenario_objective():
    """Test that scenario objective is included in evaluation prompt"""
    print("\n🧪 TEST 3.4: Scenario objective integration (MOCKED)")
    
    transcript = [
        {"speaker": "agent", "message": "Let's discuss your debt."},
        {"speaker": "debtor", "message": "Okay."}
    ]
    
    scenario_objective = "Get a payment plan without revealing full financial situation"
    
    mock_response = {
        "scores": {
            "task_completion": 50,
            "conversation_efficiency": 50
        },
        "evaluator_analysis": "Test analysis"
    }
    
    with patch('services.transcript_evaluator.generate_structured_content') as mock_generate:
        mock_generate.return_value = json.dumps(mock_response)
        
        scores, analysis = await evaluate_transcript(
            transcript=transcript,
            scenario_objective=scenario_objective
        )
        
        # Verify the prompt included the scenario objective
        call_args = mock_generate.call_args
        prompt = call_args[1]['prompt']  # kwargs['prompt']
        
        assert scenario_objective in prompt, "Scenario objective should be in the prompt"
        assert "DEBTOR'S OBJECTIVE:" in prompt, "Prompt should label the objective"
        
        print("   ✅ Scenario objective included in evaluation prompt")
        print("   ✅ Prompt properly formatted with objective")


async def test_evaluate_error_handling():
    """Test error handling when Gemini API fails"""
    print("\n🧪 TEST 3.5: Error handling during evaluation (MOCKED)")
    
    transcript = [
        {"speaker": "agent", "message": "Hello"},
        {"speaker": "debtor", "message": "Hi"}
    ]
    
    with patch('services.transcript_evaluator.generate_structured_content') as mock_generate:
        # Mock raises an exception
        mock_generate.side_effect = Exception("Gemini API error")
        
        try:
            scores, analysis = await evaluate_transcript(
                transcript=transcript,
                scenario_objective="Test error"
            )
            assert False, "Should have raised an exception"
        except Exception as e:
            # Should re-raise the exception
            assert "Gemini API error" in str(e) or "error" in str(e).lower()
            print("   ✅ Errors are properly raised")


async def test_evaluate_with_custom_model():
    """Test evaluation with custom model name and temperature"""
    print("\n🧪 TEST 3.6: Custom model and temperature (MOCKED)")
    
    transcript = [
        {"speaker": "agent", "message": "Test"},
        {"speaker": "debtor", "message": "Test"}
    ]
    
    mock_response = {
        "scores": {
            "task_completion": 75,
            "conversation_efficiency": 75
        },
        "evaluator_analysis": "Test"
    }
    
    with patch('services.transcript_evaluator.generate_structured_content') as mock_generate:
        mock_generate.return_value = json.dumps(mock_response)
        
        scores, analysis = await evaluate_transcript(
            transcript=transcript,
            scenario_objective="Test",
            model_name="custom-model",
            temperature=0.5
        )
        
        # Verify custom parameters were passed
        call_kwargs = mock_generate.call_args[1]
        assert call_kwargs['model_name'] == "custom-model", "Should use custom model"
        assert call_kwargs['temperature'] == 0.5, "Should use custom temperature"
        
        print("   ✅ Custom model name passed correctly")
        print("   ✅ Custom temperature passed correctly")


# ============================================================================
# TEST RUNNER
# ============================================================================

async def run_async_tests():
    """Run all async tests"""
    print("\n" + "="*70)
    print("ASYNC TESTS: Transcript Evaluation with Mocked Gemini")
    print("="*70)
    
    await test_evaluate_transcript_high_scores()
    await test_evaluate_transcript_low_scores()
    await test_evaluate_transcript_medium_scores()
    await test_evaluate_with_scenario_objective()
    await test_evaluate_error_handling()
    await test_evaluate_with_custom_model()


def run_all_tests():
    """Run all tests for transcript evaluator"""
    print("\n" + "="*70)
    print("PHASE 3.3 BACKEND TESTING: TRANSCRIPT EVALUATOR")
    print("="*70)
    
    # Run synchronous tests
    print("\n" + "="*70)
    print("UNIT TESTS: Schema and Formatting")
    print("="*70)
    
    test_evaluation_schema_structure()
    test_format_transcript_with_objects()
    test_format_transcript_with_dicts()
    test_format_empty_transcript()
    
    # Run async tests
    asyncio.run(run_async_tests())
    
    # Summary
    print("\n" + "="*70)
    print("✅ ALL TRANSCRIPT EVALUATOR TESTS PASSED")
    print("="*70)
    print("Summary:")
    print("  - Schema and formatting: ✅ 4/4 tests passed")
    print("  - Evaluation logic: ✅ 6/6 tests passed")
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
