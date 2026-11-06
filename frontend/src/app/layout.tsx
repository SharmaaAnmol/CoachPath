import type { Metadata, Viewport } from 'next';
import './globals.css';
import { QueryProvider } from '@/providers/query-provider';
import { AuthProvider } from '@/providers/auth-provider';
import { PwaRegister } from '@/components/pwa-register';

export const metadata: Metadata = {
  title: 'CoachPath – AI-Powered Career Intelligence & Readiness Platform',
  description:
    'Bridge the gap from uncertainty to job readiness with validated skill diagnostics, personalized roadmaps, truthful resume optimization, and deterministic career matching.',
  keywords: [
    'career intelligence',
    'skill gap analysis',
    'software engineer roadmap',
    'technical resume optimizer',
    'interview preparation',
  ],
  applicationName: 'CoachPath',
  appleWebApp: { capable: true, title: 'CoachPath', statusBarStyle: 'black-translucent' },
  icons: { icon: '/icons/icon-192.png', apple: '/icons/apple-touch-icon.png' },
};

export const viewport: Viewport = {
  themeColor: '#000000',
  width: 'device-width',
  initialScale: 1,
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="h-full">
      <head>
        {/* Funnel fonts are not in next/font's list for Next 14.2, so they load from Google Fonts. */}
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link
          rel="stylesheet"
          href="https://fonts.googleapis.com/css2?family=Funnel+Display:wght@500;600;700&family=Funnel+Sans:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap"
        />
      </head>
      <body className="h-full flex flex-col font-sans text-slate-900 bg-slate-50 antialiased selection:bg-purple-100 selection:text-purple-900">
        <QueryProvider>
          <AuthProvider>{children}</AuthProvider>
        </QueryProvider>
        <PwaRegister />
      </body>
    </html>
  );
}
