"""
Unit tests for Tuning Service
Tests the core logic functions for the Automated Tuning Loop module
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from models.tuning_loop import (
    TuningStatus,
    ScenarioWeight,
    TuningConfig,
    TuningIteration,
    TuningLoopCreate,
    TuningLoopResponse
)
from services.tuning_service import (
    calculate_weighted_average,
    run_writer_critique_cycle,
    build_context_package,
    create_writer_schema,
    create_critique_schema
)
from bson import ObjectId


class TestTuningLoopModels:
    """Test Pydantic models for TuningLoop"""
    
    def test_scenario_weight_validation(self):
        """Test ScenarioWeight model validation"""
        # Valid weight
        sw = ScenarioWeight(scenario_id="507f1f77bcf86cd799439012", weight=3)
        assert sw.weight == 3
        assert sw.scenario_id == "507f1f77bcf86cd799439012"
        
        # Weight must be 1-5
        with pytest.raises(ValueError):
            ScenarioWeight(scenario_id="507f1f77bcf86cd799439012", weight=0)
        
        with pytest.raises(ValueError):
            ScenarioWeight(scenario_id="507f1f77bcf86cd799439012", weight=6)
    
    def test_tuning_config_validation(self):
        """Test TuningConfig model validation"""
        config = TuningConfig(
            target_score=85.0,
            max_iterations=5,
            scenario_weights=[
                ScenarioWeight(scenario_id="scen1", weight=4),
                ScenarioWeight(scenario_id="scen2", weight=3)
            ]
        )
        assert config.target_score == 85.0
        assert config.max_iterations == 5
        assert len(config.scenario_weights) == 2
        
        # Target score must be 0-100
        with pytest.raises(ValueError):
            TuningConfig(
                target_score=150.0,
                max_iterations=5,
                scenario_weights=[]
            )
    
    def test_tuning_iteration_model(self):
        """Test TuningIteration model"""
        iteration = TuningIteration(
            iteration_number=1,
            prompt_id="prompt123",
            evaluation_ids=["eval1", "eval2"],
            weighted_score=78.5
        )
        assert iteration.iteration_number == 1
        assert iteration.weighted_score == 78.5
        assert len(iteration.evaluation_ids) == 2
    
    def test_tuning_loop_create_validation(self):
        """Test TuningLoopCreate request model"""
        create_request = TuningLoopCreate(
            initial_prompt_id="prompt123",
            target_score=85.0,
            max_iterations=5,
            scenarios=[
                ScenarioWeight(scenario_id="scen1", weight=4)
            ]
        )
        assert create_request.initial_prompt_id == "prompt123"
        assert len(create_request.scenarios) == 1
        
        # Scenarios must not be empty
        with pytest.raises(ValueError):
            TuningLoopCreate(
                initial_prompt_id="prompt123",
                target_score=85.0,
                max_iterations=5,
                scenarios=[]
            )
    
    def test_tuning_loop_response_model(self):
        """Test TuningLoopResponse model"""
        from datetime import datetime
        
        response = TuningLoopResponse(
            _id="loop123",
            status=TuningStatus.COMPLETED,
            config=TuningConfig(
                target_score=85.0,
                max_iterations=5,
                scenario_weights=[ScenarioWeight(scenario_id="scen1", weight=3)]
            ),
            iterations=[
                TuningIteration(
                    iteration_number=1,
                    prompt_id="prompt1",
                    evaluation_ids=["eval1"],
                    weighted_score=75.0
                )
            ],
            final_prompt_id="prompt2",
            created_at=datetime.now()
        )
        assert response.status == TuningStatus.COMPLETED
        assert response.final_prompt_id == "prompt2"
        assert len(response.iterations) == 1


class TestCalculateWeightedAverage:
    """Test calculate_weighted_average function"""
    
    @pytest.mark.asyncio
    async def test_calculate_weighted_average_basic(self):
        """Test basic weighted average calculation"""
        # Create valid ObjectIds for testing
        eval1_id = ObjectId()
        eval2_id = ObjectId()
        scenario1_id = ObjectId()
        scenario2_id = ObjectId()
        
        # Mock evaluation data
        mock_evaluations = {
            str(eval1_id): {
                "_id": eval1_id,
                "scenario_id": scenario1_id,
                "status": "COMPLETED",
                "scores": {
                    "task_completion": 80,
                    "conversation_efficiency": 70
                }
            },
            str(eval2_id): {
                "_id": eval2_id,
                "scenario_id": scenario2_id,
                "status": "COMPLETED",
                "scores": {
                    "task_completion": 60,
                    "conversation_efficiency": 80
                }
            }
        }
        
        # Mock collection
        mock_collection = AsyncMock()
        
        async def mock_find_one(query):
            eval_id = str(query["_id"])
            return mock_evaluations.get(eval_id)
        
        mock_collection.find_one = mock_find_one
        
        with patch('services.tuning_service.get_evaluations_collection', return_value=mock_collection):
            scenario_weights = [
                ScenarioWeight(scenario_id=str(scenario1_id), weight=4),
                ScenarioWeight(scenario_id=str(scenario2_id), weight=2)
            ]
            
            # Expected calculation:
            # Eval1: (80+70)/2 = 75, weighted = 75*4 = 300
            # Eval2: (60+80)/2 = 70, weighted = 70*2 = 140
            # Total: (300+140)/(4+2) = 440/6 = 73.33
            
            score = await calculate_weighted_average(
                evaluation_ids=[str(eval1_id), str(eval2_id)],
                scenario_weights=scenario_weights
            )
            
            assert score == pytest.approx(73.33, rel=0.01)
    
    @pytest.mark.asyncio
    async def test_calculate_weighted_average_single_evaluation(self):
        """Test weighted average with single evaluation"""
        eval_id = ObjectId()
        scenario_id = ObjectId()
        
        mock_evaluation = {
            "_id": eval_id,
            "scenario_id": scenario_id,
            "status": "COMPLETED",
            "scores": {
                "task_completion": 90,
                "conversation_efficiency": 85
            }
        }
        
        mock_collection = AsyncMock()
        mock_collection.find_one.return_value = mock_evaluation
        
        with patch('services.tuning_service.get_evaluations_collection', return_value=mock_collection):
            scenario_weights = [
                ScenarioWeight(scenario_id=str(scenario_id), weight=3)
            ]
            
            # Expected: (90+85)/2 = 87.5
            score = await calculate_weighted_average(
                evaluation_ids=[str(eval_id)],
                scenario_weights=scenario_weights
            )
            
            assert score == 87.5
    
    @pytest.mark.asyncio
    async def test_calculate_weighted_average_evaluation_not_found(self):
        """Test error when evaluation not found"""
        eval_id = ObjectId()
        
        mock_collection = AsyncMock()
        mock_collection.find_one.return_value = None
        
        with patch('services.tuning_service.get_evaluations_collection', return_value=mock_collection):
            scenario_weights = [
                ScenarioWeight(scenario_id="507f1f77bcf86cd799439012", weight=3)
            ]
            
            with pytest.raises(ValueError, match="Evaluation not found"):
                await calculate_weighted_average(
                    evaluation_ids=[str(eval_id)],
                    scenario_weights=scenario_weights
                )
    
    @pytest.mark.asyncio
    async def test_calculate_weighted_average_incomplete_evaluation(self):
        """Test error when evaluation not completed"""
        eval_id = ObjectId()
        scenario_id = ObjectId()
        
        mock_evaluation = {
            "_id": eval_id,
            "scenario_id": scenario_id,
            "status": "RUNNING",
            "scores": None
        }
        
        mock_collection = AsyncMock()
        mock_collection.find_one.return_value = mock_evaluation
        
        with patch('services.tuning_service.get_evaluations_collection', return_value=mock_collection):
            scenario_weights = [
                ScenarioWeight(scenario_id=str(scenario_id), weight=3)
            ]
            
            with pytest.raises(ValueError, match="is not completed"):
                await calculate_weighted_average(
                    evaluation_ids=[str(eval_id)],
                    scenario_weights=scenario_weights
                )


class TestWriterCritiqueCycle:
    """Test run_writer_critique_cycle function"""
    
    @pytest.mark.asyncio
    async def test_writer_critique_cycle_success_first_try(self):
        """Test successful Writer-Critique cycle on first attempt"""
        context = """
        CURRENT PROMPT: You are a debt collector...
        TARGET SCORE: 85
        FAILED EVALUATIONS: Agent was too aggressive...
        """
        
        # Mock responses
        writer_response = {"system_prompt": "Improved prompt with more empathy..."}
        critique_response = {"feedback": "Looks good!", "pass": True}
        
        with patch('services.tuning_service.generate_structured_content') as mock_generate:
            # First call: Writer, Second call: Critique
            mock_generate.side_effect = [writer_response, critique_response]
            
            result = await run_writer_critique_cycle(context)
            
            assert result == "Improved prompt with more empathy..."
            assert mock_generate.call_count == 2
    
    @pytest.mark.asyncio
    async def test_writer_critique_cycle_revision_needed(self):
        """Test Writer-Critique cycle with revision"""
        context = "CURRENT PROMPT: Basic prompt..."
        
        # Mock responses - first critique fails, second passes
        writer_response_1 = {"system_prompt": "First attempt..."}
        critique_response_1 = {"feedback": "Too vague", "pass": False}
        writer_response_2 = {"system_prompt": "Revised attempt..."}
        critique_response_2 = {"feedback": "Better!", "pass": True}
        
        with patch('services.tuning_service.generate_structured_content') as mock_generate:
            mock_generate.side_effect = [
                writer_response_1,
                critique_response_1,
                writer_response_2,
                critique_response_2
            ]
            
            result = await run_writer_critique_cycle(context, max_critique_cycles=3)
            
            assert result == "Revised attempt..."
            assert mock_generate.call_count == 4  # Writer, Critique, Writer, Critique
    
    @pytest.mark.asyncio
    async def test_writer_critique_cycle_max_cycles_reached(self):
        """Test Writer-Critique cycle when max cycles reached"""
        context = "CURRENT PROMPT: Basic prompt..."
        
        # Mock responses - always fail critique
        writer_response = {"system_prompt": "Attempt..."}
        critique_response = {"feedback": "Not good enough", "pass": False}
        
        with patch('services.tuning_service.generate_structured_content') as mock_generate:
            mock_generate.side_effect = [
                writer_response,
                critique_response,
                writer_response,
                critique_response,
            ]
            
            result = await run_writer_critique_cycle(context, max_critique_cycles=2)
            
            # Should return the last attempt even if not approved
            assert result == "Attempt..."
            assert mock_generate.call_count == 4


class TestBuildContextPackage:
    """Test build_context_package function"""
    
    @pytest.mark.asyncio
    async def test_build_context_package_basic(self):
        """Test building context package with evaluations"""
        current_prompt = "You are a debt collector..."
        target_score = 85.0
        
        eval_id = ObjectId()
        scenario_id = ObjectId()
        
        # Mock evaluation
        mock_evaluation = {
            "_id": eval_id,
            "scenario_id": scenario_id,
            "scores": {
                "task_completion": 60,
                "conversation_efficiency": 70
            },
            "evaluator_analysis": "Agent was too pushy",
            "transcript": [
                {"speaker": "agent", "message": "You need to pay now!"},
                {"speaker": "debtor", "message": "I can't afford it."}
            ]
        }
        
        # Mock scenario
        mock_scenario = {
            "_id": scenario_id,
            "title": "Anxious Debtor",
            "objective": "Avoid payment"
        }
        
        mock_eval_collection = AsyncMock()
        mock_eval_collection.find_one.return_value = mock_evaluation
        
        mock_scenario_collection = AsyncMock()
        mock_scenario_collection.find_one.return_value = mock_scenario
        
        with patch('services.tuning_service.get_evaluations_collection', return_value=mock_eval_collection), \
             patch('core.database.get_scenarios_collection', return_value=mock_scenario_collection):
            
            scenario_weights = [
                ScenarioWeight(scenario_id=str(scenario_id), weight=4)
            ]
            
            context = await build_context_package(
                current_prompt_text=current_prompt,
                target_score=target_score,
                failed_evaluation_ids=[str(eval_id)],
                scenario_weights=scenario_weights
            )
            
            # Verify context contains key information
            assert "You are a debt collector..." in context
            assert "TARGET SCORE: 85.0" in context
            assert "Anxious Debtor" in context
            assert "Agent was too pushy" in context
            assert "AGENT: You need to pay now!" in context
            assert "DEBTOR: I can't afford it." in context


class TestSchemaCreation:
    """Test schema creation functions"""
    
    def test_create_writer_schema(self):
        """Test Writer schema creation"""
        schema = create_writer_schema()
        assert schema is not None
        # Schema should have system_prompt property
    
    def test_create_critique_schema(self):
        """Test Critique schema creation"""
        schema = create_critique_schema()
        assert schema is not None
        # Schema should have feedback and pass properties


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
