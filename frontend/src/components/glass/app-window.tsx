import * as React from 'react';
import { cn } from '@/lib/utils';
import { GlassPanel } from './glass-panel';

export interface AppWindowProps extends React.HTMLAttributes<HTMLDivElement> {
  /** Text in the window bar, e.g. "coachpath.app / tailoring". */
  title?: string;
}

/** A product window in glass: used to show real CoachPath screens on marketing pages. */
export function AppWindow({ title, className, children, ...props }: AppWindowProps) {
  return (
    <GlassPanel className={cn('overflow-hidden', className)} {...props}>
      <div className="flex h-11 items-center gap-2 border-b border-ink-line px-4 text-[13px] text-ink-dim">
        <span className="h-2.5 w-2.5 rounded-full bg-crimson" aria-hidden />
        <span className="h-2.5 w-2.5 rounded-full bg-white/15" aria-hidden />
        <span className="h-2.5 w-2.5 rounded-full bg-white/15" aria-hidden />
        {title && <span className="ml-3">{title}</span>}
      </div>
      {children}
    </GlassPanel>
  );
}
