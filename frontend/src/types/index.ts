export type Platform = "twitter" | "reddit";

export type IdeaStatus =
  | "pending"
  | "researching"
  | "generating"
  | "completed"
  | "failed";

export type DraftStatus = "pending" | "approved" | "rejected" | "published";

export interface User {
  id: string;
  email: string;
  username: string;
  is_active: boolean;
  is_superuser: boolean;
  created_at: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export interface Idea {
  id: string;
  title: string;
  description: string | null;
  platform: Platform;
  status: IdeaStatus;
  created_at: string;
}

export interface QualityScore {
  originality: number;
  hook_strength: number;
  engagement_predicted: number;
  spam_probability: number;
  readability_score: number;
  brand_consistency: number;
  human_score: number;
  passed: boolean;
}

export interface Draft {
  id: string;
  idea_id: string;
  content: string;
  platform: Platform;
  status: DraftStatus;
  hook: string | null;
  quality_score: QualityScore | null;
  scheduled_for: string | null;
  created_at: string;
}

export interface TaskResponse {
  task_id: string;
  status: string;
}

export interface Schedule {
  id: string;
  draft_id: string;
  scheduled_for: string;
  status: string;
}

export interface PublishedPost {
  id: string;
  draft_id: string;
  platform: Platform;
  platform_post_id: string;
  url: string;
  published_at: string;
}

export interface AnalyticsSummary {
  total_posts: number;
  total_views: number;
  total_likes: number;
  total_replies: number;
  total_reposts: number;
  avg_engagement_rate: number;
}

export interface PostAnalytics {
  post_id: string;
  content_preview: string;
  platform: Platform;
  views: number;
  likes: number;
  replies: number;
  reposts: number;
  engagement_rate: number;
  published_at: string;
}

export interface PromptInfo {
  agent_name: string;
  version: number;
  updated_at: string;
}

export interface Prompt {
  agent_name: string;
  content: string;
  version: number;
  updated_at: string;
}

export interface PromptVersion {
  version: number;
  created_at: string;
  is_active: boolean;
}

export const AGENT_NAMES = [
  "research",
  "planning",
  "writer",
  "editor",
  "quality",
  "learning",
] as const;

export type AgentName = (typeof AGENT_NAMES)[number];
