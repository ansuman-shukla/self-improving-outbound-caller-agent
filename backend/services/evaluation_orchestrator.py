"""
Evaluation Orchestrator Service
Handles the complete evaluation workflow as a background task
Orchestrates conversation simulation and transcript evaluation
"""

from typing import Dict
from core.database import (
    get_evaluation_by_id,
    update_evaluation_status,
    update_evaluation_result,
    get_prompt_by_id,
    get_scenario_by_id
)
from services.conversation_moderator import run_conversation_simulation
from services.transcript_evaluator import evaluate_transcript_dict


async def perform_full_evaluation(
    result_id: str,
    prompt_id: str,
    scenario_id: str
) -> None:
    """
    Main background task that orchestrates the full evaluation process
    
    This function:
    1. Updates status to RUNNING
    2. Fetches the prompt and scenario from the database
    3. Runs the conversation simulation (Moderator)
    4. Evaluates the transcript (Evaluator Bot)
    5. Saves results to MongoDB
    6. Updates status to COMPLETED or FAILED
    
    Args:
        result_id: MongoDB ObjectId of the evaluation_results document
        prompt_id: MongoDB ObjectId of the prompt to test
        scenario_id: MongoDB ObjectId of the scenario to test
    
    Returns:
        None (updates database directly)
    
    This function is designed to run as a FastAPI BackgroundTask
    """
    try:
        print(f"🚀 Starting evaluation: {result_id}")
        
        # Step 1: Update status to RUNNING
        await update_evaluation_status(result_id, "RUNNING")
        
        # Step 2: Fetch prompt and scenario from database
        prompt = await get_prompt_by_id(prompt_id)
        scenario = await get_scenario_by_id(scenario_id)
        
        if not prompt:
            raise Exception(f"Prompt not found: {prompt_id}")
        if not scenario:
            raise Exception(f"Scenario not found: {scenario_id}")
        
        # Step 3: Fetch the personality for the scenario
        personality_id = scenario.get("personality_id")
        if not personality_id:
            raise Exception(f"Scenario {scenario_id} has no personality_id")
        
        # Import here to avoid circular dependency
        from core.database import get_personality_by_id
        personality = await get_personality_by_id(personality_id)
        
        if not personality:
            raise Exception(f"Personality not found: {personality_id}")
        
        print(f"📋 Loaded prompt: {prompt.get('name')}")
        print(f"📋 Loaded scenario: {scenario.get('title')}")
        print(f"📋 Loaded personality: {personality.get('name')}")
        
        # Extract debtor information for variable replacement
        debtor_name = personality.get("name", "Customer")
        debtor_amount = personality.get("amount")  # May be None
        
        # Step 4: Run conversation simulation with proper variable replacement
        print(f"💬 Running conversation simulation...")
        transcript = await run_conversation_simulation(
            agent_system_prompt=prompt.get("prompt_text"),
            personality_system_prompt=personality.get("system_prompt"),
            scenario_objective=scenario.get("objective"),
            debtor_name=debtor_name,
            debtor_amount=debtor_amount
        )
        
        # Convert TranscriptMessage objects to dicts for database storage
        transcript_dicts = [
            {"speaker": msg.speaker, "message": msg.message}
            for msg in transcript
        ]
        
        print(f"✅ Conversation completed: {len(transcript_dicts)} messages")
        
        # Step 5: Evaluate the transcript
        print(f"📊 Evaluating transcript...")
        evaluation_result = await evaluate_transcript_dict(
            transcript_dicts=transcript_dicts,
            scenario_objective=scenario.get("objective")
        )
        
        scores = evaluation_result.get("scores")
        analysis = evaluation_result.get("evaluator_analysis")
        
        print(f"✅ Evaluation complete:")
        print(f"   - Task Completion: {scores.get('task_completion')}/100")
        print(f"   - Conversation Efficiency: {scores.get('conversation_efficiency')}/100")
        
        # Step 6: Save results to database
        await update_evaluation_result(
            evaluation_id=result_id,
            transcript=transcript_dicts,
            scores=scores,
            evaluator_analysis=analysis
        )
        
        print(f"✅ Evaluation {result_id} completed successfully")
        
    except Exception as e:
        # Handle any errors and update status to FAILED
        error_message = str(e)
        print(f"❌ Evaluation {result_id} failed: {error_message}")
        
        await update_evaluation_status(
            evaluation_id=result_id,
            status="FAILED",
            error_message=error_message
        )


async def get_evaluation_summary(result_id: str) -> Dict:
    """
    Get a summary of an evaluation result
    
    Args:
        result_id: MongoDB ObjectId of the evaluation result
    
    Returns:
        Dict with evaluation summary or error information
    """
    evaluation = await get_evaluation_by_id(result_id)
    
    if not evaluation:
        return {
            "error": "Evaluation not found",
            "result_id": result_id
        }
    
    # Return relevant fields for summary
    summary = {
        "result_id": evaluation.get("_id"),
        "status": evaluation.get("status"),
        "prompt_id": evaluation.get("prompt_id"),
        "scenario_id": evaluation.get("scenario_id"),
        "created_at": evaluation.get("created_at"),
        "completed_at": evaluation.get("completed_at")
    }
    
    # Add scores if available
    if evaluation.get("scores"):
        summary["scores"] = evaluation.get("scores")
    
    # Add error message if failed
    if evaluation.get("error_message"):
        summary["error_message"] = evaluation.get("error_message")
    
    return summary
