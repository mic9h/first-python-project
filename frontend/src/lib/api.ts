import axios from 'axios';
import type {
  Video,
  VideoCreate,
  DailyStats,
  DailyStatsCreate,
  OverviewStats,
  ContentTypePerformance,
  PostingHeatmapCell,
  ContentIdea,
  Learning,
  SessionNote,
} from '../types';

const api = axios.create({ baseURL: '/api' });

// --- Analytics ---
export const getVideos = (params?: { content_type?: string; sort_by?: string; order?: string }) =>
  api.get<Video[]>('/analytics/videos', { params }).then(r => r.data);

export const createVideo = (data: VideoCreate) =>
  api.post('/analytics/videos', data).then(r => r.data);

export const updateVideo = (id: number, data: Partial<VideoCreate>) =>
  api.put(`/analytics/videos/${id}`, data).then(r => r.data);

export const deleteVideo = (id: number) =>
  api.delete(`/analytics/videos/${id}`).then(r => r.data);

export const importCSV = (file: File) => {
  const form = new FormData();
  form.append('file', file);
  return api.post('/analytics/videos/import-csv', form).then(r => r.data);
};

export const getDailyStats = (days?: number) =>
  api.get<DailyStats[]>('/analytics/daily-stats', { params: { days } }).then(r => r.data);

export const createDailyStats = (data: DailyStatsCreate) =>
  api.post('/analytics/daily-stats', data).then(r => r.data);

export const getOverview = () =>
  api.get<OverviewStats>('/analytics/overview').then(r => r.data);

export const getContentPerformance = () =>
  api.get<ContentTypePerformance[]>('/analytics/content-performance').then(r => r.data);

export const getPostingHeatmap = () =>
  api.get<PostingHeatmapCell[]>('/analytics/posting-heatmap').then(r => r.data);

// --- Content ---
export const generateIdeas = (count?: number) =>
  api.post<ContentIdea[]>('/content/ideas/generate', null, { params: { count } }).then(r => r.data);

export const getIdeas = (status?: string) =>
  api.get<ContentIdea[]>('/content/ideas', { params: { status } }).then(r => r.data);

export const createIdea = (data: Partial<ContentIdea>) =>
  api.post('/content/ideas', data).then(r => r.data);

export const updateIdeaStatus = (id: number, status: string) =>
  api.put(`/content/ideas/${id}/status`, null, { params: { status } }).then(r => r.data);

export const suggestHashtags = (description: string) =>
  api.post<{ hashtags: string[] }>('/content/hashtags/suggest', null, { params: { description } }).then(r => r.data);

// --- Learning ---
export const getInsights = (minConfidence?: number) =>
  api.get<Learning[]>('/learning/insights', { params: { min_confidence: minConfidence } }).then(r => r.data);

export const runAnalysis = () =>
  api.post('/learning/analyze').then(r => r.data);

export const createSessionNote = (data: { notes: string; action_items: Array<{ task: string; status: string }> }) =>
  api.post('/learning/sessions', data).then(r => r.data);

export const getLatestSession = () =>
  api.get<SessionNote | null>('/learning/sessions/latest').then(r => r.data);
