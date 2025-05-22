import { User } from '.';

export interface UserProfile extends User {
  bio?: string;
  avatar_url?: string;
  preferences?: UserPreferences;
  stats?: UserStats;
}

export interface UserPreferences {
  email_notifications: boolean;
  theme: 'light' | 'dark' | 'system';
  default_source_filter?: string[];
  default_category_filter?: string[];
}

export interface UserStats {
  articles_read: number;
  comments_posted: number;
  joined_date: string;
  last_login: string;
}

export interface ProfileUpdateRequest {
  username?: string;
  bio?: string;
  email?: string;
  avatar_url?: string;
  preferences?: Partial<UserPreferences>;
}

export interface PasswordChangeRequest {
  current_password: string;
  new_password: string;
}

export interface PasswordChangeResponse {
  message: string;
}