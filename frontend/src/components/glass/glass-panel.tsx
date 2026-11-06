'use client';

import * as React from 'react';
import { cn } from '@/lib/utils';

export interface GlassPanelProps extends React.HTMLAttributes<HTMLDivElement> {
  /** Lift 2px on hover; use for panels that are links or open something. */
  interactive?: boolean;
}

/** Liquid-glass surface. Tracks the pointer so the highlight follows it (see .liquid-glass in globals.css). */
export const GlassPanel = React.forwardRef<HTMLDivElement, GlassPanelProps>(
  ({ className, interactive = false, onPointerMove, ...props }, ref) => (
    <div
      ref={ref}
      onPointerMove={(e) => {
        const r = e.currentTarget.getBoundingClientRect();
        e.currentTarget.style.setProperty('--mx', `${e.clientX - r.left}px`);
        e.currentTarget.style.setProperty('--my', `${e.clientY - r.top}px`);
        onPointerMove?.(e);
      }}
      className={cn(
        'liquid-glass rounded-glass text-ink-fg',
        interactive && 'transition-transform duration-200 ease-out-expo hover:-translate-y-0.5',
        className
      )}
      {...props}
    />
  )
);
GlassPanel.displayName = 'GlassPanel';
