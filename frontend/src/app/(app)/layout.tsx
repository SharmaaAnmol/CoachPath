'use client';

import * as React from 'react';
import { useRouter, usePathname } from 'next/navigation';
import { AppShell } from '@/components/layout/app-shell';
import { useAuth } from '@/hooks/use-auth';
import { Sparkles } from 'lucide-react';

export default function AppLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { status, isAuthenticated, isLoading } = useAuth();
  const router = useRouter();
  const pathname = usePathname();

  React.useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      const redirectUrl = pathname ? `/login?redirect=${encodeURIComponent(pathname)}` : '/login';
      router.replace(redirectUrl);
    }
  }, [isLoading, isAuthenticated, router, pathname]);

  // Flash prevention loading screen during session verification
  if (isLoading || status === 'loading') {
    return (
      <div className="min-h-screen bg-slate-900 flex flex-col items-center justify-center text-white px-4">
        <div className="flex flex-col items-center gap-4">
          <div className="h-12 w-12 rounded-2xl bg-gradient-to-tr from-brand-600 to-purple-500 flex items-center justify-center text-white shadow-lg shadow-purple-500/20 animate-pulse">
            <Sparkles className="h-6 w-6 text-white" />
          </div>
          <div className="text-center space-y-1">
            <p className="font-bold text-base tracking-tight text-white">Loading Workspace</p>
            <p className="text-xs text-slate-400">Verifying secure career session...</p>
          </div>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-slate-900 flex flex-col items-center justify-center text-white px-4">
        <div className="flex flex-col items-center gap-4">
          <div className="h-12 w-12 rounded-2xl bg-gradient-to-tr from-brand-600 to-purple-500 flex items-center justify-center text-white shadow-lg shadow-purple-500/20 animate-pulse">
            <Sparkles className="h-6 w-6 text-white" />
          </div>
          <div className="text-center space-y-1">
            <p className="font-bold text-base tracking-tight text-white">Redirecting to Sign In</p>
            <p className="text-xs text-slate-400">Please sign in to access your workspace...</p>
          </div>
        </div>
      </div>
    );
  }

  return <AppShell>{children}</AppShell>;
}
