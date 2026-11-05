import * as React from 'react';
import { cn } from '@/lib/utils';

export type ChipTone = 'neutral' | 'active' | 'done' | 'alert';

const tones: Record<ChipTone, { chip: string; dot: string }> = {
  neutral: { chip: 'border-white/15 text-ink-muted', dot: 'bg-ink-dim' },
  active: { chip: 'border-lav/40 bg-lav/10 text-lav', dot: 'bg-lav' },
  done: { chip: 'border-lime/40 bg-lime/10 text-lime', dot: 'bg-lime' },
  alert: { chip: 'border-crimson/40 bg-crimson/10 text-crimson-soft', dot: 'bg-crimson' },
};

export interface StatusChipProps extends React.HTMLAttributes<HTMLSpanElement> {
  tone?: ChipTone;
  /** Show the coloured dot. The label always carries the meaning too, so colour is never the only signal. */
  dot?: boolean;
}

export function StatusChip({ tone = 'neutral', dot = true, className, children, ...props }: StatusChipProps) {
  const t = tones[tone];
  return (
    <span
      className={cn(
        'inline-flex h-7 items-center gap-2 rounded-full border px-3 text-xs font-medium transition-colors duration-200',
        t.chip,
        className
      )}
      {...props}
    >
      {dot && <span className={cn('h-1.5 w-1.5 rounded-full', t.dot)} aria-hidden />}
      {children}
    </span>
  );
}
