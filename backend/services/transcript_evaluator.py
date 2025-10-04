"""
Transcript Evaluator Service
Analyzes conversation transcripts and provides quantitative scores and qualitative feedback
Implements the evaluator bot logic as defined in the PRD
"""

import json
from typing import Dict, Tuple
from google import genai
from models.evaluation import TranscriptMessage, EvaluationScores
from core.gemini_client import generate_structured_content, create_schema


def create_evaluation_schema():
    """
    Create the JSON schema for evaluation scoring output
    
    Returns:
        genai.types.Schema: The schema object for structured evaluation output
    """
    return create_schema(
        genai.types.Type.OBJECT,
        properties={
            "scores": create_schema(
                genai.types.Type.OBJECT,
                properties={
                    "task_completion": create_schema(genai.types.Type.INTEGER),
                    "conversation_efficiency": create_schema(genai.types.Type.INTEGER),
                },
                required=["task_completion", "conversation_efficiency"]
            ),
            "evaluator_analysis": create_schema(genai.types.Type.STRING),
        },
        required=["scores", "evaluator_analysis"]
    )


def format_transcript_for_evaluation(transcript: list) -> str:
    """
    Format the transcript into a readable text format
    
    Args:
        transcript: List of TranscriptMessage objects or dicts
    
    Returns:
        str: Formatted transcript text
    """
    formatted_lines = []
    for msg in transcript:
        if isinstance(msg, TranscriptMessage):
            speaker = msg.speaker.upper()
            message = msg.message
        else:
            speaker = msg.get("speaker", "unknown").upper()
            message = msg.get("message", "")
        
        formatted_lines.append(f"{speaker}: {message}")
    
    return "\n".join(formatted_lines)


async def evaluate_transcript(
    transcript: list,
    scenario_objective: str,
    model_name: str = "gemini-2.0-flash-exp",
    temperature: float = 0.2
) -> Tuple[EvaluationScores, str]:
    """
    Evaluate a conversation transcript and provide scores and analysis
    
    This function implements the Evaluator Bot logic:
    - Analyzes the transcript against the debtor's objective and agent's goal
    - Provides quantitative scores for Task Completion and Conversation Efficiency
    - Provides qualitative feedback/analysis
    
    Args:
        transcript: List of TranscriptMessage objects or dicts with the conversation
        scenario_objective: The debtor's objective in this scenario
        model_name: The Gemini model to use (default: gemini-2.0-flash-exp)
        temperature: Temperature for evaluation (default: 0.2 for consistency)
    
    Returns:
        Tuple[EvaluationScores, str]: A tuple of (scores, analysis)
            - scores: EvaluationScores object with task_completion and conversation_efficiency
            - analysis: String with qualitative feedback
    
    Raises:
        Exception: If there's an error during evaluation
    
    Example:
        scores, analysis = await evaluate_transcript(
            transcript=[...],
            scenario_objective="Get payment plan without revealing full financial situation"
        )
    """
    try:
        # Format the transcript
        transcript_text = format_transcript_for_evaluation(transcript)
        
        # Create the evaluation prompt as specified in the PRD
        evaluation_prompt = f"""You are a conversation analyst. Your task is to evaluate the following debt collection call transcript.

DEBTOR'S OBJECTIVE: {scenario_objective}
AGENT'S GOAL: To collect the debt or arrange a payment plan in a compliant and efficient manner.

TRANSCRIPT:
{transcript_text}

Analyze the transcript and provide:
1. TASK COMPLETION SCORE (0-100): How well did the agent move towards their goal? Consider:
   - Did they successfully collect payment or arrange a payment plan?
   - Did they maintain compliance with regulations?
   - Did they handle objections effectively?
   - Did they achieve a concrete outcome?

2. CONVERSATION EFFICIENCY SCORE (0-100): How efficient was the agent's communication? Consider:
   - Was the dialogue relevant and on-topic?
   - Did they avoid unnecessary repetition?
   - Were they concise yet complete?
   - Did they waste time with irrelevant questions?

3. EVALUATOR ANALYSIS: Provide a brief qualitative analysis (2-4 sentences) highlighting:
   - Key strengths of the agent's approach
   - Main areas for improvement
   - How well they handled the specific debtor's objective and personality

Be objective and data-driven in your scoring."""

        # Get the evaluation schema
        response_schema = create_evaluation_schema()
        
        # Generate structured evaluation
        result_json = await generate_structured_content(
            prompt=evaluation_prompt,
            response_schema=response_schema,
            system_instruction="You are an expert conversation analyst specializing in debt collection call quality assessment. Be objective, fair, and data-driven in your evaluations.",
            model_name=model_name,
            temperature=temperature
        )
        
        # Parse the JSON response
        result_data = json.loads(result_json)
        
        # Extract scores
        scores_data = result_data.get("scores", {})
        scores = EvaluationScores(
            task_completion=scores_data.get("task_completion", 0),
            conversation_efficiency=scores_data.get("conversation_efficiency", 0)
        )
        
        # Extract analysis
        analysis = result_data.get("evaluator_analysis", "No analysis provided.")
        
        return scores, analysis
    
    except json.JSONDecodeError as e:
        print(f"❌ Error parsing evaluation JSON: {str(e)}")
        raise Exception(f"Failed to parse evaluation response: {str(e)}")
    
    except Exception as e:
        print(f"❌ Error during transcript evaluation: {str(e)}")
        raise Exception(f"Transcript evaluation failed: {str(e)}")


async def evaluate_transcript_dict(
    transcript_dicts: list,
    scenario_objective: str,
    model_name: str = "gemini-2.0-flash-exp",
    temperature: float = 0.2
) -> Dict:
    """
    Evaluate a transcript and return results as a dictionary
    
    This is a convenience wrapper around evaluate_transcript that returns
    the results as a dictionary for easier database storage.
    
    Args:
        transcript_dicts: List of dicts with conversation (format: [{"speaker": "agent", "message": "..."}])
        scenario_objective: The debtor's objective in this scenario
        model_name: The Gemini model to use
        temperature: Temperature for evaluation
    
    Returns:
        Dict: Dictionary with "scores" and "evaluator_analysis" keys
    
    Example:
        result = await evaluate_transcript_dict(
            transcript_dicts=[{"speaker": "agent", "message": "Hello"}, ...],
            scenario_objective="..."
        )
        # result = {
        #     "scores": {"task_completion": 75, "conversation_efficiency": 82},
        #     "evaluator_analysis": "The agent was empathetic..."
        # }
    """
    scores, analysis = await evaluate_transcript(
        transcript=transcript_dicts,
        scenario_objective=scenario_objective,
        model_name=model_name,
        temperature=temperature
    )
    
    return {
        "scores": {
            "task_completion": scores.task_completion,
            "conversation_efficiency": scores.conversation_efficiency
        },
        "evaluator_analysis": analysis
    }
