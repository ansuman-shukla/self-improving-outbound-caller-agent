"""
Pydantic models for Scenario (test scenarios for evaluations)
Used in the Scenario Designer module for creating and managing test scenarios
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ScenarioCreate(BaseModel):
    """Request model for creating a new scenario via AI generation"""
    personality_id: str = Field(
        ...,
        description="ID of the personality to base this scenario on",
        example="507f1f77bcf86cd799439011"
    )
    brief: str = Field(
        ...,
        description="User's brief description of the situation",
        example="just lost their job",
        min_length=1,
        max_length=500
    )


class ScenarioUpdate(BaseModel):
    """Request model for updating an existing scenario"""
    backstory: Optional[str] = Field(
        None,
        description="Updated detailed backstory for the debtor",
        min_length=10,
        max_length=2000
    )
    weight: Optional[int] = Field(
        None,
        description="Updated importance/weight of this scenario (1-5)",
        ge=1,
        le=5
    )


class ScenarioResponse(BaseModel):
    """Response model for scenario data"""
    id: str = Field(
        ...,
        description="Unique identifier for the scenario",
        alias="_id"
    )
    personality_id: str = Field(
        ...,
        description="ID of the personality this scenario is based on"
    )
    title: str = Field(
        ...,
        description="AI-generated title for the scenario",
        example="Struggling Parent - Job Loss"
    )
    brief: str = Field(
        ...,
        description="Original user brief",
        example="just lost their job"
    )
    backstory: str = Field(
        ...,
        description="AI-generated (and user-editable) detailed backstory",
        example="This debtor is a single parent who recently lost their job due to company downsizing..."
    )
    objective: str = Field(
        ...,
        description="AI-generated goal for the debtor in the conversation",
        example="Try to negotiate a payment plan while explaining their current financial hardship"
    )
    weight: int = Field(
        default=3,
        description="Importance/weight of this scenario (1-5), defaults to 3",
        ge=1,
        le=5
    )
    created_at: datetime = Field(
        ...,
        description="Timestamp when the scenario was created"
    )

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "_id": "507f1f77bcf86cd799439011",
                "personality_id": "507f1f77bcf86cd799439012",
                "title": "Anxious Debtor - First Notice Panic",
                "brief": "just received their first-ever debt notice",
                "backstory": "This debtor has never been in debt before and is experiencing significant anxiety about receiving their first collection notice. They are worried about the legal implications and potential damage to their credit score.",
                "objective": "Seek clarification on the debt and express their fear and confusion about the process",
                "weight": 4,
                "created_at": "2025-10-04T12:00:00Z"
            }
        }


class ScenarioInDB(BaseModel):
    """Internal model representing scenario as stored in MongoDB"""
    personality_id: str
    title: str
    brief: str
    backstory: str
    objective: str
    weight: int = 3
    created_at: datetime
