"""
Pydantic models for Prompt (agent system prompts)
Used in the Library module for creating and managing versioned agent prompts
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class PromptCreate(BaseModel):
    """Request model for creating a new prompt"""
    name: str = Field(
        ..., 
        description="User-defined name for the prompt",
        example="v1.1-empathetic",
        min_length=1,
        max_length=100
    )
    prompt_text: str = Field(
        ...,
        description="The full system prompt for the voice agent",
        example="You are an empathetic debt collection agent. Your goal is to help customers find a payment solution...",
        min_length=10
    )
    version: str = Field(
        ...,
        description="User-defined version identifier",
        example="1.1",
        min_length=1,
        max_length=50
    )


class PromptUpdate(BaseModel):
    """Request model for updating an existing prompt"""
    name: Optional[str] = Field(
        None,
        description="Updated name for the prompt",
        min_length=1,
        max_length=100
    )
    prompt_text: Optional[str] = Field(
        None,
        description="Updated prompt text",
        min_length=10
    )
    version: Optional[str] = Field(
        None,
        description="Updated version identifier",
        min_length=1,
        max_length=50
    )


class PromptResponse(BaseModel):
    """Response model for prompt (includes MongoDB _id)"""
    id: str = Field(
        ...,
        description="MongoDB document ID",
        alias="_id"
    )
    name: str
    prompt_text: str
    version: str
    created_at: datetime
    
    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "_id": "507f1f77bcf86cd799439012",
                "name": "v2.1-empathetic",
                "prompt_text": "You are a compassionate debt collection agent who prioritizes customer well-being...",
                "version": "2.1",
                "created_at": "2025-10-04T10:30:00Z"
            }
        }


class PromptListResponse(BaseModel):
    """Response model for list of prompts"""
    prompts: list[PromptResponse]
    total: int
