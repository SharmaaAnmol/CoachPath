'use client';

import * as React from 'react';
import { RoadmapPhaseItem, RoadmapTaskItem } from '@/types';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { ProgressBar } from '@/components/ui/progress-bar';
import { RoadmapTaskCard } from './RoadmapTaskCard';
import {
  CheckCircle2,
  ChevronDown,
  ChevronUp,
  Clock,
  Sparkles,
  Layers,
  Flag,
} from 'lucide-react';

interface RoadmapPhaseCardProps {
  phase: RoadmapPhaseItem;
  allTaskMap: Map<string, RoadmapTaskItem>;
  onStatusChange: (taskId: string, status: 'pending' | 'in_progress' | 'completed' | 'skipped') => Promise<void>;
  onSubmitDeliverable: (task: RoadmapTaskItem) => void;
  focusedTaskId?: string | null;
}

export function RoadmapPhaseCard({
  phase,
  allTaskMap,
  onStatusChange,
  onSubmitDeliverable,
  focusedTaskId,
}: RoadmapPhaseCardProps) {
  // Phase starts open if it contains the focused task or is in_progress, else true by default
  const [isOpen, setIsOpen] = React.useState(true);

  const completedCount = phase.tasks.filter((t) => t.status === 'completed' || t.status === 'skipped').length;
  const totalCount = phase.tasks.length;
  const phaseProgressPct = totalCount > 0 ? Math.round((completedCount / totalCount) * 100) : 0;
  const isPhaseCompleted = phase.is_completed || phase.status === 'completed';

  return (
    <div className="space-y-3">
      {/* Phase Header Banner */}
      <Card
        className={`p-4 sm:p-5 border cursor-pointer select-none transition-all ${
          isPhaseCompleted
            ? 'bg-emerald-950/15 border-emerald-800/60 dark:bg-emerald-950/20'
            : phase.status === 'in_progress'
            ? 'bg-slate-900 text-white border-slate-700 shadow-lg'
            : 'bg-white dark:bg-slate-900 border-slate-200 dark:border-slate-800'
        }`}
        onClick={() => setIsOpen(!isOpen)}
      >
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="space-y-1.5 flex-1">
            <div className="flex flex-wrap items-center gap-2">
              <span
                className={`font-mono text-xs px-2.5 py-0.5 rounded-full font-bold border ${
                  phase.status === 'in_progress'
                    ? 'bg-brand-500/30 text-brand-300 border-brand-500/40'
                    : isPhaseCompleted
                    ? 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30'
                    : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 border-slate-200 dark:border-slate-700'
                }`}
              >
                Phase {phase.order_index}
              </span>

              <Badge
                variant={
                  isPhaseCompleted ? 'verified' : phase.status === 'in_progress' ? 'action' : 'outline'
                }
                size="sm"
              >
                {isPhaseCompleted ? 'Completed' : phase.status === 'in_progress' ? 'Active Focus' : 'Upcoming'}
              </Badge>

              <span
                className={`text-xs ${
                  phase.status === 'in_progress' ? 'text-slate-400' : 'text-slate-500 dark:text-slate-400'
                }`}
              >
                &bull; {phase.estimated_hours} hrs total
              </span>
            </div>

            <h3
              className={`text-base font-bold ${
                phase.status === 'in_progress' ? 'text-white' : 'text-slate-900 dark:text-white'
              }`}
            >
              {phase.title}
            </h3>

            {phase.objective && (
              <p
                className={`text-xs leading-relaxed max-w-2xl ${
                  phase.status === 'in_progress' ? 'text-slate-300' : 'text-slate-600 dark:text-slate-300'
                }`}
              >
                {phase.objective}
              </p>
            )}
          </div>

          {/* Right: Phase Progress Gauge & Toggle */}
          <div className="flex items-center gap-4 sm:gap-6 self-end sm:self-center shrink-0">
            <div className="w-36 space-y-1">
              <div className="flex justify-between text-[11px] font-mono">
                <span className={phase.status === 'in_progress' ? 'text-slate-400' : 'text-slate-500'}>
                  {completedCount}/{totalCount} tasks
                </span>
                <span
                  className={`font-bold ${
                    phase.status === 'in_progress' ? 'text-brand-300' : 'text-slate-900 dark:text-white'
                  }`}
                >
                  {phaseProgressPct}%
                </span>
              </div>
              <ProgressBar
                value={phaseProgressPct}
                variant={isPhaseCompleted ? 'verified' : 'brand'}
                size="sm"
                className={phase.status === 'in_progress' ? 'bg-slate-800' : ''}
              />
            </div>

            <div className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200">
              {isOpen ? <ChevronUp className="w-5 h-5" /> : <ChevronDown className="w-5 h-5" />}
            </div>
          </div>
        </div>
      </Card>

      {/* Task List */}
      {isOpen && (
        <div className="space-y-3 pl-2 sm:pl-4 border-l-2 border-slate-200 dark:border-slate-800 ml-2 sm:ml-4">
          {phase.tasks.map((task) => (
            <RoadmapTaskCard
              key={task.id}
              task={task}
              allTaskMap={allTaskMap}
              onStatusChange={onStatusChange}
              onSubmitDeliverable={onSubmitDeliverable}
              isFocused={focusedTaskId === task.id}
            />
          ))}
        </div>
      )}
    </div>
  );
}
