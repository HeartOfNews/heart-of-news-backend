'use client';

import { useState, useEffect } from 'react';
import {
  ChartBarIcon,
  UsersIcon,
  NewspaperIcon,
  DocumentTextIcon,
  ExclamationTriangleIcon,
  ArrowUpIcon,
  ArrowDownIcon,
} from '@heroicons/react/24/outline';
import Link from 'next/link';
import api from '@/lib/api';

interface StatsCard {
  title: string;
  value: string;
  change: {
    value: string;
    isPositive: boolean;
  };
  icon: React.ForwardRefExoticComponent<React.SVGProps<SVGSVGElement>>;
  color: string;
}

export default function AdminDashboard() {
  const [isLoading, setIsLoading] = useState(true);
  const [stats, setStats] = useState<StatsCard[]>([]);
  const [recentArticles, setRecentArticles] = useState([]);
  const [recentUsers, setRecentUsers] = useState([]);
  const [alerts, setAlerts] = useState([]);

  useEffect(() => {
    // This would normally fetch data from the API
    // For now, we'll use mock data
    setTimeout(() => {
      setStats([
        {
          title: 'Total Users',
          value: '1,234',
          change: {
            value: '12%',
            isPositive: true,
          },
          icon: UsersIcon,
          color: 'bg-blue-500',
        },
        {
          title: 'Articles',
          value: '5,678',
          change: {
            value: '8%',
            isPositive: true,
          },
          icon: NewspaperIcon,
          color: 'bg-green-500',
        },
        {
          title: 'Sources',
          value: '42',
          change: {
            value: '2%',
            isPositive: true,
          },
          icon: DocumentTextIcon,
          color: 'bg-purple-500',
        },
        {
          title: 'Avg. Bias Score',
          value: '0.32',
          change: {
            value: '5%',
            isPositive: false,
          },
          icon: ChartBarIcon,
          color: 'bg-yellow-500',
        },
      ]);

      setRecentArticles([
        {
          id: '1',
          title: 'Global Climate Summit Reaches New Agreement',
          source: 'CNN',
          date: '2023-11-15',
          biasScore: 0.32,
        },
        {
          id: '2',
          title: 'Tech Giants Face New Regulations in EU',
          source: 'BBC',
          date: '2023-11-14',
          biasScore: 0.18,
        },
        {
          id: '3',
          title: 'Space Mission Successfully Lands on Mars',
          source: 'Reuters',
          date: '2023-11-13',
          biasScore: 0.05,
        },
        {
          id: '4',
          title: 'Economic Forecast Shows Growth for Next Quarter',
          source: 'Bloomberg',
          date: '2023-11-12',
          biasScore: 0.28,
        },
      ]);

      setRecentUsers([
        {
          id: '1',
          username: 'alice_smith',
          email: 'alice@example.com',
          joinDate: '2023-11-10',
          role: 'user',
        },
        {
          id: '2',
          username: 'bob_jones',
          email: 'bob@example.com',
          joinDate: '2023-11-09',
          role: 'user',
        },
        {
          id: '3',
          username: 'carol_white',
          email: 'carol@example.com',
          joinDate: '2023-11-08',
          role: 'admin',
        },
      ]);

      setAlerts([
        {
          id: '1',
          title: 'High server load detected',
          description: 'Database server CPU usage above 90%',
          severity: 'critical',
          time: '15 minutes ago',
        },
        {
          id: '2',
          title: 'Failed login attempts',
          description: 'Multiple failed login attempts for user admin@example.com',
          severity: 'warning',
          time: '2 hours ago',
        },
      ]);

      setIsLoading(false);
    }, 1000);
  }, []);

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-[60vh]">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-bold">Dashboard</h1>
        <p className="text-muted-foreground">Welcome to the Heart of News admin dashboard</p>
      </div>

      {/* Stats cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {stats.map((stat, index) => (
          <div key={index} className="bg-card rounded-lg shadow-sm p-6 border border-border">
            <div className="flex items-center">
              <div className={`rounded-full p-3 ${stat.color} text-white`}>
                <stat.icon className="h-6 w-6" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-muted-foreground">{stat.title}</p>
                <p className="text-2xl font-semibold">{stat.value}</p>
              </div>
            </div>
            <div className="mt-4 flex items-center">
              {stat.change.isPositive ? (
                <ArrowUpIcon className="h-4 w-4 text-green-500" />
              ) : (
                <ArrowDownIcon className="h-4 w-4 text-red-500" />
              )}
              <span
                className={`text-sm ml-1 ${
                  stat.change.isPositive ? 'text-green-500' : 'text-red-500'
                }`}
              >
                {stat.change.value} from last month
              </span>
            </div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        {/* Recent articles */}
        <div className="bg-card rounded-lg shadow-sm border border-border p-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-lg font-semibold">Recent Articles</h2>
            <Link href="/admin/articles" className="text-sm text-primary hover:underline">
              View all
            </Link>
          </div>
          <div className="space-y-4">
            {recentArticles.map((article: any) => (
              <div key={article.id} className="flex justify-between items-center border-b border-border pb-3 last:border-0 last:pb-0">
                <div>
                  <p className="font-medium">{article.title}</p>
                  <div className="flex space-x-2 text-sm text-muted-foreground">
                    <span>{article.source}</span>
                    <span>•</span>
                    <span>{article.date}</span>
                  </div>
                </div>
                <div className="text-sm">
                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full bg-secondary text-secondary-foreground">
                    Bias: {article.biasScore}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Recent users */}
        <div className="bg-card rounded-lg shadow-sm border border-border p-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-lg font-semibold">Recent Users</h2>
            <Link href="/admin/users" className="text-sm text-primary hover:underline">
              View all
            </Link>
          </div>
          <div className="space-y-4">
            {recentUsers.map((user: any) => (
              <div key={user.id} className="flex justify-between items-center border-b border-border pb-3 last:border-0 last:pb-0">
                <div>
                  <p className="font-medium">{user.username}</p>
                  <p className="text-sm text-muted-foreground">{user.email}</p>
                </div>
                <div className="text-sm">
                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full bg-secondary text-secondary-foreground">
                    {user.role}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* System alerts */}
      <div className="bg-card rounded-lg shadow-sm border border-border p-6 mb-6">
        <div className="flex items-center mb-4">
          <ExclamationTriangleIcon className="h-5 w-5 text-yellow-500 mr-2" />
          <h2 className="text-lg font-semibold">System Alerts</h2>
        </div>
        {alerts.length === 0 ? (
          <p className="text-muted-foreground">No alerts at this time.</p>
        ) : (
          <div className="space-y-4">
            {alerts.map((alert: any) => (
              <div key={alert.id} className="flex justify-between items-center border-b border-border pb-3 last:border-0 last:pb-0">
                <div>
                  <p className="font-medium">{alert.title}</p>
                  <p className="text-sm text-muted-foreground">{alert.description}</p>
                </div>
                <div className="text-sm">
                  <span
                    className={`inline-flex items-center px-2.5 py-0.5 rounded-full ${
                      alert.severity === 'critical'
                        ? 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
                        : 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200'
                    }`}
                  >
                    {alert.severity}
                  </span>
                  <p className="mt-1 text-xs text-muted-foreground">{alert.time}</p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Quick actions */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Link
          href="/admin/articles/new"
          className="flex flex-col items-center justify-center p-6 bg-card rounded-lg shadow-sm border border-border hover:bg-muted/50 transition-colors"
        >
          <NewspaperIcon className="h-8 w-8 text-primary mb-2" />
          <span className="font-medium">Add New Article</span>
        </Link>
        <Link
          href="/admin/sources/new"
          className="flex flex-col items-center justify-center p-6 bg-card rounded-lg shadow-sm border border-border hover:bg-muted/50 transition-colors"
        >
          <DocumentTextIcon className="h-8 w-8 text-primary mb-2" />
          <span className="font-medium">Add New Source</span>
        </Link>
        <Link
          href="/admin/users/new"
          className="flex flex-col items-center justify-center p-6 bg-card rounded-lg shadow-sm border border-border hover:bg-muted/50 transition-colors"
        >
          <UsersIcon className="h-8 w-8 text-primary mb-2" />
          <span className="font-medium">Add New User</span>
        </Link>
      </div>
    </div>
  );
}