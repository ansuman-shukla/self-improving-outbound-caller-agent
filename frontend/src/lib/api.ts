/**
 * API Client for communicating with FastAPI backend
 * Base URL: http://localhost:8000
 */

import axios, { AxiosInstance } from "axios";
import {
  Country,
  CallRequest,
  CallResponse,
  CallsResponse,
  TranscriptResponse,
  CheckStatusResponse,
} from "@/types/call";
import {
  Personality,
  PersonalityCreate,
  PersonalityUpdate,
  PersonalityListResponse,
  Prompt,
  PromptCreate,
  PromptUpdate,
  PromptListResponse,
} from "@/types/library";
import {
  Scenario,
  ScenarioCreate,
  ScenarioUpdate,
} from "@/types/scenario";
import {
  Evaluation,
  EvaluationCreate,
  EvaluationStatusResponse,
} from "@/types/evaluation";
import {
  TuningLoop,
  TuningLoopCreate,
  TuningLoopStatusResponse,
} from "@/types/tuning";

// Create axios instance with base configuration
const apiClient: AxiosInstance = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000",
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 30000, // 30 seconds
});

// Add request interceptor for logging
apiClient.interceptors.request.use(
  (config) => {
    console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`, {
      data: config.data,
      params: config.params,
    });
    return config;
  },
  (error) => {
    console.error("Request Error:", error);
    return Promise.reject(error);
  }
);

// Add response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      // Server responded with error status
      console.error("API Error Response:", {
        status: error.response.status,
        data: error.response.data,
        headers: error.response.headers,
      });
      const errorMessage = 
        error.response.data?.detail || 
        error.response.data?.message || 
        JSON.stringify(error.response.data) ||
        `HTTP ${error.response.status} Error`;
      throw new Error(errorMessage);
    } else if (error.request) {
      // Request made but no response
      console.error("Network Error:", error.message);
      throw new Error("Network error. Please check if the backend server is running.");
    } else {
      // Something else happened
      console.error("Error:", error.message);
      throw error;
    }
  }
);

/**
 * Get list of supported countries for country code dropdown
 */
export const getCountries = async (): Promise<Country[]> => {
  const response = await apiClient.get<{ countries: Country[] }>("/countries");
  return response.data.countries;
};

/**
 * Initiate an outbound call
 * @param data Call details including name, phone, amount, and country code
 */
export const makeCall = async (data: CallRequest): Promise<CallResponse> => {
  const response = await apiClient.post<CallResponse>("/call", data);
  return response.data;
};

/**
 * Get all call records from database
 * Returns list sorted by newest first
 */
export const getCalls = async (): Promise<CallsResponse> => {
  const response = await apiClient.get<CallsResponse>("/calls");
  return response.data;
};

/**
 * Get transcript for a specific call by call_id
 * @param callId MongoDB _id of the call
 */
export const getCallTranscript = async (
  callId: string
): Promise<TranscriptResponse> => {
  const response = await apiClient.get<TranscriptResponse>(
    `/transcripts/${callId}`
  );
  return response.data;
};

/**
 * Manually trigger status check for in-progress calls
 * Useful if file watcher missed a transcript file
 */
export const checkCallStatus = async (): Promise<CheckStatusResponse> => {
  const response = await apiClient.post<CheckStatusResponse>(
    "/calls/check-status"
  );
  return response.data;
};

/**
 * Health check endpoint
 */
export const healthCheck = async (): Promise<{ status: string }> => {
  const response = await apiClient.get("/health");
  return response.data;
};

// ============= LIBRARY API - PERSONALITIES =============

/**
 * Get all personalities
 * Returns list of all debtor personalities in the library
 */
export const getPersonalities = async (): Promise<PersonalityListResponse> => {
  const response = await apiClient.get<PersonalityListResponse>("/personalities");
  return response.data;
};

/**
 * Get a single personality by ID
 * @param id MongoDB _id of the personality
 */
export const getPersonalityById = async (id: string): Promise<Personality> => {
  const response = await apiClient.get<Personality>(`/personalities/${id}`);
  return response.data;
};

/**
 * Create a new personality
 * @param data Personality details including name, description, core_traits, and system_prompt
 */
export const createPersonality = async (data: PersonalityCreate): Promise<Personality> => {
  const response = await apiClient.post<Personality>("/personalities", data);
  return response.data;
};

/**
 * Update an existing personality
 * @param id MongoDB _id of the personality to update
 * @param data Partial personality data to update
 */
export const updatePersonality = async (
  id: string,
  data: PersonalityUpdate
): Promise<Personality> => {
  const response = await apiClient.put<Personality>(`/personalities/${id}`, data);
  return response.data;
};

/**
 * Delete a personality
 * @param id MongoDB _id of the personality to delete
 */
export const deletePersonality = async (id: string): Promise<{ message: string }> => {
  const response = await apiClient.delete<{ message: string }>(`/personalities/${id}`);
  return response.data;
};

// ============= LIBRARY API - PROMPTS =============

/**
 * Get all prompts
 * Returns list of all agent system prompts in the library
 */
export const getPrompts = async (): Promise<PromptListResponse> => {
  const response = await apiClient.get<PromptListResponse>("/prompts");
  return response.data;
};

/**
 * Get a single prompt by ID
 * @param id MongoDB _id of the prompt
 */
export const getPromptById = async (id: string): Promise<Prompt> => {
  const response = await apiClient.get<Prompt>(`/prompts/${id}`);
  return response.data;
};

/**
 * Create a new prompt
 * @param data Prompt details including name, prompt_text, and version
 */
export const createPrompt = async (data: PromptCreate): Promise<Prompt> => {
  const response = await apiClient.post<Prompt>("/prompts", data);
  return response.data;
};

/**
 * Update an existing prompt
 * @param id MongoDB _id of the prompt to update
 * @param data Partial prompt data to update
 */
export const updatePrompt = async (
  id: string,
  data: PromptUpdate
): Promise<Prompt> => {
  const response = await apiClient.put<Prompt>(`/prompts/${id}`, data);
  return response.data;
};

/**
 * Delete a prompt
 * @param id MongoDB _id of the prompt to delete
 */
export const deletePrompt = async (id: string): Promise<{ message: string }> => {
  const response = await apiClient.delete<{ message: string }>(`/prompts/${id}`);
  return response.data;
};

// ============= SCENARIO API =============

/**
 * Get all scenarios
 * Returns list of all test scenarios
 */
export const getScenarios = async (): Promise<Scenario[]> => {
  const response = await apiClient.get<Scenario[]>("/scenarios");
  return response.data;
};

/**
 * Get a single scenario by ID
 * @param id MongoDB _id of the scenario
 */
export const getScenarioById = async (id: string): Promise<Scenario> => {
  const response = await apiClient.get<Scenario>(`/scenarios/${id}`);
  return response.data;
};

/**
 * Generate a new scenario using AI
 * @param data Scenario generation details including personality_id and brief
 */
export const generateScenario = async (data: ScenarioCreate): Promise<Scenario> => {
  const response = await apiClient.post<Scenario>("/scenarios/generate", data);
  return response.data;
};

/**
 * Update an existing scenario
 * @param id MongoDB _id of the scenario to update
 * @param data Partial scenario data to update (backstory and/or weight)
 */
export const updateScenario = async (
  id: string,
  data: ScenarioUpdate
): Promise<Scenario> => {
  const response = await apiClient.put<Scenario>(`/scenarios/${id}`, data);
  return response.data;
};

/**
 * Delete a scenario
 * @param id MongoDB _id of the scenario to delete
 */
export const deleteScenario = async (id: string): Promise<{ message: string }> => {
  const response = await apiClient.delete<{ message: string }>(`/scenarios/${id}`);
  return response.data;
};

// ============================================================================
// EVALUATION API ENDPOINTS
// Part of Phase 3, Module 3: The Manual Evaluation Engine
// ============================================================================

/**
 * Create a new evaluation (async operation)
 * Returns immediately with result_id and PENDING status
 * Use getEvaluation to poll for completion
 * @param data Evaluation details including prompt_id and scenario_id
 */
export const createEvaluation = async (
  data: EvaluationCreate
): Promise<EvaluationStatusResponse> => {
  const response = await apiClient.post<EvaluationStatusResponse>(
    "/evaluations",
    data
  );
  return response.data;
};

/**
 * Get evaluation result by ID (polling endpoint)
 * @param id MongoDB _id of the evaluation result
 */
export const getEvaluation = async (id: string): Promise<Evaluation> => {
  const response = await apiClient.get<Evaluation>(`/evaluations/${id}`);
  return response.data;
};

/**
 * List all evaluation results
 * Returns evaluations sorted by created_at (newest first)
 */
export const listEvaluations = async (): Promise<Evaluation[]> => {
  const response = await apiClient.get<Evaluation[]>("/evaluations");
  return response.data;
};

/**
 * Delete an evaluation result
 * @param id MongoDB _id of the evaluation to delete
 */
export const deleteEvaluation = async (id: string): Promise<void> => {
  await apiClient.delete(`/evaluations/${id}`);
};

// ============================================================================
// TUNING API ENDPOINTS
// Part of Phase 4, Module 4: The Automated Tuning Loop
// ============================================================================

/**
 * Create a new tuning loop (async operation)
 * Returns immediately with tuning_loop_id and PENDING status
 * Use getTuningLoop to poll for progress
 * @param data Tuning loop configuration including initial_prompt_id, target_score, max_iterations, and scenarios
 */
export const createTuningLoop = async (
  data: TuningLoopCreate
): Promise<TuningLoopStatusResponse> => {
  const response = await apiClient.post<TuningLoopStatusResponse>(
    "/tuning",
    data
  );
  return response.data;
};

/**
 * Get tuning loop by ID (polling endpoint)
 * @param id MongoDB _id of the tuning loop
 */
export const getTuningLoop = async (id: string): Promise<TuningLoop> => {
  const response = await apiClient.get<TuningLoop>(`/tuning/${id}`);
  return response.data;
};

/**
 * List all tuning loops
 * Returns tuning loops sorted by created_at (newest first)
 */
export const listTuningLoops = async (): Promise<TuningLoop[]> => {
  const response = await apiClient.get<TuningLoop[]>("/tuning");
  return response.data;
};

export default apiClient;
