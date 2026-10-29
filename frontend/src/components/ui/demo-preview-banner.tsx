import * as React from 'react';
import { FlaskConical } from 'lucide-react';
import { cn } from '@/lib/utils';

export interface DemoPreviewBannerProps extends React.HTMLAttributes<HTMLDivElement> {
  plannedPhase?: string;
  featureName?: string;
}

export function DemoPreviewBanner({
  plannedPhase,
  featureName,
  className,
  ...props
}: DemoPreviewBannerProps) {
  return (
    <div
      role="status"
      aria-label="Demonstration preview notice"
      className={cn(
        'rounded-xl border border-amber-200/90 bg-amber-50/80 px-4 py-3 text-xs text-amber-900 shadow-sm dark:border-amber-800/60 dark:bg-amber-950/30 dark:text-amber-200',
        'flex flex-col sm:flex-row sm:items-center gap-2.5',
        className
      )}
      {...props}
    >
      <div className="flex items-center gap-2 shrink-0">
        <span className="flex h-6 w-6 items-center justify-center rounded-lg bg-amber-200/70 text-amber-800 dark:bg-amber-900/60 dark:text-amber-300">
          <FlaskConical className="h-3.5 w-3.5" aria-hidden="true" />
        </span>
        <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-bold uppercase tracking-wider bg-amber-200/80 text-amber-900 dark:bg-amber-900/80 dark:text-amber-100">
          Demo Preview
        </span>
      </div>
      <p className="flex-1 leading-relaxed text-amber-950/90 dark:text-amber-200/90">
        <strong>Demo Preview</strong> — This screen currently uses demonstration data and is not connected to your real records.
        {plannedPhase && (
          <span className="ml-1 text-amber-900/80 dark:text-amber-300/80">
            {featureName ? `${featureName} is` : 'Live functionality is'} scheduled for {plannedPhase}.
          </span>
        )}
      </p>
    </div>
  );
}
