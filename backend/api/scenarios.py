"""
Scenario Router - Handles all scenario-related endpoints
Part of Phase 2, Module 2: The Scenario Designer
"""

from fastapi import APIRouter, HTTPException
import logging

from core import database
from core.gemini_client import generate_scenario_from_ai
from models.scenario import (
    ScenarioCreate,
    ScenarioUpdate,
    ScenarioResponse
)

# Setup logging
logger = logging.getLogger(__name__)

# Create router instance
router = APIRouter(
    prefix="/scenarios",
    tags=["Scenarios"]
)


@router.post("/generate", response_model=ScenarioResponse, status_code=201)
async def generate_scenario(scenario_request: ScenarioCreate):
    """
    Generate a new scenario using AI
    
    This endpoint takes a personality ID and a brief situation description,
    then uses AI to generate a detailed scenario including title, backstory,
    and objective for testing purposes.
    
    - **personality_id**: ID of the personality to base this scenario on
    - **brief**: User's brief description of the situation (e.g., "just lost their job")
    
    Returns:
        The newly created scenario with AI-generated content
    """
    try:
        # First, fetch the personality to get its details
        personality = await database.get_personality_by_id(scenario_request.personality_id)
        
        if not personality:
            raise HTTPException(
                status_code=404,
                detail=f"Personality with ID {scenario_request.personality_id} not found"
            )
        
        # Generate the scenario using AI
        logger.info(f"Generating scenario for personality: {personality['name']}")
        ai_generated = await generate_scenario_from_ai(
            personality_name=personality["name"],
            personality_description=personality["description"],
            personality_system_prompt=personality["system_prompt"],
            user_brief=scenario_request.brief
        )
        
        # Save the scenario to database
        scenario_id = await database.insert_scenario(
            personality_id=scenario_request.personality_id,
            title=ai_generated["title"],
            brief=scenario_request.brief,
            backstory=ai_generated["backstory"],
            objective=ai_generated["objective"],
            weight=3  # Default weight
        )
        
        # Fetch and return the created scenario
        created_scenario = await database.get_scenario_by_id(scenario_id)
        
        if not created_scenario:
            raise HTTPException(
                status_code=500,
                detail="Failed to retrieve created scenario"
            )
        
        return ScenarioResponse(**created_scenario)
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error generating scenario: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate scenario: {str(e)}"
        )


@router.get("", response_model=list[ScenarioResponse])
async def get_scenarios():
    """
    Retrieve all scenario records
    
    Returns list of all scenarios sorted by creation date (newest first)
    """
    try:
        scenarios = await database.get_all_scenarios()
        
        return [ScenarioResponse(**s) for s in scenarios]
        
    except Exception as e:
        logger.error(f"Error fetching scenarios: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch scenarios: {str(e)}"
        )


@router.get("/{scenario_id}", response_model=ScenarioResponse)
async def get_scenario(scenario_id: str):
    """
    Retrieve a specific scenario by ID
    
    Args:
        scenario_id: MongoDB ObjectId of the scenario
    
    Returns:
        Scenario data
    """
    try:
        scenario = await database.get_scenario_by_id(scenario_id)
        
        if not scenario:
            raise HTTPException(
                status_code=404,
                detail=f"Scenario with ID {scenario_id} not found"
            )
        
        return ScenarioResponse(**scenario)
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error fetching scenario: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch scenario: {str(e)}"
        )


@router.put("/{scenario_id}", response_model=ScenarioResponse)
async def update_scenario(scenario_id: str, scenario_update: ScenarioUpdate):
    """
    Update a scenario's backstory and/or weight
    
    This allows users to refine the AI-generated backstory or adjust the
    importance/weight of the scenario.
    
    Args:
        scenario_id: MongoDB ObjectId of the scenario
        scenario_update: Fields to update (backstory and/or weight)
    
    Returns:
        Updated scenario data
    """
    try:
        # Check if scenario exists
        existing_scenario = await database.get_scenario_by_id(scenario_id)
        
        if not existing_scenario:
            raise HTTPException(
                status_code=404,
                detail=f"Scenario with ID {scenario_id} not found"
            )
        
        # Build update dictionary with only provided fields
        update_data = {}
        if scenario_update.backstory is not None:
            update_data["backstory"] = scenario_update.backstory
        if scenario_update.weight is not None:
            update_data["weight"] = scenario_update.weight
        
        if not update_data:
            # No fields to update
            return ScenarioResponse(**existing_scenario)
        
        # Perform the update
        success = await database.update_scenario(scenario_id, update_data)
        
        if not success:
            raise HTTPException(
                status_code=500,
                detail="Failed to update scenario"
            )
        
        # Fetch and return the updated scenario
        updated_scenario = await database.get_scenario_by_id(scenario_id)
        
        return ScenarioResponse(**updated_scenario)
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error updating scenario: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update scenario: {str(e)}"
        )


@router.delete("/{scenario_id}", status_code=204)
async def delete_scenario(scenario_id: str):
    """
    Delete a scenario by ID
    
    Args:
        scenario_id: MongoDB ObjectId of the scenario
    """
    try:
        # Check if scenario exists
        existing_scenario = await database.get_scenario_by_id(scenario_id)
        
        if not existing_scenario:
            raise HTTPException(
                status_code=404,
                detail=f"Scenario with ID {scenario_id} not found"
            )
        
        # Delete the scenario
        success = await database.delete_scenario(scenario_id)
        
        if not success:
            raise HTTPException(
                status_code=500,
                detail="Failed to delete scenario"
            )
        
        return None
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error deleting scenario: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete scenario: {str(e)}"
        )
