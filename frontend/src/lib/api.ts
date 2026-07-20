import axios from "axios";
import type {
  AnalyticsSummary,
  Draft,
  DraftStatus,
  Idea,
  IdeaStatus,
  Platform,
  PostAnalytics,
  Prompt,
  PromptInfo,
  PromptVersion,
  PublishedPost,
  Schedule,
  TaskResponse,
  TokenResponse,
  User,
} from "@/types";

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1",
});

api.interceptors.request.use((config) => {
  const token =
    typeof window !== "undefined" ? localStorage.getItem("token") : null;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (
      error.response?.status === 401 &&
      typeof window !== "undefined" &&
      window.location.pathname !== "/login"
    ) {
      localStorage.removeItem("token");
      window.location.href = "/login";
    }
    return Promise.reject(error);
  }
);

// ---------- Auth ----------

export const register = async (data: {
  email: string;
  username: string;
  password: string;
}): Promise<User> => {
  const response = await api.post<User>("/auth/register", data);
  return response.data;
};

export const login = async (data: {
  username: string;
  password: string;
}): Promise<TokenResponse> => {
  const body = new URLSearchParams();
  body.set("username", data.username);
  body.set("password", data.password);
  const response = await api.post<TokenResponse>("/auth/login", body, {
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
  });
  return response.data;
};

export const getMe = async (): Promise<User> => {
  const response = await api.get<User>("/auth/me");
  return response.data;
};

// ---------- Content: ideas ----------

export const createIdea = async (data: {
  title: string;
  description?: string;
  platform: Platform;
}): Promise<Idea> => {
  const response = await api.post<Idea>("/content/ideas", data);
  return response.data;
};

export const getIdeas = async (params?: {
  status?: IdeaStatus;
  limit?: number;
  offset?: number;
}): Promise<Idea[]> => {
  const response = await api.get<Idea[]>("/content/ideas", { params });
  return response.data;
};

export const getIdea = async (id: string): Promise<Idea> => {
  const response = await api.get<Idea>(`/content/ideas/${id}`);
  return response.data;
};

export const triggerResearch = async (id: string): Promise<TaskResponse> => {
  const response = await api.post<TaskResponse>(`/content/ideas/${id}/research`);
  return response.data;
};

export const triggerGenerate = async (
  id: string,
  numVariations?: number
): Promise<TaskResponse> => {
  const response = await api.post<TaskResponse>(
    `/content/ideas/${id}/generate`,
    numVariations !== undefined ? { num_variations: numVariations } : {}
  );
  return response.data;
};

// ---------- Content: drafts ----------

export const getDrafts = async (params?: {
  status?: DraftStatus;
}): Promise<Draft[]> => {
  const response = await api.get<Draft[]>("/content/drafts", { params });
  return response.data;
};

export const getDraft = async (id: string): Promise<Draft> => {
  const response = await api.get<Draft>(`/content/drafts/${id}`);
  return response.data;
};

export const approveDraft = async (
  id: string,
  scheduledFor?: string
): Promise<Draft> => {
  const response = await api.post<Draft>(
    `/content/drafts/${id}/approve`,
    scheduledFor ? { scheduled_for: scheduledFor } : {}
  );
  return response.data;
};

export const rejectDraft = async (
  id: string,
  reason: string
): Promise<Draft> => {
  const response = await api.post<Draft>(`/content/drafts/${id}/reject`, {
    reason,
  });
  return response.data;
};

// ---------- Publishing ----------

export const publishDraft = async (draftId: string): Promise<TaskResponse> => {
  const response = await api.post<TaskResponse>("/publishing/publish", {
    draft_id: draftId,
  });
  return response.data;
};

export const scheduleDraft = async (
  draftId: string,
  scheduledFor: string
): Promise<Schedule> => {
  const response = await api.post<Schedule>("/publishing/schedule", {
    draft_id: draftId,
    scheduled_for: scheduledFor,
  });
  return response.data;
};

export const deleteSchedule = async (id: string): Promise<void> => {
  await api.delete(`/publishing/schedule/${id}`);
};

export const getScheduled = async (): Promise<Schedule[]> => {
  const response = await api.get<Schedule[]>("/publishing/scheduled");
  return response.data;
};

export const getPublished = async (): Promise<PublishedPost[]> => {
  const response = await api.get<PublishedPost[]>("/publishing/published");
  return response.data;
};

// ---------- Analytics ----------

export const getAnalyticsSummary = async (): Promise<AnalyticsSummary> => {
  const response = await api.get<AnalyticsSummary>("/analytics/summary");
  return response.data;
};

export const getAnalyticsPosts = async (): Promise<PostAnalytics[]> => {
  const response = await api.get<PostAnalytics[]>("/analytics/posts");
  return response.data;
};

// ---------- Prompts ----------

export const getPrompts = async (): Promise<PromptInfo[]> => {
  const response = await api.get<PromptInfo[]>("/prompts");
  return response.data;
};

export const getPrompt = async (agentName: string): Promise<Prompt> => {
  const response = await api.get<Prompt>(`/prompts/${agentName}`);
  return response.data;
};

export const updatePrompt = async (
  agentName: string,
  content: string
): Promise<Prompt> => {
  const response = await api.put<Prompt>(`/prompts/${agentName}`, { content });
  return response.data;
};

export const getPromptVersions = async (
  agentName: string
): Promise<PromptVersion[]> => {
  const response = await api.get<PromptVersion[]>(
    `/prompts/${agentName}/versions`
  );
  return response.data;
};

export const rollbackPrompt = async (
  agentName: string,
  version: number
): Promise<Prompt> => {
  const response = await api.post<Prompt>(
    `/prompts/${agentName}/rollback/${version}`
  );
  return response.data;
};

export default api;
