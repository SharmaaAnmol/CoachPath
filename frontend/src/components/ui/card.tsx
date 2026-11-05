import * as React from 'react';
import { cn } from '@/lib/utils';

export interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  hoverable?: boolean;
  glass?: boolean;
}

export function Card({ className, hoverable = false, glass = false, ...props }: CardProps) {
  return (
    <div
      className={cn(
        'rounded-2xl border border-slate-200/80 bg-white text-slate-900 shadow-card transition-all duration-200 dark:rounded-[1.25rem] dark:border-white/10 dark:bg-white/[0.04] dark:text-ink-fg dark:shadow-none dark:backdrop-blur-xl',
        glass && 'glass-panel border-white/40 dark:border-white/10 shadow-elevated',
        hoverable && 'hover:border-slate-300 dark:hover:border-white/15 hover:shadow-elevated hover:-translate-y-0.5',
        className
      )}
      {...props}
    />
  );
}

export function CardHeader({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return <div className={cn('flex flex-col space-y-1.5 p-5 md:p-6', className)} {...props} />;
}

export function CardTitle({ className, ...props }: React.HTMLAttributes<HTMLHeadingElement>) {
  return <h3 className={cn('text-lg font-semibold leading-none tracking-tight dark:font-display dark:tracking-[-0.02em] text-slate-900 dark:text-white', className)} {...props} />;
}

export function CardDescription({ className, ...props }: React.HTMLAttributes<HTMLParagraphElement>) {
  return <p className={cn('text-sm text-slate-500 dark:text-ink-muted', className)} {...props} />;
}

export function CardContent({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return <div className={cn('p-5 pt-0 md:p-6 md:pt-0', className)} {...props} />;
}

export function CardFooter({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return <div className={cn('flex items-center p-5 pt-0 md:p-6 md:pt-0 border-t border-slate-100 dark:border-white/10 mt-4', className)} {...props} />;
}
