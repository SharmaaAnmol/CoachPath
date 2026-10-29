'use client';

import * as React from 'react';
import Link from 'next/link';
import {
  SkillGapAnalysisData,
  TargetRoleDetail,
} from '@/types';
import { skillGapClient } from '@/lib/skill-gap-client';
import { profileClient } from '@/lib/profile-client';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { Alert } from '@/components/ui/alert';
import { TargetRoleSelector } from '@/components/skills/TargetRoleSelector';
import { ScoreOverviewCards } from '@/components/skills/ScoreOverviewCards';
import { ScoreExplanationModal } from '@/components/skills/ScoreExplanationModal';
import { SkillComparisonTable } from '@/components/skills/SkillComparisonTable';
import { SkillEvidenceModal } from '@/components/skills/SkillEvidenceModal';
import { GapPriorityList } from '@/components/skills/GapPriorityList';
import { RecommendedAssessmentsSection } from '@/components/skills/RecommendedAssessmentsSection';
import { AnalysisHistoryModal } from '@/components/skills/AnalysisHistoryModal';
import { DiagnosticNarrativeCard } from '@/components/skills/DiagnosticNarrativeCard';
import {
  Cpu,
  RotateCcw,
  History,
  ClipboardCheck,
  AlertCircle,
  Loader2,
  Sparkles,
  Calendar,
  CheckCircle2,
  Compass,
  ArrowRight,
} from 'lucide-react';

export default function SkillsPage() {
  const [roles, setRoles] = React.useState<TargetRoleDetail[]>([]);
  const [selectedRoleId, setSelectedRoleId] = React.useState<string>('');
  const [profileRoleId, setProfileRoleId] = React.useState<string | null>(null);
  const [analysis, setAnalysis] = React.useState<SkillGapAnalysisData | null>(null);

  const [isLoading, setIsLoading] = React.useState<boolean>(true);
  const [isRecalculating, setIsRecalculating] = React.useState<boolean>(false);
  const [errorMessage, setErrorMessage] = React.useState<string | null>(null);
  const [successToast, setSuccessToast] = React.useState<string | null>(null);

  // Modal states
  const [isExplanationOpen, setIsExplanationOpen] = React.useState<boolean>(false);
  const [isHistoryOpen, setIsHistoryOpen] = React.useState<boolean>(false);
  const [evidenceModalSkill, setEvidenceModalSkill] = React.useState<{ id: string; name: string } | null>(null);

  // Initial Data Fetch
  const loadInitialData = React.useCallback(async () => {
    try {
      setIsLoading(true);
      setErrorMessage(null);

      // 1. Fetch available target roles
      const rolesRes = await skillGapClient.listRoles();
      setRoles(rolesRes.roles);

      // 2. Fetch profile career goals to preselect role if available
      let candidateTargetRoleId = rolesRes.roles[0]?.id || '';
      try {
        const goals = await profileClient.getCareerGoals();
        if (goals.primary_role?.id) {
          candidateTargetRoleId = goals.primary_role.id;
          setProfileRoleId(goals.primary_role.id);
        }
      } catch {
        // Fallback to default if profile not yet completed
      }

      // 3. Fetch latest active analysis
      let activeAnalysis: SkillGapAnalysisData | null = null;
      try {
        activeAnalysis = await skillGapClient.getLatestAnalysis();
      } catch {
        // If no analysis exists yet, compute one
        activeAnalysis = await skillGapClient.calculateAnalysis(candidateTargetRoleId);
      }

      if (activeAnalysis) {
        setAnalysis(activeAnalysis);
        setSelectedRoleId(activeAnalysis.role_id);
      } else {
        setSelectedRoleId(candidateTargetRoleId);
      }
    } catch (err: any) {
      setErrorMessage(err?.message || 'Failed to initialize skill gap analysis engine.');
    } finally {
      setIsLoading(false);
    }
  }, []);

  React.useEffect(() => {
    loadInitialData();
  }, [loadInitialData]);

  // Handle switching target roles
  const handleSelectRole = async (newRoleId: string) => {
    if (newRoleId === selectedRoleId && analysis) return;

    try {
      setIsRecalculating(true);
      setErrorMessage(null);
      setSelectedRoleId(newRoleId);

      const updated = await skillGapClient.calculateAnalysis(newRoleId);
      setAnalysis(updated);
      setSuccessToast(`Evaluated alignment against ${updated.role_title}.`);
      setTimeout(() => setSuccessToast(null), 3000);
    } catch (err: any) {
      setErrorMessage(err?.message || `Failed to analyze gaps for ${newRoleId}.`);
    } finally {
      setIsRecalculating(false);
    }
  };

  // Handle explicit recalculation
  const handleRecalculate = async () => {
    if (isRecalculating) return;

    try {
      setIsRecalculating(true);
      setErrorMessage(null);

      const refreshed = await skillGapClient.recalculateAnalysis(selectedRoleId);
      setAnalysis(refreshed);
      setSuccessToast('Analysis successfully updated with latest evidence!');
      setTimeout(() => setSuccessToast(null), 3000);
    } catch (err: any) {
      setErrorMessage(err?.message || 'Failed to recalculate skill gap analysis.');
    } finally {
      setIsRecalculating(false);
    }
  };

  // Inspect skill evidence callback
  const handleInspectEvidence = (skillId: string, skillName: string) => {
    setEvidenceModalSkill({ id: skillId, name: skillName });
  };

  const formatCalculatedTime = (isoString?: string) => {
    if (!isoString) return '';
    try {
      const d = new Date(isoString);
      return d.toLocaleDateString(undefined, {
        month: 'short',
        day: 'numeric',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      });
    } catch {
      return isoString;
    }
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto pb-12">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="p-2 rounded-xl bg-indigo-50 dark:bg-indigo-950 text-indigo-600 dark:text-indigo-400">
              <Cpu className="w-5 h-5" />
            </span>
            <h1 className="text-2xl font-bold text-slate-900 dark:text-white tracking-tight">
              Skill Gap Analysis Engine
            </h1>
          </div>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
            Grounded benchmark comparison comparing your verified assessments, projects, and career evidence against role requirements.
          </p>
        </div>

        {/* Action Controls */}
        <div className="flex flex-wrap items-center gap-2">
          <Button
            size="sm"
            variant="outline"
            onClick={() => setIsHistoryOpen(true)}
            disabled={isLoading || isRecalculating}
            className="text-xs"
          >
            <History className="w-3.5 h-3.5 mr-1.5" /> Snapshot History
          </Button>

          <Button
            size="sm"
            variant="outline"
            onClick={handleRecalculate}
            disabled={isLoading || isRecalculating}
            className="text-xs font-semibold"
          >
            {isRecalculating ? (
              <>
                <Loader2 className="w-3.5 h-3.5 mr-1.5 animate-spin" /> Recalculating...
              </>
            ) : (
              <>
                <RotateCcw className="w-3.5 h-3.5 mr-1.5" /> Recalculate
              </>
            )}
          </Button>

          <Link href="/roadmap">
            <Button size="sm" variant="outline" className="text-xs font-semibold">
              <Compass className="w-3.5 h-3.5 mr-1.5" /> Learning Roadmap
            </Button>
          </Link>

          <Link href="/assessments">
            <Button size="sm" variant="intelligence" className="text-xs font-semibold">
              <ClipboardCheck className="w-3.5 h-3.5 mr-1.5" /> Take Assessment
            </Button>
          </Link>
        </div>
      </div>

      {/* Success Notification */}
      {successToast && (
        <div className="p-3 rounded-xl bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-200 dark:border-emerald-800 text-xs text-emerald-800 dark:text-emerald-200 flex items-center justify-between animate-in fade-in-50">
          <div className="flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-600 dark:text-emerald-400 shrink-0" />
            <span>{successToast}</span>
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
            <Button size="sm" variant="outline" className="text-xs h-6 px-2 ml-4" onClick={loadInitialData}>
              Retry
            </Button>
          </div>
        </Alert>
      )}

      {/* Initial Loading Skeleton */}
      {isLoading && !analysis && (
        <div className="space-y-4">
          <Card className="p-5">
            <div className="space-y-2">
              <Skeleton className="h-4 w-48" />
              <Skeleton className="h-3 w-96" />
            </div>
          </Card>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Skeleton className="h-40 rounded-xl" />
            <Skeleton className="h-40 rounded-xl" />
          </div>
          <Skeleton className="h-96 rounded-xl" />
        </div>
      )}

      {/* Loaded Analysis View */}
      {!isLoading && analysis && (
        <div className="space-y-6">
          {/* Target Role Selector Component */}
          <TargetRoleSelector
            roles={roles}
            selectedRoleId={selectedRoleId}
            onSelectRole={handleSelectRole}
            profileRoleId={profileRoleId}
            isLoading={isRecalculating}
            disabled={isRecalculating}
          />

          {/* Timestamp and Version Bar */}
          <div className="flex items-center justify-between px-1 text-[11px] text-slate-400">
            <div className="flex items-center gap-2">
              <span className="flex items-center gap-1">
                <Calendar className="w-3 h-3" />
                Snapshot: <strong>{formatCalculatedTime(analysis.calculated_at)}</strong>
              </span>
              <span>•</span>
              <span>Algorithm v{analysis.algorithm_version}</span>
              <span>•</span>
              <span>Benchmark v{analysis.role_version}</span>
            </div>
            {isRecalculating && (
              <span className="flex items-center gap-1 text-indigo-600 dark:text-indigo-400 font-semibold animate-pulse">
                <Loader2 className="w-3 h-3 animate-spin" /> Updating scores...
              </span>
            )}
          </div>

          {/* Primary Score Overview Cards */}
          <ScoreOverviewCards
            analysis={analysis}
            onOpenExplanation={() => setIsExplanationOpen(true)}
            onRecalculate={handleRecalculate}
            isRecalculating={isRecalculating}
          />

          {/* Deterministic Diagnostic Narrative Report */}
          <DiagnosticNarrativeCard
            narrative={analysis.explanation_narrative}
            roleTitle={analysis.role_title}
          />

          {/* Prioritized Remedial Gap Plan */}
          <GapPriorityList
            gaps={analysis.prioritized_gaps}
            roleTitle={analysis.role_title}
          />

          {/* Actionable Learning Roadmap Bridge */}
          <Card className="p-4 bg-gradient-to-r from-brand-900/30 via-indigo-950/30 to-slate-900/50 border border-brand-500/30 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div className="space-y-1">
              <div className="flex items-center gap-2 text-brand-400 font-semibold text-xs uppercase tracking-wider">
                <Compass className="w-4 h-4 text-brand-400" />
                <span>Bridge Your Skill Gaps</span>
              </div>
              <p className="text-xs text-slate-300">
                Ready to resolve these prioritized gaps? Follow your personalized milestone curriculum with verifiable deliverables.
              </p>
            </div>
            <Link href="/roadmap" className="shrink-0">
              <Button size="sm" variant="intelligence" className="text-xs font-semibold whitespace-nowrap">
                Open Learning Roadmap <ArrowRight className="w-3.5 h-3.5 ml-1.5" />
              </Button>
            </Link>
          </Card>

          {/* Recommended Diagnostic Assessments Bridge */}
          <RecommendedAssessmentsSection
            assessments={analysis.recommended_assessments}
          />

          {/* Granular Skill-by-Skill Comparison Table */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-sm font-bold text-slate-900 dark:text-white uppercase tracking-wider">
                  Comprehensive Role Skill Breakdown
                </h3>
                <p className="text-xs text-slate-500 dark:text-slate-400">
                  Individual competency calibration comparing required levels (1-4) against supported evidence.
                </p>
              </div>
            </div>

            <SkillComparisonTable
              skills={analysis.skill_details}
              onInspectEvidence={handleInspectEvidence}
            />
          </div>
        </div>
      )}

      {/* Educational Explanation Modal */}
      <ScoreExplanationModal
        isOpen={isExplanationOpen}
        onClose={() => setIsExplanationOpen(false)}
      />

      {/* Snapshot History Modal */}
      <AnalysisHistoryModal
        isOpen={isHistoryOpen}
        onClose={() => setIsHistoryOpen(false)}
      />

      {/* Granular Evidence Drill-Down Modal */}
      <SkillEvidenceModal
        skillId={evidenceModalSkill?.id || null}
        skillName={evidenceModalSkill?.name || ''}
        isOpen={evidenceModalSkill !== null}
        onClose={() => setEvidenceModalSkill(null)}
      />
    </div>
  );
}
