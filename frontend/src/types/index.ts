export interface ContentIdea {
  id: string;
  topic: string;
  platform: string;
  status: 'new' | 'researching' | 'drafting' | 'completed';
  createdAt: string;
}

export interface QualityScore {
  engagement: number;
  spam: number;
  readability: number;
  originality: number;
}

export interface Draft {
  id: string;
  ideaId: string;
  content: string;
  platform: string;
  status: 'pending' | 'approved' | 'rejected';
  qualityScore: QualityScore;
  createdAt: string;
}

export interface Analytics {
  totalViews: number;
  totalLikes: number;
  totalReplies: number;
  totalReach: number;
  postsOverTime: { date: string; posts: number; engagement: number }[];
  topPerforming: { id: string; content: string; engagement: number }[];
  platformDistribution: { platform: string; percentage: number }[];
}

export interface PublishedPost {
  id: string;
  draftId: string;
  platform: string;
  externalId: string;
  publishedAt: string;
}

export interface User {
  id: string;
  email: string;
  name: string;
}

export interface SocialAccount {
  id: string;
  platform: string;
  username: string;
  connectedAt: string;
}
