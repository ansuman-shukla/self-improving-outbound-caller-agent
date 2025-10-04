"""
Main FastAPI Application
Handles app initialization, middleware, startup/shutdown events
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import logging
import os
import asyncio
import uvicorn

from core import database
from core.gemini_client import configure_gemini, cleanup_gemini
from api.router import router as main_router
from api.personalities import router as personalities_router
from api.prompts import router as prompts_router
from api.scenarios import router as scenarios_router
from api.evaluations import router as evaluations_router
from api.tuning import router as tuning_router
from services import transcript_watcher

# Load environment variables
load_dotenv(dotenv_path=".env.local")

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app instance
app = FastAPI(
    title="Outbound Caller API",
    description="API to trigger outbound calls with LiveKit agent",
    version="1.0.0"
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Next.js frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(main_router)  # Main endpoints (calls, transcripts, etc.)
app.include_router(personalities_router)  # Phase 1 - Personalities endpoints
app.include_router(prompts_router)  # Phase 1 - Prompts endpoints
app.include_router(scenarios_router)  # Phase 2 - Scenarios endpoints
app.include_router(evaluations_router)  # Phase 3 - Evaluations endpoints
app.include_router(tuning_router)  # Phase 4 - Tuning Loop endpoints


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    try:
        # Connect to MongoDB
        await database.connect_to_mongodb()
        logger.info("✅ MongoDB connected")
        
        # Configure Gemini API
        configure_gemini()
        logger.info("✅ Gemini API configured")
        
        # Start transcript file watcher
        transcript_dir = os.getenv("TRANSCRIPT_DIR", "backend/transcripts")
        loop = asyncio.get_event_loop()
        transcript_watcher.start_watcher(transcript_dir, loop)
        logger.info("✅ Transcript watcher started")
        
        logger.info("✅ All services initialized successfully")
    except Exception as e:
        logger.error(f"❌ Failed to initialize services: {e}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    try:
        # Stop transcript watcher
        transcript_watcher.stop_watcher()
        logger.info("✅ Transcript watcher stopped")
        
        # Cleanup Gemini client
        cleanup_gemini()
        logger.info("✅ Gemini client cleaned up")
        
        # Close MongoDB connection
        await database.close_mongodb_connection()
        logger.info("✅ MongoDB connection closed")
        
        logger.info("✅ All services shut down successfully")
    except Exception as e:
        logger.error(f"❌ Error during shutdown: {e}")


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "Internal server error",
            "error": str(exc)
        }
    )


if __name__ == "__main__":
    # Run the server
    port = int(os.getenv("API_PORT", "8000"))
    host = os.getenv("API_HOST", "localhost")
    
    logger.info(f"Starting Outbound Caller API on {host}:{port}")
    logger.info("Make sure the agent is running with: python run_agent.py")
    
    uvicorn.run(
        app,
        host=host,
        port=port,
        reload=True,  # Enable auto-reload for development
        log_level="info"
    )
