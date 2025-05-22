'use client';

import { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import { useForm } from 'react-hook-form';
import { LoginRequest } from '@/types';

export default function LoginPage() {
  const { login } = useAuth();
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginRequest>();
  
  const onSubmit = async (data: LoginRequest) => {
    setIsLoading(true);
    setError(null);
    
    try {
      await login(data);
      router.push('/');
    } catch (error: any) {
      setError(error.response?.data?.detail || 'Login failed. Please check your credentials and try again.');
    } finally {
      setIsLoading(false);
    }
  };
  
  return (
    <div className="bg-background flex min-h-full flex-1 flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <div className="mx-auto h-12 w-12 rounded-full bg-primary flex items-center justify-center">
          <span className="text-primary-foreground font-bold text-lg">H</span>
        </div>
        <h2 className="mt-6 text-center text-2xl font-bold leading-9 tracking-tight text-foreground">
          Sign in to your account
        </h2>
      </div>

      <div className="mt-10 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-card px-6 py-8 shadow sm:rounded-lg sm:px-12">
          {error && (
            <div className="mb-4 p-3 rounded-md bg-destructive/10 text-destructive text-sm">
              {error}
            </div>
          )}
          
          <form className="space-y-6" onSubmit={handleSubmit(onSubmit)}>
            <div>
              <label htmlFor="email" className="block text-sm font-medium leading-6 text-foreground">
                Email address
              </label>
              <div className="mt-2">
                <input
                  id="email"
                  type="email"
                  autoComplete="email"
                  required
                  className={`block w-full rounded-md border-0 py-2 px-3 text-foreground shadow-sm ring-1 ring-inset ${
                    errors.email ? 'ring-destructive' : 'ring-border'
                  } placeholder:text-muted-foreground focus:ring-2 focus:ring-inset focus:ring-primary bg-background sm:text-sm sm:leading-6`}
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
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium leading-6 text-foreground">
                Password
              </label>
              <div className="mt-2">
                <input
                  id="password"
                  type="password"
                  autoComplete="current-password"
                  required
                  className={`block w-full rounded-md border-0 py-2 px-3 text-foreground shadow-sm ring-1 ring-inset ${
                    errors.password ? 'ring-destructive' : 'ring-border'
                  } placeholder:text-muted-foreground focus:ring-2 focus:ring-inset focus:ring-primary bg-background sm:text-sm sm:leading-6`}
                  {...register('password', {
                    required: 'Password is required',
                    minLength: {
                      value: 6,
                      message: 'Password must be at least 6 characters',
                    },
                  })}
                />
                {errors.password && (
                  <p className="mt-1 text-sm text-destructive">{errors.password.message}</p>
                )}
              </div>
            </div>

            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <input
                  id="remember-me"
                  name="remember-me"
                  type="checkbox"
                  className="h-4 w-4 rounded border-border text-primary focus:ring-primary"
                />
                <label htmlFor="remember-me" className="ml-3 block text-sm leading-6 text-foreground">
                  Remember me
                </label>
              </div>

              <div className="text-sm leading-6">
                <Link href="/forgot-password" className="font-semibold text-primary hover:text-primary/80">
                  Forgot password?
                </Link>
              </div>
            </div>

            <div>
              <button
                type="submit"
                disabled={isLoading}
                className="flex w-full justify-center rounded-md bg-primary px-3 py-2 text-sm font-semibold text-primary-foreground shadow-sm hover:bg-primary/90 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isLoading ? 'Signing in...' : 'Sign in'}
              </button>
            </div>
          </form>

          <div className="mt-6">
            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-border" />
              </div>
              <div className="relative flex justify-center text-sm font-medium leading-6">
                <span className="bg-card px-6 text-muted-foreground">Or continue with</span>
              </div>
            </div>

            <div className="mt-6 grid grid-cols-2 gap-4">
              <a
                href="#"
                className="flex w-full items-center justify-center gap-3 rounded-md border border-border bg-background px-3 py-2 text-sm font-semibold text-foreground shadow-sm hover:bg-muted focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary"
              >
                <svg className="h-5 w-5" aria-hidden="true" viewBox="0 0 24 24">
                  <path
                    d="M12.0003 4.75C13.7703 4.75 15.3553 5.36002 16.6053 6.54998L20.0303 3.125C17.9502 1.19 15.2353 0 12.0003 0C7.31028 0 3.25527 2.69 1.28027 6.60998L5.27028 9.70498C6.21525 6.86002 8.87028 4.75 12.0003 4.75Z"
                    fill="#EA4335"
                  />
                  <path
                    d="M23.49 12.275C23.49 11.49 23.415 10.73 23.3 10H12V14.51H18.47C18.18 15.99 17.34 17.25 16.08 18.1L19.945 21.1C22.2 19.01 23.49 15.92 23.49 12.275Z"
                    fill="#4285F4"
                  />
                  <path
                    d="M5.26498 14.2949C5.02498 13.5699 4.88501 12.7999 4.88501 11.9999C4.88501 11.1999 5.01998 10.4299 5.26498 9.7049L1.275 6.60986C0.46 8.22986 0 10.0599 0 11.9999C0 13.9399 0.46 15.7699 1.28 17.3899L5.26498 14.2949Z"
                    fill="#FBBC05"
                  />
                  <path
                    d="M12.0004 24.0001C15.2404 24.0001 17.9654 22.935 19.9454 21.095L16.0804 18.095C15.0054 18.82 13.6204 19.245 12.0004 19.245C8.8704 19.245 6.21537 17.135 5.2654 14.29L1.27539 17.385C3.25539 21.31 7.3104 24.0001 12.0004 24.0001Z"
                    fill="#34A853"
                  />
                </svg>
                <span className="text-sm font-semibold leading-6">Google</span>
              </a>

              <a
                href="#"
                className="flex w-full items-center justify-center gap-3 rounded-md border border-border bg-background px-3 py-2 text-sm font-semibold text-foreground shadow-sm hover:bg-muted focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary"
              >
                <svg className="h-5 w-5 text-[#24292F]" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                  <path
                    fillRule="evenodd"
                    d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385c.6.105.825-.255.825-.57c0-.285-.015-1.23-.015-2.235c-3.015.555-3.795-.735-4.035-1.41c-.135-.345-.72-1.41-1.23-1.695c-.42-.225-1.02-.78-.015-.795c.945-.015 1.62.87 1.845 1.23c1.08 1.815 2.805 1.305 3.495.99c.105-.78.42-1.305.765-1.605c-2.67-.3-5.46-1.335-5.46-5.925c0-1.305.465-2.385 1.23-3.225c-.12-.3-.54-1.53.12-3.18c0 0 1.005-.315 3.3 1.23c.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23c.66 1.65.24 2.88.12 3.18c.765.84 1.23 1.905 1.23 3.225c0 4.605-2.805 5.625-5.475 5.925c.435.375.81 1.095.81 2.22c0 1.605-.015 2.895-.015 3.3c0 .315.225.69.825.57A12.02 12.02 0 0 0 24 12c0-6.63-5.37-12-12-12z"
                    clipRule="evenodd"
                  />
                </svg>
                <span className="text-sm font-semibold leading-6">GitHub</span>
              </a>
            </div>
          </div>
        </div>

        <p className="mt-10 text-center text-sm text-muted-foreground">
          Not a member?{' '}
          <Link href="/register" className="font-semibold leading-6 text-primary hover:text-primary/80">
            Create an account
          </Link>
        </p>
      </div>
    </div>
  );
}