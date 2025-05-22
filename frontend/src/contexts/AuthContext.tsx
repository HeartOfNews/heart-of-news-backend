'use client';

import React, { createContext, useContext, useEffect, useState } from 'react';
import api, { endpoints } from '@/lib/api';
import { User, LoginRequest, RegisterRequest, AuthResponse } from '@/types';

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (data: LoginRequest) => Promise<void>;
  register: (data: RegisterRequest) => Promise<void>;
  logout: () => void;
  error: string | null;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const checkAuth = async () => {
      const token = localStorage.getItem('authToken');
      if (!token) {
        setIsLoading(false);
        return;
      }

      try {
        const response = await api.get(endpoints.auth.me);
        setUser(response.data);
      } catch (error) {
        console.error('Auth check failed:', error);
        localStorage.removeItem('authToken');
      } finally {
        setIsLoading(false);
      }
    };

    checkAuth();
  }, []);

  const login = async (data: LoginRequest): Promise<void> => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await api.post<AuthResponse>(endpoints.auth.login, data);
      localStorage.setItem('authToken', response.data.access_token);
      setUser(response.data.user);
    } catch (error: any) {
      console.error('Login failed:', error);
      setError(error.response?.data?.detail || 'Login failed. Please try again.');
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const register = async (data: RegisterRequest): Promise<void> => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await api.post<AuthResponse>(endpoints.auth.register, data);
      localStorage.setItem('authToken', response.data.access_token);
      setUser(response.data.user);
    } catch (error: any) {
      console.error('Registration failed:', error);
      setError(error.response?.data?.detail || 'Registration failed. Please try again.');
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const logout = (): void => {
    localStorage.removeItem('authToken');
    setUser(null);
  };

  const value = {
    user,
    isLoading,
    isAuthenticated: !!user,
    login,
    register,
    logout,
    error,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export default AuthContext;