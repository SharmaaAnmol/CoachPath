'use client';

import * as React from 'react';
import { RoadmapData } from '@/types';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import {
  Clock,
  Calendar,
  CheckCircle2,
  AlertTriangle,
  AlertOctagon,
  Sparkles,
  Zap,
} from 'lucide-react';

interface RoadmapScheduleBannerProps {
  roadmap: RoadmapData;
}

export function RoadmapScheduleBanner({ roadmap }: RoadmapScheduleBannerProps) {
  const isFeasible = roadmap.feasibility_status === 'feasible';
  const isDemanding = roadmap.feasibility_status === 'demanding';

  const formattedTargetDate = roadmap.target_completion_date
    ? new Date(roadmap.target_completion_date).toLocaleDateString(undefined, {
        month: 'short',
        day: 'numeric',
        year: 'numeric',
      })
    : null;

  return (
    <Card
      className={`p-4 border transition-colors ${
        isFeasible
          ? 'bg-emerald-50/40 dark:bg-emerald-950/20 border-emerald-200/80 dark:border-emerald-800/60'
          : isDemanding
          ? 'bg-amber-50/40 dark:bg-amber-950/20 border-amber-200/80 dark:border-amber-800/60'
          : 'bg-rose-50/40 dark:bg-rose-950/20 border-rose-200/80 dark:border-rose-800/60'
      }`}
    >
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
        {/* Left: Status & Narrative */}
        <div className="space-y-1.5 flex-1">
          <div className="flex flex-wrap items-center gap-2">
            <span
              className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-bold uppercase tracking-wider ${
                isFeasible
                  ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900/60 dark:text-emerald-300'
                  : isDemanding
                  ? 'bg-amber-100 text-amber-800 dark:bg-amber-900/60 dark:text-amber-300'
                  : 'bg-rose-100 text-rose-800 dark:bg-rose-900/60 dark:text-rose-300'
              }`}
            >
              {isFeasible ? (
                <>
                  <CheckCircle2 className="w-3.5 h-3.5" /> Feasible Timeline
                </>
              ) : isDemanding ? (
                <>
                  <AlertTriangle className="w-3.5 h-3.5" /> Demanding Schedule
                </>
              ) : (
                <>
                  <AlertOctagon className="w-3.5 h-3.5" /> Timeline Adjustment Needed
                </>
              )}
            </span>

            <span className="text-xs text-slate-400">&bull;</span>
            <span className="text-xs text-slate-500 dark:text-slate-400 font-medium">
              Curriculum Engine: {roadmap.generation_mode === 'deterministic_ai' ? 'Deterministic + Gemini Personalization' : 'Deterministic Rule Engine'}
            </span>
          </div>

          <p className="text-xs text-slate-700 dark:text-slate-300 leading-relaxed">
            {roadmap.feasibility_note ||
              `Target workload: ${roadmap.total_estimated_hours} total hours planned at ${roadmap.weekly_hours} hours/week.`}
          </p>
        </div>

        {/* Right: Metric Pills */}
        <div className="flex flex-wrap items-center gap-2 lg:gap-3 shrink-0">
          <div className="px-3 py-2 rounded-lg bg-white/80 dark:bg-slate-900/80 border border-slate-200/70 dark:border-slate-800 text-center min-w-[90px]">
            <span className="block text-[10px] font-bold text-slate-400 uppercase tracking-wider">Total Effort</span>
            <span className="text-sm font-mono font-bold text-slate-900 dark:text-white">
              {roadmap.total_estimated_hours} <span className="text-[10px] text-slate-400 font-normal">hrs</span>
            </span>
          </div>

          <div className="px-3 py-2 rounded-lg bg-white/80 dark:bg-slate-900/80 border border-slate-200/70 dark:border-slate-800 text-center min-w-[90px]">
            <span className="block text-[10px] font-bold text-slate-400 uppercase tracking-wider">Weekly Pace</span>
            <span className="text-sm font-mono font-bold text-brand-600 dark:text-brand-400">
              {roadmap.weekly_hours} <span className="text-[10px] text-slate-400 font-normal">hrs/wk</span>
            </span>
          </div>

          {formattedTargetDate && (
            <div className="px-3 py-2 rounded-lg bg-white/80 dark:bg-slate-900/80 border border-slate-200/70 dark:border-slate-800 text-center min-w-[110px]">
              <span className="block text-[10px] font-bold text-slate-400 uppercase tracking-wider">Target Date</span>
              <span className="text-xs font-mono font-bold text-slate-900 dark:text-white">
                {formattedTargetDate}
              </span>
            </div>
          )}
        </div>
      </div>
    </Card>
  );
}
