/**
 * TypeScript types for Tuning Loop module
 * Used in the Automated Tuning Loop (Phase 4, Module 4)
 */

/**
 * Tuning loop status enum matching backend
 */
export type TuningStatus = "PENDING" | "RUNNING" | "COMPLETED" | "FAILED";

/**
 * Scenario with weight for tuning configuration
 */
export interface ScenarioWeight {
  scenario_id: string;
  weight: number; // 1-5
}

/**
 * Configuration for a tuning loop
 */
export interface TuningConfig {
  target_score: number; // 0-100
  max_iterations: number; // 1-10
  scenario_weights: ScenarioWeight[];
}

/**
 * Evaluation scores from a single iteration
 */
export interface IterationScores {
  task_completion: number; // 0-100
  conversation_efficiency: number; // 0-100
}

/**
 * A single iteration in the tuning loop
 */
export interface TuningIteration {
  iteration_number: number;
  prompt_id: string;
  evaluation_ids: string[];
  weighted_score: number;
  timestamp: string;
}

/**
 * Request payload to create a new tuning loop
 */
export interface TuningLoopCreate {
  initial_prompt_id: string;
  target_score: number;
  max_iterations: number;
  scenarios: ScenarioWeight[];
}

/**
 * Complete tuning loop response from API
 */
export interface TuningLoop {
  _id: string;
  status: TuningStatus;
  config: TuningConfig;
  iterations: TuningIteration[];
  final_prompt_id?: string;
  error_message?: string;
  created_at: string;
  completed_at?: string;
}

/**
 * Simplified status response when creating a tuning loop
 */
export interface TuningLoopStatusResponse {
  tuning_loop_id: string;
  status: TuningStatus;
  current_iteration: number | null;
  latest_score: number | null;
}

/**
 * Enriched tuning loop with prompt and scenario names for display
 */
export interface TuningLoopWithDetails extends TuningLoop {
  initial_prompt_name?: string;
  final_prompt_name?: string;
  scenario_names?: { [key: string]: string }; // scenario_id -> name mapping
}
