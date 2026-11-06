'use client';

import * as React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Menu, Bell, Sparkles, Shield, User, LogOut } from 'lucide-react';
import { useAuth } from '@/hooks/use-auth';
import { profileClient } from '@/lib/profile-client';

export interface TopbarProps {
  onMobileMenuToggle: () => void;
}

export function Topbar({ onMobileMenuToggle }: TopbarProps) {
  const pathname = usePathname();
  const { user, logout } = useAuth();
  const [showNotifications, setShowNotifications] = React.useState(false);
  const [showUserMenu, setShowUserMenu] = React.useState(false);
  const [isLoggingOut, setIsLoggingOut] = React.useState(false);
  const [targetRole, setTargetRole] = React.useState<string | null>(null);

  React.useEffect(() => {
    let isMounted = true;
    profileClient
      .getMasterProfile()
      .then((data) => {
        if (isMounted && data?.primary_role?.title) {
          setTargetRole(data.primary_role.title);
        }
      })
      .catch(() => {
        // Silently continue with default
      });
    return () => {
      isMounted = false;
    };
  }, []);

  const displayName = user?.full_name || 'Candidate';
  const displayEmail = user?.email || '';
  const initials = React.useMemo(() => {
    if (!displayName) return 'CP';
    const parts = displayName.trim().split(/\s+/);
    if (parts.length >= 2) {
      return `${parts[0][0]}${parts[1][0]}`.toUpperCase();
    }
    return displayName.slice(0, 2).toUpperCase();
  }, [displayName]);

  // Generate page title from route
  const getPageTitle = (path: string) => {
    switch (path) {
      case '/dashboard':
        return 'Executive Career Dashboard';
      case '/career-profile':
      case '/profile':
        return 'Career Profile & Evidence Graph';
      case '/skills':
        return 'Skill Taxonomy & Gap Engine';
      case '/assessments':
        return 'Diagnostic Skill Assessments';
      case '/roadmap':
        return 'Dynamic Milestone Roadmap';
      case '/jobs':
        return 'Job Discovery & Semantic Matching';
      case '/resume':
        return 'Resume Optimization & Anti-Hallucination Diff';
      case '/applications':
        return 'Application Tracker & Pipeline';
      case '/recruiters':
        return 'Recruiter Discovery & Outreach Gate';
      case '/interviews':
        return 'Interview Preparation & STAR Question Bank';
      case '/career-readiness':
      case '/readiness':
        return 'Career Readiness Index (4 Pillars)';
      case '/settings':
        return 'Settings & Privacy Controls';
      default:
        return 'CoachPath Platform';
    }
  };

  const menuItem =
    'flex h-10 items-center gap-2 rounded-xl px-3 text-sm text-ink-muted transition-colors hover:bg-white/5 hover:text-ink-fg';

  return (
    <header className="sticky top-0 z-20 flex h-16 items-center justify-between gap-3 border-b border-white/[0.08] bg-black/60 px-4 backdrop-blur-xl sm:px-6 md:border-none md:bg-transparent md:backdrop-blur-none">
      {/* Left: menu button and page context */}
      <div className="flex min-w-0 items-center gap-2">
        <button
          onClick={onMobileMenuToggle}
          className="grid h-11 w-11 shrink-0 place-items-center rounded-full text-ink-fg transition-colors hover:bg-white/5 md:hidden"
          aria-label="Open navigation menu"
        >
          <Menu className="h-5 w-5" />
        </button>
        <div className="min-w-0">
          <p className="truncate text-sm font-medium text-ink-fg">{getPageTitle(pathname || '')}</p>
          <p className="hidden truncate text-xs text-ink-dim sm:block">
            {displayName} {targetRole ? `· Target: ${targetRole}` : '· Career Intelligence'}
          </p>
        </div>
      </div>

      {/* Right controls */}
      <div className="flex shrink-0 items-center gap-2">
        <Link
          href="/career-readiness"
          className="hidden h-9 items-center gap-1.5 rounded-full border border-lav/30 bg-lav/10 px-3.5 text-[13px] font-medium text-lav transition-colors hover:bg-lav/15 sm:flex"
        >
          <Sparkles className="h-3.5 w-3.5" />
          Readiness Hub
        </Link>

        <div className="relative">
          <button
            onClick={() => {
              setShowNotifications(!showNotifications);
              setShowUserMenu(false);
            }}
            className="relative grid h-10 w-10 place-items-center rounded-full text-ink-muted transition-colors hover:bg-white/5 hover:text-ink-fg"
            aria-label="Notifications"
            aria-expanded={showNotifications}
          >
            <Bell className="h-5 w-5" />
            <span className="absolute right-2 top-2 h-2 w-2 rounded-full bg-lime ring-2 ring-black" aria-hidden />
          </button>

          {showNotifications && (
            <div className="liquid-glass absolute right-0 z-50 mt-2 w-80 rounded-2xl p-4 text-sm text-ink-fg">
              <div className="flex items-center justify-between border-b border-white/10 pb-2 font-medium">
                <span>Recent updates</span>
                <span className="text-xs text-ink-dim">All caught up</span>
              </div>
              <div className="space-y-2 py-2">
                <div className="rounded-xl border border-lav/25 bg-lav/[0.08] p-3">
                  <p className="font-medium text-lav">AI Career Discovery</p>
                  <p className="mt-0.5 text-xs text-ink-muted">
                    Complete your onboarding conversation to calibrate your skill baseline.
                  </p>
                </div>
                <div className="rounded-xl border border-lime/25 bg-lime/[0.06] p-3">
                  <p className="font-medium text-lime">Diagnostic Benchmarks</p>
                  <p className="mt-0.5 text-xs text-ink-muted">
                    Assessments available to verify proficiency in system architecture and backend foundations.
                  </p>
                </div>
              </div>
            </div>
          )}
        </div>

        <div className="relative">
          <button
            onClick={() => {
              setShowUserMenu(!showUserMenu);
              setShowNotifications(false);
            }}
            className="grid h-10 w-10 place-items-center rounded-full transition-colors hover:bg-white/5"
            aria-label="User menu"
            aria-expanded={showUserMenu}
          >
            <span className="grid h-8 w-8 place-items-center rounded-full bg-lav/15 text-xs font-semibold text-lav">{initials}</span>
          </button>

          {showUserMenu && (
            <div className="liquid-glass absolute right-0 z-50 mt-2 w-60 rounded-2xl p-2 text-sm">
              <div className="border-b border-white/10 px-3 py-2.5">
                <p className="truncate font-medium text-ink-fg">{displayName}</p>
                <p className="truncate text-xs text-ink-dim">{displayEmail}</p>
              </div>
              <div className="py-1">
                <Link href="/career-profile" onClick={() => setShowUserMenu(false)} className={menuItem}>
                  <User className="h-4 w-4" />
                  Edit Profile
                </Link>
                <Link href="/settings" onClick={() => setShowUserMenu(false)} className={menuItem}>
                  <Shield className="h-4 w-4" />
                  Privacy & Security
                </Link>
                <button
                  type="button"
                  disabled={isLoggingOut}
                  onClick={async () => {
                    setIsLoggingOut(true);
                    setShowUserMenu(false);
                    await logout();
                    setIsLoggingOut(false);
                  }}
                  className="flex h-10 w-full items-center gap-2 rounded-xl px-3 text-left text-sm text-crimson-soft transition-colors hover:bg-crimson/10 disabled:opacity-50"
                >
                  <LogOut className="h-4 w-4" />
                  {isLoggingOut ? 'Signing out...' : 'Sign Out'}
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
