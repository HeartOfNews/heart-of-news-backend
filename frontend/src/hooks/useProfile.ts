'use client';

import { useState, useEffect, useCallback } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { 
  fetchUserProfile, 
  updateUserProfile, 
  changePassword, 
  updateUserPreferences,
  uploadAvatar
} from '@/lib/api-profile';
import { UserProfile, ProfileUpdateRequest, PasswordChangeRequest } from '@/types/profile';

interface UseProfileReturn {
  profile: UserProfile | null;
  isLoading: boolean;
  error: string | null;
  updateProfile: (data: ProfileUpdateRequest) => Promise<void>;
  updatePassword: (data: PasswordChangeRequest) => Promise<void>;
  updatePreferences: (preferences: Partial<UserProfile['preferences']>) => Promise<void>;
  uploadProfileImage: (file: File) => Promise<void>;
  refreshProfile: () => Promise<void>;
}

export function useProfile(): UseProfileReturn {
  const { isAuthenticated } = useAuth();
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Fetch profile on mount if authenticated
  const refreshProfile = useCallback(async () => {
    if (!isAuthenticated) {
      setProfile(null);
      setIsLoading(false);
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const data = await fetchUserProfile();
      setProfile(data);
    } catch (err: any) {
      console.error('Error fetching profile:', err);
      setError(err.response?.data?.detail || 'Failed to load profile');
    } finally {
      setIsLoading(false);
    }
  }, [isAuthenticated]);

  useEffect(() => {
    refreshProfile();
  }, [refreshProfile]);

  // Update profile information
  const updateProfile = async (data: ProfileUpdateRequest): Promise<void> => {
    setIsLoading(true);
    setError(null);

    try {
      const updatedProfile = await updateUserProfile(data);
      setProfile(updatedProfile);
    } catch (err: any) {
      console.error('Error updating profile:', err);
      setError(err.response?.data?.detail || 'Failed to update profile');
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  // Change password
  const updatePassword = async (data: PasswordChangeRequest): Promise<void> => {
    setIsLoading(true);
    setError(null);

    try {
      await changePassword(data);
    } catch (err: any) {
      console.error('Error changing password:', err);
      setError(err.response?.data?.detail || 'Failed to change password');
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  // Update preferences
  const updatePreferences = async (preferences: Partial<UserProfile['preferences']>): Promise<void> => {
    setIsLoading(true);
    setError(null);

    try {
      const updatedProfile = await updateUserPreferences(preferences);
      setProfile(updatedProfile);
    } catch (err: any) {
      console.error('Error updating preferences:', err);
      setError(err.response?.data?.detail || 'Failed to update preferences');
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  // Upload profile image
  const uploadProfileImage = async (file: File): Promise<void> => {
    setIsLoading(true);
    setError(null);

    try {
      const result = await uploadAvatar(file);
      setProfile(prev => prev ? { ...prev, avatar_url: result.avatar_url } : null);
    } catch (err: any) {
      console.error('Error uploading profile image:', err);
      setError(err.response?.data?.detail || 'Failed to upload profile image');
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  return {
    profile,
    isLoading,
    error,
    updateProfile,
    updatePassword,
    updatePreferences,
    uploadProfileImage,
    refreshProfile,
  };
}