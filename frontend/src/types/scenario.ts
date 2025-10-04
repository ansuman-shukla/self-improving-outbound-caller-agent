/**
 * TypeScript types for the Scenario module
 * Matches backend Pydantic models for Scenarios
 */

// ============= SCENARIO TYPES =============

/**
 * Request model for generating a new scenario with AI
 */
export interface ScenarioCreate {
  personality_id: string; // ID of personality to base scenario on
  brief: string; // User's brief situation description
}

/**
 * Request model for updating an existing scenario
 * All fields are optional
 */
export interface ScenarioUpdate {
  backstory?: string; // Updated detailed backstory
  weight?: number; // Updated importance/weight (1-5)
}

/**
 * Response model for scenario (includes MongoDB _id and AI-generated content)
 */
export interface Scenario {
  _id: string; // MongoDB document ID
  personality_id: string; // ID of personality this scenario is based on
  title: string; // AI-generated title
  brief: string; // Original user brief
  backstory: string; // AI-generated (and user-editable) detailed backstory
  objective: string; // AI-generated goal for the debtor
  weight: number; // Importance/weight (1-5), defaults to 3
  created_at: string; // ISO date string
}

/**
 * Extended scenario with personality name for display purposes
 */
export interface ScenarioWithPersonality extends Scenario {
  personality_name?: string; // Name of the associated personality
}
