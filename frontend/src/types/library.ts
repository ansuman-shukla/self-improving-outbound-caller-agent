/**
 * TypeScript types for the Library module
 * Matches backend Pydantic models for Personalities and Prompts
 */

// ============= PERSONALITY TYPES =============

/**
 * Request model for creating a new personality
 */
export interface PersonalityCreate {
  name: string;
  description: string;
  core_traits: Record<string, string>; // Key-value pairs for traits
  system_prompt: string;
  amount?: number; // Optional pending debt amount in rupees
}

/**
 * Request model for updating an existing personality
 * All fields are optional
 */
export interface PersonalityUpdate {
  name?: string;
  description?: string;
  core_traits?: Record<string, string>;
  system_prompt?: string;
  amount?: number; // Optional pending debt amount in rupees
}

/**
 * Response model for personality (includes MongoDB _id)
 */
export interface Personality {
  _id: string; // MongoDB document ID
  name: string;
  description: string;
  core_traits: Record<string, string>;
  system_prompt: string;
  amount?: number; // Optional pending debt amount in rupees
  created_at: string; // ISO date string
}

/**
 * Response model for list of personalities
 */
export interface PersonalityListResponse {
  personalities: Personality[];
  total: number;
}

// ============= PROMPT TYPES =============

/**
 * Request model for creating a new prompt
 */
export interface PromptCreate {
  name: string;
  prompt_text: string;
  version: string;
}

/**
 * Request model for updating an existing prompt
 * All fields are optional
 */
export interface PromptUpdate {
  name?: string;
  prompt_text?: string;
  version?: string;
}

/**
 * Response model for prompt (includes MongoDB _id)
 */
export interface Prompt {
  _id: string; // MongoDB document ID
  name: string;
  prompt_text: string;
  version: string;
  created_at: string; // ISO date string
}

/**
 * Response model for list of prompts
 */
export interface PromptListResponse {
  prompts: Prompt[];
  total: number;
}
