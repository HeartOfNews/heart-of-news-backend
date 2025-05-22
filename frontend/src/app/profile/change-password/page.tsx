'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useForm } from 'react-hook-form';
import { useAuth } from '@/contexts/AuthContext';
import { useProfile } from '@/hooks/useProfile';
import { PasswordChangeRequest } from '@/types/profile';
import { ArrowLeftIcon, LockClosedIcon } from '@heroicons/react/24/outline';

export default function ChangePasswordPage() {
  const router = useRouter();
  const { isAuthenticated, isLoading: authLoading } = useAuth();
  const { updatePassword } = useProfile();
  
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);
  
  const {
    register,
    handleSubmit,
    watch,
    reset,
    formState: { errors },
  } = useForm<PasswordChangeRequest & { confirm_password: string }>();
  
  const watchNewPassword = watch('new_password', '');
  
  // Redirect if not authenticated
  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push('/login?redirect=/profile/change-password');
    }
  }, [authLoading, isAuthenticated, router]);
  
  // Handle form submission
  const onSubmit = async (data: PasswordChangeRequest & { confirm_password: string }) => {
    if (data.new_password !== data.confirm_password) {
      setSubmitError('Passwords do not match');
      return;
    }
    
    setIsSubmitting(true);
    setSubmitError(null);
    
    try {
      // Only send the required fields, not confirm_password
      const { confirm_password, ...passwordData } = data;
      await updatePassword(passwordData);
      setIsSuccess(true);
      reset(); // Clear form
    } catch (error: any) {
      console.error('Error changing password:', error);
      setSubmitError(error.response?.data?.detail || 'Failed to change password');
    } finally {
      setIsSubmitting(false);
    }
  };
  
  if (authLoading) {
    return (
      <div className="flex justify-center items-center min-h-[60vh]">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary"></div>
      </div>
    );
  }
  
  if (!isAuthenticated) {
    return null; // Will redirect in useEffect
  }
  
  return (
    <div className="bg-background">
      <div className="mx-auto max-w-3xl px-4 sm:px-6 lg:px-8 py-12">
        <div className="mb-6">
          <Link href="/profile" className="inline-flex items-center text-primary hover:underline">
            <ArrowLeftIcon className="h-4 w-4 mr-2" />
            Back to Profile
          </Link>
        </div>
        
        <div className="mb-6">
          <h1 className="text-2xl font-bold tracking-tight text-foreground">Change Password</h1>
          <p className="text-muted-foreground">Update your password to keep your account secure</p>
        </div>
        
        <div className="bg-card rounded-lg shadow-sm border border-border overflow-hidden">
          {isSuccess ? (
            <div className="p-6">
              <div className="p-4 rounded-md bg-green-50 dark:bg-green-900/20 text-green-800 dark:text-green-200 mb-4">
                <p>Your password has been successfully updated.</p>
              </div>
              <div className="flex justify-end">
                <Link
                  href="/profile"
                  className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary hover:bg-primary/90"
                >
                  Return to Profile
                </Link>
              </div>
            </div>
          ) : (
            <form onSubmit={handleSubmit(onSubmit)} className="p-6 space-y-6">
              {submitError && (
                <div className="p-4 rounded-md bg-destructive/10 text-destructive">
                  {submitError}
                </div>
              )}
              
              <div className="space-y-6">
                {/* Current Password */}
                <div>
                  <label htmlFor="current_password" className="block text-sm font-medium text-foreground mb-1">
                    Current Password
                  </label>
                  <input
                    type="password"
                    id="current_password"
                    className={`block w-full rounded-md border-0 py-2 px-3 text-foreground shadow-sm ring-1 ring-inset ${
                      errors.current_password ? 'ring-destructive' : 'ring-border'
                    } focus:ring-2 focus:ring-inset focus:ring-primary bg-background sm:text-sm sm:leading-6`}
                    {...register('current_password', {
                      required: 'Current password is required',
                    })}
                  />
                  {errors.current_password && (
                    <p className="mt-1 text-sm text-destructive">{errors.current_password.message}</p>
                  )}
                </div>
                
                {/* New Password */}
                <div>
                  <label htmlFor="new_password" className="block text-sm font-medium text-foreground mb-1">
                    New Password
                  </label>
                  <input
                    type="password"
                    id="new_password"
                    className={`block w-full rounded-md border-0 py-2 px-3 text-foreground shadow-sm ring-1 ring-inset ${
                      errors.new_password ? 'ring-destructive' : 'ring-border'
                    } focus:ring-2 focus:ring-inset focus:ring-primary bg-background sm:text-sm sm:leading-6`}
                    {...register('new_password', {
                      required: 'New password is required',
                      minLength: {
                        value: 8,
                        message: 'Password must be at least 8 characters',
                      },
                      pattern: {
                        value: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/,
                        message: 'Password must include uppercase, lowercase, number and special character',
                      },
                    })}
                  />
                  {errors.new_password && (
                    <p className="mt-1 text-sm text-destructive">{errors.new_password.message}</p>
                  )}
                </div>
                
                {/* Confirm New Password */}
                <div>
                  <label htmlFor="confirm_password" className="block text-sm font-medium text-foreground mb-1">
                    Confirm New Password
                  </label>
                  <input
                    type="password"
                    id="confirm_password"
                    className={`block w-full rounded-md border-0 py-2 px-3 text-foreground shadow-sm ring-1 ring-inset ${
                      errors.confirm_password ? 'ring-destructive' : 'ring-border'
                    } focus:ring-2 focus:ring-inset focus:ring-primary bg-background sm:text-sm sm:leading-6`}
                    {...register('confirm_password', {
                      required: 'Please confirm your password',
                      validate: value => value === watchNewPassword || 'Passwords do not match',
                    })}
                  />
                  {errors.confirm_password && (
                    <p className="mt-1 text-sm text-destructive">{errors.confirm_password.message}</p>
                  )}
                </div>
              </div>
              
              <div className="pt-4 flex justify-end space-x-4">
                <Link
                  href="/profile"
                  className="inline-flex items-center px-4 py-2 border border-border rounded-md bg-background text-foreground hover:bg-muted"
                >
                  Cancel
                </Link>
                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary hover:bg-primary/90 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary disabled:opacity-70 disabled:cursor-not-allowed"
                >
                  {isSubmitting ? (
                    <>
                      <span className="mr-2">Updating...</span>
                      <div className="animate-spin rounded-full h-4 w-4 border-t-2 border-b-2 border-white"></div>
                    </>
                  ) : (
                    <>
                      <LockClosedIcon className="h-5 w-5 mr-2" />
                      Update Password
                    </>
                  )}
                </button>
              </div>
            </form>
          )}
        </div>
        
        <div className="mt-8 bg-card rounded-lg shadow-sm border border-border p-6">
          <h2 className="text-lg font-semibold mb-4">Password Security Tips</h2>
          <ul className="space-y-2 text-muted-foreground">
            <li className="flex items-start">
              <span className="text-primary mr-2">•</span>
              Use a minimum of 8 characters with a mix of uppercase, lowercase, numbers, and special characters
            </li>
            <li className="flex items-start">
              <span className="text-primary mr-2">•</span>
              Avoid using easily guessable information like birthdays or names
            </li>
            <li className="flex items-start">
              <span className="text-primary mr-2">•</span>
              Use a unique password for each website and service
            </li>
            <li className="flex items-start">
              <span className="text-primary mr-2">•</span>
              Consider using a password manager to generate and store strong passwords
            </li>
            <li className="flex items-start">
              <span className="text-primary mr-2">•</span>
              Enable two-factor authentication for an additional layer of security
            </li>
          </ul>
        </div>
      </div>
    </div>
  );
}