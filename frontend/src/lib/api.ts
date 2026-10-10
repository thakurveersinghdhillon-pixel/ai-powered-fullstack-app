import {
  AuthToken,
  User,
  Conversation,
  ConversationList,
  Message,
  MessageList,
  PromptTemplate,
  PromptTemplateList,
} from "./types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

class APIError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.name = "APIError";
    this.status = status;
  }
}

async function fetchAPI<T>(
  endpoint: string,
  options: RequestInit = {},
  token?: string | null
): Promise<T> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string>),
  };

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
    credentials: "include", // Transmits HttpOnly refresh_token cookie
  });

  if (response.status === 204) {
    return null as T;
  }

  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    const errorMsg = data.detail || `HTTP Error ${response.status}`;
    throw new APIError(errorMsg, response.status);
  }

  return data as T;
}

export const api = {
  // --- Auth Endpoints ---
  async register(email: string, password: string): Promise<User> {
    return fetchAPI<User>("/auth/register", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    });
  },

  async login(email: string, password: string): Promise<AuthToken> {
    return fetchAPI<AuthToken>("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    });
  },

  async refreshToken(): Promise<AuthToken> {
    return fetchAPI<AuthToken>("/auth/refresh", {
      method: "POST",
    });
  },

  async logout(): Promise<{ message: string }> {
    return fetchAPI<{ message: string }>("/auth/logout", {
      method: "POST",
    });
  },

  async getMe(token: string): Promise<User> {
    return fetchAPI<User>("/auth/me", { method: "GET" }, token);
  },

  // --- Conversations ---
  async getConversations(token: string, limit = 20, offset = 0): Promise<ConversationList> {
    return fetchAPI<ConversationList>(`/conversations?limit=${limit}&offset=${offset}`, { method: "GET" }, token);
  },

  async createConversation(token: string, title: string): Promise<Conversation> {
    return fetchAPI<Conversation>("/conversations", {
      method: "POST",
      body: JSON.stringify({ title }),
    }, token);
  },

  async updateConversation(token: string, id: string, title: string): Promise<Conversation> {
    return fetchAPI<Conversation>(`/conversations/${id}`, {
      method: "PATCH",
      body: JSON.stringify({ title }),
    }, token);
  },

  async deleteConversation(token: string, id: string): Promise<void> {
    return fetchAPI<void>(`/conversations/${id}`, { method: "DELETE" }, token);
  },

  // --- Messages ---
  async getMessages(token: string, conversationId: string, limit = 50, offset = 0): Promise<MessageList> {
    return fetchAPI<MessageList>(`/conversations/${conversationId}/messages?limit=${limit}&offset=${offset}`, { method: "GET" }, token);
  },

  async createMessage(token: string, conversationId: string, content: string): Promise<Message> {
    return fetchAPI<Message>(`/conversations/${conversationId}/messages`, {
      method: "POST",
      body: JSON.stringify({ role: "user", content }),
    }, token);
  },

  // --- Prompt Templates ---
  async getTemplates(token: string, limit = 20, offset = 0): Promise<PromptTemplateList> {
    return fetchAPI<PromptTemplateList>(`/templates?limit=${limit}&offset=${offset}`, { method: "GET" }, token);
  },

  async createTemplate(token: string, data: { name: string; description?: string; template_content: string }): Promise<PromptTemplate> {
    return fetchAPI<PromptTemplate>("/templates", {
      method: "POST",
      body: JSON.stringify(data),
    }, token);
  },

  async updateTemplate(token: string, id: string, data: Partial<{ name: string; description?: string; template_content: string; version: number }>): Promise<PromptTemplate> {
    return fetchAPI<PromptTemplate>(`/templates/${id}`, {
      method: "PATCH",
      body: JSON.stringify(data),
    }, token);
  },

  async deleteTemplate(token: string, id: string): Promise<void> {
    return fetchAPI<void>(`/templates/${id}`, { method: "DELETE" }, token);
  },
};
