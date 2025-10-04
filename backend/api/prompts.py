"""
Prompt Router - Handles all prompt-related endpoints
Part of Phase 1, Module 1: The Library (Personalities & Prompts)
"""

from fastapi import APIRouter, HTTPException
import logging

from core import database
from models.prompt import (
    PromptCreate,
    PromptUpdate,
    PromptResponse,
    PromptListResponse
)

# Setup logging
logger = logging.getLogger(__name__)

# Create router instance
router = APIRouter(
    prefix="/prompts",
    tags=["Prompts"]
)


@router.post("", response_model=PromptResponse, status_code=201)
async def create_prompt(prompt: PromptCreate):
    """
    Create a new agent system prompt
    
    - **name**: User-defined name for the prompt (e.g., "v1.1-empathetic")
    - **prompt_text**: The full system prompt for the voice agent
    - **version**: Version identifier (e.g., "1.1")
    """
    try:
        prompt_id = await database.insert_prompt(
            name=prompt.name,
            prompt_text=prompt.prompt_text,
            version=prompt.version
        )
        
        # Fetch and return the created prompt
        created_prompt = await database.get_prompt_by_id(prompt_id)
        
        if not created_prompt:
            raise HTTPException(
                status_code=500,
                detail="Failed to retrieve created prompt"
            )
        
        return PromptResponse(**created_prompt)
        
    except Exception as e:
        logger.error(f"Error creating prompt: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create prompt: {str(e)}"
        )


@router.get("", response_model=PromptListResponse)
async def get_prompts():
    """
    Retrieve all prompt records
    
    Returns list of all prompts sorted by creation date (newest first)
    """
    try:
        prompts = await database.get_all_prompts()
        
        return PromptListResponse(
            prompts=[PromptResponse(**p) for p in prompts],
            total=len(prompts)
        )
        
    except Exception as e:
        logger.error(f"Error fetching prompts: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch prompts: {str(e)}"
        )


@router.get("/{prompt_id}", response_model=PromptResponse)
async def get_prompt(prompt_id: str):
    """
    Retrieve a specific prompt by ID
    
    Args:
        prompt_id: MongoDB ObjectId of the prompt
    
    Returns:
        Prompt data
    """
    try:
        prompt = await database.get_prompt_by_id(prompt_id)
        
        if not prompt:
            raise HTTPException(
                status_code=404,
                detail=f"Prompt with ID {prompt_id} not found"
            )
        
        return PromptResponse(**prompt)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching prompt: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch prompt: {str(e)}"
        )


@router.put("/{prompt_id}", response_model=PromptResponse)
async def update_prompt(prompt_id: str, prompt: PromptUpdate):
    """
    Update an existing prompt
    
    Args:
        prompt_id: MongoDB ObjectId of the prompt
        prompt: Fields to update (all optional)
    
    Returns:
        Updated prompt data
    """
    try:
        # Build update data from non-None fields
        update_data = prompt.model_dump(exclude_unset=True)
        
        if not update_data:
            raise HTTPException(
                status_code=400,
                detail="No fields to update"
            )
        
        success = await database.update_prompt(prompt_id, update_data)
        
        if not success:
            raise HTTPException(
                status_code=404,
                detail=f"Prompt with ID {prompt_id} not found"
            )
        
        # Fetch and return the updated prompt
        updated_prompt = await database.get_prompt_by_id(prompt_id)
        
        return PromptResponse(**updated_prompt)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating prompt: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update prompt: {str(e)}"
        )


@router.delete("/{prompt_id}", status_code=204)
async def delete_prompt(prompt_id: str):
    """
    Delete a prompt by ID
    
    Args:
        prompt_id: MongoDB ObjectId of the prompt
    """
    try:
        success = await database.delete_prompt(prompt_id)
        
        if not success:
            raise HTTPException(
                status_code=404,
                detail=f"Prompt with ID {prompt_id} not found"
            )
        
        return None
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting prompt: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete prompt: {str(e)}"
        )
