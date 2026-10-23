'use client';

import * as React from 'react';
import Link from 'next/link';
import { RoadmapTaskItem } from '@/types';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import {
  CheckCircle2,
  Clock,
  Circle,
  FileCheck,
  ExternalLink,
  Lock,
  Sparkles,
  ArrowRight,
  BookOpen,
  FolderGit2,
  Check,
} from 'lucide-react';

interface RoadmapTaskCardProps {
  task: RoadmapTaskItem;
  allTaskMap?: Map<string, RoadmapTaskItem>;
  onStatusChange: (taskId: string, status: 'pending' | 'in_progress' | 'completed' | 'skipped') => Promise<void>;
  onSubmitDeliverable: (task: RoadmapTaskItem) => void;
  isFocused?: boolean;
}

export function RoadmapTaskCard({
  task,
  allTaskMap,
  onStatusChange,
  onSubmitDeliverable,
  isFocused = false,
}: RoadmapTaskCardProps) {
  const isDone = task.status === 'completed';
  const isInProgress = task.status === 'in_progress';

  // Check if any prerequisite tasks are pending
  const pendingPrereqs: RoadmapTaskItem[] = [];
  if (task.prerequisite_task_ids && allTaskMap) {
    for (const prereqId of task.prerequisite_task_ids) {
      const pTask = allTaskMap.get(prereqId);
      if (pTask && pTask.status !== 'completed' && pTask.status !== 'skipped') {
        pendingPrereqs.push(pTask);
      }
    }
  }
  const isBlocked = pendingPrereqs.length > 0 && !isDone;

  return (
    <Card
      id={`task-${task.id}`}
      className={`p-4 sm:p-5 transition-all text-xs space-y-3.5 ${
        isDone
          ? 'border-emerald-200/90 bg-emerald-50/20 dark:bg-emerald-950/10'
          : isInProgress
          ? 'border-brand-300 dark:border-brand-800 bg-brand-50/15 dark:bg-brand-950/15 shadow-sm'
          : 'border-slate-200 dark:border-slate-800 hover:border-slate-300 dark:hover:border-slate-700'
      } ${isFocused ? 'ring-2 ring-brand-500 shadow-md' : ''}`}
    >
      {/* Top row: Checkbox, Title, Badges, Hours */}
      <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-3">
        <div className="flex items-start gap-2.5 flex-1">
          {/* Status Toggle Button */}
          <button
            type="button"
            onClick={() => {
              if (isDone) {
                onStatusChange(task.id, 'in_progress');
              } else if (task.deliverable_requirement && !task.submission_url) {
                onSubmitDeliverable(task);
              } else {
                onStatusChange(task.id, 'completed');
              }
            }}
            className="mt-0.5 text-slate-400 hover:text-emerald-600 transition-colors shrink-0"
            title={isDone ? 'Mark in progress' : 'Complete task'}
          >
            {isDone ? (
              <CheckCircle2 className="w-5 h-5 text-emerald-600 fill-emerald-100 dark:fill-emerald-950" />
            ) : isInProgress ? (
              <Clock className="w-5 h-5 text-brand-600 animate-pulse" />
            ) : (
              <Circle className="w-5 h-5 text-slate-300 dark:text-slate-600 hover:text-brand-500" />
            )}
          </button>

          <div className="space-y-1 flex-1">
            <div className="flex flex-wrap items-center gap-2">
              <h4
                className={`text-sm font-bold tracking-tight ${
                  isDone ? 'text-slate-500 dark:text-slate-400 line-through' : 'text-slate-900 dark:text-white'
                }`}
              >
                {task.title}
              </h4>

              {/* Priority Badge */}
              <Badge
                variant={
                  task.priority === 'critical'
                    ? 'gap'
                    : task.priority === 'high'
                    ? 'action'
                    : 'default'
                }
                size="sm"
                className="text-[10px]"
              >
                {task.priority.toUpperCase()}
              </Badge>

              {/* Task Type Badge */}
              <Badge variant="outline" size="sm" className="text-[10px] capitalize">
                {task.task_type}
              </Badge>

              {/* Skill Badge */}
              {task.skill_name && (
                <span className="font-mono text-[10px] px-2 py-0.5 rounded bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 font-semibold border border-slate-200 dark:border-slate-700">
                  {task.skill_name}
                </span>
              )}

              <span className="text-[11px] text-slate-400 font-mono">&bull; {task.estimated_hours} hrs</span>
            </div>

            {/* Description */}
            <p className="text-slate-600 dark:text-slate-300 leading-relaxed text-xs">
              {task.description}
            </p>

            {/* Learning Objective */}
            {task.learning_objective && (
              <p className="text-[11px] text-slate-500 dark:text-slate-400 italic">
                <span className="font-semibold text-slate-700 dark:text-slate-300 not-italic">Objective:</span> {task.learning_objective}
              </p>
            )}
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center sm:flex-col items-end gap-2 shrink-0 pl-7 sm:pl-0">
          {!isDone ? (
            <>
              {isInProgress ? (
                <Button
                  size="sm"
                  variant="primary"
                  className="text-xs h-7 px-3 bg-emerald-600 hover:bg-emerald-700"
                  onClick={() => {
                    if (task.deliverable_requirement && !task.submission_url) {
                      onSubmitDeliverable(task);
                    } else {
                      onStatusChange(task.id, 'completed');
                    }
                  }}
                >
                  <Check className="w-3.5 h-3.5 mr-1" /> Complete
                </Button>
              ) : (
                <Button
                  size="sm"
                  variant="outline"
                  className="text-xs h-7 px-3"
                  onClick={() => onStatusChange(task.id, 'in_progress')}
                >
                  Start Task
                </Button>
              )}

              {task.deliverable_requirement && (
                <Button
                  size="sm"
                  variant="ghost"
                  className="text-xs h-7 px-2.5 text-purple-600 dark:text-purple-400 hover:bg-purple-50 dark:hover:bg-purple-950/30"
                  onClick={() => onSubmitDeliverable(task)}
                >
                  <FolderGit2 className="w-3.5 h-3.5 mr-1" />
                  {task.submission_url ? 'Update Proof' : 'Submit Proof'}
                </Button>
              )}
            </>
          ) : (
            <div className="flex items-center gap-1.5">
              <Button
                size="sm"
                variant="ghost"
                className="text-xs h-7 text-slate-400 hover:text-slate-600"
                onClick={() => onStatusChange(task.id, 'in_progress')}
              >
                Reopen
              </Button>
              {task.deliverable_requirement && (
                <Button
                  size="sm"
                  variant="outline"
                  className="text-xs h-7 px-2.5 text-purple-600 dark:text-purple-400"
                  onClick={() => onSubmitDeliverable(task)}
                >
                  {task.submission_url ? 'Proof URL' : 'Add Proof'}
                </Button>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Blocked by Prerequisites Alert */}
      {isBlocked && (
        <div className="p-2.5 rounded-lg bg-amber-50/70 dark:bg-amber-950/20 border border-amber-200/80 dark:border-amber-800/60 flex items-start gap-2 text-amber-800 dark:text-amber-300 text-[11px]">
          <Lock className="w-3.5 h-3.5 shrink-0 text-amber-600 mt-0.5" />
          <div className="space-y-0.5">
            <span className="font-semibold">Prerequisites Incomplete:</span>
            <p className="text-amber-700 dark:text-amber-400">
              For best pedagogical sequencing, complete earlier milestone(s) first:{' '}
              <span className="font-semibold">{pendingPrereqs.map((p) => p.title).join(', ')}</span>.
            </p>
          </div>
        </div>
      )}

      {/* Deliverable Requirement & Submitted Proof Link */}
      {task.deliverable_requirement && (
        <div className="p-3 rounded-lg bg-slate-50 dark:bg-slate-800/60 border border-slate-200/80 dark:border-slate-700/60 space-y-1.5 text-xs">
          <div className="flex items-center justify-between gap-2">
            <div className="flex items-center gap-1.5 font-bold text-slate-700 dark:text-slate-300 text-[11px]">
              <FileCheck className="w-3.5 h-3.5 text-purple-600 shrink-0" />
              <span>Verifiable Deliverable Requirement:</span>
            </div>
            {task.completion_criteria && (
              <span className="text-[10px] text-slate-400 italic">Criteria: {task.completion_criteria}</span>
            )}
          </div>
          <p className="text-[11px] text-slate-600 dark:text-slate-400 leading-relaxed pl-5">
            {task.deliverable_requirement}
          </p>

          {task.submission_url && (
            <div className="pl-5 pt-1 flex items-center gap-1.5 text-[11px]">
              <span className="font-semibold text-emerald-600 dark:text-emerald-400 flex items-center gap-1">
                <Check className="w-3 h-3" /> Submitted Proof:
              </span>
              <a
                href={task.submission_url}
                target="_blank"
                rel="noopener noreferrer"
                className="font-mono text-brand-600 dark:text-brand-400 hover:underline flex items-center gap-1 truncate max-w-sm"
              >
                {task.submission_url} <ExternalLink className="w-3 h-3 shrink-0" />
              </a>
            </div>
          )}
        </div>
      )}

      {/* Curated Educational Resources */}
      {task.resource_urls && task.resource_urls.length > 0 && (
        <div className="flex flex-wrap items-center gap-2 pt-1 border-t border-slate-100 dark:border-slate-800 text-[11px]">
          <span className="text-slate-400 font-semibold flex items-center gap-1">
            <BookOpen className="w-3 h-3 text-slate-500" /> Curated Resources:
          </span>
          {task.resource_urls.map((res, idx) => (
            <a
              key={idx}
              href={res.url}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1 px-2 py-0.5 rounded bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-brand-600 dark:text-brand-400 font-medium transition-colors"
            >
              <ExternalLink className="w-2.5 h-2.5" />
              <span>{res.title}</span>
              <span className="text-[9px] text-slate-400 uppercase">({res.type})</span>
            </a>
          ))}
        </div>
      )}
    </Card>
  );
}
