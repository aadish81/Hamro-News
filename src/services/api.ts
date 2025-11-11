import axios from 'axios';
import type { NewsCart, NewsDetailResponse } from '../types/news';

const API_BASE_URL = 'https://hamro-news.onrender.com';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
});

export const newsAPI = {
  // Get news carts in English
  getEnglishNews: async (): Promise<NewsCart[]> => {
    const response = await api.get<NewsCart[]>('/news-carts/english/');
    return response.data;
  },

  // Get news carts in Nepali
  getNepaliNews: async (): Promise<NewsCart[]> => {
    const response = await api.get<NewsCart[]>('/news-carts/nepali/');
    return response.data;
  },

  // Get English detail specifically
  getEnglishDetail: async (detailId: string): Promise<NewsDetailResponse> => {
    const response = await api.get<NewsDetailResponse>(`/detail/english/${detailId}`);
    return response.data;
  },

  // Get Nepali detail specifically
  getNepaliDetail: async (detailId: string): Promise<NewsDetailResponse> => {
    const response = await api.get<NewsDetailResponse>(`/detail/nepali/${detailId}`);
    return response.data;
  }
};

export default api;