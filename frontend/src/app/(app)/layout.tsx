'use client';

import * as React from 'react';
import { useRouter, usePathname } from 'next/navigation';
import { AppShell } from '@/components/layout/app-shell';
import { useAuth } from '@/hooks/use-auth';

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
      <div className="cp-dark flex min-h-screen flex-col items-center justify-center px-4">
        <div className="flex flex-col items-center gap-4">
          <span className="grid h-12 w-12 animate-pulse place-items-center rounded-2xl bg-gradient-to-b from-lav-light to-lav text-lg font-bold text-lav-ink">C</span>
          <div className="text-center space-y-1">
            <p className="font-display text-base font-semibold tracking-[-0.02em] text-ink-fg">Loading Workspace</p>
            <p className="text-sm text-ink-muted">Verifying secure career session...</p>
          </div>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return (
      <div className="cp-dark flex min-h-screen flex-col items-center justify-center px-4">
        <div className="flex flex-col items-center gap-4">
          <span className="grid h-12 w-12 animate-pulse place-items-center rounded-2xl bg-gradient-to-b from-lav-light to-lav text-lg font-bold text-lav-ink">C</span>
          <div className="text-center space-y-1">
            <p className="font-display text-base font-semibold tracking-[-0.02em] text-ink-fg">Redirecting to Sign In</p>
            <p className="text-sm text-ink-muted">Please sign in to access your workspace...</p>
          </div>
        </div>
      </div>
    );
  }

  return <AppShell>{children}</AppShell>;
}
