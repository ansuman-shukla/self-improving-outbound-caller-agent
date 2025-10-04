"""
Pydantic models for call requests, responses, and database records
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class CallRequest(BaseModel):
    """Request model for making an outbound call"""
    phone_number: str = Field(
        ..., 
        description="Phone number to call (without country code, e.g., 9262561716)",
        example="9262561716"
    )
    country_code: str = Field(
        ...,
        description="Country code (e.g., +91, +44, +1)",
        example="+91"
    )
    name: str = Field(
        ...,
        description="Customer name for personalized conversation",
        example="Jayden"
    )
    amount: float = Field(
        ...,
        description="Outstanding bill amount",
        example=1250.75
    )
    transfer_to: Optional[str] = Field(
        None,
        description="Phone number to transfer to if requested (with country code)",
        example="+916203834111"
    )


class CallResponse(BaseModel):
    """Response model for call dispatch"""
    success: bool
    message: str
    call_id: Optional[str] = None
    room: Optional[str] = None
    dispatch_id: Optional[str] = None
    error: Optional[str] = None


class CallRecord(BaseModel):
    """Model for a single call record"""
    call_id: str
    room_name: str
    dispatch_id: str
    name: str
    phone_number: str
    country_code: str
    amount: float
    status: str
    created_at: datetime
    completed_at: Optional[datetime] = None
    transcript_file: Optional[str] = None
    transfer_to: Optional[str] = None


class CallsResponse(BaseModel):
    """Response model for list of calls"""
    calls: List[CallRecord]
    total: int


class TranscriptMessage(BaseModel):
    """Model for a single transcript message"""
    role: str  # "agent" | "user"
    message: str  # Changed from 'text' to 'message' to match frontend
    timestamp: Optional[str] = None


class TranscriptResponse(BaseModel):
    """Response model for call transcript"""
    call_id: str
    room_name: str
    name: str
    phone_number: str
    amount: float
    status: str
    created_at: datetime
    completed_at: Optional[datetime] = None
    transcript: List[TranscriptMessage]
    # LLM-generated risk scores (1-100 scale, higher = lower risk)
    loan_recovery_score: Optional[float] = None
    willingness_to_pay_score: Optional[float] = None
    escalation_risk_score: Optional[float] = None
    customer_sentiment_score: Optional[float] = None
    promise_to_pay_reliability_index: Optional[float] = None


class Country(BaseModel):
    """Model for country information"""
    code: str
    name: str
    flag: str
    iso: str
