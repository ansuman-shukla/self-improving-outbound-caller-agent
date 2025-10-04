"""
Pydantic models for Tuning Loop
Used in the Automated Tuning Loop module for prompt optimization
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class TuningStatus(str, Enum):
    """Possible statuses for a tuning loop run"""
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class ScenarioWeight(BaseModel):
    """Represents a scenario and its weight in the tuning loop"""
    scenario_id: str = Field(
        ...,
        description="ID of the scenario to use in tuning",
        example="507f1f77bcf86cd799439012"
    )
    weight: int = Field(
        ...,
        description="Weight/importance of this scenario (1-5)",
        ge=1,
        le=5,
        example=3
    )


class TuningConfig(BaseModel):
    """Configuration for a tuning loop run"""
    target_score: float = Field(
        ...,
        description="Target weighted average score to achieve (0-100)",
        ge=0,
        le=100,
        example=85.0
    )
    max_iterations: int = Field(
        ...,
        description="Maximum number of iterations to run",
        ge=1,
        le=10,
        example=5
    )
    scenario_weights: List[ScenarioWeight] = Field(
        ...,
        description="List of scenarios with their weights for evaluation"
    )


class TuningIteration(BaseModel):
    """Represents a single iteration in the tuning loop"""
    iteration_number: int = Field(
        ...,
        description="The iteration number (1-indexed)",
        ge=1,
        example=1
    )
    prompt_id: str = Field(
        ...,
        description="ID of the prompt used in this iteration",
        example="507f1f77bcf86cd799439011"
    )
    evaluation_ids: List[str] = Field(
        ...,
        description="IDs of evaluations run in this iteration"
    )
    weighted_score: float = Field(
        ...,
        description="Weighted average score for this iteration (0-100)",
        ge=0,
        le=100,
        example=78.5
    )


class TuningLoopCreate(BaseModel):
    """Request model for creating a new tuning loop"""
    initial_prompt_id: str = Field(
        ...,
        description="ID of the starting agent prompt",
        example="507f1f77bcf86cd799439011"
    )
    target_score: float = Field(
        ...,
        description="Target weighted average score to achieve (0-100)",
        ge=0,
        le=100,
        example=85.0
    )
    max_iterations: int = Field(
        ...,
        description="Maximum number of iterations to run",
        ge=1,
        le=10,
        example=5
    )
    scenarios: List[ScenarioWeight] = Field(
        ...,
        description="List of scenarios with their weights for evaluation",
        min_length=1
    )


class TuningLoopResponse(BaseModel):
    """Response model for tuning loop data"""
    id: str = Field(
        ...,
        description="Unique identifier for the tuning loop",
        alias="_id"
    )
    status: TuningStatus = Field(
        ...,
        description="Current status of the tuning loop",
        example="RUNNING"
    )
    config: TuningConfig = Field(
        ...,
        description="Configuration for this tuning loop"
    )
    iterations: List[TuningIteration] = Field(
        default_factory=list,
        description="List of completed iterations"
    )
    final_prompt_id: Optional[str] = Field(
        None,
        description="ID of the best prompt produced by the loop (when completed)"
    )
    error_message: Optional[str] = Field(
        None,
        description="Error message if the tuning loop failed"
    )
    created_at: datetime = Field(
        ...,
        description="When the tuning loop was created"
    )
    completed_at: Optional[datetime] = Field(
        None,
        description="When the tuning loop was completed"
    )

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "_id": "507f1f77bcf86cd799439015",
                "status": "COMPLETED",
                "config": {
                    "target_score": 85.0,
                    "max_iterations": 5,
                    "scenario_weights": [
                        {"scenario_id": "507f1f77bcf86cd799439012", "weight": 4},
                        {"scenario_id": "507f1f77bcf86cd799439013", "weight": 3},
                        {"scenario_id": "507f1f77bcf86cd799439014", "weight": 5}
                    ]
                },
                "iterations": [
                    {
                        "iteration_number": 1,
                        "prompt_id": "507f1f77bcf86cd799439011",
                        "evaluation_ids": ["507f1f77bcf86cd799439016", "507f1f77bcf86cd799439017"],
                        "weighted_score": 67.5
                    },
                    {
                        "iteration_number": 2,
                        "prompt_id": "507f1f77bcf86cd799439018",
                        "evaluation_ids": ["507f1f77bcf86cd799439019", "507f1f77bcf86cd799439020"],
                        "weighted_score": 78.0
                    },
                    {
                        "iteration_number": 3,
                        "prompt_id": "507f1f77bcf86cd799439021",
                        "evaluation_ids": ["507f1f77bcf86cd799439022", "507f1f77bcf86cd799439023"],
                        "weighted_score": 86.2
                    }
                ],
                "final_prompt_id": "507f1f77bcf86cd799439021",
                "created_at": "2025-10-04T11:00:00Z",
                "completed_at": "2025-10-04T11:15:30Z"
            }
        }


class TuningLoopStatusResponse(BaseModel):
    """Simplified response for status checks"""
    tuning_loop_id: str = Field(
        ...,
        description="The ID of the tuning loop"
    )
    status: TuningStatus = Field(
        ...,
        description="Current status of the tuning loop"
    )
    current_iteration: Optional[int] = Field(
        None,
        description="Current iteration number (if running)"
    )
    latest_score: Optional[float] = Field(
        None,
        description="Latest weighted score achieved"
    )
