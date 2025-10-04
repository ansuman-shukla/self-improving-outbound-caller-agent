"""
Pydantic models for Evaluation Results
Used in the Manual Evaluation Engine module for running tests and storing results
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class EvaluationStatus(str, Enum):
    """Possible statuses for an evaluation run"""
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class TranscriptMessage(BaseModel):
    """A single message in the conversation transcript"""
    speaker: str = Field(
        ...,
        description="Speaker of this message - either 'agent' or 'debtor'",
        example="agent"
    )
    message: str = Field(
        ...,
        description="The text content of the message",
        example="Hello, I'm calling regarding an outstanding balance on your account."
    )


class EvaluationScores(BaseModel):
    """Scores from the evaluation"""
    task_completion: int = Field(
        ...,
        description="Score for how well the agent achieved their goal (0-100)",
        ge=0,
        le=100,
        example=75
    )
    conversation_efficiency: int = Field(
        ...,
        description="Score for how relevant and non-repetitive the agent was (0-100)",
        ge=0,
        le=100,
        example=82
    )


class EvaluationCreate(BaseModel):
    """Request model for creating a new evaluation run"""
    prompt_id: str = Field(
        ...,
        description="ID of the agent prompt to test",
        example="507f1f77bcf86cd799439011"
    )
    scenario_id: str = Field(
        ...,
        description="ID of the scenario to test against",
        example="507f1f77bcf86cd799439012"
    )


class EvaluationResponse(BaseModel):
    """Response model for evaluation data"""
    id: str = Field(
        ...,
        description="Unique identifier for the evaluation result",
        alias="_id"
    )
    prompt_id: str = Field(
        ...,
        description="ID of the agent prompt used in this evaluation"
    )
    scenario_id: str = Field(
        ...,
        description="ID of the scenario used in this evaluation"
    )
    status: EvaluationStatus = Field(
        ...,
        description="Current status of the evaluation run",
        example="COMPLETED"
    )
    transcript: Optional[List[TranscriptMessage]] = Field(
        None,
        description="The full conversation transcript (available when completed)"
    )
    scores: Optional[EvaluationScores] = Field(
        None,
        description="The evaluation scores (available when completed)"
    )
    evaluator_analysis: Optional[str] = Field(
        None,
        description="Qualitative feedback from the evaluator bot"
    )
    error_message: Optional[str] = Field(
        None,
        description="Error message if the evaluation failed"
    )
    created_at: datetime = Field(
        ...,
        description="When the evaluation was created"
    )
    completed_at: Optional[datetime] = Field(
        None,
        description="When the evaluation was completed"
    )

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "_id": "507f1f77bcf86cd799439013",
                "prompt_id": "507f1f77bcf86cd799439011",
                "scenario_id": "507f1f77bcf86cd799439012",
                "status": "COMPLETED",
                "transcript": [
                    {
                        "speaker": "agent",
                        "message": "Hello, I'm calling regarding an outstanding balance."
                    },
                    {
                        "speaker": "debtor",
                        "message": "I don't have the money right now."
                    }
                ],
                "scores": {
                    "task_completion": 75,
                    "conversation_efficiency": 82
                },
                "evaluator_analysis": "The agent was empathetic but could have offered more concrete solutions.",
                "created_at": "2025-10-04T10:30:00Z",
                "completed_at": "2025-10-04T10:32:15Z"
            }
        }


class EvaluationStatusResponse(BaseModel):
    """Simplified response for status checks"""
    result_id: str = Field(
        ...,
        description="The ID of the evaluation result"
    )
    status: EvaluationStatus = Field(
        ...,
        description="Current status of the evaluation"
    )
