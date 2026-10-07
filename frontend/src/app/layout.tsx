import type { Metadata } from 'next';
import './globals.css';
import { QueryProvider } from '@/providers/query-provider';

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
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="h-full">
      <body className="h-full flex flex-col font-sans text-slate-900 bg-slate-50 antialiased selection:bg-purple-100 selection:text-purple-900">
        <QueryProvider>{children}</QueryProvider>
      </body>
    </html>
  );
}
