import * as React from 'react';
import { cn } from '@/lib/utils';

export interface AIThinkingProps {
  /** What the AI is doing right now, e.g. "Reading your resume". */
  label: string;
  /** Hint about the wait, e.g. "Usually 10–20 seconds". */
  hint?: string;
  className?: string;
}

/** Waiting state for the 5–20 s AI calls: typing dots plus a moving line. Reduced motion stops both (globals.css). */
export function AIThinking({ label, hint, className }: AIThinkingProps) {
  return (
    <div role="status" aria-live="polite" className={cn('flex flex-col gap-3', className)}>
      <div className="flex items-center gap-3 text-sm text-ink-fg">
        <span className="flex gap-1" aria-hidden>
          {[0, 150, 300].map((d) => (
            <span key={d} className="h-1.5 w-1.5 animate-think-dot rounded-full bg-lav" style={{ animationDelay: `${d}ms` }} />
          ))}
        </span>
        <span>{label}</span>
      </div>
      <div className="h-0.5 w-full overflow-hidden rounded-full bg-white/10" aria-hidden>
        <div className="h-full w-2/5 animate-think-line rounded-full bg-gradient-to-r from-transparent via-lav to-transparent" />
      </div>
      {hint && <p className="text-xs text-ink-dim">{hint}</p>}
    </div>
  );
}
