"""
Pydantic models for Personality (debtor personas)
Used in the Library module for creating and managing debtor personalities
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict
from datetime import datetime


class PersonalityCreate(BaseModel):
    """Request model for creating a new personality"""
    name: str = Field(
        ..., 
        description="User-defined name for the personality",
        example="Willful Defaulter",
        min_length=1,
        max_length=100
    )
    description: str = Field(
        ...,
        description="Short description of the personality for UI lists",
        example="A person who has the means to pay but is avoiding payment",
        min_length=1,
        max_length=500
    )
    core_traits: Dict[str, str] = Field(
        ...,
        description="Key-value pairs defining behavioral traits",
        example={
            "Attitude": "Cynical",
            "Communication Style": "Evasive",
            "Financial Situation": "Stable but uncooperative"
        }
    )
    system_prompt: str = Field(
        ...,
        description="Detailed prompt for AI to role-play this personality",
        example="You are a debtor who has the financial means to pay but is choosing not to. You make excuses and try to avoid commitment...",
        min_length=10
    )
    amount: Optional[float] = Field(
        None,
        description="The pending debt amount for this personality (in rupees)",
        example=5000.0,
        gt=0
    )


class PersonalityUpdate(BaseModel):
    """Request model for updating an existing personality"""
    name: Optional[str] = Field(
        None,
        description="Updated name for the personality",
        min_length=1,
        max_length=100
    )
    description: Optional[str] = Field(
        None,
        description="Updated description",
        min_length=1,
        max_length=500
    )
    core_traits: Optional[Dict[str, str]] = Field(
        None,
        description="Updated core traits"
    )
    system_prompt: Optional[str] = Field(
        None,
        description="Updated system prompt",
        min_length=10
    )
    amount: Optional[float] = Field(
        None,
        description="Updated pending debt amount (in rupees)",
        gt=0
    )


class PersonalityResponse(BaseModel):
    """Response model for personality (includes MongoDB _id)"""
    id: str = Field(
        ...,
        description="MongoDB document ID",
        alias="_id"
    )
    name: str
    description: str
    core_traits: Dict[str, str]
    system_prompt: str
    amount: Optional[float] = Field(
        None,
        description="The pending debt amount for this personality (in rupees)"
    )
    created_at: datetime
    
    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "_id": "507f1f77bcf86cd799439011",
                "name": "Anxious First-Time Debtor",
                "description": "Nervous about debt, lacks knowledge of the process",
                "core_traits": {
                    "Attitude": "Fearful",
                    "Communication Style": "Uncertain",
                    "Financial Situation": "Struggling"
                },
                "system_prompt": "You are a person who has just received their first debt notice...",
                "amount": 5000.0,
                "created_at": "2025-10-04T10:30:00Z"
            }
        }


class PersonalityListResponse(BaseModel):
    """Response model for list of personalities"""
    personalities: list[PersonalityResponse]
    total: int
