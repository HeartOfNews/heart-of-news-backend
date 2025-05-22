'use client';

import React, { useState, useEffect } from 'react';
import { useWebSocket } from '@/contexts/WebSocketContext';
import { useWebSocketMessage } from '@/hooks/useWebSocketMessage';

interface Notification {
  id: string;
  message: string;
  type: 'info' | 'success' | 'warning' | 'error';
  timestamp: number;
  read: boolean;
}

export default function NotificationCenter() {
  const { connectionStatus } = useWebSocket();
  const { lastData, messageHistory } = useWebSocketMessage('notification');
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [showNotifications, setShowNotifications] = useState(false);
  const [unreadCount, setUnreadCount] = useState(0);

  // Process new notifications
  useEffect(() => {
    if (lastData) {
      const newNotification: Notification = {
        id: crypto.randomUUID(),
        message: lastData.message,
        type: lastData.type || 'info',
        timestamp: Date.now(),
        read: false,
      };
      
      setNotifications(prev => [newNotification, ...prev]);
      setUnreadCount(prev => prev + 1);
      
      // Auto-hide notification after 5 seconds
      setTimeout(() => {
        setNotifications(prev => 
          prev.map(n => n.id === newNotification.id ? { ...n, read: true } : n)
        );
      }, 5000);
    }
  }, [lastData]);

  // Update unread count when notifications change
  useEffect(() => {
    setUnreadCount(notifications.filter(n => !n.read).length);
  }, [notifications]);

  // Mark all as read
  const markAllAsRead = () => {
    setNotifications(prev => prev.map(n => ({ ...n, read: true })));
    setUnreadCount(0);
  };

  // Clear all notifications
  const clearAll = () => {
    setNotifications([]);
    setUnreadCount(0);
  };

  // Connection status indicator color
  const statusColor = {
    connected: 'bg-green-500',
    connecting: 'bg-yellow-500',
    disconnected: 'bg-gray-500',
    error: 'bg-red-500',
  };

  return (
    <div className="relative">
      {/* Notification bell icon */}
      <button
        onClick={() => setShowNotifications(!showNotifications)}
        className="p-2 rounded-full hover:bg-gray-200 dark:hover:bg-gray-700 relative"
        aria-label="Notifications"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          className="h-6 w-6"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"
          />
        </svg>
        
        {/* Connection status indicator */}
        <span 
          className={`absolute top-1 right-1 h-2 w-2 rounded-full ${statusColor[connectionStatus]}`} 
          title={`WebSocket ${connectionStatus}`}
        />
        
        {/* Unread badge */}
        {unreadCount > 0 && (
          <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center">
            {unreadCount}
          </span>
        )}
      </button>

      {/* Notification dropdown */}
      {showNotifications && (
        <div className="absolute right-0 mt-2 w-80 bg-white dark:bg-gray-800 rounded-md shadow-lg overflow-hidden z-20 border border-gray-200 dark:border-gray-700">
          <div className="p-3 border-b border-gray-200 dark:border-gray-700 flex justify-between items-center">
            <h3 className="font-medium">Notifications</h3>
            <div className="space-x-2">
              <button 
                onClick={markAllAsRead}
                className="text-xs text-blue-600 dark:text-blue-400 hover:underline"
              >
                Mark all as read
              </button>
              <button 
                onClick={clearAll}
                className="text-xs text-red-600 dark:text-red-400 hover:underline"
              >
                Clear all
              </button>
            </div>
          </div>
          
          <div className="max-h-96 overflow-y-auto">
            {notifications.length === 0 ? (
              <div className="p-4 text-center text-gray-500 dark:text-gray-400">
                No notifications
              </div>
            ) : (
              notifications.map(notification => (
                <div 
                  key={notification.id} 
                  className={`p-3 border-b border-gray-100 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700 ${
                    !notification.read ? 'bg-blue-50 dark:bg-blue-900/20' : ''
                  }`}
                >
                  <div className="flex items-start">
                    <div className={`mt-1 mr-3 rounded-full w-2 h-2 flex-shrink-0 ${
                      notification.type === 'info' ? 'bg-blue-500' : 
                      notification.type === 'success' ? 'bg-green-500' : 
                      notification.type === 'warning' ? 'bg-yellow-500' : 
                      'bg-red-500'
                    }`} />
                    <div className="flex-1">
                      <p className="text-sm">{notification.message}</p>
                      <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                        {new Date(notification.timestamp).toLocaleTimeString()}
                      </p>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
          
          <div className="p-2 border-t border-gray-200 dark:border-gray-700 text-center">
            <p className="text-xs text-gray-500 dark:text-gray-400">
              WebSocket Status: {connectionStatus}
            </p>
          </div>
        </div>
      )}
    </div>
  );
}