'use client';

import * as React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  Briefcase, ClipboardCheck, Compass, Cpu, FileText, Gauge, Kanban, LayoutDashboard,
  Menu, MessageSquareCode, Settings, Sparkles, User, Users, X,
} from 'lucide-react';
import { LightField } from '@/components/glass';
import { cn } from '@/lib/utils';

// Same groups and labels as components/layout/sidebar.tsx; only the look changes.
const groups = [
  { name: 'Foundation', items: [
    { title: 'Dashboard', href: '/design-system/samples/dashboard', icon: LayoutDashboard },
    { title: 'AI Onboarding', href: '#', icon: Sparkles },
    { title: 'Career Profile', href: '#', icon: User },
    { title: 'Skill Gap Analysis', href: '#', icon: Cpu },
    { title: 'Assessments', href: '#', icon: ClipboardCheck },
  ] },
  { name: 'Execution & Growth', items: [
    { title: 'Milestone Roadmap', href: '#', icon: Compass },
    { title: 'Job Matching', href: '/design-system/samples/jobs', icon: Briefcase },
    { title: 'Resume Optimizer', href: '/design-system/samples/resume', icon: FileText },
    { title: 'Applications', href: '#', icon: Kanban },
  ] },
  { name: 'Outreach & Readiness', items: [
    { title: 'Recruiters', href: '#', icon: Users },
    { title: 'Interview Prep', href: '#', icon: MessageSquareCode },
    { title: 'Career Readiness', href: '#', icon: Gauge },
  ] },
  { name: 'System', items: [{ title: 'Settings', href: '#', icon: Settings }] },
];

function Nav({ onNavigate }: { onNavigate?: () => void }) {
  const path = usePathname();
  return (
    <nav aria-label="App" className="flex flex-col gap-6">
      {groups.map((g) => (
        <div key={g.name}>
          <p className="px-3 pb-2 text-[11px] font-medium uppercase tracking-[0.12em] text-ink-dim">{g.name}</p>
          <ul className="flex flex-col gap-0.5">
            {g.items.map(({ title, href, icon: Icon }) => {
              const active = href === path;
              return (
                <li key={title}>
                  <Link
                    href={href}
                    onClick={onNavigate}
                    aria-current={active ? 'page' : undefined}
                    className={cn(
                      'flex h-10 items-center gap-3 rounded-xl px-3 text-sm transition-colors duration-200',
                      active ? 'bg-lav/[0.14] text-ink-fg shadow-[inset_0_0_0_1px_rgba(196,181,253,.28)]' : 'text-ink-muted hover:bg-white/5 hover:text-ink-fg'
                    )}
                  >
                    <Icon className={cn('h-4 w-4', active ? 'text-lav' : 'text-ink-dim')} aria-hidden />
                    {title}
                  </Link>
                </li>
              );
            })}
          </ul>
        </div>
      ))}
    </nav>
  );
}

function Brand() {
  return (
    <span className="flex items-center gap-2.5 font-display text-[17px] font-semibold tracking-[-0.02em] text-ink-fg">
      <span className="grid h-7 w-7 place-items-center rounded-lg bg-gradient-to-b from-lav-light to-lav text-[13px] font-bold text-lav-ink">C</span>
      CoachPath
    </span>
  );
}

export function SampleShell({ children }: { children: React.ReactNode }) {
  const [open, setOpen] = React.useState(false);
  return (
    <div className="cp-dark relative min-h-screen shrink-0 overflow-x-clip">
      <LightField tone="violet" className="left-[18%] top-[-8%] h-[420px] w-[680px]" />
      <LightField tone="lavender" className="right-[-6%] top-[40%] h-[360px] w-[420px]" />
      <LightField tone="lime" className="left-[40%] bottom-[4%] h-[200px] w-[280px]" />

      {/* Phone bar */}
      <header className="sticky top-0 z-30 flex h-14 items-center justify-between border-b border-white/10 bg-black/70 px-4 backdrop-blur-xl lg:hidden">
        <Brand />
        <button type="button" onClick={() => setOpen(true)} aria-label="Open menu" className="grid h-11 w-11 place-items-center rounded-full text-ink-fg hover:bg-white/5">
          <Menu className="h-5 w-5" aria-hidden />
        </button>
      </header>
      {open && (
        <div className="fixed inset-0 z-40 overflow-y-auto bg-black/95 p-4 backdrop-blur-xl lg:hidden" role="dialog" aria-modal="true" aria-label="Menu">
          <div className="mb-6 flex items-center justify-between">
            <Brand />
            <button type="button" onClick={() => setOpen(false)} aria-label="Close menu" className="grid h-11 w-11 place-items-center rounded-full text-ink-fg hover:bg-white/5">
              <X className="h-5 w-5" aria-hidden />
            </button>
          </div>
          <Nav onNavigate={() => setOpen(false)} />
        </div>
      )}

      {/* Desktop rail */}
      <div className="relative lg:flex lg:gap-6 lg:p-3">
      <aside className="sticky top-3 z-20 hidden h-[calc(100dvh-24px)] w-[248px] shrink-0 flex-col gap-8 overflow-y-auto rounded-glass border border-white/10 bg-ink-900/70 p-4 backdrop-blur-xl lg:flex">
        <div className="px-3 pt-2"><Brand /></div>
        <Nav />
        <div className="mt-auto flex items-center gap-3 rounded-xl border border-white/10 bg-white/[0.03] p-3">
          <span className="grid h-8 w-8 place-items-center rounded-full bg-lav/15 text-xs font-semibold text-lav">PS</span>
          <span className="min-w-0">
            <span className="block truncate text-sm text-ink-fg">Priya Sharma</span>
            <span className="block truncate text-xs text-ink-dim">Backend Engineer track</span>
          </span>
        </div>
      </aside>

      <main className="relative mx-auto w-full min-w-0 max-w-[1040px] px-4 pb-16 pt-6 sm:px-6 lg:px-4 lg:pt-7">{children}</main>
      </div>
    </div>
  );
}
