'use client';

import * as React from 'react';
import { cn } from '@/lib/utils';
import { ShieldCheck, Info } from 'lucide-react';

export interface MatchEvidenceCoverageProps {
  coverage: number;
  className?: string;
  showBar?: boolean;
  isProvisional?: boolean;
  size?: 'sm' | 'md';
}

export function MatchEvidenceCoverage({
  coverage,
  className,
  showBar = true,
  isProvisional,
  size = 'md',
}: MatchEvidenceCoverageProps) {
  const rounded = Math.min(100, Math.max(0, Math.round(coverage)));

  const getTier = (c: number) => {
    if (c >= 70) {
      return {
        label: 'High Confidence',
        color: 'text-emerald-600 dark:text-emerald-400',
        barColor: 'bg-emerald-500',
      };
    } else if (c >= 40) {
      return {
        label: 'Moderate Data',
        color: 'text-sky-600 dark:text-sky-400',
        barColor: 'bg-sky-500',
      };
    } else {
      return {
        label: 'Sparse Evidence',
        color: 'text-amber-600 dark:text-amber-400',
        barColor: 'bg-amber-500',
      };
    }
  };

  const tier = getTier(rounded);

  return (
    <div
      title="Evidence Coverage measures the completeness of evaluated data (skills extracted, completed diagnostic assessments, verified experience, and portfolio projects). It is distinct from hiring probability."
      className={cn('inline-flex flex-col gap-1', className)}
    >
      <div className="flex items-center gap-1.5 text-xs text-slate-500 dark:text-slate-400">
        <ShieldCheck className={cn('w-3.5 h-3.5', tier.color)} />
        <span>
          Evidence Coverage: <strong className="text-slate-800 dark:text-slate-200">{rounded}%</strong>
        </span>
        <span className="text-[11px] opacity-75">({tier.label})</span>
      </div>

      {showBar && (
        <div className="w-24 sm:w-28 h-1.5 rounded-full bg-slate-100 dark:bg-slate-800 overflow-hidden">
          <div
            className={cn('h-full rounded-full transition-all duration-300', tier.barColor)}
            style={{ width: `${rounded}%` }}
          />
        </div>
      )}
    </div>
  );
}
