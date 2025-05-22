'use client';

import { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import Image from 'next/image';
import { Bars3Icon, XMarkIcon } from '@heroicons/react/24/outline';
import { useAuth } from '@/contexts/AuthContext';
import ThemeToggle from '@/components/ui/ThemeToggle';
import NotificationCenter from '@/components/features/NotificationCenter';

const navigation = [
  { name: 'Home', href: '/' },
  { name: 'Articles', href: '/articles' },
  { name: 'Sources', href: '/sources' },
  { name: 'About', href: '/about' },
];

export default function Header() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const pathname = usePathname();
  const { user, isAuthenticated, logout } = useAuth();

  return (
    <header className="bg-background">
      <nav className="mx-auto flex max-w-7xl items-center justify-between p-6 lg:px-8" aria-label="Global">
        <div className="flex lg:flex-1">
          <Link href="/" className="-m-1.5 p-1.5">
            <span className="sr-only">Heart of News</span>
            <div className="flex items-center">
              <div className="relative h-8 w-8 mr-2">
                {/* Replace with your logo */}
                <div className="h-8 w-8 rounded-full bg-primary flex items-center justify-center">
                  <span className="text-primary-foreground font-bold">H</span>
                </div>
              </div>
              <span className="text-lg font-semibold">Heart of News</span>
            </div>
          </Link>
        </div>
        <div className="flex lg:hidden">
          <button
            type="button"
            className="-m-2.5 inline-flex items-center justify-center rounded-md p-2.5 text-gray-700 dark:text-gray-200"
            onClick={() => setMobileMenuOpen(true)}
          >
            <span className="sr-only">Open main menu</span>
            <Bars3Icon className="h-6 w-6" aria-hidden="true" />
          </button>
        </div>
        <div className="hidden lg:flex lg:gap-x-12">
          {navigation.map((item) => (
            <Link
              key={item.name}
              href={item.href}
              className={`text-sm font-semibold leading-6 ${
                pathname === item.href
                  ? 'text-primary dark:text-primary'
                  : 'text-muted-foreground hover:text-foreground'
              }`}
            >
              {item.name}
            </Link>
          ))}
        </div>
        <div className="hidden lg:flex lg:flex-1 lg:justify-end lg:gap-x-4 items-center">
          <NotificationCenter />
          <ThemeToggle />
          {isAuthenticated ? (
            <>
              {user?.role === 'admin' && (
                <Link
                  href="/admin"
                  className="text-sm font-semibold leading-6 text-muted-foreground hover:text-foreground"
                >
                  Admin
                </Link>
              )}
              <Link
                href="/profile"
                className="text-sm font-semibold leading-6 text-muted-foreground hover:text-foreground"
              >
                Profile
              </Link>
              <button
                onClick={logout}
                className="text-sm font-semibold leading-6 text-muted-foreground hover:text-foreground"
              >
                Log out
              </button>
            </>
          ) : (
            <>
              <Link
                href="/login"
                className="text-sm font-semibold leading-6 text-muted-foreground hover:text-foreground"
              >
                Log in
              </Link>
              <Link
                href="/register"
                className="rounded-md bg-primary px-3 py-2 text-sm font-semibold text-primary-foreground shadow-sm hover:bg-primary/90 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary"
              >
                Sign up
              </Link>
            </>
          )}
        </div>
      </nav>
      
      {/* Mobile menu */}
      <div className={`lg:hidden ${mobileMenuOpen ? 'fixed inset-0 z-50' : 'hidden'}`}>
        <div className="fixed inset-0 bg-black/20 backdrop-blur-sm dark:bg-gray-900/80" />
        <div className="fixed inset-y-0 right-0 z-50 w-full overflow-y-auto bg-background px-6 py-6 sm:max-w-sm sm:ring-1 sm:ring-gray-900/10">
          <div className="flex items-center justify-between">
            <Link href="/" className="-m-1.5 p-1.5">
              <span className="sr-only">Heart of News</span>
              <div className="flex items-center">
                <div className="relative h-8 w-8 mr-2">
                  {/* Replace with your logo */}
                  <div className="h-8 w-8 rounded-full bg-primary flex items-center justify-center">
                    <span className="text-primary-foreground font-bold">H</span>
                  </div>
                </div>
                <span className="text-lg font-semibold">Heart of News</span>
              </div>
            </Link>
            <button
              type="button"
              className="-m-2.5 rounded-md p-2.5 text-gray-700 dark:text-gray-200"
              onClick={() => setMobileMenuOpen(false)}
            >
              <span className="sr-only">Close menu</span>
              <XMarkIcon className="h-6 w-6" aria-hidden="true" />
            </button>
          </div>
          <div className="mt-6 flow-root">
            <div className="-my-6 divide-y divide-gray-500/10">
              <div className="space-y-2 py-6">
                {navigation.map((item) => (
                  <Link
                    key={item.name}
                    href={item.href}
                    className={`-mx-3 block rounded-lg px-3 py-2 text-base font-semibold leading-7 ${
                      pathname === item.href
                        ? 'text-primary dark:text-primary'
                        : 'text-muted-foreground hover:text-foreground hover:bg-muted/50'
                    }`}
                    onClick={() => setMobileMenuOpen(false)}
                  >
                    {item.name}
                  </Link>
                ))}
              </div>
              <div className="py-6">
                <div className="flex items-center mb-4">
                  <NotificationCenter />
                  <span className="mr-2 ml-4">Theme:</span>
                  <ThemeToggle />
                </div>
                {isAuthenticated ? (
                  <>
                    {user?.role === 'admin' && (
                      <Link
                        href="/admin"
                        className="-mx-3 block rounded-lg px-3 py-2.5 text-base font-semibold leading-7 text-muted-foreground hover:text-foreground hover:bg-muted/50"
                        onClick={() => setMobileMenuOpen(false)}
                      >
                        Admin
                      </Link>
                    )}
                    <Link
                      href="/profile"
                      className="-mx-3 block rounded-lg px-3 py-2.5 text-base font-semibold leading-7 text-muted-foreground hover:text-foreground hover:bg-muted/50"
                      onClick={() => setMobileMenuOpen(false)}
                    >
                      Profile
                    </Link>
                    <button
                      onClick={() => {
                        logout();
                        setMobileMenuOpen(false);
                      }}
                      className="-mx-3 block rounded-lg px-3 py-2.5 text-base font-semibold leading-7 text-muted-foreground hover:text-foreground hover:bg-muted/50 w-full text-left"
                    >
                      Log out
                    </button>
                  </>
                ) : (
                  <>
                    <Link
                      href="/login"
                      className="-mx-3 block rounded-lg px-3 py-2.5 text-base font-semibold leading-7 text-muted-foreground hover:text-foreground hover:bg-muted/50"
                      onClick={() => setMobileMenuOpen(false)}
                    >
                      Log in
                    </Link>
                    <Link
                      href="/register"
                      className="-mx-3 block rounded-lg px-3 py-2.5 text-base font-semibold leading-7 text-muted-foreground hover:text-foreground hover:bg-muted/50"
                      onClick={() => setMobileMenuOpen(false)}
                    >
                      Sign up
                    </Link>
                  </>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}