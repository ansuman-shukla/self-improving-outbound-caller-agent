"""
Unit Tests for Transcript Evaluator Service
Tests the AI-powered transcript evaluation logic with mocked Gemini API calls
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
import json
from unittest.mock import AsyncMock, patch
from services.transcript_evaluator import (
    evaluate_transcript,
    evaluate_transcript_dict,
    create_evaluation_schema,
    format_transcript_for_evaluation
)
from models.evaluation import TranscriptMessage, EvaluationScores


class TestSchemaCreation:
    """Test evaluation schema creation"""
    
    def test_create_evaluation_schema_structure(self):
        """Test that evaluation schema has correct structure"""
        schema = create_evaluation_schema()
        
        # Schema should be an object
        assert schema.type.name == "OBJECT"
        
        # Should have required fields
        assert "scores" in schema.required
        assert "evaluator_analysis" in schema.required
        
        # Scores should have nested structure
        assert "scores" in schema.properties
        scores_schema = schema.properties["scores"]
        assert scores_schema.type.name == "OBJECT"
        assert "task_completion" in scores_schema.required
        assert "conversation_efficiency" in scores_schema.required


class TestTranscriptFormatting:
    """Test transcript formatting for evaluation"""
    
    def test_format_transcript_with_objects(self):
        """Test formatting TranscriptMessage objects"""
        transcript = [
            TranscriptMessage(speaker="agent", message="Hello, I'm calling about your debt."),
            TranscriptMessage(speaker="debtor", message="I can't pay right now."),
            TranscriptMessage(speaker="agent", message="Let's discuss options.")
        ]
        
        formatted = format_transcript_for_evaluation(transcript)
        
        lines = formatted.split("\n")
        assert len(lines) == 3
        assert "AGENT: Hello, I'm calling about your debt." in formatted
        assert "DEBTOR: I can't pay right now." in formatted
        assert "AGENT: Let's discuss options." in formatted
    
    def test_format_transcript_with_dicts(self):
        """Test formatting transcript as dictionaries"""
        transcript = [
            {"speaker": "agent", "message": "Hello"},
            {"speaker": "debtor", "message": "Hi"}
        ]
        
        formatted = format_transcript_for_evaluation(transcript)
        
        assert "AGENT: Hello" in formatted
        assert "DEBTOR: Hi" in formatted
    
    def test_format_empty_transcript(self):
        """Test formatting empty transcript"""
        formatted = format_transcript_for_evaluation([])
        assert formatted == ""


class TestEvaluateTranscript:
    """Test transcript evaluation with mocked Gemini API"""
    
    @pytest.mark.asyncio
    async def test_evaluate_transcript_success(self):
        """Test successful transcript evaluation"""
        transcript = [
            {"speaker": "agent", "message": "Hello, calling about your debt."},
            {"speaker": "debtor", "message": "I can pay $100 today."},
            {"speaker": "agent", "message": "Great! Let me set that up."}
        ]
        
        # Mock Gemini API response
        mock_response = json.dumps({
            "scores": {
                "task_completion": 85,
                "conversation_efficiency": 90
            },
            "evaluator_analysis": "The agent handled the call efficiently and achieved payment commitment."
        })
        
        with patch('services.transcript_evaluator.generate_structured_content') as mock_generate:
            mock_generate.return_value = mock_response
            
            scores, analysis = await evaluate_transcript(
                transcript=transcript,
                scenario_objective="Avoid making payment"
            )
            
            # Verify scores
            assert isinstance(scores, EvaluationScores)
            assert scores.task_completion == 85
            assert scores.conversation_efficiency == 90
            
            # Verify analysis
            assert "efficiently" in analysis.lower()
            assert "payment" in analysis.lower()
            
            # Verify API was called
            assert mock_generate.called
            call_args = mock_generate.call_args
            
            # Check that transcript was included in prompt
            prompt = call_args[1]['prompt']
            assert "Hello, calling about your debt" in prompt
            assert "I can pay $100 today" in prompt
            
            # Check that objective was included
            assert "Avoid making payment" in prompt
    
    @pytest.mark.asyncio
    async def test_evaluate_transcript_with_objects(self):
        """Test evaluation with TranscriptMessage objects"""
        transcript = [
            TranscriptMessage(speaker="agent", message="How can I help?"),
            TranscriptMessage(speaker="debtor", message="I need more time.")
        ]
        
        mock_response = json.dumps({
            "scores": {
                "task_completion": 50,
                "conversation_efficiency": 75
            },
            "evaluator_analysis": "Agent was efficient but didn't secure commitment."
        })
        
        with patch('services.transcript_evaluator.generate_structured_content') as mock_generate:
            mock_generate.return_value = mock_response
            
            scores, analysis = await evaluate_transcript(
                transcript=transcript,
                scenario_objective="Get more time to pay"
            )
            
            assert scores.task_completion == 50
            assert scores.conversation_efficiency == 75
            assert "efficient" in analysis.lower()
    
    @pytest.mark.asyncio
    async def test_evaluate_transcript_score_ranges(self):
        """Test that scores are validated to be in 0-100 range"""
        transcript = [{"speaker": "agent", "message": "Test"}]
        
        # Test with valid scores
        mock_response = json.dumps({
            "scores": {
                "task_completion": 0,
                "conversation_efficiency": 100
            },
            "evaluator_analysis": "Test analysis"
        })
        
        with patch('services.transcript_evaluator.generate_structured_content') as mock_generate:
            mock_generate.return_value = mock_response
            
            scores, _ = await evaluate_transcript(transcript, "Test objective")
            
            # Pydantic should validate these are in range
            assert 0 <= scores.task_completion <= 100
            assert 0 <= scores.conversation_efficiency <= 100
    
    @pytest.mark.asyncio
    async def test_evaluate_transcript_json_error(self):
        """Test handling of invalid JSON response"""
        transcript = [{"speaker": "agent", "message": "Test"}]
        
        with patch('services.transcript_evaluator.generate_structured_content') as mock_generate:
            # Return invalid JSON
            mock_generate.return_value = "Not valid JSON"
            
            with pytest.raises(Exception) as exc_info:
                await evaluate_transcript(transcript, "Test objective")
            
            assert "Failed to parse evaluation response" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_evaluate_transcript_missing_fields(self):
        """Test handling of response with missing fields"""
        transcript = [{"speaker": "agent", "message": "Test"}]
        
        # Response missing required fields
        mock_response = json.dumps({
            "scores": {
                "task_completion": 75
                # Missing conversation_efficiency
            }
            # Missing evaluator_analysis
        })
        
        with patch('services.transcript_evaluator.generate_structured_content') as mock_generate:
            mock_generate.return_value = mock_response
            
            # Should handle gracefully with defaults
            scores, analysis = await evaluate_transcript(transcript, "Test")
            
            assert scores.task_completion == 75
            assert scores.conversation_efficiency == 0  # Default
            assert analysis == "No analysis provided."  # Default
    
    @pytest.mark.asyncio
    async def test_evaluate_transcript_api_error(self):
        """Test handling of API errors"""
        transcript = [{"speaker": "agent", "message": "Test"}]
        
        with patch('services.transcript_evaluator.generate_structured_content') as mock_generate:
            mock_generate.side_effect = Exception("API error")
            
            with pytest.raises(Exception) as exc_info:
                await evaluate_transcript(transcript, "Test objective")
            
            assert "Transcript evaluation failed" in str(exc_info.value)


class TestEvaluateTranscriptDict:
    """Test the dictionary wrapper function"""
    
    @pytest.mark.asyncio
    async def test_evaluate_transcript_dict_format(self):
        """Test that dict wrapper returns properly formatted dict"""
        transcript = [{"speaker": "agent", "message": "Hello"}]
        
        mock_response = json.dumps({
            "scores": {
                "task_completion": 80,
                "conversation_efficiency": 85
            },
            "evaluator_analysis": "Good performance"
        })
        
        with patch('services.transcript_evaluator.generate_structured_content') as mock_generate:
            mock_generate.return_value = mock_response
            
            result = await evaluate_transcript_dict(
                transcript_dicts=transcript,
                scenario_objective="Test objective"
            )
            
            # Verify result is a dict with correct structure
            assert isinstance(result, dict)
            assert "scores" in result
            assert "evaluator_analysis" in result
            
            # Verify scores structure
            scores = result["scores"]
            assert scores["task_completion"] == 80
            assert scores["conversation_efficiency"] == 85
            
            # Verify analysis
            assert result["evaluator_analysis"] == "Good performance"


class TestEvaluationCriteria:
    """Test that evaluation considers the right criteria"""
    
    @pytest.mark.asyncio
    async def test_evaluation_includes_criteria(self):
        """Test that evaluation prompt includes proper criteria"""
        transcript = [{"speaker": "agent", "message": "Test"}]
        
        mock_response = json.dumps({
            "scores": {"task_completion": 50, "conversation_efficiency": 50},
            "evaluator_analysis": "Test"
        })
        
        with patch('services.transcript_evaluator.generate_structured_content') as mock_generate:
            mock_generate.return_value = mock_response
            
            await evaluate_transcript(transcript, "Test objective")
            
            # Get the prompt that was sent
            call_args = mock_generate.call_args
            prompt = call_args[1]['prompt']
            
            # Verify criteria are mentioned
            assert "task completion" in prompt.lower()
            assert "conversation efficiency" in prompt.lower()
            assert "relevant" in prompt.lower()
            assert "repetition" in prompt.lower()
    
    @pytest.mark.asyncio
    async def test_evaluation_includes_goals(self):
        """Test that evaluation includes both agent and debtor goals"""
        transcript = [{"speaker": "agent", "message": "Test"}]
        objective = "Specific debtor objective here"
        
        mock_response = json.dumps({
            "scores": {"task_completion": 50, "conversation_efficiency": 50},
            "evaluator_analysis": "Test"
        })
        
        with patch('services.transcript_evaluator.generate_structured_content') as mock_generate:
            mock_generate.return_value = mock_response
            
            await evaluate_transcript(transcript, objective)
            
            call_args = mock_generate.call_args
            prompt = call_args[1]['prompt']
            
            # Verify both goals are in prompt
            assert objective in prompt
            assert "collect the debt" in prompt.lower() or "payment plan" in prompt.lower()


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
