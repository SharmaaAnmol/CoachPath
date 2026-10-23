'use client';

import * as React from 'react';
import Link from 'next/link';
import {
  RoadmapData,
  RoadmapProgressData,
  RoadmapTaskItem,
  TargetRoleDetail,
  SkillGapAnalysisData,
} from '@/types';
import { roadmapClient } from '@/lib/roadmap-client';
import { skillGapClient } from '@/lib/skill-gap-client';
import { profileClient } from '@/lib/profile-client';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Skeleton } from '@/components/ui/skeleton';
import { Alert } from '@/components/ui/alert';
import { RoadmapHeader } from '@/components/roadmap/RoadmapHeader';
import { RoadmapScheduleBanner } from '@/components/roadmap/RoadmapScheduleBanner';
import { RoadmapProgressSummary } from '@/components/roadmap/RoadmapProgressSummary';
import { RoadmapPhaseList } from '@/components/roadmap/RoadmapPhaseList';
import { RoadmapEmptyState } from '@/components/roadmap/RoadmapEmptyState';
import { DeliverableModal } from '@/components/roadmap/DeliverableModal';
import { RegenerateRoadmapModal } from '@/components/roadmap/RegenerateRoadmapModal';
import {
  Compass,
  CheckCircle2,
  AlertCircle,
  Loader2,
  RotateCcw,
} from 'lucide-react';

export default function RoadmapPage() {
  // Core Roadmap State
  const [roadmap, setRoadmap] = React.useState<RoadmapData | null>(null);
  const [progress, setProgress] = React.useState<RoadmapProgressData | null>(null);

  // Fallback / Prerequisite State (if roadmap does not exist yet)
  const [targetRole, setTargetRole] = React.useState<TargetRoleDetail | null>(null);
  const [gapAnalysis, setGapAnalysis] = React.useState<SkillGapAnalysisData | null>(null);

  // UI / Async State
  const [isLoading, setIsLoading] = React.useState<boolean>(true);
  const [isGenerating, setIsGenerating] = React.useState<boolean>(false);
  const [isAdapting, setIsAdapting] = React.useState<boolean>(false);
  const [errorMessage, setErrorMessage] = React.useState<string | null>(null);
  const [successToast, setSuccessToast] = React.useState<string | null>(null);
  const [focusedTaskId, setFocusedTaskId] = React.useState<string | null>(null);

  // Modal States
  const [deliverableTask, setDeliverableTask] = React.useState<RoadmapTaskItem | null>(null);
  const [isRegenerateModalOpen, setIsRegenerateModalOpen] = React.useState<boolean>(false);

  const showToast = (message: string) => {
    setSuccessToast(message);
    setTimeout(() => {
      setSuccessToast(null);
    }, 4000);
  };

  // Fetch active roadmap and real-time progress
  const loadRoadmap = React.useCallback(async () => {
    try {
      setIsLoading(true);
      setErrorMessage(null);

      // 1. Try to fetch active roadmap
      let activeRoadmap: RoadmapData | null = null;
      try {
        activeRoadmap = await roadmapClient.getActiveRoadmap();
      } catch (err: any) {
        // If 404 (or no active roadmap), catch and prepare empty state
        if (err?.status !== 404 && err?.status_code !== 404 && !err?.message?.includes('404')) {
          // Log other errors if critical, but still check prerequisites
          console.warn('Roadmap fetch note:', err?.message);
        }
      }

      if (activeRoadmap) {
        setRoadmap(activeRoadmap);
        try {
          const progressData = await roadmapClient.getRoadmapProgress(activeRoadmap.id);
          setProgress(progressData);
        } catch (progErr) {
          console.warn('Progress metrics fetch note:', progErr);
        }
      } else {
        // 2. No active roadmap found — load prerequisite data to display RoadmapEmptyState
        setRoadmap(null);
        setProgress(null);

        let roleList: TargetRoleDetail[] = [];
        try {
          const rolesRes = await skillGapClient.listRoles();
          roleList = rolesRes.roles || [];
        } catch {
          // Ignore role list failure
        }

        let userRoleId: string | null = null;
        try {
          const careerGoals = await profileClient.getCareerGoals();
          if (careerGoals?.primary_role?.id) {
            userRoleId = careerGoals.primary_role.id;
          }
        } catch {
          // Ignore profile failure
        }

        let latestAnalysis: SkillGapAnalysisData | null = null;
        try {
          latestAnalysis = await skillGapClient.getLatestAnalysis();
        } catch {
          // Ignore gap analysis failure
        }

        if (latestAnalysis) {
          setGapAnalysis(latestAnalysis);
          const matchedRole = roleList.find(
            (r) => r.id === latestAnalysis?.role_id || r.id === userRoleId
          );
          if (matchedRole) {
            setTargetRole(matchedRole);
          } else if (latestAnalysis.role_title) {
            setTargetRole({
              id: latestAnalysis.role_id,
              title: latestAnalysis.role_title,
              category: 'Engineering',
              description: '',
              version: '1.0',
              source: 'canonical',
              is_complete: true,
              requirements: [],
            });
          }
        } else if (userRoleId && roleList.length > 0) {
          const matchedRole = roleList.find((r) => r.id === userRoleId) || roleList[0];
          setTargetRole(matchedRole);
        } else if (roleList.length > 0) {
          setTargetRole(roleList[0]);
        }
      }
    } catch (err: any) {
      setErrorMessage(err?.message || 'Failed to initialize Personalized Learning Roadmap.');
    } finally {
      setIsLoading(false);
    }
  }, []);

  React.useEffect(() => {
    loadRoadmap();
  }, [loadRoadmap]);

  // Handle roadmap generation from empty state
  const handleGenerateRoadmap = async (payload: { weekly_hours: number; target_timeline_months: number }) => {
    try {
      setIsGenerating(true);
      setErrorMessage(null);

      const generated = await roadmapClient.generateRoadmap({
        role_id: targetRole?.id,
        weekly_hours: payload.weekly_hours,
        target_timeline_months: payload.target_timeline_months,
      });

      setRoadmap(generated);

      try {
        const progressData = await roadmapClient.getRoadmapProgress(generated.id);
        setProgress(progressData);
      } catch {
        // Non-blocking
      }

      showToast(`Personalized roadmap generated! Version 1 created for ${generated.target_role_title}.`);
    } catch (err: any) {
      setErrorMessage(err?.message || 'Failed to generate personalized learning roadmap.');
    } finally {
      setIsGenerating(false);
    }
  };

  // Handle roadmap regeneration from modal
  const handleRegenerateRoadmap = async (payload: {
    weekly_hours: number;
    target_timeline_months: number;
    force_regenerate: boolean;
  }) => {
    try {
      setErrorMessage(null);
      const regenerated = await roadmapClient.generateRoadmap({
        role_id: roadmap?.target_role_id,
        weekly_hours: payload.weekly_hours,
        target_timeline_months: payload.target_timeline_months,
        force_regenerate: payload.force_regenerate,
      });

      setRoadmap(regenerated);

      try {
        const progressData = await roadmapClient.getRoadmapProgress(regenerated.id);
        setProgress(progressData);
      } catch {
        // Non-blocking
      }

      setIsRegenerateModalOpen(false);
      showToast(`Roadmap successfully regenerated! Now on version v${regenerated.version}.`);
    } catch (err: any) {
      setErrorMessage(err?.message || 'Failed to regenerate roadmap with updated parameters.');
      throw err;
    }
  };

  // Handle task status transitions
  const handleStatusChange = async (
    taskId: string,
    newStatus: 'pending' | 'in_progress' | 'completed' | 'skipped'
  ) => {
    if (!roadmap) return;

    try {
      // Optimistic state update across phases & tasks
      const updatedPhases = roadmap.phases.map((phase) => {
        const updatedTasks = phase.tasks.map((task) => {
          if (task.id === taskId) {
            return {
              ...task,
              status: newStatus,
              completed_at: newStatus === 'completed' ? new Date().toISOString() : null,
            };
          }
          return task;
        });

        const completedCount = updatedTasks.filter((t) => t.status === 'completed').length;
        const phaseCompleted = completedCount === updatedTasks.length && updatedTasks.length > 0;
        const phaseInProgress = updatedTasks.some((t) => t.status === 'in_progress' || t.status === 'completed');

        return {
          ...phase,
          tasks: updatedTasks,
          status: phaseCompleted
            ? ('completed' as const)
            : phaseInProgress
            ? ('in_progress' as const)
            : ('pending' as const),
        };
      });

      // Recalculate summary stats
      let totalCompletedTasks = 0;
      let totalTasksCount = 0;
      for (const phase of updatedPhases) {
        totalTasksCount += phase.tasks.length;
        totalCompletedTasks += phase.tasks.filter((t) => t.status === 'completed').length;
      }
      const progressPercentage = totalTasksCount > 0
        ? Math.round((totalCompletedTasks / totalTasksCount) * 100)
        : 0;

      setRoadmap({
        ...roadmap,
        phases: updatedPhases,
        completed_tasks: totalCompletedTasks,
        progress_percentage: progressPercentage,
      });

      // Call authoritative backend API
      await roadmapClient.updateTaskStatus(taskId, { status: newStatus });

      // Refresh authoritative progress metrics in background
      try {
        const progressData = await roadmapClient.getRoadmapProgress(roadmap.id);
        setProgress(progressData);
      } catch {
        // Ignore background failure
      }

      if (newStatus === 'completed') {
        showToast('Milestone completed! Authoritative progress updated.');
      }
    } catch (err: any) {
      setErrorMessage(err?.message || 'Failed to update milestone status.');
      // Re-fetch authoritative state on error
      await loadRoadmap();
    }
  };

  // Handle deliverable submission
  const handleSubmitDeliverable = async (taskId: string, submissionUrl: string) => {
    try {
      await roadmapClient.updateTaskStatus(taskId, {
        submission_url: submissionUrl,
        status: 'completed',
      });

      setDeliverableTask(null);
      showToast('Deliverable proof verified and recorded!');

      // Re-fetch roadmap & progress to ensure consistency
      if (roadmap) {
        const refreshed = await roadmapClient.getActiveRoadmap();
        setRoadmap(refreshed);
        const progressData = await roadmapClient.getRoadmapProgress(refreshed.id);
        setProgress(progressData);
      }
    } catch (err: any) {
      setErrorMessage(err?.message || 'Failed to submit milestone deliverable.');
      throw err;
    }
  };

  // Handle adaptation to passed diagnostic assessments
  const handleAdaptRoadmap = async () => {
    if (!roadmap) return;

    try {
      setIsAdapting(true);
      setErrorMessage(null);

      const adaptation = await roadmapClient.adaptRoadmap(roadmap.id);

      if (adaptation.tasks_auto_completed > 0) {
        showToast(
          `Adapted roadmap based on passed assessments! Completed ${adaptation.tasks_auto_completed} milestone${
            adaptation.tasks_auto_completed > 1 ? 's' : ''
          }.`
        );
      } else {
        showToast('Roadmap is already synchronized with all passed diagnostic assessments.');
      }

      // Re-fetch active roadmap and progress
      const refreshed = await roadmapClient.getActiveRoadmap();
      setRoadmap(refreshed);
      const progressData = await roadmapClient.getRoadmapProgress(refreshed.id);
      setProgress(progressData);
    } catch (err: any) {
      setErrorMessage(err?.message || 'Failed to adapt roadmap to assessment results.');
    } finally {
      setIsAdapting(false);
    }
  };

  // Handle selecting a recommended task from progress summary
  const handleSelectRecommendedTask = (task: RoadmapTaskItem) => {
    setFocusedTaskId(task.id);
    const element = document.getElementById(`task-card-${task.id}`);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto pb-16">
      {/* Toast Notification */}
      {successToast && (
        <div className="p-3.5 rounded-xl bg-emerald-50 dark:bg-emerald-950/50 border border-emerald-200 dark:border-emerald-800 text-xs text-emerald-900 dark:text-emerald-100 flex items-center justify-between shadow-sm animate-in fade-in-50">
          <div className="flex items-center gap-2.5">
            <CheckCircle2 className="w-4 h-4 text-emerald-600 dark:text-emerald-400 shrink-0" />
            <span className="font-medium">{successToast}</span>
          </div>
        </div>
      )}

      {/* Error Alert */}
      {errorMessage && (
        <Alert variant="destructive">
          <div className="flex items-start justify-between w-full">
            <div className="flex items-center gap-2">
              <AlertCircle className="w-4 h-4 shrink-0" />
              <span>{errorMessage}</span>
            </div>
            <Button
              size="sm"
              variant="outline"
              className="text-xs h-6 px-2 ml-4"
              onClick={loadRoadmap}
            >
              Retry
            </Button>
          </div>
        </Alert>
      )}

      {/* Loading Skeleton */}
      {isLoading && (
        <div className="space-y-6">
          <Card className="p-6">
            <div className="space-y-3">
              <Skeleton className="h-5 w-48" />
              <Skeleton className="h-8 w-96" />
              <Skeleton className="h-4 w-72" />
            </div>
          </Card>
          <Skeleton className="h-28 rounded-2xl" />
          <Skeleton className="h-52 rounded-2xl" />
          <div className="space-y-4">
            <Skeleton className="h-48 rounded-2xl" />
            <Skeleton className="h-48 rounded-2xl" />
          </div>
        </div>
      )}

      {/* Empty State (No Roadmap Generated Yet) */}
      {!isLoading && !roadmap && (
        <RoadmapEmptyState
          targetRole={targetRole}
          gapAnalysis={gapAnalysis}
          onGenerate={handleGenerateRoadmap}
          isGenerating={isGenerating}
        />
      )}

      {/* Active Roadmap View */}
      {!isLoading && roadmap && (
        <div className="space-y-6">
          {/* Header */}
          <RoadmapHeader
            roadmap={roadmap}
            onOpenRegenerateModal={() => setIsRegenerateModalOpen(true)}
            onAdaptRoadmap={handleAdaptRoadmap}
            isAdapting={isAdapting}
          />

          {/* Feasibility & Schedule Banner */}
          <RoadmapScheduleBanner roadmap={roadmap} />

          {/* Authoritative Progress Summary */}
          <RoadmapProgressSummary
            roadmap={roadmap}
            progress={progress}
            onSelectTask={handleSelectRecommendedTask}
          />

          {/* Sequential Phase Breakdown & Milestone DAG */}
          <div className="space-y-3 pt-2">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-base font-bold text-slate-900 dark:text-white tracking-tight">
                  Curriculum Phases & Milestones
                </h3>
                <p className="text-xs text-slate-500 dark:text-slate-400">
                  Step-by-step sequential learning phases tailored to your skill gaps. Milestone locks enforce prerequisite mastery.
                </p>
              </div>

              <span className="text-xs text-slate-500 dark:text-slate-400 font-mono">
                {roadmap.completed_tasks} / {roadmap.total_tasks} milestones completed
              </span>
            </div>

            <RoadmapPhaseList
              phases={roadmap.phases}
              onStatusChange={handleStatusChange}
              onSubmitDeliverable={(task) => setDeliverableTask(task)}
              focusedTaskId={focusedTaskId}
            />
          </div>
        </div>
      )}

      {/* Deliverable Proof Submission Modal */}
      <DeliverableModal
        isOpen={deliverableTask !== null}
        onClose={() => setDeliverableTask(null)}
        task={deliverableTask}
        onSubmit={handleSubmitDeliverable}
      />

      {/* Regenerate Roadmap Modal */}
      {roadmap && (
        <RegenerateRoadmapModal
          isOpen={isRegenerateModalOpen}
          onClose={() => setIsRegenerateModalOpen(false)}
          currentWeeklyHours={roadmap.weekly_hours}
          onRegenerate={handleRegenerateRoadmap}
          targetRoleTitle={roadmap.target_role_title}
        />
      )}
    </div>
  );
}
