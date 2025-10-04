"""
Personality Router - Handles all personality-related endpoints
Part of Phase 1, Module 1: The Library (Personalities & Prompts)
"""

from fastapi import APIRouter, HTTPException
import logging

from core import database
from models.personality import (
    PersonalityCreate,
    PersonalityUpdate,
    PersonalityResponse,
    PersonalityListResponse
)

# Setup logging
logger = logging.getLogger(__name__)

# Create router instance
router = APIRouter(
    prefix="/personalities",
    tags=["Personalities"]
)


@router.post("", response_model=PersonalityResponse, status_code=201)
async def create_personality(personality: PersonalityCreate):
    """
    Create a new debtor personality
    
    - **name**: User-defined name for the personality (e.g., "Willful Defaulter")
    - **description**: Short description for UI lists
    - **core_traits**: Dictionary of behavioral traits
    - **system_prompt**: Detailed prompt for AI to role-play this personality
    """
    try:
        personality_id = await database.insert_personality(
            name=personality.name,
            description=personality.description,
            core_traits=personality.core_traits,
            system_prompt=personality.system_prompt
        )
        
        # Fetch and return the created personality
        created_personality = await database.get_personality_by_id(personality_id)
        
        if not created_personality:
            raise HTTPException(
                status_code=500,
                detail="Failed to retrieve created personality"
            )
        
        return PersonalityResponse(**created_personality)
        
    except Exception as e:
        logger.error(f"Error creating personality: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create personality: {str(e)}"
        )


@router.get("", response_model=PersonalityListResponse)
async def get_personalities():
    """
    Retrieve all personality records
    
    Returns list of all personalities sorted by creation date (newest first)
    """
    try:
        personalities = await database.get_all_personalities()
        
        return PersonalityListResponse(
            personalities=[PersonalityResponse(**p) for p in personalities],
            total=len(personalities)
        )
        
    except Exception as e:
        logger.error(f"Error fetching personalities: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch personalities: {str(e)}"
        )


@router.get("/{personality_id}", response_model=PersonalityResponse)
async def get_personality(personality_id: str):
    """
    Retrieve a specific personality by ID
    
    Args:
        personality_id: MongoDB ObjectId of the personality
    
    Returns:
        Personality data
    """
    try:
        personality = await database.get_personality_by_id(personality_id)
        
        if not personality:
            raise HTTPException(
                status_code=404,
                detail=f"Personality with ID {personality_id} not found"
            )
        
        return PersonalityResponse(**personality)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching personality: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch personality: {str(e)}"
        )


@router.put("/{personality_id}", response_model=PersonalityResponse)
async def update_personality(personality_id: str, personality: PersonalityUpdate):
    """
    Update an existing personality
    
    Args:
        personality_id: MongoDB ObjectId of the personality
        personality: Fields to update (all optional)
    
    Returns:
        Updated personality data
    """
    try:
        # Build update data from non-None fields
        update_data = personality.model_dump(exclude_unset=True)
        
        if not update_data:
            raise HTTPException(
                status_code=400,
                detail="No fields to update"
            )
        
        success = await database.update_personality(personality_id, update_data)
        
        if not success:
            raise HTTPException(
                status_code=404,
                detail=f"Personality with ID {personality_id} not found"
            )
        
        # Fetch and return the updated personality
        updated_personality = await database.get_personality_by_id(personality_id)
        
        return PersonalityResponse(**updated_personality)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating personality: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update personality: {str(e)}"
        )


@router.delete("/{personality_id}", status_code=204)
async def delete_personality(personality_id: str):
    """
    Delete a personality by ID
    
    Args:
        personality_id: MongoDB ObjectId of the personality
    """
    try:
        success = await database.delete_personality(personality_id)
        
        if not success:
            raise HTTPException(
                status_code=404,
                detail=f"Personality with ID {personality_id} not found"
            )
        
        return None
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting personality: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete personality: {str(e)}"
        )
