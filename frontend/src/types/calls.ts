// Call Types (matching backend models)
export interface CallResponse {
  id: string;
  restaurant_id: string;
  caller: string;
  started_at: string;
  ended_at: string | null;
  duration_seconds: number | null;
  outcome: string;
  cost: number | null;
  messages: CallMessage[];
}

export interface CallMessage {
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: string;
}

export interface CallListResponse {
  data: CallResponse[];
}

