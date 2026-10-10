export interface User {
  id: string;
  email: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface Conversation {
  id: string;
  user_id: string;
  title: string;
  created_at: string;
  updated_at: string;
}

export interface ConversationList {
  items: Conversation[];
  total: number;
  limit: number;
  offset: number;
}

export interface Message {
  id: string;
  conversation_id: string;
  role: "user" | "assistant" | "system";
  content: string;
  structured_output?: Record<string, any> | null;
  created_at: string;
}

export interface MessageList {
  items: Message[];
  total: number;
  limit: number;
  offset: number;
}

export interface PromptTemplate {
  id: string;
  user_id: string;
  name: string;
  description?: string | null;
  template_content: string;
  version: number;
  created_at: string;
  updated_at: string;
}

export interface PromptTemplateList {
  items: PromptTemplate[];
  total: number;
  limit: number;
  offset: number;
}

export interface AuthToken {
  access_token: string;
  token_type: string;
}

export interface SSEStartPayload {
  user_message_id: string;
  assistant_message_id: string;
  conversation_id: string;
}

export interface SSETokenPayload {
  content: string;
}

export interface SSEMetadataPayload {
  provider: string;
  model: string;
  usage?: {
    prompt_tokens: number;
    completion_tokens: number;
    total_tokens: number;
  } | null;
  structured_output?: Record<string, any> | null;
}

export interface SSEDonePayload {
  status: string;
  assistant_message_id: string;
}

export interface SSEErrorPayload {
  error: string;
  code: string;
}
