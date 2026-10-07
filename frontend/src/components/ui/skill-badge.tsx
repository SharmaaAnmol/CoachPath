import * as React from 'react';
import { cn } from '@/lib/utils';
import { SkillItem } from '@/types';
import { CheckCircle2, Clock, AlertCircle } from 'lucide-react';

export interface SkillBadgeProps {
  skill: SkillItem;
  showConfidence?: boolean;
  showEvidence?: boolean;
  className?: string;
  onClick?: () => void;
}

export function SkillBadge({
  skill,
  showConfidence = true,
  showEvidence = false,
  className,
  onClick,
}: SkillBadgeProps) {
  const statusStyles = {
    verified: {
      container:
        'bg-emerald-50/80 border-emerald-200/90 text-emerald-800 dark:bg-emerald-950/30 dark:border-emerald-800 dark:text-emerald-300',
      icon: <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 dark:text-emerald-400 shrink-0" />,
      tag: 'Verified',
      bar: 'bg-emerald-500',
    },
    developing: {
      container:
        'bg-amber-50/80 border-amber-200/90 text-amber-800 dark:bg-amber-950/30 dark:border-amber-800 dark:text-amber-300',
      icon: <Clock className="w-3.5 h-3.5 text-amber-600 dark:text-amber-400 shrink-0" />,
      tag: 'Developing',
      bar: 'bg-amber-500',
    },
    missing: {
      container:
        'bg-rose-50/80 border-rose-200/90 text-rose-800 dark:bg-rose-950/30 dark:border-rose-800 dark:text-rose-300',
      icon: <AlertCircle className="w-3.5 h-3.5 text-rose-600 dark:text-rose-400 shrink-0" />,
      tag: 'Skill Gap',
      bar: 'bg-rose-500',
    },
  };

  const current = statusStyles[skill.status];

  return (
    <div
      onClick={onClick}
      className={cn(
        'inline-flex items-center gap-2 rounded-lg border px-3 py-1.5 text-xs font-medium transition-all shadow-subtle',
        current.container,
        onClick && 'cursor-pointer hover:shadow hover:scale-[1.02]',
        className
      )}
    >
      {current.icon}
      <span className="font-semibold text-slate-900 dark:text-white">{skill.name}</span>

      {showConfidence && (
        <span className="ml-1 text-[11px] font-mono text-slate-500 dark:text-slate-400">
          {skill.confidenceScore}%
        </span>
      )}

      {showEvidence && (
        <span className="ml-1 rounded px-1.5 py-0.5 text-[10px] bg-white/70 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-300">
          {skill.evidenceSource}
        </span>
      )}
    </div>
  );
}
