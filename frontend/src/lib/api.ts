const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
const API_PREFIX = import.meta.env.VITE_API_PREFIX || "/api/v1";

const baseUrl = `${API_BASE_URL}${API_PREFIX}`.replace(/\/$/, "");

export interface OrchestratorResponse {
  conversation_id?: string | null;
  stage: string;
  message_to_user: string;
  invoke_worker: Record<string, unknown>;
  state_updates: Record<string, unknown>;
  next_action: string;
  explainability?: Record<string, unknown> | null;
  audit_entry?: Record<string, unknown> | null;
  fallback_needed?: boolean;
  model_version?: string | null;
}

export async function postChatMessage(
  userMessage: string,
  options?: { conversationId?: string | null; language?: string }
): Promise<OrchestratorResponse> {
  const payload: Record<string, unknown> = {
    user_message: userMessage,
    state: {},
  };

  if (options?.conversationId) {
    payload.state = {
      conversation_id: options.conversationId,
      language: options.language || "en",
    };
  }

  const res = await fetch(`${baseUrl}/chat/orchestrate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    throw new Error(`Chat request failed with status ${res.status}`);
  }

  return (await res.json()) as OrchestratorResponse;
}

export async function getConversationState(conversationId: string): Promise<OrchestratorResponse> {
  const res = await fetch(`${baseUrl}/chat/state/${encodeURIComponent(conversationId)}`);
  if (!res.ok) {
    throw new Error(`Failed to fetch conversation state: ${res.status}`);
  }
  return (await res.json()) as OrchestratorResponse;
}

export async function uploadSalarySlip(
  conversationId: string,
  file: File
): Promise<OrchestratorResponse> {
  const formData = new FormData();
  formData.append("conversation_id", conversationId);
  formData.append("file", file);

  const res = await fetch(`${baseUrl}/upload/salary-slip`, {
    method: "POST",
    body: formData,
  });

  if (!res.ok) {
    throw new Error(`Salary slip upload failed with status ${res.status}`);
  }

  return (await res.json()) as OrchestratorResponse;
}

export async function postVoiceMessage(
  file: File,
  options?: { conversationId?: string | null }
): Promise<OrchestratorResponse> {
  const formData = new FormData();
  formData.append("file", file);
  if (options?.conversationId) {
    formData.append("conversation_id", options.conversationId);
  }

  const res = await fetch(`${baseUrl}/chat/voice`, {
    method: "POST",
    body: formData,
  });

  if (!res.ok) {
    throw new Error(`Voice chat request failed with status ${res.status}`);
  }

  return (await res.json()) as OrchestratorResponse;
}

export interface SanctionLetterResponse {
  sanction_number: string;
  amount: number;
  tenure_months: number;
  rate_percent: number;
  emi: number;
  pdf_url: string;
  valid_until: string;
}

export async function generateSanctionLetter(
  conversationId: string
): Promise<SanctionLetterResponse> {
  const url = new URL(`${baseUrl}/sanction/generate`);
  url.searchParams.set("conversation_id", conversationId);

  const res = await fetch(url.toString(), { method: "POST" });
  if (!res.ok) {
    throw new Error(`Failed to generate sanction letter: ${res.status}`);
  }

  return (await res.json()) as SanctionLetterResponse;
}

export async function acceptSanction(conversationId: string): Promise<{
  status: string;
  transaction_id: string;
  gross_amount: number;
  processing_fee: number;
  net_disbursed: number;
  disbursed_at: string;
  message: string;
}> {
  const url = new URL(`${baseUrl}/sanction/accept`);
  url.searchParams.set("conversation_id", conversationId);

  const res = await fetch(url.toString(), { method: "POST" });
  if (!res.ok) {
    throw new Error(`Failed to accept sanction: ${res.status}`);
  }

  return (await res.json()) as {
    status: string;
    transaction_id: string;
    gross_amount: number;
    processing_fee: number;
    net_disbursed: number;
    disbursed_at: string;
    message: string;
  };
}

export async function checkBackendHealth(): Promise<boolean> {
  try {
    const res = await fetch(`${API_BASE_URL}/health`);
    return res.ok;
  } catch {
    return false;
  }
}
