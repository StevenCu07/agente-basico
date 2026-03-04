import type { ChatResponse, GlobalMetrics, UserMetrics } from "../types";

const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const response = await fetch(`${BASE_URL}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers ?? {}),
    },
    ...options,
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || "Error en la solicitud");
  }
  return (await response.json()) as T;
}

export function sendChat(payload: { user_token: string; message: string; tool?: string; context?: string }): Promise<ChatResponse> {
  return request<ChatResponse>("/api/chat", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function createDocument(payload: { user_token: string; title: string; content: string }): Promise<{ document_id: number; message: string }> {
  return request<{ document_id: number; message: string }>("/api/documents", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function fetchUserMetrics(userToken: string): Promise<UserMetrics> {
  return request<UserMetrics>(`/api/metrics/user/${encodeURIComponent(userToken)}`);
}

export function fetchGlobalMetrics(): Promise<GlobalMetrics> {
  return request<GlobalMetrics>("/api/metrics/global");
}

export function estimateCost(payload: {
  daily_interactions: number;
  avg_tokens_in: number;
  avg_tokens_out: number;
  days: number;
}): Promise<{
  monthly_total_tokens: number;
  monthly_cost: { total_cost: number; currency: string };
}> {
  return request("/api/cost/estimate", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

