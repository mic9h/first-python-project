export interface Video {
  id: number;
  title: string;
  description: string;
  posted_at: string;
  duration_sec: number;
  content_type: string;
  hashtags: string[];
  sound_name: string;
  views: number;
  likes: number;
  comments: number;
  shares: number;
  saves: number;
  engagement_rate: number;
  source: string;
  created_at: string;
  updated_at: string;
}

export interface VideoCreate {
  title: string;
  description: string;
  posted_at: string;
  duration_sec: number;
  content_type: string;
  hashtags: string[];
  sound_name: string;
  views: number;
  likes: number;
  comments: number;
  shares: number;
  saves: number;
}

export interface DailyStats {
  id: number;
  date: string;
  followers: number;
  following: number;
  total_likes: number;
  total_views: number;
  profile_views: number;
  new_followers: number;
  created_at: string;
}

export interface DailyStatsCreate {
  date: string;
  followers: number;
  following: number;
  total_likes: number;
  total_views: number;
  profile_views: number;
}

export interface OverviewStats {
  current_followers: number;
  follower_growth: number;
  total_videos: number;
  total_views: number;
  avg_engagement_rate: number;
  best_content_type: string;
  best_posting_hour: number;
}

export interface ContentTypePerformance {
  content_type: string;
  avg_views: number;
  avg_engagement: number;
  count: number;
}

export interface PostingHeatmapCell {
  day: number;
  hour: number;
  avg_views: number;
  count: number;
}

export interface ContentIdea {
  id: number;
  title: string;
  description: string;
  content_type: string;
  estimated_effort: string;
  hashtags: string[];
  status: string;
  scheduled_for: string | null;
  generated_by: string;
  created_at: string;
}

export interface Learning {
  id: number;
  category: string;
  insight: string;
  evidence: Record<string, unknown>;
  confidence: number;
  source: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface SessionNote {
  id: number;
  session_date: string;
  notes: string;
  action_items: Array<{ task: string; status: string; due_date?: string }>;
  metrics_snapshot: Record<string, unknown>;
  created_at: string;
}
