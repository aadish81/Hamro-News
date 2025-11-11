export interface NewsCart {
  id: string;
  title: string;
  cover_image: string;
  source: string[];
  category: string;
  time_of_release: string;
}

export interface NewsDetail {
  id?: number;
  description: string;
  cart_id: string;
}

export interface NewsDetailResponse {
  id: number;
  description: string;
}

export type Language = 'english' | 'nepali';

export type SortOption = 'latest' | 'oldest';