'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import Link from 'next/link';
import {
  HomeIcon,
  NewspaperIcon,
  DocumentTextIcon,
  UsersIcon,
  ChartBarIcon,
  Cog6ToothIcon,
} from '@heroicons/react/24/outline';

interface AdminLayoutProps {
  children: React.ReactNode;
}

export default function AdminLayout({ children }: AdminLayoutProps) {
  const { user, isLoading, isAuthenticated } = useAuth();
  const router = useRouter();

  // Check if user is authenticated and has admin role
  useEffect(() => {
    if (!isLoading && (!isAuthenticated || user?.role !== 'admin')) {
      router.push('/login?redirect=/admin');
    }
  }, [isLoading, isAuthenticated, user, router]);

  if (isLoading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary"></div>
      </div>
    );
  }

  if (!isAuthenticated || user?.role !== 'admin') {
    return null;
  }

  return (
    <div className="flex h-full">
      {/* Sidebar */}
      <div className="w-64 bg-card border-r border-border hidden md:block">
        <div className="h-16 flex items-center px-6 border-b border-border">
          <h2 className="text-lg font-semibold">Admin Dashboard</h2>
        </div>
        <nav className="mt-6">
          <ul className="space-y-2 px-4">
            <li>
              <Link
                href="/admin"
                className="flex items-center p-2 rounded-md hover:bg-muted text-foreground"
              >
                <HomeIcon className="h-5 w-5 mr-3 text-muted-foreground" />
                Dashboard
              </Link>
            </li>
            <li>
              <Link
                href="/admin/articles"
                className="flex items-center p-2 rounded-md hover:bg-muted text-foreground"
              >
                <NewspaperIcon className="h-5 w-5 mr-3 text-muted-foreground" />
                Articles
              </Link>
            </li>
            <li>
              <Link
                href="/admin/sources"
                className="flex items-center p-2 rounded-md hover:bg-muted text-foreground"
              >
                <DocumentTextIcon className="h-5 w-5 mr-3 text-muted-foreground" />
                Sources
              </Link>
            </li>
            <li>
              <Link
                href="/admin/users"
                className="flex items-center p-2 rounded-md hover:bg-muted text-foreground"
              >
                <UsersIcon className="h-5 w-5 mr-3 text-muted-foreground" />
                Users
              </Link>
            </li>
            <li>
              <Link
                href="/admin/analytics"
                className="flex items-center p-2 rounded-md hover:bg-muted text-foreground"
              >
                <ChartBarIcon className="h-5 w-5 mr-3 text-muted-foreground" />
                Analytics
              </Link>
            </li>
            <li>
              <Link
                href="/admin/settings"
                className="flex items-center p-2 rounded-md hover:bg-muted text-foreground"
              >
                <Cog6ToothIcon className="h-5 w-5 mr-3 text-muted-foreground" />
                Settings
              </Link>
            </li>
          </ul>
        </nav>
      </div>

      {/* Mobile sidebar */}
      <div className="fixed bottom-0 left-0 right-0 z-50 bg-card border-t border-border md:hidden">
        <nav className="flex justify-around">
          <Link href="/admin" className="p-4 text-center">
            <HomeIcon className="h-6 w-6 mx-auto text-foreground" />
            <span className="text-xs mt-1 block">Dashboard</span>
          </Link>
          <Link href="/admin/articles" className="p-4 text-center">
            <NewspaperIcon className="h-6 w-6 mx-auto text-foreground" />
            <span className="text-xs mt-1 block">Articles</span>
          </Link>
          <Link href="/admin/sources" className="p-4 text-center">
            <DocumentTextIcon className="h-6 w-6 mx-auto text-foreground" />
            <span className="text-xs mt-1 block">Sources</span>
          </Link>
          <Link href="/admin/users" className="p-4 text-center">
            <UsersIcon className="h-6 w-6 mx-auto text-foreground" />
            <span className="text-xs mt-1 block">Users</span>
          </Link>
        </nav>
      </div>

      {/* Main content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        <div className="h-16 border-b border-border flex items-center justify-between px-6">
          <div className="md:hidden">
            <h2 className="text-lg font-semibold">Admin Dashboard</h2>
          </div>
          <div className="ml-auto flex items-center space-x-4">
            <span className="text-sm text-muted-foreground">
              Logged in as: <span className="font-medium text-foreground">{user?.username}</span>
            </span>
          </div>
        </div>
        <div className="flex-1 overflow-auto p-6 pb-20 md:pb-6">{children}</div>
      </div>
    </div>
  );
}