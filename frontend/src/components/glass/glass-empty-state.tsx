import * as React from 'react';
import { cn } from '@/lib/utils';
import { GlassPanel } from './glass-panel';

export interface GlassEmptyStateProps {
  icon?: React.ReactNode;
  title: string;
  description: string;
  /** Usually one GlassButton that starts the missing step. */
  action?: React.ReactNode;
  className?: string;
}

export function GlassEmptyState({ icon, title, description, action, className }: GlassEmptyStateProps) {
  return (
    <GlassPanel className={cn('flex flex-col items-center px-8 py-12 text-center', className)}>
      {icon && (
        <div className="mb-5 grid h-12 w-12 place-items-center rounded-2xl bg-lav/10 text-lav" aria-hidden>
          {icon}
        </div>
      )}
      <h3 className="font-display text-lg font-semibold tracking-[-0.02em] text-ink-fg">{title}</h3>
      <p className="mt-2 max-w-sm text-sm leading-relaxed text-ink-muted">{description}</p>
      {action && <div className="mt-6">{action}</div>}
    </GlassPanel>
  );
}
