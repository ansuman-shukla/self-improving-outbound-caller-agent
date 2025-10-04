"""
Tuning Service
Implements the core logic for the Automated Tuning Loop module
Handles weighted score calculation and Writer-Critique cycle for prompt improvement
"""

from typing import List, Dict, Tuple
import json
from google import genai
from models.tuning_loop import ScenarioWeight
from models.evaluation import EvaluationScores
from core.database import get_evaluations_collection
from core.gemini_client import generate_structured_content, create_schema
from bson import ObjectId


async def calculate_weighted_average(
    evaluation_ids: List[str],
    scenario_weights: List[ScenarioWeight]
) -> float:
    """
    Calculate the weighted average score from multiple evaluation results
    
    This function:
    1. Fetches evaluation results from the database
    2. Matches each evaluation with its scenario weight
    3. Calculates a weighted average of both task_completion and conversation_efficiency
    4. Returns a single weighted score (0-100)
    
    The formula:
    - For each evaluation, calculate: (task_completion + conversation_efficiency) / 2
    - Multiply each evaluation's average by its scenario weight
    - Sum all weighted scores and divide by the sum of weights
    
    Args:
        evaluation_ids: List of evaluation result IDs to include in calculation
        scenario_weights: List of ScenarioWeight objects mapping scenario_id to weight
    
    Returns:
        float: Weighted average score (0-100)
    
    Raises:
        ValueError: If evaluation not found or missing required data
        
    Example:
        # Scenario A (weight=4): task=80, efficiency=70 -> avg=75, weighted=300
        # Scenario B (weight=2): task=60, efficiency=80 -> avg=70, weighted=140
        # Total: (300+140)/(4+2) = 440/6 = 73.33
        score = await calculate_weighted_average(
            evaluation_ids=["eval1", "eval2"],
            scenario_weights=[
                ScenarioWeight(scenario_id="scen1", weight=4),
                ScenarioWeight(scenario_id="scen2", weight=2)
            ]
        )
    """
    collection = get_evaluations_collection()
    
    # Create a map of scenario_id to weight for quick lookup
    weight_map = {sw.scenario_id: sw.weight for sw in scenario_weights}
    
    total_weighted_score = 0.0
    total_weight = 0
    
    # Fetch and process each evaluation
    for eval_id in evaluation_ids:
        # Fetch evaluation from database
        evaluation = await collection.find_one({"_id": ObjectId(eval_id)})
        
        if not evaluation:
            raise ValueError(f"Evaluation not found: {eval_id}")
        
        # Ensure evaluation is completed and has scores
        if evaluation.get("status") != "COMPLETED":
            raise ValueError(f"Evaluation {eval_id} is not completed")
        
        scores = evaluation.get("scores")
        if not scores:
            raise ValueError(f"Evaluation {eval_id} has no scores")
        
        # Get the scenario_id for this evaluation
        scenario_id = str(evaluation.get("scenario_id"))
        
        # Get the weight for this scenario
        weight = weight_map.get(scenario_id)
        if weight is None:
            raise ValueError(f"No weight found for scenario {scenario_id}")
        
        # Calculate average score for this evaluation
        # (task_completion + conversation_efficiency) / 2
        task_completion = scores.get("task_completion", 0)
        conversation_efficiency = scores.get("conversation_efficiency", 0)
        evaluation_avg = (task_completion + conversation_efficiency) / 2.0
        
        # Add weighted score to total
        total_weighted_score += evaluation_avg * weight
        total_weight += weight
    
    # Calculate final weighted average
    if total_weight == 0:
        return 0.0
    
    weighted_average = total_weighted_score / total_weight
    return round(weighted_average, 2)


def create_writer_schema():
    """
    Create the JSON schema for Writer agent output (new prompt)
    
    Returns:
        genai.types.Schema: The schema object for structured prompt generation
    """
    return create_schema(
        genai.types.Type.OBJECT,
        properties={
            "system_prompt": create_schema(genai.types.Type.STRING),
        },
        required=["system_prompt"]
    )


def create_critique_schema():
    """
    Create the JSON schema for Critique agent output (feedback and pass/fail)
    
    Returns:
        genai.types.Schema: The schema object for structured critique output
    """
    return create_schema(
        genai.types.Type.OBJECT,
        properties={
            "feedback": create_schema(genai.types.Type.STRING),
            "pass": create_schema(genai.types.Type.BOOLEAN),
        },
        required=["feedback", "pass"]
    )


async def run_writer_critique_cycle(
    context_package: str,
    model_name: str = "gemini-2.5-flash",
    temperature: float = 0.5,
    max_critique_cycles: int = 3
) -> str:
    """
    Run the Writer-Critique cycle to generate an improved prompt
    
    This implements the Writer-Critique loop as specified in the PRD:
    1. Writer Agent: Analyzes failed evaluations and generates a new improved prompt
    2. Critique Agent: Reviews the new prompt and provides feedback
    3. If critique passes, return the prompt; otherwise, Writer revises (up to max cycles)
    
    The context_package should contain:
    - Current prompt text
    - Target score
    - Failed evaluation transcripts and scores
    - Evaluator analysis for each failure
    - Instructions for improvement
    
    Args:
        context_package: Comprehensive context string with all information for prompt improvement
        model_name: The Gemini model to use (default: gemini-2.5-flash)
        temperature: Temperature for generation (default: 0.5 for creativity)
        max_critique_cycles: Maximum number of Writer-Critique cycles (default: 3)
    
    Returns:
        str: The improved system prompt text
    
    Raises:
        Exception: If there's an error during generation or max cycles exceeded
        
    Example:
        context = '''
        CURRENT PROMPT:
        You are a debt collection agent...
        
        TARGET SCORE: 85
        
        FAILED EVALUATIONS:
        Scenario: Anxious Debtor
        Score: 65
        Transcript: ...
        Analysis: Agent was too pushy and didn't show empathy...
        '''
        
        new_prompt = await run_writer_critique_cycle(context)
    """
    writer_schema = create_writer_schema()
    critique_schema = create_critique_schema()
    
    # Initial Writer prompt
    writer_prompt = f"""You are an expert prompt engineer specializing in conversational AI for debt collection.

Your task is to create an improved system prompt for a debt collection voice agent based on the following context:

{context_package}

INSTRUCTIONS:
1. Analyze the failed evaluations to identify patterns and weaknesses
2. Understand what caused low scores in Task Completion and Conversation Efficiency
3. Create a new system prompt that addresses these weaknesses
4. The new prompt should be clear, comprehensive, and actionable
5. Focus on empathy, compliance, efficiency, and goal achievement
6. Include specific behavioral guidelines based on the failure patterns

Generate a complete, ready-to-use system prompt that will perform better than the current one."""

    current_prompt_text = None
    
    for cycle in range(max_critique_cycles):
        # Step 1: Writer generates (or revises) the prompt
        if current_prompt_text is None:
            # First generation
            writer_input = writer_prompt
        else:
            # Revision based on critique feedback
            writer_input = f"""{writer_prompt}

PREVIOUS ATTEMPT:
{current_prompt_text}

CRITIQUE FEEDBACK:
{critique_feedback}

Please revise the prompt to address the critique feedback."""

        # Call Writer agent
        writer_response_json = await generate_structured_content(
            prompt=writer_input,
            response_schema=writer_schema,
            model_name=model_name,
            temperature=temperature
        )
        
        # Parse JSON response
        writer_response = json.loads(writer_response_json)
        current_prompt_text = writer_response.get("system_prompt")
        
        # Step 2: Critique agent reviews the prompt
        critique_prompt = f"""You are a senior AI quality reviewer for conversational agents.

Your task is to evaluate the following system prompt for a debt collection agent.

CONTEXT PACKAGE:
{context_package}

PROPOSED SYSTEM PROMPT:
{current_prompt_text}

EVALUATION CRITERIA:
1. Does it address the specific failures identified in the context?
2. Is it clear, specific, and actionable?
3. Does it include appropriate empathy and compliance guidelines?
4. Does it provide concrete behavioral instructions?
5. Is it likely to improve both Task Completion and Conversation Efficiency?

Provide constructive feedback and indicate whether this prompt is acceptable (pass=true) or needs revision (pass=false)."""

        # Call Critique agent
        critique_response_json = await generate_structured_content(
            prompt=critique_prompt,
            response_schema=critique_schema,
            model_name=model_name,
            temperature=0.3  # Lower temperature for more consistent critique
        )
        
        # Parse JSON response
        critique_response = json.loads(critique_response_json)
        critique_feedback = critique_response.get("feedback")
        critique_pass = critique_response.get("pass")
        
        # Step 3: Check if critique passed
        if critique_pass:
            print(f"✅ Writer-Critique cycle completed in {cycle + 1} cycles")
            return current_prompt_text
        
        # If not passed and not the last cycle, continue to next iteration
        if cycle < max_critique_cycles - 1:
            print(f"🔄 Critique cycle {cycle + 1}: Revision needed. Feedback: {critique_feedback[:100]}...")
    
    # If we've exhausted max cycles, return the best attempt
    print(f"⚠️ Max critique cycles ({max_critique_cycles}) reached. Returning latest prompt.")
    return current_prompt_text


async def build_context_package(
    current_prompt_text: str,
    target_score: float,
    failed_evaluation_ids: List[str],
    scenario_weights: List[ScenarioWeight]
) -> str:
    """
    Build a comprehensive context package for the Writer-Critique cycle
    
    This function gathers all relevant information for prompt improvement:
    - Current prompt
    - Target score
    - Details of failed evaluations (transcripts, scores, analysis)
    - Scenario information
    
    Args:
        current_prompt_text: The current system prompt being improved
        target_score: The target weighted average score
        failed_evaluation_ids: List of evaluation IDs that didn't meet the target
        scenario_weights: List of ScenarioWeight objects for context
    
    Returns:
        str: Formatted context package string
    """
    from core.database import get_scenarios_collection
    
    evaluations_collection = get_evaluations_collection()
    scenarios_collection = get_scenarios_collection()
    
    # Start building the context
    context = f"""CURRENT SYSTEM PROMPT:
{current_prompt_text}

TARGET SCORE: {target_score}

"""
    
    # Add details for each failed evaluation
    context += "FAILED EVALUATIONS:\n\n"
    
    for i, eval_id in enumerate(failed_evaluation_ids, 1):
        evaluation = await evaluations_collection.find_one({"_id": ObjectId(eval_id)})
        
        if not evaluation:
            continue
        
        # Get scenario details
        scenario = await scenarios_collection.find_one({"_id": ObjectId(evaluation.get("scenario_id"))})
        
        scores = evaluation.get("scores", {})
        task_completion = scores.get("task_completion", 0)
        conversation_efficiency = scores.get("conversation_efficiency", 0)
        avg_score = (task_completion + conversation_efficiency) / 2.0
        
        context += f"--- Evaluation {i} ---\n"
        if scenario:
            context += f"Scenario: {scenario.get('title', 'Unknown')}\n"
            context += f"Scenario Objective: {scenario.get('objective', 'N/A')}\n"
        context += f"Scores: Task Completion={task_completion}, Conversation Efficiency={conversation_efficiency}, Average={avg_score:.1f}\n"
        context += f"Evaluator Analysis: {evaluation.get('evaluator_analysis', 'N/A')}\n"
        
        # Add transcript excerpt (first 5 exchanges)
        transcript = evaluation.get("transcript", [])
        context += f"Transcript Excerpt (first 5 exchanges):\n"
        for msg in transcript[:10]:  # 10 messages = 5 exchanges (agent + debtor)
            speaker = msg.get("speaker", "unknown").upper()
            message = msg.get("message", "")
            context += f"  {speaker}: {message}\n"
        
        context += "\n"
    
    context += """
IMPROVEMENT GUIDELINES:
- Focus on addressing the specific weaknesses identified in the evaluations
- Enhance empathy and rapport-building techniques
- Improve goal-oriented dialogue flow
- Reduce repetitive or irrelevant responses
- Maintain compliance and professionalism
- Provide clear, actionable instructions for the agent
"""
    
    return context


async def perform_tuning_loop(
    tuning_loop_id: str,
    initial_prompt_id: str,
    target_score: float,
    max_iterations: int,
    scenario_weights: List[ScenarioWeight]
):
    """
    Orchestrate the complete automated tuning loop process
    
    This is the main background task that:
    1. Updates status to RUNNING
    2. For each iteration (up to max_iterations):
       a. Runs evaluations for all scenarios with current prompt
       b. Calculates weighted average score
       c. Saves iteration results to database
       d. If target score reached, mark COMPLETED and stop
       e. If not, generate improved prompt using Writer-Critique cycle
       f. Save new prompt to database for next iteration
    3. Sets final_prompt_id to the best performing prompt
    4. Updates status to COMPLETED or FAILED
    
    Args:
        tuning_loop_id: ID of the tuning loop document in MongoDB
        initial_prompt_id: ID of the starting agent prompt
        target_score: Target weighted average score to achieve (0-100)
        max_iterations: Maximum number of iterations to run
        scenario_weights: List of ScenarioWeight objects for evaluation
    
    This function updates the MongoDB document at each step to allow
    frontend polling to track progress.
    """
    from core import database
    from services.evaluation_orchestrator import perform_full_evaluation
    import asyncio
    
    try:
        print(f"🚀 Starting tuning loop {tuning_loop_id}")
        
        # Update status to RUNNING
        await database.update_tuning_loop_status(tuning_loop_id, "RUNNING")
        
        current_prompt_id = initial_prompt_id
        best_prompt_id = initial_prompt_id
        best_score = 0.0
        
        # Main tuning loop
        for iteration_num in range(1, max_iterations + 1):
            print(f"🔄 Tuning Loop - Iteration {iteration_num}/{max_iterations}")
            
            # Step 1: Run evaluations for all scenarios with current prompt
            evaluation_ids = []
            
            for scenario_weight in scenario_weights:
                scenario_id = scenario_weight.scenario_id
                
                print(f"  📝 Running evaluation: Prompt={current_prompt_id[:8]}..., Scenario={scenario_id[:8]}...")
                
                # Create evaluation and run in background
                eval_result_id = await database.create_evaluation(
                    prompt_id=current_prompt_id,
                    scenario_id=scenario_id
                )
                
                # Run the evaluation (this will update the document)
                await perform_full_evaluation(
                    result_id=eval_result_id,
                    prompt_id=current_prompt_id,
                    scenario_id=scenario_id
                )
                
                evaluation_ids.append(eval_result_id)
                
                # Small delay between evaluations to avoid rate limiting
                await asyncio.sleep(2)
            
            # Step 2: Calculate weighted average score
            print(f"  📊 Calculating weighted average score...")
            weighted_score = await calculate_weighted_average(
                evaluation_ids=evaluation_ids,
                scenario_weights=scenario_weights
            )
            
            print(f"  ✅ Iteration {iteration_num} Score: {weighted_score:.2f}")
            
            # Step 3: Save iteration results
            await database.add_tuning_loop_iteration(
                tuning_loop_id=tuning_loop_id,
                iteration_number=iteration_num,
                prompt_id=current_prompt_id,
                evaluation_ids=evaluation_ids,
                weighted_score=weighted_score
            )
            
            # Track best prompt
            if weighted_score > best_score:
                best_score = weighted_score
                best_prompt_id = current_prompt_id
            
            # Step 4: Check if target score reached
            if weighted_score >= target_score:
                print(f"🎯 Target score {target_score} reached! Score: {weighted_score:.2f}")
                await database.set_tuning_loop_final_prompt(tuning_loop_id, best_prompt_id)
                await database.update_tuning_loop_status(tuning_loop_id, "COMPLETED")
                return
            
            # Step 5: If not last iteration, generate improved prompt
            if iteration_num < max_iterations:
                print(f"  🤖 Generating improved prompt using Writer-Critique cycle...")
                
                # Get failed evaluations (those below target)
                failed_eval_ids = []
                for eval_id in evaluation_ids:
                    eval_doc = await database.get_evaluation_by_id(eval_id)
                    if eval_doc and eval_doc.get("scores"):
                        scores = eval_doc["scores"]
                        avg = (scores["task_completion"] + scores["conversation_efficiency"]) / 2.0
                        if avg < target_score:
                            failed_eval_ids.append(eval_id)
                
                # Get current prompt text
                current_prompt_doc = await database.get_prompt_by_id(current_prompt_id)
                current_prompt_text = current_prompt_doc.get("prompt_text", "")
                
                # Build context package for Writer-Critique
                context_package = await build_context_package(
                    current_prompt_text=current_prompt_text,
                    target_score=target_score,
                    failed_evaluation_ids=failed_eval_ids if failed_eval_ids else evaluation_ids,
                    scenario_weights=scenario_weights
                )
                
                # Run Writer-Critique cycle to generate improved prompt
                improved_prompt_text = await run_writer_critique_cycle(
                    context_package=context_package,
                    temperature=0.7
                )
                
                # Save the improved prompt to database
                new_prompt_name = f"Tuned-AI-Iter{iteration_num}-{tuning_loop_id[:8]}"
                new_prompt_version = f"Auto-generated from tuning loop iteration {iteration_num}"
                
                new_prompt_id = await database.insert_prompt(
                    name=new_prompt_name,
                    prompt_text=improved_prompt_text,
                    version=new_prompt_version
                )
                
                print(f"  ✅ New prompt created: {new_prompt_id}")
                
                # Use this new prompt for next iteration
                current_prompt_id = new_prompt_id
        
        # If we've completed all iterations without reaching target
        print(f"⚠️ Max iterations ({max_iterations}) reached. Best score: {best_score:.2f}")
        await database.set_tuning_loop_final_prompt(tuning_loop_id, best_prompt_id)
        await database.update_tuning_loop_status(tuning_loop_id, "COMPLETED")
        
    except Exception as e:
        error_message = f"Error in tuning loop: {str(e)}"
        print(f"❌ {error_message}")
        await database.update_tuning_loop_status(
            tuning_loop_id,
            "FAILED",
            error_message=error_message
        )
        raise
