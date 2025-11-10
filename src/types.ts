export interface NewsCartRead {
  id: string;
  title: string;
  cover_image: string;  // URL
  source?: string[];
  category: string;
  time_of_release: string; // ISO datetime string
}
