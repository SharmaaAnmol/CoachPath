'use client';

import * as React from 'react';
import { Badge } from '@/components/ui/badge';
import { ProgressBar } from '@/components/ui/progress-bar';
import { CheckCircle2, Circle, Sparkles, ChevronDown, ChevronUp } from 'lucide-react';
import { cn } from '@/lib/utils';

export interface OnboardingProgressProps {
  areasCovered: string[];
  areasRemaining: string[];
  turnCount: number;
  maxTurns?: number;
  currentCategory?: string | null;
  readyToSummarize?: boolean;
  className?: string;
}

const CATEGORY_LABELS: Record<string, string> = {
  target_role: 'Target Role',
  career_stage: 'Career Stage',
  education: 'Education',
  skills: 'Existing Skills',
  technologies: 'Technologies & Tools',
  projects: 'Projects',
  experience: 'Work Experience',
  learning_time: 'Weekly Bandwidth',
  learning_resources: 'Learning Resources',
  timeline: 'Target Timeline',
  industries: 'Industries',
  companies: 'Companies of Interest',
  salary: 'Salary Range',
  goals: 'Career Goals',
  preferences: 'Work Preferences',
};

const ALL_AREAS = [
  'target_role',
  'career_stage',
  'education',
  'skills',
  'technologies',
  'projects',
  'experience',
  'learning_time',
  'learning_resources',
  'timeline',
  'industries',
  'companies',
  'salary',
  'goals',
  'preferences',
];

export function OnboardingProgress({
  areasCovered,
  turnCount,
  maxTurns = 20,
  currentCategory,
  readyToSummarize = false,
  className,
}: OnboardingProgressProps) {
  const [isExpanded, setIsExpanded] = React.useState(false);

  const coveredSet = React.useMemo(() => new Set(areasCovered), [areasCovered]);
  const totalAreas = ALL_AREAS.length;
  const coveredCount = coveredSet.size;
  const progressPercent = Math.min(Math.round((coveredCount / totalAreas) * 100), 100);

  const currentCategoryLabel = currentCategory ? (CATEGORY_LABELS[currentCategory] || currentCategory) : null;

  return (
    <div
      className={cn(
        'rounded-xl border border-slate-200/90 dark:border-slate-800 bg-white dark:bg-slate-900 p-4 shadow-sm transition-all',
        className
      )}
    >
      <div className="flex flex-col gap-3">
        {/* Top Header Row */}
        <div className="flex items-center justify-between gap-2 flex-wrap">
          <div className="flex items-center gap-2">
            <div className="h-7 w-7 rounded-lg bg-purple-100 dark:bg-purple-950/60 text-purple-600 dark:text-purple-400 flex items-center justify-center">
              <Sparkles className="w-4 h-4" />
            </div>
            <div>
              <span className="text-xs font-bold tracking-tight text-slate-900 dark:text-white uppercase">
                Profile Discovery Progress
              </span>
              <span className="text-xs text-slate-500 dark:text-slate-400 ml-2">
                Turn {turnCount} / ~{maxTurns}
              </span>
            </div>
          </div>

          <div className="flex items-center gap-2">
            {readyToSummarize ? (
              <Badge variant="verified" size="sm">
                <CheckCircle2 className="w-3 h-3 mr-1" /> Ready for Summary
              </Badge>
            ) : currentCategoryLabel ? (
              <Badge variant="intelligence" size="sm">
                Topic: {currentCategoryLabel}
              </Badge>
            ) : null}

            <button
              type="button"
              onClick={() => setIsExpanded(!isExpanded)}
              className="text-xs text-slate-500 hover:text-slate-800 dark:hover:text-slate-200 flex items-center gap-1 py-1 px-1.5 rounded-md hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
              aria-label="Toggle all topics breakdown"
            >
              <span>{coveredCount}/{totalAreas} Topics</span>
              {isExpanded ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
            </button>
          </div>
        </div>

        {/* Progress Bar */}
        <div className="space-y-1">
          <ProgressBar
            value={progressPercent}
            variant={readyToSummarize ? 'verified' : 'intelligence'}
            size="sm"
          />
          <div className="flex justify-between items-center text-[11px] text-slate-500 dark:text-slate-400">
            <span>{coveredCount} of {totalAreas} discovery areas covered</span>
            <span className="font-semibold text-slate-700 dark:text-slate-300">{progressPercent}%</span>
          </div>
        </div>

        {/* Expandable Topic Checklist */}
        {isExpanded && (
          <div className="pt-3 border-t border-slate-100 dark:border-slate-800 grid grid-cols-2 sm:grid-cols-3 gap-2">
            {ALL_AREAS.map((areaKey) => {
              const isCovered = coveredSet.has(areaKey);
              const isCurrent = currentCategory === areaKey;
              const label = CATEGORY_LABELS[areaKey] || areaKey;

              return (
                <div
                  key={areaKey}
                  className={cn(
                    'flex items-center gap-2 px-2.5 py-1.5 rounded-lg text-xs transition-colors',
                    isCurrent
                      ? 'bg-purple-50 dark:bg-purple-950/40 text-purple-700 dark:text-purple-300 font-medium border border-purple-200/60 dark:border-purple-800'
                      : isCovered
                      ? 'bg-slate-50 dark:bg-slate-800/60 text-slate-700 dark:text-slate-300'
                      : 'text-slate-400 dark:text-slate-500'
                  )}
                >
                  {isCovered ? (
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500 shrink-0" />
                  ) : (
                    <Circle className="w-3.5 h-3.5 text-slate-300 dark:text-slate-600 shrink-0" />
                  )}
                  <span className="truncate">{label}</span>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
