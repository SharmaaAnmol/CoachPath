'use client';

import * as React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';
import {
  LayoutDashboard,
  User,
  Cpu,
  ClipboardCheck,
  Compass,
  Briefcase,
  FileText,
  Kanban,
  Users,
  MessageSquareCode,
  Gauge,
  Settings,
  ChevronLeft,
  ChevronRight,
  Sparkles,
  X,
} from 'lucide-react';
import { useAuth } from '@/hooks/use-auth';

interface NavItem {
  title: string;
  href: string;
  icon: React.ComponentType<{ className?: string }>;
  badge?: string | number;
}

interface NavGroup {
  groupName: string;
  items: NavItem[];
}

const navGroups: NavGroup[] = [
  {
    groupName: 'Foundation',
    items: [
      { title: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
      { title: 'AI Onboarding', href: '/onboarding', icon: Sparkles },
      { title: 'Career Profile', href: '/career-profile', icon: User },
      { title: 'Skill Gap Analysis', href: '/skills', icon: Cpu },
      { title: 'Assessments', href: '/assessments', icon: ClipboardCheck },
    ],
  },
  {
    groupName: 'Execution & Growth',
    items: [
      { title: 'Milestone Roadmap', href: '/roadmap', icon: Compass },
      { title: 'Job Matching', href: '/jobs', icon: Briefcase },
      { title: 'Resume Optimizer', href: '/resume', icon: FileText },
      { title: 'Applications', href: '/applications', icon: Kanban },
    ],
  },
  {
    groupName: 'Outreach & Readiness',
    items: [
      { title: 'Recruiters', href: '/recruiters', icon: Users },
      { title: 'Interview Prep', href: '/interviews', icon: MessageSquareCode },
      { title: 'Career Readiness', href: '/career-readiness', icon: Gauge },
    ],
  },
  {
    groupName: 'System',
    items: [{ title: 'Settings', href: '/settings', icon: Settings }],
  },
];

export interface SidebarProps {
  isMobileOpen?: boolean;
  onMobileClose?: () => void;
}

export function Sidebar({ isMobileOpen = false, onMobileClose }: SidebarProps) {
  const pathname = usePathname();
  const { user } = useAuth();
  const [isCollapsed, setIsCollapsed] = React.useState(false);

  const displayName = user?.full_name || 'Candidate';
  const initials = React.useMemo(() => {
    if (!displayName) return 'CP';
    const parts = displayName.trim().split(/\s+/);
    if (parts.length >= 2) {
      return `${parts[0][0]}${parts[1][0]}`.toUpperCase();
    }
    return displayName.slice(0, 2).toUpperCase();
  }, [displayName]);

  const isActive = (href: string) => {
    if (href === '/career-profile' && pathname === '/profile') return true;
    if (href === '/career-readiness' && pathname === '/readiness') return true;
    return pathname === href || pathname?.startsWith(href + '/');
  };

  const navContent = (
    <div className="flex h-full flex-col select-none overflow-hidden rounded-glass border border-white/10 bg-ink-900/70 text-ink-muted backdrop-blur-xl">
      {/* Platform logo */}
      <div className="flex h-16 items-center justify-between px-4">
        <Link href="/dashboard" className="flex items-center gap-2.5 rounded-lg">
          <span className="grid h-8 w-8 shrink-0 place-items-center rounded-lg bg-gradient-to-b from-lav-light to-lav text-sm font-bold text-lav-ink">
            C
          </span>
          {!isCollapsed && (
            <span className="font-display text-[17px] font-semibold tracking-[-0.02em] text-ink-fg">CoachPath</span>
          )}
        </Link>

        {onMobileClose && (
          <button
            onClick={onMobileClose}
            className="grid h-11 w-11 place-items-center rounded-full text-ink-muted transition-colors hover:bg-white/5 hover:text-ink-fg md:hidden"
            aria-label="Close menu"
          >
            <X className="h-5 w-5" />
          </button>
        )}
      </div>

      {/* Nav groups */}
      <nav aria-label="App" className="flex-1 space-y-5 overflow-y-auto px-3 py-2">
        {navGroups.map((group) => (
          <div key={group.groupName}>
            {!isCollapsed && (
              <p className="px-3 pb-2 text-[11px] font-medium uppercase tracking-[0.12em] text-ink-dim">
                {group.groupName}
              </p>
            )}
            <ul className="space-y-0.5">
              {group.items.map((item) => {
                const active = isActive(item.href);
                const Icon = item.icon;
                return (
                  <li key={item.href}>
                    <Link
                      href={item.href}
                      onClick={onMobileClose}
                      aria-current={active ? 'page' : undefined}
                      className={cn(
                        'flex h-9 items-center gap-3 rounded-xl px-3 text-sm transition-colors duration-200',
                        isCollapsed && 'justify-center px-0',
                        active
                          ? 'bg-lav/[0.14] text-ink-fg shadow-[inset_0_0_0_1px_rgba(196,181,253,.28)]'
                          : 'hover:bg-white/5 hover:text-ink-fg'
                      )}
                      title={isCollapsed ? item.title : undefined}
                    >
                      <Icon className={cn('h-4 w-4 shrink-0', active ? 'text-lav' : 'text-ink-dim')} />
                      {!isCollapsed && (
                        <>
                          <span className="flex-1 truncate">{item.title}</span>
                          {item.badge && (
                            <span className="rounded-full bg-white/10 px-2 py-0.5 text-[11px] text-ink-fg">{item.badge}</span>
                          )}
                        </>
                      )}
                    </Link>
                  </li>
                );
              })}
            </ul>
          </div>
        ))}
      </nav>

      {/* Candidate profile */}
      <div className="p-3">
        <Link
          href="/career-profile"
          className="flex items-center gap-3 rounded-xl border border-white/10 bg-white/[0.03] p-2.5 transition-colors hover:bg-white/[0.06]"
        >
          <span className="grid h-8 w-8 shrink-0 place-items-center rounded-full bg-lav/15 text-xs font-semibold text-lav">
            {initials}
          </span>
          {!isCollapsed && (
            <span className="min-w-0 flex-1">
              <span className="block truncate text-sm text-ink-fg">{displayName}</span>
              <span className="block truncate text-xs text-ink-dim">Career profile</span>
            </span>
          )}
        </Link>

        <div className="hidden justify-end pt-2 md:flex">
          <button
            onClick={() => setIsCollapsed(!isCollapsed)}
            className="grid h-9 w-9 place-items-center rounded-full text-ink-dim transition-colors hover:bg-white/5 hover:text-ink-fg"
            aria-label={isCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
          >
            {isCollapsed ? <ChevronRight className="h-4 w-4" /> : <ChevronLeft className="h-4 w-4" />}
          </button>
        </div>
      </div>
    </div>
  );

  return (
    <>
      {/* Desktop: floating glass rail, sticky so it never covers content */}
      <aside className="hidden shrink-0 py-3 pl-3 md:block">
        <div
          className={cn(
            'sticky top-3 h-[calc(100dvh-24px)] transition-[width] duration-300 ease-out-expo',
            isCollapsed ? 'w-[76px]' : 'w-64'
          )}
        >
          {navContent}
        </div>
      </aside>

      {/* Mobile drawer */}
      {isMobileOpen && (
        <div className="fixed inset-0 z-50 md:hidden" role="dialog" aria-modal="true" aria-label="Menu">
          <div className="fixed inset-0 bg-black/80 backdrop-blur-sm" onClick={onMobileClose} />
          <div className="fixed inset-y-2 left-2 z-50 w-72 animate-in slide-in-from-left duration-200">{navContent}</div>
        </div>
      )}
    </>
  );
}
