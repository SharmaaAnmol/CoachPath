import * as React from 'react';
import { cn } from '@/lib/utils';

export interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: 'default' | 'verified' | 'intelligence' | 'action' | 'gap' | 'secondary' | 'outline' | 'brand';
  size?: 'sm' | 'md';
}

export function Badge({ className, variant = 'default', size = 'md', children, ...props }: BadgeProps) {
  const baseStyles = 'inline-flex items-center font-medium rounded-full';

  const variants = {
    default: 'bg-slate-100 text-slate-700 dark:bg-white/[0.07] dark:text-ink-fg/80',
    brand: 'bg-indigo-50 text-indigo-700 border border-indigo-200/80 dark:bg-lav/10 dark:text-lav-light dark:border-lav/30',
    verified: 'bg-emerald-50 text-emerald-700 border border-emerald-200/80 dark:bg-lime/10 dark:text-lime-soft dark:border-lime/30',
    intelligence: 'bg-purple-50 text-purple-700 border border-purple-200/80 dark:bg-lav/10 dark:text-lav-light dark:border-lav/30',
    action: 'bg-amber-50 text-amber-800 border border-amber-200/80 dark:bg-amber-950/40 dark:text-amber-300 dark:border-amber-800',
    gap: 'bg-rose-50 text-rose-700 border border-rose-200/80 dark:bg-crimson/10 dark:text-crimson-tint dark:border-crimson/30',
    secondary: 'bg-slate-200 text-slate-800 dark:bg-white/10 dark:text-ink-fg',
    outline: 'border border-slate-300 text-slate-600 bg-transparent dark:border-white/15 dark:text-ink-muted',
  };

  const sizes = {
    sm: 'text-[11px] px-2 py-0.5 gap-1',
    md: 'text-xs px-2.5 py-1 gap-1.5',
  };

  return (
    <span className={cn(baseStyles, variants[variant], sizes[size], className)} {...props}>
      {children}
    </span>
  );
}
