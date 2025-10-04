"""
Tuning Router - Handles all automated tuning loop endpoints
Part of Phase 4, Module 4: The Automated Tuning Loop
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
import logging
from datetime import datetime

from core import database
from models.tuning_loop import (
    TuningLoopCreate,
    TuningLoopResponse,
    TuningLoopStatusResponse,
    TuningStatus,
    ScenarioWeight
)
from services.tuning_service import perform_tuning_loop

# Setup logging
logger = logging.getLogger(__name__)

# Create router instance
router = APIRouter(
    prefix="/tuning",
    tags=["Tuning Loop"]
)


@router.post("", response_model=TuningLoopStatusResponse, status_code=202)
async def start_tuning_loop(
    tuning_request: TuningLoopCreate,
    background_tasks: BackgroundTasks
):
    """
    Start a new automated tuning loop
    
    This endpoint kicks off an asynchronous tuning loop that will:
    1. Run evaluations across all specified scenarios
    2. Calculate weighted average scores
    3. Generate improved prompts using AI
    4. Iterate until target score is reached or max iterations completed
    
    The process runs in the background. Use the returned tuning_loop_id
    to poll the status endpoint and track progress.
    
    - **initial_prompt_id**: ID of the starting agent prompt to improve
    - **target_score**: Target weighted average score to achieve (0-100)
    - **max_iterations**: Maximum number of improvement iterations (1-10)
    - **scenarios**: List of scenarios with weights to use for evaluation
    
    Returns:
        202 Accepted with tuning_loop_id and initial PENDING status
    """
    try:
        # Validate that the initial prompt exists
        prompt = await database.get_prompt_by_id(tuning_request.initial_prompt_id)
        if not prompt:
            raise HTTPException(
                status_code=404,
                detail=f"Prompt with ID {tuning_request.initial_prompt_id} not found"
            )
        
        # Validate that all scenarios exist
        for scenario_weight in tuning_request.scenarios:
            scenario = await database.get_scenario_by_id(scenario_weight.scenario_id)
            if not scenario:
                raise HTTPException(
                    status_code=404,
                    detail=f"Scenario with ID {scenario_weight.scenario_id} not found"
                )
        
        logger.info(f"Starting tuning loop with initial prompt: {prompt['name']}")
        
        # Create the tuning loop document in MongoDB
        scenario_weights_dict = [
            {"scenario_id": sw.scenario_id, "weight": sw.weight}
            for sw in tuning_request.scenarios
        ]
        
        tuning_loop_id = await database.insert_tuning_loop(
            initial_prompt_id=tuning_request.initial_prompt_id,
            target_score=tuning_request.target_score,
            max_iterations=tuning_request.max_iterations,
            scenario_weights=scenario_weights_dict
        )
        
        # Schedule the background task
        background_tasks.add_task(
            perform_tuning_loop,
            tuning_loop_id=tuning_loop_id,
            initial_prompt_id=tuning_request.initial_prompt_id,
            target_score=tuning_request.target_score,
            max_iterations=tuning_request.max_iterations,
            scenario_weights=tuning_request.scenarios
        )
        
        logger.info(f"Tuning loop {tuning_loop_id} scheduled for background execution")
        
        return TuningLoopStatusResponse(
            tuning_loop_id=tuning_loop_id,
            status=TuningStatus.PENDING,
            current_iteration=None,
            latest_score=None
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error starting tuning loop: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start tuning loop: {str(e)}"
        )


@router.get("/{tuning_loop_id}", response_model=TuningLoopResponse)
async def get_tuning_loop(tuning_loop_id: str):
    """
    Get the status and details of a tuning loop
    
    This is the polling endpoint for tracking tuning loop progress.
    The frontend should call this endpoint every 3-5 seconds to update
    the UI with the current status, iteration progress, and scores.
    
    - **tuning_loop_id**: The ID returned from the POST /tuning endpoint
    
    Returns:
        Full tuning loop data including:
        - status (PENDING, RUNNING, COMPLETED, FAILED)
        - config (target_score, max_iterations, scenarios)
        - iterations (array of completed iterations with scores)
        - final_prompt_id (when completed)
    """
    try:
        tuning_loop = await database.get_tuning_loop_by_id(tuning_loop_id)
        
        if not tuning_loop:
            raise HTTPException(
                status_code=404,
                detail=f"Tuning loop with ID {tuning_loop_id} not found"
            )
        
        return TuningLoopResponse(**tuning_loop)
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error fetching tuning loop {tuning_loop_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve tuning loop: {str(e)}"
        )


@router.get("", response_model=list[TuningLoopResponse])
async def get_all_tuning_loops():
    """
    Retrieve all tuning loop records
    
    Returns list of all tuning loops sorted by creation date (newest first).
    Useful for displaying a history of all tuning runs.
    """
    try:
        tuning_loops = await database.get_all_tuning_loops()
        return [TuningLoopResponse(**loop) for loop in tuning_loops]
        
    except Exception as e:
        logger.error(f"Error fetching tuning loops: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve tuning loops: {str(e)}"
        )
