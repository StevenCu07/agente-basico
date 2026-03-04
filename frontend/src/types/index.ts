export type ToolName = "resumir" | "quiz" | "flashcards" | "plan" | "buscar" | "cost";

export interface TokenUsage {
  prompt_tokens: number;
  completion_tokens: number;
  total_tokens: number;
  estimated_cost: {
    input_cost: number;
    output_cost: number;
    total_cost: number;
    currency: string;
  };
}

export interface ChatResponse {
  tool_used: ToolName;
  response: string;
  token_usage: TokenUsage;
}

export interface UserMetrics {
  user_token: string;
  month: string;
  total_tokens: number;
  total_cost: number;
  interactions: number;
}

export interface GlobalMetrics {
  month: string;
  total_tokens: number;
  total_cost: number;
  interactions: number;
  active_users: number;
}

