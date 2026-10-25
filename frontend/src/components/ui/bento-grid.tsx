import * as React from 'react';
import { cn } from '@/lib/utils';

export interface BentoGridProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
}

export function BentoGrid({ className, children, ...props }: BentoGridProps) {
  return (
    <div
      className={cn('grid grid-cols-1 md:grid-cols-3 gap-5 w-full', className)}
      {...props}
    >
      {children}
    </div>
  );
}

export interface BentoCardProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
  colSpan?: 1 | 2 | 3;
  rowSpan?: 1 | 2;
  gradient?: boolean;
}

export function BentoCard({
  className,
  children,
  colSpan = 1,
  rowSpan = 1,
  gradient = false,
  ...props
}: BentoCardProps) {
  const colSpanClasses = {
    1: 'md:col-span-1',
    2: 'md:col-span-2',
    3: 'md:col-span-3',
  };

  const rowSpanClasses = {
    1: 'row-span-1',
    2: 'row-span-2',
  };

  return (
    <div
      className={cn(
        'group relative rounded-2xl border border-slate-200/80 bg-white p-6 text-slate-900 shadow-card transition-all duration-300 hover:border-slate-300 hover:shadow-elevated dark:border-slate-800/80 dark:bg-slate-900/90 dark:text-slate-100 dark:hover:border-slate-700 overflow-hidden flex flex-col justify-between',
        colSpanClasses[colSpan],
        rowSpanClasses[rowSpan],
        gradient && 'bg-gradient-to-br from-white via-slate-50/50 to-indigo-50/20 dark:from-slate-900 dark:via-slate-900 dark:to-indigo-950/20',
        className
      )}
      {...props}
    >
      {/* Subtle border illumination on hover */}
      <div className="pointer-events-none absolute -inset-px rounded-2xl opacity-0 transition-opacity duration-300 group-hover:opacity-100 bg-gradient-to-r from-brand-500/10 via-purple-500/10 to-transparent" />
      <div className="relative z-10 w-full flex-1 flex flex-col">{children}</div>
    </div>
  );
}
