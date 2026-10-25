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
    <div className="flex flex-col h-full bg-slate-950 text-slate-300 border-r border-slate-800/80 select-none">
      {/* Platform Logo */}
      <div className="flex items-center justify-between px-5 h-16 border-b border-slate-800/80">
        <Link href="/dashboard" className="flex items-center gap-2.5">
          <div className="h-9 w-9 rounded-xl bg-gradient-to-tr from-brand-600 to-purple-500 flex items-center justify-center text-white shadow-glow">
            <Sparkles className="h-5 w-5" />
          </div>
          {!isCollapsed && (
            <div className="flex flex-col">
              <span className="font-bold text-white text-base tracking-tight leading-none">CoachPath</span>
              <span className="text-[10px] text-purple-400 font-mono tracking-wider uppercase mt-1">
                Career Intelligence
              </span>
            </div>
          )}
        </Link>

        {/* Mobile Close Button */}
        {onMobileClose && (
          <button
            onClick={onMobileClose}
            className="md:hidden text-slate-400 hover:text-white p-1.5 rounded-lg hover:bg-slate-800 transition-colors"
            aria-label="Close menu"
          >
            <X className="w-5 h-5" />
          </button>
        )}
      </div>

      {/* Nav Groups */}
      <div className="flex-1 overflow-y-auto px-3 py-4 space-y-6">
        {navGroups.map((group) => (
          <div key={group.groupName} className="space-y-1">
            {!isCollapsed && (
              <h4 className="px-3 text-[10px] font-bold uppercase tracking-wider text-slate-500">
                {group.groupName}
              </h4>
            )}
            {group.items.map((item) => {
              const active = isActive(item.href);
              const Icon = item.icon;
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  onClick={onMobileClose}
                  className={cn(
                    'group flex items-center gap-3 rounded-xl px-3 py-2 text-xs font-medium transition-all duration-150',
                    active
                      ? 'bg-gradient-to-r from-brand-600 to-indigo-600 text-white shadow-glow'
                      : 'text-slate-400 hover:bg-slate-900 hover:text-slate-100'
                  )}
                  title={isCollapsed ? item.title : undefined}
                >
                  <Icon
                    className={cn(
                      'h-4 w-4 shrink-0 transition-transform duration-150 group-hover:scale-110',
                      active ? 'text-white' : 'text-slate-400 group-hover:text-slate-200'
                    )}
                  />
                  {!isCollapsed && (
                    <>
                      <span className="flex-1 truncate">{item.title}</span>
                      {item.badge && (
                        <span
                          className={cn(
                            'rounded-full px-2 py-0.5 text-[10px] font-bold',
                            active
                              ? 'bg-white/20 text-white'
                              : 'bg-slate-800 text-slate-400 group-hover:bg-slate-700'
                          )}
                        >
                          {item.badge}
                        </span>
                      )}
                    </>
                  )}
                </Link>
              );
            })}
          </div>
        ))}
      </div>

      {/* Candidate Profile Widget at Bottom */}
      <div className="p-3 border-t border-slate-800/80 bg-slate-950/80">
        <Link
          href="/career-profile"
          className="flex items-center gap-3 p-2 rounded-xl hover:bg-slate-900 transition-colors"
        >
          <div className="h-9 w-9 rounded-full bg-brand-600/30 border border-brand-500/50 flex items-center justify-center text-white font-bold text-xs shrink-0">
            {initials}
          </div>
          {!isCollapsed && (
            <div className="flex-1 min-w-0">
              <div className="text-xs font-semibold text-white truncate">{displayName}</div>
              <div className="text-[10px] text-slate-400 truncate">Candidate Profile</div>
            </div>
          )}
        </Link>

        {/* Desktop Collapse Toggle */}
        <div className="hidden md:flex justify-end pt-2">
          <button
            onClick={() => setIsCollapsed(!isCollapsed)}
            className="p-1.5 rounded-lg text-slate-500 hover:text-slate-300 hover:bg-slate-900 transition-colors"
            title={isCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
            aria-label={isCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
          >
            {isCollapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
          </button>
        </div>
      </div>
    </div>
  );

  return (
    <>
      {/* Desktop Sidebar */}
      <aside
        className={cn(
          'hidden md:block shrink-0 transition-all duration-300 ease-in-out',
          isCollapsed ? 'w-20' : 'w-64'
        )}
      >
        <div className={cn('fixed top-0 bottom-0 left-0 z-30 transition-all duration-300', isCollapsed ? 'w-20' : 'w-64')}>
          {navContent}
        </div>
      </aside>

      {/* Mobile Drawer */}
      {isMobileOpen && (
        <div className="fixed inset-0 z-50 md:hidden">
          <div
            className="fixed inset-0 bg-slate-950/80 backdrop-blur-sm"
            onClick={onMobileClose}
          />
          <div className="fixed top-0 bottom-0 left-0 w-72 z-50 animate-in slide-in-from-left duration-200">
            {navContent}
          </div>
        </div>
      )}
    </>
  );
}
