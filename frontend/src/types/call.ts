/**
 * TypeScript interfaces matching backend Pydantic models
 * These types ensure type safety when communicating with the FastAPI backend
 */

export interface Country {
  code: string;
  name: string;
  flag: string;
  iso: string;
}

export interface CallRequest {
  name: string;
  phone_number: string;
  country_code: string;
  amount: number;
  transfer_to?: string;
}

export interface CallResponse {
  success: boolean;
  message: string;
  dispatch_id: string;
  room_name: string;
  call_id: string;
}

export interface CallRecord {
  call_id: string;
  room_name: string;
  dispatch_id: string;
  name: string;
  phone_number: string;
  country_code: string;
  amount: number;
  status: "in_progress" | "completed" | "failed";
  created_at: string;
  completed_at?: string;
  transcript_file?: string;
}

export interface CallsResponse {
  calls: CallRecord[];
  total: number;
}

export interface TranscriptMessage {
  role: "agent" | "user";
  message: string;
  timestamp: string;
}

export interface TranscriptResponse {
  call_id: string;
  room_name: string;
  name: string;
  phone_number: string;
  amount: number;
  status: string;
  created_at: string;
  completed_at?: string;
  transcript: TranscriptMessage[];
  // LLM-generated risk scores (1-100 scale, higher = lower risk)
  loan_recovery_score?: number;
  willingness_to_pay_score?: number;
  escalation_risk_score?: number;
  customer_sentiment_score?: number;
  promise_to_pay_reliability_index?: number;
}

export interface CheckStatusResponse {
  message: string;
  updated_count: number;
}
