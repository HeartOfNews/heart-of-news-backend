'use client';

import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';

interface NewArticlesNotificationProps {
  count: number;
  onClick: () => void;
}

export default function NewArticlesNotification({ count, onClick }: NewArticlesNotificationProps) {
  if (count === 0) return null;

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -20 }}
        transition={{ duration: 0.2 }}
        className="sticky top-2 z-10 w-full flex justify-center"
      >
        <button
          onClick={onClick}
          className="bg-primary text-primary-foreground px-4 py-2 rounded-full shadow-lg flex items-center space-x-2 hover:bg-primary/90 transition-colors"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            className="h-5 w-5 animate-bounce"
            viewBox="0 0 20 20"
            fill="currentColor"
          >
            <path
              fillRule="evenodd"
              d="M5.293 9.707a1 1 0 010-1.414l4-4a1 1 0 011.414 0l4 4a1 1 0 01-1.414 1.414L11 7.414V15a1 1 0 11-2 0V7.414L6.707 9.707a1 1 0 01-1.414 0z"
              clipRule="evenodd"
            />
          </svg>
          <span>
            {count} new article{count !== 1 ? 's' : ''} available
          </span>
        </button>
      </motion.div>
    </AnimatePresence>
  );
}