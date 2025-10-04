"""
Transcript File Watcher Service
Monitors the transcripts folder for new transcript files and updates MongoDB
"""

import os
import re
import json
import asyncio
import logging
from pathlib import Path
from typing import Optional
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileCreatedEvent

from core import database
from services.transcript_analyzer import get_analyzer

logger = logging.getLogger(__name__)

# Regex pattern to extract room_name from transcript filename
# Format: transcript_{room_name}_{timestamp}.json
# Example: transcript_outbound-4986973328_20251003_231604.json
TRANSCRIPT_FILENAME_PATTERN = re.compile(r"^transcript_(.+?)_\d{8}_\d{6}\.json$")


class TranscriptFileHandler(FileSystemEventHandler):
    """
    Handler for file system events in the transcripts directory
    Processes newly created transcript files
    """
    
    def __init__(self, loop: asyncio.AbstractEventLoop):
        """
        Initialize the handler with an event loop for async operations
        
        Args:
            loop: Asyncio event loop to run async database updates
        """
        self.loop = loop
        super().__init__()
    
    def on_created(self, event: FileCreatedEvent):
        """
        Called when a file is created in the watched directory
        
        Args:
            event: File system event containing file path
        """
        # Only process file creation events (not directories)
        if event.is_directory:
            return
        
        # Get the filename from the full path
        filepath = Path(event.src_path)
        filename = filepath.name
        
        # Only process JSON files
        if not filename.endswith('.json'):
            logger.debug(f"Ignoring non-JSON file: {filename}")
            return
        
        logger.info(f"New transcript file detected: {filename}")
        
        # Extract room_name from filename
        room_name = self._extract_room_name(filename)
        
        if room_name:
            # Schedule async update in the event loop
            asyncio.run_coroutine_threadsafe(
                self._update_call_status(room_name, filename),
                self.loop
            )
        else:
            logger.warning(f"Could not extract room_name from filename: {filename}")
    
    def _extract_room_name(self, filename: str) -> Optional[str]:
        """
        Extract room_name from transcript filename
        
        Args:
            filename: Transcript filename (e.g., transcript_outbound-4986973328_20251003_231604.json)
        
        Returns:
            Extracted room_name (e.g., outbound-4986973328) or None if pattern doesn't match
        """
        match = TRANSCRIPT_FILENAME_PATTERN.match(filename)
        if match:
            return match.group(1)
        return None
    
    async def _update_call_status(self, room_name: str, transcript_file: str):
        """
        Update the call record in MongoDB with transcript information
        and analyze transcript to generate risk scores
        
        Args:
            room_name: Unique room identifier
            transcript_file: Name of the transcript file
        """
        try:
            logger.info(f"Updating call status for room: {room_name}")
            
            # Update MongoDB record with transcript file
            success = await database.update_call_status(
                room_name=room_name,
                status="completed",
                transcript_file=transcript_file
            )
            
            if success:
                logger.info(f"✅ Successfully updated call {room_name} with transcript {transcript_file}")
                
                # Now analyze the transcript with LLM
                await self._analyze_and_update_scores(room_name, transcript_file)
            else:
                logger.warning(f"⚠️ No call record found for room_name: {room_name}")
                
        except Exception as e:
            logger.error(f"❌ Error updating call status for {room_name}: {e}")
    
    async def _analyze_and_update_scores(self, room_name: str, transcript_file: str):
        """
        Read transcript file, analyze with LLM, and update scores in MongoDB
        
        Args:
            room_name: Unique room identifier
            transcript_file: Name of the transcript file
        """
        try:
            logger.info(f"🤖 Starting LLM analysis for transcript: {transcript_file}")
            
            # Construct path to transcript file
            transcript_path = Path(os.getenv("TRANSCRIPT_DIR", "backend/transcripts")) / transcript_file
            
            if not transcript_path.exists():
                logger.error(f"❌ Transcript file not found: {transcript_path}")
                return
            
            # Read transcript JSON
            with open(transcript_path, 'r', encoding='utf-8') as f:
                transcript_data = json.load(f)
            
            # Get the analyzer instance and analyze transcript
            analyzer = get_analyzer()
            scores = await analyzer.analyze_transcript(transcript_data)
            
            if scores:
                # Update MongoDB with the scores
                success = await database.update_call_scores(
                    room_name=room_name,
                    loan_recovery_score=scores["loan_recovery_score"],
                    willingness_to_pay_score=scores["willingness_to_pay_score"],
                    escalation_risk_score=scores["escalation_risk_score"],
                    customer_sentiment_score=scores["customer_sentiment_score"],
                    promise_to_pay_reliability_index=scores["promise_to_pay_reliability_index"]
                )
                
                if success:
                    logger.info(f"✅ Successfully updated risk scores for {room_name}")
                else:
                    logger.warning(f"⚠️ Failed to update risk scores for {room_name}")
            else:
                logger.warning(f"⚠️ LLM analysis failed for {transcript_file}")
                
        except json.JSONDecodeError as e:
            logger.error(f"❌ Error parsing transcript JSON {transcript_file}: {e}")
        except Exception as e:
            logger.error(f"❌ Error analyzing transcript {transcript_file}: {e}")


class TranscriptWatcher:
    """
    Manages the file system observer for transcript monitoring
    """
    
    def __init__(self, transcript_dir: str, loop: asyncio.AbstractEventLoop):
        """
        Initialize the transcript watcher
        
        Args:
            transcript_dir: Path to the directory containing transcripts
            loop: Asyncio event loop for async operations
        """
        self.transcript_dir = Path(transcript_dir)
        self.loop = loop
        self.observer: Optional[Observer] = None
        self.handler: Optional[TranscriptFileHandler] = None
        
        # Create transcripts directory if it doesn't exist
        self.transcript_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Transcript watcher initialized for directory: {self.transcript_dir}")
    
    def start(self):
        """
        Start monitoring the transcripts directory
        """
        if self.observer is not None:
            logger.warning("Transcript watcher is already running")
            return
        
        # Create handler and observer
        self.handler = TranscriptFileHandler(self.loop)
        self.observer = Observer()
        
        # Schedule the observer to watch the transcripts directory
        self.observer.schedule(
            self.handler,
            path=str(self.transcript_dir),
            recursive=False
        )
        
        # Start the observer thread
        self.observer.start()
        logger.info(f"🔍 Transcript watcher started monitoring: {self.transcript_dir}")
    
    def stop(self):
        """
        Stop monitoring the transcripts directory
        """
        if self.observer is None:
            logger.warning("Transcript watcher is not running")
            return
        
        logger.info("Stopping transcript watcher...")
        self.observer.stop()
        self.observer.join()
        self.observer = None
        self.handler = None
        logger.info("✅ Transcript watcher stopped")


# Global watcher instance
_watcher: Optional[TranscriptWatcher] = None


def start_watcher(transcript_dir: str, loop: asyncio.AbstractEventLoop) -> TranscriptWatcher:
    """
    Start the transcript file watcher
    
    Args:
        transcript_dir: Path to the directory containing transcripts
        loop: Asyncio event loop for async operations
    
    Returns:
        TranscriptWatcher instance
    """
    global _watcher
    
    if _watcher is not None:
        logger.warning("Transcript watcher already exists")
        return _watcher
    
    _watcher = TranscriptWatcher(transcript_dir, loop)
    _watcher.start()
    return _watcher


def stop_watcher():
    """
    Stop the transcript file watcher
    """
    global _watcher
    
    if _watcher is not None:
        _watcher.stop()
        _watcher = None
    else:
        logger.warning("No watcher to stop")


def get_watcher() -> Optional[TranscriptWatcher]:
    """
    Get the current watcher instance
    
    Returns:
        Current TranscriptWatcher instance or None
    """
    return _watcher
