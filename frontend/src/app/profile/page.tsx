'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Image from 'next/image';
import { useForm } from 'react-hook-form';
import { useAuth } from '@/contexts/AuthContext';
import { useProfile } from '@/hooks/useProfile';
import { ProfileUpdateRequest } from '@/types/profile';
import { UserIcon, PencilIcon, CheckIcon, XMarkIcon } from '@heroicons/react/24/outline';

export default function ProfilePage() {
  const router = useRouter();
  const { user, isAuthenticated, isLoading: authLoading } = useAuth();
  const { 
    profile, 
    isLoading: profileLoading, 
    error: profileError,
    updateProfile,
    refreshProfile,
    uploadProfileImage
  } = useProfile();
  
  const [isEditing, setIsEditing] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  
  const { register, handleSubmit, reset, formState: { errors, isDirty } } = useForm<ProfileUpdateRequest>({
    defaultValues: {
      username: profile?.username || '',
      email: profile?.email || '',
      bio: profile?.bio || '',
    }
  });
  
  // Redirect if not authenticated
  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push('/login?redirect=/profile');
    }
  }, [authLoading, isAuthenticated, router]);
  
  // Reset form when profile changes
  useEffect(() => {
    if (profile) {
      reset({
        username: profile.username,
        email: profile.email,
        bio: profile.bio || '',
      });
    }
  }, [profile, reset]);
  
  // Handle form submission
  const onSubmit = async (data: ProfileUpdateRequest) => {
    try {
      await updateProfile(data);
      setIsEditing(false);
    } catch (error) {
      console.error('Error updating profile:', error);
    }
  };
  
  // Handle image upload
  const handleImageUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    
    // Validate file type
    if (!file.type.startsWith('image/')) {
      setUploadError('Please upload an image file');
      return;
    }
    
    // Validate file size (max 2MB)
    if (file.size > 2 * 1024 * 1024) {
      setUploadError('Image must be less than 2MB');
      return;
    }
    
    setIsUploading(true);
    setUploadError(null);
    
    try {
      await uploadProfileImage(file);
    } catch (error) {
      console.error('Error uploading image:', error);
      setUploadError('Failed to upload image');
    } finally {
      setIsUploading(false);
    }
  };
  
  // Cancel editing
  const handleCancel = () => {
    setIsEditing(false);
    if (profile) {
      reset({
        username: profile.username,
        email: profile.email,
        bio: profile.bio || '',
      });
    }
  };
  
  if (authLoading || profileLoading) {
    return (
      <div className="flex justify-center items-center min-h-[60vh]">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary"></div>
      </div>
    );
  }
  
  if (!isAuthenticated || !user) {
    return null; // Will redirect in useEffect
  }
  
  return (
    <div className="bg-background">
      <div className="mx-auto max-w-3xl px-4 sm:px-6 lg:px-8 py-12">
        <div className="mb-6">
          <h1 className="text-2xl font-bold tracking-tight text-foreground">Your Profile</h1>
          <p className="text-muted-foreground">Manage your personal information and preferences</p>
        </div>
        
        {profileError && (
          <div className="mb-6 p-4 rounded-md bg-destructive/10 text-destructive">
            {profileError}
          </div>
        )}
        
        <div className="bg-card rounded-lg shadow-sm border border-border overflow-hidden">
          {/* Profile header */}
          <div className="p-6 border-b border-border">
            <div className="flex flex-col sm:flex-row items-center gap-6">
              {/* Profile image */}
              <div className="relative">
                <div className="relative h-24 w-24 rounded-full overflow-hidden bg-muted">
                  {profile?.avatar_url ? (
                    <Image
                      src={profile.avatar_url}
                      alt={profile.username}
                      fill
                      className="object-cover"
                    />
                  ) : (
                    <div className="flex items-center justify-center h-full w-full">
                      <UserIcon className="h-12 w-12 text-muted-foreground" />
                    </div>
                  )}
                </div>
                
                {/* Image upload button */}
                <label
                  htmlFor="avatar-upload"
                  className="absolute bottom-0 right-0 p-1.5 rounded-full bg-primary text-primary-foreground shadow-sm cursor-pointer"
                >
                  <PencilIcon className="h-4 w-4" />
                  <input
                    type="file"
                    id="avatar-upload"
                    className="sr-only"
                    accept="image/*"
                    onChange={handleImageUpload}
                    disabled={isUploading}
                  />
                </label>
              </div>
              
              <div className="flex-1 text-center sm:text-left">
                <h2 className="text-xl font-semibold">{profile?.username}</h2>
                <p className="text-muted-foreground">{profile?.email}</p>
                <p className="text-muted-foreground text-sm mt-1">
                  Member since {profile?.created_at ? new Date(profile.created_at).toLocaleDateString() : 'N/A'}
                </p>
                
                {uploadError && (
                  <p className="text-sm text-destructive mt-2">{uploadError}</p>
                )}
                
                {isUploading && (
                  <p className="text-sm text-muted-foreground mt-2">Uploading image...</p>
                )}
              </div>
              
              <div>
                {!isEditing && (
                  <button
                    type="button"
                    onClick={() => setIsEditing(true)}
                    className="inline-flex items-center px-4 py-2 border border-border rounded-md bg-background text-foreground hover:bg-muted"
                  >
                    <PencilIcon className="h-5 w-5 mr-2" />
                    Edit Profile
                  </button>
                )}
              </div>
            </div>
          </div>
          
          {/* Profile form */}
          <form onSubmit={handleSubmit(onSubmit)}>
            <div className="p-6 space-y-6">
              {/* Username */}
              <div>
                <label htmlFor="username" className="block text-sm font-medium text-foreground mb-1">
                  Username
                </label>
                <input
                  type="text"
                  id="username"
                  className={`block w-full rounded-md border-0 py-2 px-3 text-foreground shadow-sm ring-1 ring-inset ${
                    errors.username ? 'ring-destructive' : 'ring-border'
                  } focus:ring-2 focus:ring-inset focus:ring-primary bg-background sm:text-sm sm:leading-6 ${
                    !isEditing ? 'opacity-70 cursor-not-allowed' : ''
                  }`}
                  disabled={!isEditing}
                  {...register('username', {
                    required: 'Username is required',
                    minLength: {
                      value: 3,
                      message: 'Username must be at least 3 characters',
                    },
                  })}
                />
                {errors.username && (
                  <p className="mt-1 text-sm text-destructive">{errors.username.message}</p>
                )}
              </div>
              
              {/* Email */}
              <div>
                <label htmlFor="email" className="block text-sm font-medium text-foreground mb-1">
                  Email
                </label>
                <input
                  type="email"
                  id="email"
                  className={`block w-full rounded-md border-0 py-2 px-3 text-foreground shadow-sm ring-1 ring-inset ${
                    errors.email ? 'ring-destructive' : 'ring-border'
                  } focus:ring-2 focus:ring-inset focus:ring-primary bg-background sm:text-sm sm:leading-6 ${
                    !isEditing ? 'opacity-70 cursor-not-allowed' : ''
                  }`}
                  disabled={!isEditing}
                  {...register('email', {
                    required: 'Email is required',
                    pattern: {
                      value: /\S+@\S+\.\S+/,
                      message: 'Invalid email address',
                    },
                  })}
                />
                {errors.email && (
                  <p className="mt-1 text-sm text-destructive">{errors.email.message}</p>
                )}
              </div>
              
              {/* Bio */}
              <div>
                <label htmlFor="bio" className="block text-sm font-medium text-foreground mb-1">
                  Bio
                </label>
                <textarea
                  id="bio"
                  rows={4}
                  className={`block w-full rounded-md border-0 py-2 px-3 text-foreground shadow-sm ring-1 ring-inset ${
                    errors.bio ? 'ring-destructive' : 'ring-border'
                  } focus:ring-2 focus:ring-inset focus:ring-primary bg-background sm:text-sm sm:leading-6 ${
                    !isEditing ? 'opacity-70 cursor-not-allowed' : ''
                  }`}
                  placeholder={isEditing ? "Tell us about yourself..." : "No bio provided"}
                  disabled={!isEditing}
                  {...register('bio')}
                />
              </div>
            </div>
            
            {/* Form actions */}
            {isEditing && (
              <div className="px-6 py-4 border-t border-border flex justify-end space-x-4">
                <button
                  type="button"
                  onClick={handleCancel}
                  className="inline-flex items-center px-4 py-2 border border-border rounded-md bg-background text-foreground hover:bg-muted"
                >
                  <XMarkIcon className="h-5 w-5 mr-2" />
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={!isDirty}
                  className={`inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary hover:bg-primary/90 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary ${
                    !isDirty ? 'opacity-70 cursor-not-allowed' : ''
                  }`}
                >
                  <CheckIcon className="h-5 w-5 mr-2" />
                  Save Changes
                </button>
              </div>
            )}
          </form>
        </div>
        
        {/* Account settings */}
        <div className="mt-8">
          <h2 className="text-xl font-semibold mb-4">Account Settings</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-card rounded-lg shadow-sm border border-border p-6">
              <h3 className="text-lg font-medium mb-4">Security</h3>
              <div className="space-y-4">
                <button
                  type="button"
                  onClick={() => router.push('/profile/change-password')}
                  className="inline-flex items-center px-4 py-2 border border-border rounded-md bg-background text-foreground hover:bg-muted w-full justify-center sm:w-auto"
                >
                  Change Password
                </button>
                
                <button
                  type="button"
                  onClick={() => router.push('/profile/two-factor')}
                  className="inline-flex items-center px-4 py-2 border border-border rounded-md bg-background text-foreground hover:bg-muted w-full justify-center sm:w-auto"
                >
                  Two-Factor Authentication
                </button>
              </div>
            </div>
            
            <div className="bg-card rounded-lg shadow-sm border border-border p-6">
              <h3 className="text-lg font-medium mb-4">Preferences</h3>
              <div className="space-y-4">
                <button
                  type="button"
                  onClick={() => router.push('/profile/preferences')}
                  className="inline-flex items-center px-4 py-2 border border-border rounded-md bg-background text-foreground hover:bg-muted w-full justify-center sm:w-auto"
                >
                  Notification Settings
                </button>
                
                <button
                  type="button"
                  onClick={() => router.push('/profile/favorites')}
                  className="inline-flex items-center px-4 py-2 border border-border rounded-md bg-background text-foreground hover:bg-muted w-full justify-center sm:w-auto"
                >
                  Favorite Sources
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}