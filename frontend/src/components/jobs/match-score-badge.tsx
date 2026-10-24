'use client';

import * as React from 'react';
import { cn } from '@/lib/utils';
import { Sparkles, AlertCircle, Info } from 'lucide-react';

export interface MatchScoreBadgeProps {
  score: number;
  isProvisional?: boolean;
  size?: 'sm' | 'md' | 'lg';
  showLabel?: boolean;
  className?: string;
}

export function MatchScoreBadge({
  score,
  isProvisional = false,
  size = 'md',
  showLabel = true,
  className,
}: MatchScoreBadgeProps) {
  const rounded = Math.round(score);

  const getTier = (s: number) => {
    if (s >= 80) {
      return {
        label: 'Strong Fit',
        classes:
          'bg-emerald-50 text-emerald-700 border-emerald-200/90 dark:bg-emerald-950/40 dark:text-emerald-300 dark:border-emerald-800',
        ring: 'ring-emerald-500/20',
      };
    } else if (s >= 60) {
      return {
        label: 'Good Fit',
        classes:
          'bg-sky-50 text-sky-700 border-sky-200/90 dark:bg-sky-950/40 dark:text-sky-300 dark:border-sky-800',
        ring: 'ring-sky-500/20',
      };
    } else if (s >= 40) {
      return {
        label: 'Moderate Fit',
        classes:
          'bg-amber-50 text-amber-800 border-amber-200/90 dark:bg-amber-950/40 dark:text-amber-300 dark:border-amber-800',
        ring: 'ring-amber-500/20',
      };
    } else {
      return {
        label: 'Developing',
        classes:
          'bg-slate-100 text-slate-700 border-slate-200 dark:bg-slate-800 dark:text-slate-300 dark:border-slate-700',
        ring: 'ring-slate-500/20',
      };
    }
  };

  const tier = getTier(rounded);

  const sizeClasses = {
    sm: 'text-xs px-2 py-0.5 gap-1',
    md: 'text-xs sm:text-sm px-2.5 py-1 gap-1.5',
    lg: 'text-sm sm:text-base px-3.5 py-1.5 gap-2 font-bold',
  };

  return (
    <div className={cn('inline-flex items-center gap-1.5', className)}>
      <span
        title="Deterministic match score calculated from verified skill evidence, experience, and preferences. Does not represent hiring probability."
        className={cn(
          'inline-flex items-center font-semibold rounded-full border shadow-xs transition-colors',
          sizeClasses[size],
          tier.classes,
          tier.ring
        )}
      >
        <Sparkles className={cn(size === 'sm' ? 'w-3 h-3' : 'w-3.5 h-3.5', 'shrink-0')} />
        <span>{rounded}%</span>
        {showLabel && (
          <span className="font-normal opacity-90 hidden xs:inline">• {tier.label}</span>
        )}
      </span>

      {isProvisional && (
        <span
          title="Provisional Match: Calculated with limited underlying evidence (<40% data coverage). Complete diagnostic assessments to increase score precision."
          className="inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-[10px] font-medium bg-amber-100/80 text-amber-900 border border-amber-300/60 dark:bg-amber-950/50 dark:text-amber-300 dark:border-amber-800"
        >
          <AlertCircle className="w-2.5 h-2.5 text-amber-700 dark:text-amber-400 shrink-0" />
          Provisional
        </span>
      )}
    </div>
  );
}
