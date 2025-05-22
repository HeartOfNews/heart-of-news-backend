'use client';

import { Inter, Roboto_Mono } from 'next/font/google';
import { ThemeProvider } from 'next-themes';
import Header from '@/components/layout/Header';
import Footer from '@/components/layout/Footer';
import { AuthProvider } from '@/contexts/AuthContext';
import { WebSocketProvider } from '@/contexts/WebSocketContext';
import '@/styles/globals.css';

const inter = Inter({
  subsets: ['latin'],
  display: 'swap',
  variable: '--font-inter',
});

const roboto_mono = Roboto_Mono({
  subsets: ['latin'],
  display: 'swap',
  variable: '--font-roboto-mono',
});

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={`${inter.variable} ${roboto_mono.variable} font-sans`}>
        <ThemeProvider attribute="class" defaultTheme="system" enableSystem>
          <AuthProvider>
            <WebSocketProvider>
              <div className="flex min-h-screen flex-col">
                <Header />
                <main className="flex-grow">{children}</main>
                <Footer />
              </div>
            </WebSocketProvider>
          </AuthProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}