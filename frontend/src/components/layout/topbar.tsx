'use client';

import * as React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Menu, Search, Bell, Sparkles, Shield, User, LogOut } from 'lucide-react';
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

  return (
    <header className="sticky top-0 z-20 h-16 bg-white/90 dark:bg-slate-900/90 backdrop-blur-md border-b border-slate-200/80 dark:border-slate-800 flex items-center justify-between px-4 sm:px-6">
      {/* Left: Hamburger & Page Breadcrumb */}
      <div className="flex items-center gap-3">
        <button
          onClick={onMobileMenuToggle}
          className="md:hidden p-2 text-slate-500 hover:text-slate-800 dark:hover:text-slate-200 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
          aria-label="Toggle navigation menu"
        >
          <Menu className="w-5 h-5" />
        </button>

        <div>
          <h1 className="text-base font-bold text-slate-900 dark:text-white leading-tight">
            {getPageTitle(pathname || '')}
          </h1>
          <p className="hidden sm:block text-[11px] text-slate-500 dark:text-slate-400">
            {displayName} {targetRole ? `• Target: ${targetRole}` : '• Career Intelligence'}
          </p>
        </div>
      </div>

      {/* Right Controls */}
      <div className="flex items-center gap-3">
        {/* Global Search Bar Placeholder */}
        <div className="hidden lg:flex items-center gap-2 bg-slate-100 dark:bg-slate-800 px-3 py-1.5 rounded-xl text-slate-400 text-xs w-64 border border-transparent focus-within:border-brand-500 focus-within:bg-white dark:focus-within:bg-slate-800 transition-all">
          <Search className="w-3.5 h-3.5 shrink-0" />
          <input
            type="text"
            placeholder="Search skills, jobs, tasks..."
            className="bg-transparent border-none outline-none text-xs text-slate-800 dark:text-slate-200 w-full placeholder:text-slate-400"
          />
          <kbd className="hidden xl:inline text-[10px] font-mono bg-white dark:bg-slate-700 px-1.5 py-0.5 rounded border border-slate-200 dark:border-slate-600">
            ⌘K
          </kbd>
        </div>

        {/* Readiness Pill Shortcut */}
        <Link
          href="/career-readiness"
          className="flex items-center gap-1.5 bg-purple-50 dark:bg-purple-950/40 text-purple-700 dark:text-purple-300 border border-purple-200/80 dark:border-purple-800/60 px-3 py-1.5 rounded-full text-xs font-semibold hover:bg-purple-100 dark:hover:bg-purple-900/40 transition-colors"
        >
          <Sparkles className="w-3.5 h-3.5 text-purple-600 dark:text-purple-400" />
          <span>Readiness Hub</span>
        </Link>

        {/* Notification Bell */}
        <div className="relative">
          <button
            onClick={() => {
              setShowNotifications(!showNotifications);
              setShowUserMenu(false);
            }}
            className="relative p-2 text-slate-500 hover:text-slate-800 dark:hover:text-slate-200 rounded-xl hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
            aria-label="Notifications"
          >
            <Bell className="w-5 h-5" />
            <span className="absolute top-1.5 right-1.5 w-2 h-2 rounded-full bg-brand-600 ring-2 ring-white dark:ring-slate-900" />
          </button>

          {/* Notifications Popover */}
          {showNotifications && (
            <div className="absolute right-0 mt-2 w-80 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-modal p-4 z-50 text-xs">
              <div className="flex items-center justify-between pb-2 border-b border-slate-100 dark:border-slate-800 font-bold text-slate-900 dark:text-white">
                <span>Recent Updates</span>
                <span className="text-[10px] text-brand-600 dark:text-brand-400 font-medium">All caught up</span>
              </div>
              <div className="py-2 space-y-2">
                <div className="p-2.5 rounded-xl bg-purple-50/70 dark:bg-purple-950/30 border border-purple-100 dark:border-purple-900/40">
                  <div className="font-semibold text-purple-900 dark:text-purple-300">
                    AI Career Discovery
                  </div>
                  <p className="text-slate-600 dark:text-slate-400 mt-0.5">
                    Complete your onboarding conversation to calibrate your skill baseline.
                  </p>
                </div>
                <div className="p-2.5 rounded-xl bg-emerald-50/70 dark:bg-emerald-950/30 border border-emerald-100 dark:border-emerald-900/40">
                  <div className="font-semibold text-emerald-900 dark:text-emerald-300">
                    Diagnostic Benchmarks
                  </div>
                  <p className="text-slate-600 dark:text-slate-400 mt-0.5">
                    Assessments available to verify proficiency in system architecture and backend foundations.
                  </p>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* User Profile Avatar & Dropdown */}
        <div className="relative">
          <button
            onClick={() => {
              setShowUserMenu(!showUserMenu);
              setShowNotifications(false);
            }}
            className="flex items-center gap-2 p-0.5 rounded-full hover:ring-2 hover:ring-brand-500/30 transition-all"
            aria-label="User menu"
          >
            <div className="h-8 w-8 rounded-full bg-gradient-to-tr from-brand-600 to-indigo-600 text-white flex items-center justify-center font-bold text-xs shadow-sm">
              {initials}
            </div>
          </button>

          {showUserMenu && (
            <div className="absolute right-0 mt-2 w-56 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-modal p-2 z-50 text-xs">
              <div className="px-3 py-2.5 border-b border-slate-100 dark:border-slate-800">
                <p className="font-semibold text-slate-900 dark:text-white truncate">{displayName}</p>
                <p className="text-slate-400 text-[11px] truncate">{displayEmail}</p>
              </div>
              <div className="py-1">
                <Link
                  href="/career-profile"
                  onClick={() => setShowUserMenu(false)}
                  className="flex items-center gap-2 px-3 py-2 text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-xl transition-colors"
                >
                  <User className="w-4 h-4 text-slate-400" />
                  <span>Edit Profile</span>
                </Link>
                <Link
                  href="/settings"
                  onClick={() => setShowUserMenu(false)}
                  className="flex items-center gap-2 px-3 py-2 text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-xl transition-colors"
                >
                  <Shield className="w-4 h-4 text-slate-400" />
                  <span>Privacy & Security</span>
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
                  className="w-full flex items-center gap-2 px-3 py-2 text-rose-600 hover:bg-rose-50 dark:hover:bg-rose-950/30 rounded-xl text-left disabled:opacity-50 transition-colors"
                >
                  <LogOut className="w-4 h-4 text-rose-500" />
                  <span>{isLoggingOut ? 'Signing out...' : 'Sign Out'}</span>
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
