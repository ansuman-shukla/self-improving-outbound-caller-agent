/**
 * TypeScript types for Evaluation module
 * Used in the Manual Evaluation Engine (Phase 3, Module 3)
 */

/**
 * Evaluation status enum matching backend
 */
export type EvaluationStatus = "PENDING" | "RUNNING" | "COMPLETED" | "FAILED";

/**
 * A single message in the conversation transcript
 */
export interface TranscriptMessage {
  speaker: "agent" | "debtor";
  message: string;
}

/**
 * Scores from the evaluation
 */
export interface EvaluationScores {
  task_completion: number; // 0-100
  conversation_efficiency: number; // 0-100
}

/**
 * Request payload to create a new evaluation
 */
export interface EvaluationCreate {
  prompt_id: string;
  scenario_id: string;
}

/**
 * Evaluation result from the API
 */
export interface Evaluation {
  _id: string;
  prompt_id: string;
  scenario_id: string;
  status: EvaluationStatus;
  transcript?: TranscriptMessage[];
  scores?: EvaluationScores;
  evaluator_analysis?: string;
  error_message?: string;
  created_at: string;
  completed_at?: string;
}

/**
 * Response when creating a new evaluation
 */
export interface EvaluationStatusResponse {
  result_id: string;
  status: EvaluationStatus;
}

/**
 * Enriched evaluation with prompt and scenario names for display
 */
export interface EvaluationWithDetails extends Evaluation {
  prompt_name?: string;
  scenario_title?: string;
}
