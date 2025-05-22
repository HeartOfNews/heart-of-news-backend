'use client';

import { useState, useEffect } from 'react';
import { useTheme } from 'next-themes';
import { SunIcon, MoonIcon, ComputerDesktopIcon } from '@heroicons/react/24/outline';

export default function ThemeToggle() {
  const [mounted, setMounted] = useState(false);
  const { theme, setTheme } = useTheme();
  
  // Avoid hydration mismatch
  useEffect(() => setMounted(true), []);
  
  if (!mounted) return null;
  
  return (
    <div className="flex items-center space-x-2 border rounded-md p-1">
      <button
        onClick={() => setTheme('light')}
        className={`p-1.5 rounded-md ${
          theme === 'light' 
            ? 'bg-primary text-primary-foreground' 
            : 'text-muted-foreground hover:text-foreground hover:bg-muted/50'
        }`}
        aria-label="Light mode"
      >
        <SunIcon className="h-4 w-4" />
      </button>
      
      <button
        onClick={() => setTheme('dark')}
        className={`p-1.5 rounded-md ${
          theme === 'dark' 
            ? 'bg-primary text-primary-foreground' 
            : 'text-muted-foreground hover:text-foreground hover:bg-muted/50'
        }`}
        aria-label="Dark mode"
      >
        <MoonIcon className="h-4 w-4" />
      </button>
      
      <button
        onClick={() => setTheme('system')}
        className={`p-1.5 rounded-md ${
          theme === 'system' 
            ? 'bg-primary text-primary-foreground' 
            : 'text-muted-foreground hover:text-foreground hover:bg-muted/50'
        }`}
        aria-label="System mode"
      >
        <ComputerDesktopIcon className="h-4 w-4" />
      </button>
    </div>
  );
}