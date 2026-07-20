import axios from 'axios';
import { ContentIdea, Draft, Analytics } from '../types';

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || '/api',
});

api.interceptors.request.use((config) => {
  const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const getIdeas = async (): Promise<ContentIdea[]> => {
  const response = await api.get('/ideas');
  return response.data;
};

export const createIdea = async (idea: Partial<ContentIdea>): Promise<ContentIdea> => {
  const response = await api.post('/ideas', idea);
  return response.data;
};

export const generateDrafts = async (ideaId: string): Promise<Draft[]> => {
  const response = await api.post(`/ideas/${ideaId}/generate`);
  return response.data;
};

export const approveDraft = async (draftId: string): Promise<Draft> => {
  const response = await api.post(`/drafts/${draftId}/approve`);
  return response.data;
};

export const rejectDraft = async (draftId: string): Promise<Draft> => {
  const response = await api.post(`/drafts/${draftId}/reject`);
  return response.data;
};

export const getAnalytics = async (): Promise<Analytics> => {
  const response = await api.get('/analytics');
  return response.data;
};

export default api;
