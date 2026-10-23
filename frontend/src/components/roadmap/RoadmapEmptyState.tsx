'use client';

import * as React from 'react';
import Link from 'next/link';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { TargetRoleDetail, SkillGapAnalysisData } from '@/types';
import {
  Compass,
  CheckCircle2,
  AlertCircle,
  Clock,
  Calendar,
  Layers,
  ArrowRight,
  Cpu,
  Loader2,
  Sparkles,
} from 'lucide-react';

interface RoadmapEmptyStateProps {
  targetRole: TargetRoleDetail | null;
  gapAnalysis: SkillGapAnalysisData | null;
  onGenerate: (payload: { weekly_hours: number; target_timeline_months: number }) => Promise<void>;
  isGenerating: boolean;
}

export function RoadmapEmptyState({
  targetRole,
  gapAnalysis,
  onGenerate,
  isGenerating,
}: RoadmapEmptyStateProps) {
  const [weeklyHours, setWeeklyHours] = React.useState<number>(10);
  const [timelineMonths, setTimelineMonths] = React.useState<number>(6);
  const [error, setError] = React.useState<string | null>(null);

  const hasRole = !!targetRole;
  const hasAnalysis = !!gapAnalysis;

  const handleGenerateClick = async () => {
    if (!hasRole) {
      setError('Please select or configure a target role before generating a learning roadmap.');
      return;
    }
    if (weeklyHours < 1 || weeklyHours > 60) {
      setError('Weekly study commitment must be between 1 and 60 hours.');
      return;
    }
    if (timelineMonths < 1 || timelineMonths > 36) {
      setError('Target timeline must be between 1 and 36 months.');
      return;
    }

    try {
      setError(null);
      await onGenerate({
        weekly_hours: Number(weeklyHours),
        target_timeline_months: Number(timelineMonths),
      });
    } catch (err: any) {
      setError(err?.message || 'Failed to generate roadmap. Please verify role prerequisites.');
    }
  };

  return (
    <Card className="p-6 sm:p-10 max-w-3xl mx-auto border-dashed border-2 border-slate-300 dark:border-slate-800 text-center space-y-6">
      <div className="w-16 h-16 rounded-2xl bg-brand-50 dark:bg-brand-950/50 text-brand-600 dark:text-brand-400 mx-auto flex items-center justify-center border border-brand-200 dark:border-brand-800 shadow-sm">
        <Compass className="w-8 h-8" />
      </div>

      <div className="space-y-2 max-w-xl mx-auto">
        <h3 className="text-2xl font-bold text-slate-900 dark:text-white tracking-tight">
          Personalized Learning Roadmap
        </h3>
        <p className="text-xs sm:text-sm text-slate-600 dark:text-slate-400 leading-relaxed">
          CoachPath builds a tailored, milestone-based curriculum to close your verified skill gaps,
          balance study hours against your target deadline, and prepare real portfolio deliverables.
        </p>
      </div>

      {/* Prerequisites Verification Checklist */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-left max-w-xl mx-auto text-xs">
        {/* Prerequisite 1: Target Role */}
        <div
          className={`p-3.5 rounded-xl border ${
            hasRole
              ? 'bg-emerald-50/50 dark:bg-emerald-950/20 border-emerald-200 dark:border-emerald-800/60'
              : 'bg-amber-50/50 dark:bg-amber-950/20 border-amber-200 dark:border-amber-800/60'
          }`}
        >
          <div className="flex items-start gap-2.5">
            {hasRole ? (
              <CheckCircle2 className="w-4 h-4 text-emerald-600 mt-0.5 shrink-0" />
            ) : (
              <AlertCircle className="w-4 h-4 text-amber-600 mt-0.5 shrink-0" />
            )}
            <div className="space-y-0.5">
              <span className="font-bold text-slate-900 dark:text-white">Target Role</span>
              <p className="text-[11px] text-slate-600 dark:text-slate-400">
                {hasRole ? (
                  <span className="font-semibold text-emerald-700 dark:text-emerald-400">
                    {targetRole.title}
                  </span>
                ) : (
                  <span>
                    No target role designated.{' '}
                    <Link href="/skills" className="text-brand-600 underline font-semibold">
                      Select Role
                    </Link>
                  </span>
                )}
              </p>
            </div>
          </div>
        </div>

        {/* Prerequisite 2: Skill Gap Analysis */}
        <div
          className={`p-3.5 rounded-xl border ${
            hasAnalysis
              ? 'bg-emerald-50/50 dark:bg-emerald-950/20 border-emerald-200 dark:border-emerald-800/60'
              : 'bg-slate-50 dark:bg-slate-800/50 border-slate-200 dark:border-slate-700'
          }`}
        >
          <div className="flex items-start gap-2.5">
            {hasAnalysis ? (
              <CheckCircle2 className="w-4 h-4 text-emerald-600 mt-0.5 shrink-0" />
            ) : (
              <Cpu className="w-4 h-4 text-slate-400 mt-0.5 shrink-0" />
            )}
            <div className="space-y-0.5">
              <span className="font-bold text-slate-900 dark:text-white">Skill Gap Analysis</span>
              <p className="text-[11px] text-slate-600 dark:text-slate-400">
                {hasAnalysis ? (
                  <span className="text-emerald-700 dark:text-emerald-400 font-semibold">
                    Calibrated ({gapAnalysis.role_alignment_score.toFixed(1)}% Alignment)
                  </span>
                ) : (
                  <span>Will be automatically calibrated on generation.</span>
                )}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Constraints Inputs */}
      <div className="p-5 rounded-2xl bg-slate-50 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-800 max-w-xl mx-auto space-y-4 text-left">
        <h4 className="text-xs font-bold text-slate-900 dark:text-white uppercase tracking-wider flex items-center gap-1.5">
          <Clock className="w-3.5 h-3.5 text-brand-600" />
          Set Your Study Constraints & Pace
        </h4>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
          <div className="space-y-1">
            <label className="font-semibold text-slate-700 dark:text-slate-300 text-[11px]">
              Available Weekly Hours
            </label>
            <Input
              type="number"
              min={1}
              max={60}
              value={weeklyHours}
              onChange={(e) => setWeeklyHours(Math.max(1, Number(e.target.value)))}
              className="h-9 text-xs"
            />
            <span className="text-[10px] text-slate-400">e.g. 10 hours/week</span>
          </div>

          <div className="space-y-1">
            <label className="font-semibold text-slate-700 dark:text-slate-300 text-[11px]">
              Target Deadline (Months)
            </label>
            <Input
              type="number"
              min={1}
              max={36}
              value={timelineMonths}
              onChange={(e) => setTimelineMonths(Math.max(1, Number(e.target.value)))}
              className="h-9 text-xs"
            />
            <span className="text-[10px] text-slate-400">e.g. 6 months</span>
          </div>
        </div>
      </div>

      {error && (
        <div className="p-3 rounded-lg bg-red-50 dark:bg-red-950/30 border border-red-200 dark:border-red-800 text-red-700 dark:text-red-300 text-xs max-w-xl mx-auto">
          {error}
        </div>
      )}

      {/* CTA Button */}
      <div className="pt-2">
        <Button
          size="lg"
          variant="primary"
          onClick={handleGenerateClick}
          disabled={isGenerating || !hasRole}
          className="text-sm px-6 h-11"
        >
          {isGenerating ? (
            <>
              <Loader2 className="w-4 h-4 mr-2 animate-spin" />
              Generating Curriculum...
            </>
          ) : (
            <>
              <Sparkles className="w-4 h-4 mr-2" />
              Generate Learning Roadmap
            </>
          )}
        </Button>
      </div>
    </Card>
  );
}
