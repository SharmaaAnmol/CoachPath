'use client';

import * as React from 'react';
import { RoadmapData, RoadmapProgressData, RoadmapTaskItem } from '@/types';
import { Card } from '@/components/ui/card';
import { ProgressBar } from '@/components/ui/progress-bar';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  CheckCircle2,
  Clock,
  ArrowRight,
  Sparkles,
  Target,
  Award,
} from 'lucide-react';

interface RoadmapProgressSummaryProps {
  roadmap: RoadmapData;
  progress: RoadmapProgressData | null;
  onSelectTask?: (task: RoadmapTaskItem) => void;
}

export function RoadmapProgressSummary({
  roadmap,
  progress,
  onSelectTask,
}: RoadmapProgressSummaryProps) {
  const completedTasks = roadmap.completed_tasks;
  const totalTasks = roadmap.total_tasks;
  const progressPct = roadmap.progress_percentage;

  const completedHours = progress?.completed_hours ?? 0;
  const remainingHours = progress?.remaining_hours ?? (roadmap.total_estimated_hours - completedHours);
  const weeksRemaining = progress?.estimated_weeks_remaining ?? (Math.ceil(remainingHours / Math.max(1, roadmap.weekly_hours)));

  // Next recommended task
  const nextTask = progress?.next_recommended_tasks?.[0] || null;

  return (
    <Card className="p-5 bg-gradient-to-br from-slate-900 via-slate-900 to-slate-950 text-white border-slate-800 shadow-xl space-y-5">
      {/* Top: Progress and Metrics */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <span className="text-xs font-mono font-bold uppercase tracking-wider text-brand-400">
              Curriculum Execution
            </span>
            <span className="text-slate-500">&bull;</span>
            <span className="text-xs text-slate-300">
              {progress?.current_phase_title || 'In Progress'}
            </span>
          </div>
          <h3 className="text-xl font-bold tracking-tight">Overall Progress: {progressPct}%</h3>
        </div>

        {/* Big numbers */}
        <div className="flex items-center gap-4 text-xs">
          <div className="border-l border-slate-800 pl-3 space-y-0.5">
            <span className="text-slate-400 block text-[10px] uppercase font-bold tracking-wider">Milestones</span>
            <span className="text-base font-mono font-bold text-white">
              {completedTasks} <span className="text-xs text-slate-500 font-normal">/ {totalTasks}</span>
            </span>
          </div>

          <div className="border-l border-slate-800 pl-3 space-y-0.5">
            <span className="text-slate-400 block text-[10px] uppercase font-bold tracking-wider">Hours Completed</span>
            <span className="text-base font-mono font-bold text-emerald-400">
              {completedHours} <span className="text-xs text-slate-500 font-normal">hrs</span>
            </span>
          </div>

          <div className="border-l border-slate-800 pl-3 space-y-0.5">
            <span className="text-slate-400 block text-[10px] uppercase font-bold tracking-wider">Est. Weeks Left</span>
            <span className="text-base font-mono font-bold text-brand-300">
              ~{weeksRemaining} <span className="text-xs text-slate-500 font-normal">wks</span>
            </span>
          </div>
        </div>
      </div>

      {/* Progress Bar */}
      <div className="space-y-1">
        <ProgressBar value={progressPct} variant="brand" size="md" className="bg-slate-800" />
        <div className="flex justify-between text-[11px] text-slate-400 font-mono">
          <span>{completedTasks} completed</span>
          <span>{totalTasks - completedTasks} remaining</span>
        </div>
      </div>

      {/* Next Recommended Milestone Callout */}
      {nextTask && (
        <div className="p-3.5 rounded-xl bg-slate-800/80 border border-slate-700/80 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs">
          <div className="flex items-start gap-2.5">
            <div className="w-7 h-7 rounded-lg bg-brand-500/20 text-brand-400 border border-brand-500/30 flex items-center justify-center shrink-0 mt-0.5">
              <Target className="w-4 h-4" />
            </div>
            <div className="space-y-0.5">
              <div className="flex items-center gap-2">
                <span className="text-[10px] font-bold uppercase tracking-wider text-brand-300">
                  Next Priority Action
                </span>
                <Badge variant="default" size="sm" className="bg-slate-700 text-slate-200 text-[10px]">
                  {nextTask.priority.toUpperCase()}
                </Badge>
                <span className="text-slate-400 text-[11px]">&bull; {nextTask.estimated_hours} hrs</span>
              </div>
              <p className="font-semibold text-white text-xs">{nextTask.title}</p>
            </div>
          </div>

          {onSelectTask && (
            <Button
              size="sm"
              variant="outline"
              className="text-xs border-slate-600 text-white hover:bg-slate-700 self-end sm:self-auto shrink-0"
              onClick={() => onSelectTask(nextTask)}
            >
              Focus Task <ArrowRight className="w-3.5 h-3.5 ml-1.5" />
            </Button>
          )}
        </div>
      )}
    </Card>
  );
}
