import * as React from 'react';
import { cn } from '@/lib/utils';

export interface PageHeaderProps {
  title: string;
  description?: string;
  actions?: React.ReactNode;
  className?: string;
}

/** Top of every redesigned app page: one heading, one line of context, actions on the right. */
export function PageHeader({ title, description, actions, className }: PageHeaderProps) {
  return (
    <header className={cn('flex flex-wrap items-end justify-between gap-6', className)}>
      <div className="min-w-0">
        <h1 className="font-display text-3xl font-semibold tracking-[-0.035em] text-ink-fg [text-wrap:balance] md:text-4xl">
          {title}
        </h1>
        {description && <p className="mt-2 max-w-[60ch] text-[15px] leading-relaxed text-ink-muted">{description}</p>}
      </div>
      {actions && <div className="flex flex-wrap items-center gap-3">{actions}</div>}
    </header>
  );
}
