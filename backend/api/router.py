"""
API Router - Route definitions only
Contains all endpoint handlers for the Outbound Caller API
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
import random
from livekit import api
import os
import logging
import json
from pathlib import Path
from typing import Optional

from core import database
from config.countries import COUNTRIES
from models.call import (
    CallRequest,
    CallResponse,
    CallRecord,
    CallsResponse,
    TranscriptResponse,
    TranscriptMessage
)

# Setup logging
logger = logging.getLogger(__name__)

# Create router instance
router = APIRouter(
    tags=["caller"]
)


@router.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "running",
        "service": "Outbound Caller API",
        "message": "Use POST /call to dispatch an outbound call"
    }


@router.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}


@router.get("/countries")
async def get_countries():
    """
    Get list of supported countries with their calling codes
    
    Returns list of countries with code, name, flag, and ISO code
    """
    return {"countries": COUNTRIES}


@router.post("/call", response_model=CallResponse)
async def make_call(call_request: CallRequest):
    """
    Dispatch an agent to make an outbound call
    
    - **phone_number**: The phone number to call (without country code, required)
    - **country_code**: Country code (e.g., +91, +44, +1, required)
    - **name**: Customer name (required)
    - **amount**: Bill amount (required)
    - **transfer_to**: Phone number to transfer to if requested (optional)
    """
    
    try:
        # Validate environment variables
        if not all([
            os.getenv("LIVEKIT_URL"),
            os.getenv("LIVEKIT_API_KEY"),
            os.getenv("LIVEKIT_API_SECRET")
        ]):
            raise HTTPException(
                status_code=500,
                detail="Missing LiveKit environment variables. Check .env.local file."
            )
        
        # Combine country code and phone number
        full_phone_number = f"{call_request.country_code}{call_request.phone_number}"
        
        # Initialize LiveKit API client
        lkapi = api.LiveKitAPI()
        
        try:
            # Generate unique room name for each call
            room_name = f"outbound-{''.join(str(random.randint(0, 9)) for _ in range(10))}"
            
            # Prepare metadata
            metadata = {
                "phone_number": full_phone_number,
                "name": call_request.name,
                "amount": call_request.amount,
                "transfer_to": call_request.transfer_to or ""
            }
            
            # Create dispatch
            dispatch = await lkapi.agent_dispatch.create_dispatch(
                api.CreateAgentDispatchRequest(
                    # Must match the agent_name in WorkerOptions
                    agent_name="outbound-caller",
                    room=room_name,
                    metadata=str(metadata).replace("'", '"'),  # Convert to JSON string
                )
            )
            
            # Save call record to MongoDB
            call_id = await database.insert_call(
                room_name=dispatch.room,
                dispatch_id=dispatch.id,
                name=call_request.name,
                phone_number=full_phone_number,
                country_code=call_request.country_code,
                amount=call_request.amount,
                transfer_to=call_request.transfer_to
            )

            logger.info(f"Dispatch created successfully: {dispatch.id}")
            logger.info(f"Room: {dispatch.room}")
            logger.info(f"Calling: {full_phone_number}")
            logger.info(f"MongoDB call_id: {call_id}")
            
            return CallResponse(
                success=True,
                message="Call dispatched successfully",
                call_id=call_id,
                room=dispatch.room,
                dispatch_id=dispatch.id
            )
            
        except Exception as e:
            logger.error(f"Error creating dispatch: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to dispatch call: {str(e)}"
            )
        finally:
            await lkapi.aclose()
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/calls", response_model=CallsResponse)
async def get_calls():
    """
    Retrieve all call records
    
    Returns list of all calls sorted by creation date (newest first)
    """
    try:
        calls = await database.get_all_calls(limit=100)
        
        # Convert to CallRecord models
        call_records = []
        for call in calls:
            call_records.append(
                CallRecord(
                    call_id=call["_id"],
                    room_name=call["room_name"],
                    dispatch_id=call["dispatch_id"],
                    name=call["name"],
                    phone_number=call["phone_number"],
                    country_code=call["country_code"],
                    amount=call["amount"],
                    status=call["status"],
                    created_at=call["created_at"],
                    completed_at=call.get("completed_at"),
                    transcript_file=call.get("transcript_file"),
                    transfer_to=call.get("transfer_to")
                )
            )
        
        return CallsResponse(
            calls=call_records,
            total=len(call_records)
        )
        
    except Exception as e:
        logger.error(f"Error fetching calls: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch calls: {str(e)}"
        )


@router.get("/transcripts/{call_id}", response_model=TranscriptResponse)
async def get_transcript(call_id: str):
    """
    Retrieve transcript for a specific call
    
    Args:
        call_id: MongoDB ObjectId of the call
    
    Returns:
        Transcript data with messages and metadata
    """
    try:
        # Get call record from MongoDB
        call = await database.get_call_by_id(call_id)
        
        if not call:
            raise HTTPException(
                status_code=404,
                detail=f"Call with ID {call_id} not found"
            )
        
        # Check if transcript file exists
        transcript_filename = call.get("transcript_file")
        if not transcript_filename:
            raise HTTPException(
                status_code=404,
                detail=f"No transcript available for call {call_id}. Call may still be in progress."
            )
        
        # Construct full path to transcript file
        transcript_dir = os.getenv("TRANSCRIPT_DIR", "backend/transcripts")
        transcript_path = Path(transcript_dir) / transcript_filename
        
        if not transcript_path.exists():
            raise HTTPException(
                status_code=404,
                detail=f"Transcript file not found: {transcript_filename}"
            )
        
        # Read and parse transcript JSON
        try:
            with open(transcript_path, 'r', encoding='utf-8') as f:
                transcript_data = json.load(f)
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing transcript JSON: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to parse transcript file"
            )
        
        # Extract messages from transcript
        messages = []
        for item in transcript_data.get("items", []):
            if item.get("type") == "message":
                # Extract text from content array
                content = item.get("content", [])
                text = " ".join(content) if isinstance(content, list) else str(content)
                
                # Map 'assistant' role to 'agent' for frontend
                role = item.get("role", "unknown")
                if role == "assistant":
                    role = "agent"
                
                messages.append(
                    TranscriptMessage(
                        role=role,
                        message=text,  # Changed from 'text' to 'message'
                        timestamp=item.get("timestamp", "")
                    )
                )
        
        # Return transcript response with LLM-generated risk scores
        return TranscriptResponse(
            call_id=call["_id"],
            room_name=call["room_name"],
            name=call["name"],
            phone_number=call["phone_number"],
            amount=call["amount"],
            status=call["status"],
            created_at=call["created_at"],
            completed_at=call.get("completed_at"),
            transcript=messages,
            loan_recovery_score=call.get("loan_recovery_score"),
            willingness_to_pay_score=call.get("willingness_to_pay_score"),
            escalation_risk_score=call.get("escalation_risk_score"),
            customer_sentiment_score=call.get("customer_sentiment_score"),
            promise_to_pay_reliability_index=call.get("promise_to_pay_reliability_index")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching transcript: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch transcript: {str(e)}"
        )


