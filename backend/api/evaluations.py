"""
Evaluations Router - Handles all evaluation-related endpoints
Part of Phase 3, Module 3: The Manual Evaluation Engine
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List
import logging

from core import database
from models.evaluation import (
    EvaluationCreate,
    EvaluationResponse,
    EvaluationStatusResponse,
    EvaluationStatus
)
from services.evaluation_orchestrator import perform_full_evaluation

# Setup logging
logger = logging.getLogger(__name__)

# Create router instance
router = APIRouter(
    prefix="/evaluations",
    tags=["Evaluations"]
)


@router.post("", response_model=EvaluationStatusResponse, status_code=202)
async def create_evaluation(
    evaluation_request: EvaluationCreate,
    background_tasks: BackgroundTasks
):
    """
    Start a new evaluation run (asynchronous)
    
    This endpoint creates an evaluation result document and triggers a background
    task to run the complete evaluation process:
    1. Simulate conversation between agent and debtor
    2. Evaluate the transcript with AI scoring
    3. Save results to database
    
    The endpoint returns immediately with a 202 Accepted response.
    Use the polling endpoint GET /evaluations/{result_id} to check status.
    
    - **prompt_id**: ID of the agent prompt to test
    - **scenario_id**: ID of the scenario to test against
    
    Returns:
        EvaluationStatusResponse with result_id and initial status (PENDING)
    """
    try:
        # Validate that prompt and scenario exist
        prompt = await database.get_prompt_by_id(evaluation_request.prompt_id)
        if not prompt:
            raise HTTPException(
                status_code=404,
                detail=f"Prompt with ID {evaluation_request.prompt_id} not found"
            )
        
        scenario = await database.get_scenario_by_id(evaluation_request.scenario_id)
        if not scenario:
            raise HTTPException(
                status_code=404,
                detail=f"Scenario with ID {evaluation_request.scenario_id} not found"
            )
        
        # Create the evaluation result document with PENDING status
        result_id = await database.create_evaluation(
            prompt_id=evaluation_request.prompt_id,
            scenario_id=evaluation_request.scenario_id,
            status="PENDING"
        )
        
        logger.info(f"Created evaluation {result_id} for prompt {evaluation_request.prompt_id} and scenario {evaluation_request.scenario_id}")
        
        # Trigger background task to perform the evaluation
        background_tasks.add_task(
            perform_full_evaluation,
            result_id=result_id,
            prompt_id=evaluation_request.prompt_id,
            scenario_id=evaluation_request.scenario_id
        )
        
        return EvaluationStatusResponse(
            result_id=result_id,
            status=EvaluationStatus.PENDING
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating evaluation: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create evaluation: {str(e)}"
        )


@router.get("/{result_id}", response_model=EvaluationResponse)
async def get_evaluation(result_id: str):
    """
    Get evaluation result by ID (polling endpoint)
    
    This endpoint retrieves the current state of an evaluation run.
    The frontend should poll this endpoint every 3-5 seconds to check
    for status updates while an evaluation is RUNNING.
    
    Status progression:
    - PENDING: Evaluation created, not yet started
    - RUNNING: Conversation simulation and evaluation in progress
    - COMPLETED: Evaluation finished successfully, results available
    - FAILED: Evaluation encountered an error
    
    - **result_id**: MongoDB ObjectId of the evaluation result
    
    Returns:
        Complete evaluation result including status, transcript, scores, and analysis
    """
    try:
        evaluation = await database.get_evaluation_by_id(result_id)
        
        if not evaluation:
            raise HTTPException(
                status_code=404,
                detail=f"Evaluation with ID {result_id} not found"
            )
        
        return EvaluationResponse(**evaluation)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching evaluation {result_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch evaluation: {str(e)}"
        )


@router.get("", response_model=List[EvaluationResponse])
async def list_evaluations():
    """
    List all evaluation results
    
    Returns all evaluations sorted by created_at (newest first).
    This is useful for displaying a history of all evaluation runs.
    
    Returns:
        List of all evaluation results
    """
    try:
        evaluations = await database.get_all_evaluations()
        return [EvaluationResponse(**eval) for eval in evaluations]
    
    except Exception as e:
        logger.error(f"Error listing evaluations: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list evaluations: {str(e)}"
        )


@router.delete("/{result_id}", status_code=204)
async def delete_evaluation(result_id: str):
    """
    Delete an evaluation result by ID
    
    Permanently removes an evaluation result from the database.
    
    - **result_id**: MongoDB ObjectId of the evaluation to delete
    
    Returns:
        204 No Content on success
    """
    try:
        # Check if evaluation exists
        evaluation = await database.get_evaluation_by_id(result_id)
        if not evaluation:
            raise HTTPException(
                status_code=404,
                detail=f"Evaluation with ID {result_id} not found"
            )
        
        # Delete the evaluation
        success = await database.delete_evaluation(result_id)
        
        if not success:
            raise HTTPException(
                status_code=500,
                detail="Failed to delete evaluation"
            )
        
        logger.info(f"Deleted evaluation {result_id}")
        return None
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting evaluation {result_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete evaluation: {str(e)}"
        )
