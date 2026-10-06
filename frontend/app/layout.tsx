import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'CoachPath · AI Career Intelligence & Placement Assistant',
  description: 'AI-powered Career Intelligence & Job Application Assistant for Bharat Hackathon 2.0',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="bg-brand-dark text-slate-100 font-sans min-h-screen antialiased selection:bg-brand-purple selection:text-white">
        {children}
      </body>
    </html>
  );
}
