export type ChatRole = "user" | "assistant";

export interface ToolCallInfo {
  name: string;
  input: Record<string, unknown>;
  result: string;
  is_error: boolean;
}

export interface ChatMessage {
  id: string;
  role: ChatRole;
  content: string;
  toolCalls?: ToolCallInfo[];
}

export interface Conversation {
  id: string;
  /** null hasta que se envía el primer mensaje (aún no existe conversation_id del backend). */
  conversationId: string | null;
  title: string;
  messages: ChatMessage[];
}

export interface ChatRequestBody {
  message: string;
  conversation_id?: string | null;
}

export interface ChatResponseBody {
  reply: string;
  conversation_id: string;
  tool_calls: ToolCallInfo[];
}

export interface HealthResponseBody {
  status: string;
  llm_backend: string;
}

export interface ApiErrorBody {
  detail?: string;
}
