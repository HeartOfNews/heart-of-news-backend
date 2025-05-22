// Article types
export interface Article {
  id: string;
  title: string;
  content: string;
  summary: string;
  url: string;
  published_at: string;
  source_id: string;
  source: Source;
  categories: string[];
  image_url?: string;
  bias_score?: BiasScore;
}

export interface ArticleListResponse {
  items: Article[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

// Source types
export interface Source {
  id: string;
  name: string;
  url: string;
  rss_feed?: string;
  is_active: boolean;
  reliability_score: number;
  bias_score: number;
}

export interface SourceListResponse {
  items: Source[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

// Bias score types
export interface BiasScore {
  political_bias: number; // -1 to 1 scale (left to right)
  emotional_tone: number; // 0 to 1 scale (neutral to emotional)
  propaganda_techniques: PropagandaTechnique[];
  overall_score: number; // 0 to 1 scale (neutral to biased)
}

export interface PropagandaTechnique {
  name: string;
  score: number;
  examples: string[];
}

// User types
export interface User {
  id: string;
  email: string;
  username: string;
  role: 'user' | 'admin';
  created_at: string;
}

// Auth types
export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  username: string;
  password: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

// Filter and query types
export interface ArticleFilters {
  source_id?: string;
  category?: string;
  date_from?: string;
  date_to?: string;
  query?: string;
  page?: number;
  size?: number;
}

// API response types
export interface ApiError {
  detail: string | { [key: string]: string[] };
  status_code: number;
}

// Theme types
export type ThemeMode = 'light' | 'dark' | 'system';