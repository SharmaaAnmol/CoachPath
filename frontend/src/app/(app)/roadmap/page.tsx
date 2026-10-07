'use client';

import * as React from 'react';
import { mockRoadmapPhases } from '@/lib/mock/data';
import { RoadmapPhase, RoadmapTask } from '@/types';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { ProgressBar } from '@/components/ui/progress-bar';
import { Modal } from '@/components/ui/modal';
import {
  Compass,
  CheckCircle2,
  Clock,
  ExternalLink,
  RotateCcw,
  Sparkles,
  FileCheck,
  AlertCircle,
  Plus,
} from 'lucide-react';

export default function RoadmapPage() {
  const [phases, setPhases] = React.useState<RoadmapPhase[]>(mockRoadmapPhases);
  const [activeDeliverableTask, setActiveDeliverableTask] = React.useState<RoadmapTask | null>(null);
  const [deliverableUrl, setDeliverableUrl] = React.useState('');

  const toggleTaskStatus = (phaseId: string, taskId: string) => {
    setPhases((prev) =>
      prev.map((phase) => {
        if (phase.id !== phaseId) return phase;
        const updatedTasks: RoadmapTask[] = phase.tasks.map((task) => {
          if (task.id !== taskId) return task;
          const nextStatus: RoadmapTask['status'] = task.status === 'completed' ? 'in_progress' : 'completed';
          return { ...task, status: nextStatus };
        });
        const completedCount = updatedTasks.filter((t) => t.status === 'completed').length;
        const progressPercentage = Math.round((completedCount / updatedTasks.length) * 100);
        return { ...phase, tasks: updatedTasks, progressPercentage };
      })
    );
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-slate-900 dark:text-white">
            Dynamic Milestone Roadmap Planner
          </h2>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
            Personalized 9-week curriculum designed to close identified market gaps through verifiable deliverables.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Button
            size="sm"
            variant="outline"
            onClick={() => alert('Roadmap engine checked: Profile is already aligned with current market gaps.')}
          >
            <RotateCcw className="w-3.5 h-3.5 mr-1.5" /> Re-sync with Market
          </Button>
        </div>
      </div>

      {/* Phases Timeline */}
      <div className="space-y-8">
        {phases.map((phase) => (
          <div key={phase.id} className="space-y-4">
            {/* Phase Title Card */}
            <Card className="p-5 bg-slate-900 text-white border-slate-800 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <span className="font-mono text-xs px-2.5 py-0.5 rounded-full bg-brand-500/30 text-brand-300 border border-brand-500/40 font-bold">
                    Phase {phase.phaseNumber}
                  </span>
                  <span className="text-xs text-slate-400">{phase.timeline}</span>
                  <Badge
                    variant={
                      phase.status === 'in_progress'
                        ? 'action'
                        : phase.status === 'completed'
                        ? 'verified'
                        : 'outline'
                    }
                    size="sm"
                  >
                    {phase.status === 'in_progress'
                      ? 'In Progress'
                      : phase.status === 'completed'
                      ? 'Completed'
                      : 'Upcoming'}
                  </Badge>
                </div>
                <h3 className="text-lg font-bold">{phase.title}</h3>
              </div>

              <div className="w-full sm:w-48 space-y-1">
                <div className="flex justify-between text-xs text-slate-400">
                  <span>Milestone Completion</span>
                  <span className="font-mono font-bold text-white">{phase.progressPercentage}%</span>
                </div>
                <ProgressBar value={phase.progressPercentage} variant="brand" size="sm" />
              </div>
            </Card>

            {/* Phase Task Cards List */}
            <div className="space-y-3 pl-0 sm:pl-4 border-l-2 border-slate-200 dark:border-slate-800 space-y-3">
              {phase.tasks.map((task) => {
                const isDone = task.status === 'completed';
                return (
                  <Card
                    key={task.id}
                    className={`p-5 transition-all ${
                      isDone
                        ? 'border-emerald-200/80 bg-emerald-50/20 dark:bg-emerald-950/10'
                        : 'hover:border-slate-300'
                    }`}
                  >
                    <div className="flex flex-col md:flex-row md:items-start justify-between gap-4">
                      <div className="space-y-2 flex-1">
                        <div className="flex flex-wrap items-center gap-2">
                          <button
                            onClick={() => toggleTaskStatus(phase.id, task.id)}
                            className="text-slate-400 hover:text-emerald-600 transition-colors"
                            title="Toggle completed"
                          >
                            <CheckCircle2
                              className={`w-5 h-5 ${isDone ? 'text-emerald-600 fill-emerald-100 dark:fill-emerald-950' : 'text-slate-300'}`}
                            />
                          </button>
                          <h4
                            className={`text-sm font-bold ${
                              isDone ? 'line-through text-slate-500' : 'text-slate-900 dark:text-white'
                            }`}
                          >
                            {task.title}
                          </h4>
                          <Badge variant="default" size="sm">
                            {task.category}
                          </Badge>
                          <span className="text-xs text-slate-400">&bull; {task.estimatedHours} hrs</span>
                        </div>

                        <p className="text-xs text-slate-600 dark:text-slate-300 leading-relaxed pl-7">
                          {task.description}
                        </p>

                        {/* Deliverable Proof Callout */}
                        <div className="ml-7 p-3 rounded-lg bg-slate-50 dark:bg-slate-800/60 border border-slate-200/80 dark:border-slate-700/60 text-xs space-y-1">
                          <div className="flex items-center gap-1.5 font-semibold text-slate-700 dark:text-slate-300">
                            <FileCheck className="w-3.5 h-3.5 text-purple-600" />
                            <span>Verifiable Deliverable Required:</span>
                          </div>
                          <p className="text-slate-500 dark:text-slate-400">{task.deliverableRequired}</p>
                        </div>
                      </div>

                      <div className="flex flex-col sm:flex-row md:flex-col items-end gap-2 shrink-0 pl-7 md:pl-0">
                        <a
                          href={task.resourceUrl}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-xs font-semibold text-brand-600 hover:underline flex items-center gap-1"
                        >
                          <ExternalLink className="w-3 h-3" /> Resource Link
                        </a>

                        <div className="flex items-center gap-2 pt-1">
                          <Button
                            size="sm"
                            variant={isDone ? 'secondary' : 'outline'}
                            onClick={() => setActiveDeliverableTask(task)}
                          >
                            {isDone ? 'Update Evidence' : 'Submit Proof'}
                          </Button>
                          <Button
                            size="sm"
                            variant={isDone ? 'ghost' : 'primary'}
                            onClick={() => toggleTaskStatus(phase.id, task.id)}
                          >
                            {isDone ? 'Mark Incomplete' : 'Complete Task'}
                          </Button>
                        </div>
                      </div>
                    </div>
                  </Card>
                );
              })}
            </div>
          </div>
        ))}
      </div>

      {/* Deliverable Evidence Submission Modal */}
      {activeDeliverableTask && (
        <Modal
          isOpen={!!activeDeliverableTask}
          onClose={() => setActiveDeliverableTask(null)}
          title="Submit Verifiable Project Deliverable"
          description={`Task: ${activeDeliverableTask.title}`}
          footer={
            <div className="flex justify-end gap-2">
              <Button size="sm" variant="outline" onClick={() => setActiveDeliverableTask(null)}>
                Cancel
              </Button>
              <Button
                size="sm"
                variant="primary"
                onClick={() => {
                  alert('Deliverable URL saved! Verification pipeline initiated.');
                  setActiveDeliverableTask(null);
                }}
              >
                Submit for Verification
              </Button>
            </div>
          }
        >
          <div className="space-y-4 text-xs">
            <div className="p-3 rounded-lg bg-purple-50 dark:bg-purple-950/30 border border-purple-200 dark:border-purple-800 text-purple-900 dark:text-purple-300">
              <p className="font-semibold">Required Artifact Rubric:</p>
              <p className="mt-1 text-slate-600 dark:text-slate-400">{activeDeliverableTask.deliverableRequired}</p>
            </div>

            <div className="space-y-1.5">
              <label className="font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider text-[10px]">
                GitHub Repository or Live Demo URL
              </label>
              <input
                type="url"
                value={deliverableUrl}
                onChange={(e) => setDeliverableUrl(e.target.value)}
                placeholder="https://github.com/your-username/project-repo"
                className="w-full h-10 px-3 rounded-lg border border-slate-300 bg-white text-xs text-slate-900 focus:outline-none focus:ring-2 focus:ring-brand-500"
              />
              <p className="text-[11px] text-slate-400">
                Our verification auditor will parse code commits and automated tests to corroborate skill calibration.
              </p>
            </div>
          </div>
        </Modal>
      )}
    </div>
  );
}
