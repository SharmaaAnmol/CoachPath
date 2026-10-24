'use client';

import * as React from 'react';
import Link from 'next/link';
import { cn } from '@/lib/utils';
import {
  JobOpportunity,
  JobMatchResponse,
  SkillMatchItem,
  SkillMatchClassification,
} from '@/types';
import { jobMatchingClient } from '@/lib/job-matching-client';
import { MatchScoreBadge } from './match-score-badge';
import { MatchEvidenceCoverage } from './match-evidence-coverage';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { ProgressBar } from '@/components/ui/progress-bar';
import {
  X,
  RefreshCw,
  ExternalLink,
  Building2,
  MapPin,
  DollarSign,
  AlertTriangle,
  CheckCircle2,
  XCircle,
  HelpCircle,
  Clock,
  Layers,
  Sparkles,
  ArrowRight,
  ShieldCheck,
  Award,
  BookOpen,
  FolderGit2,
  FileText,
  UserCheck,
  ChevronRight,
  Info,
} from 'lucide-react';

export interface JobMatchDrawerProps {
  job: JobOpportunity | null;
  match: JobMatchResponse | null;
  isOpen: boolean;
  onClose: () => void;
  onRecalculateSuccess?: (updatedMatch: JobMatchResponse) => void;
  onViewFullJob?: (job: JobOpportunity) => void;
}

type TabType = 'breakdown' | 'skills' | 'strengths_gaps' | 'actions';

export function JobMatchDrawer({
  job,
  match: initialMatch,
  isOpen,
  onClose,
  onRecalculateSuccess,
  onViewFullJob,
}: JobMatchDrawerProps) {
  const [activeTab, setActiveTab] = React.useState<TabType>('breakdown');
  const [currentMatch, setCurrentMatch] = React.useState<JobMatchResponse | null>(initialMatch);
  const [isRecalculating, setIsRecalculating] = React.useState(false);
  const [isLoadingMatch, setIsLoadingMatch] = React.useState(false);
  const [recalcError, setRecalcError] = React.useState<string | null>(null);
  const [skillFilter, setSkillFilter] = React.useState<string>('all');

  // Sync state when props change
  React.useEffect(() => {
    setCurrentMatch(initialMatch);
  }, [initialMatch]);

  // Load match if not provided but drawer opened with a job
  React.useEffect(() => {
    if (isOpen && job && !currentMatch) {
      setIsLoadingMatch(true);
      jobMatchingClient
        .getJobMatch(job.id)
        .then((m) => setCurrentMatch(m))
        .catch((err) => {
          console.error('Failed to load job match details:', err);
          setRecalcError('Unable to load match calculation for this role.');
        })
        .finally(() => setIsLoadingMatch(false));
    }
  }, [isOpen, job, currentMatch]);

  // Keyboard navigation (ESC to close)
  React.useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };
    if (isOpen) {
      document.body.style.overflow = 'hidden';
      window.addEventListener('keydown', handleKeyDown);
    }
    return () => {
      document.body.style.overflow = 'unset';
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, [isOpen, onClose]);

  if (!isOpen || !job) return null;

  const handleRecalculate = async () => {
    if (!job) return;
    setIsRecalculating(true);
    setRecalcError(null);
    try {
      const updated = await jobMatchingClient.recalculateJobMatch(job.id);
      setCurrentMatch(updated);
      if (onRecalculateSuccess) {
        onRecalculateSuccess(updated);
      }
    } catch (err: any) {
      setRecalcError(err?.message || 'Failed to recalculate match score.');
    } finally {
      setIsRecalculating(false);
    }
  };

  const formatSalary = () => {
    if (job.min_salary && job.max_salary) {
      return `$${job.min_salary.toLocaleString()} – $${job.max_salary.toLocaleString()}/yr ${job.currency}`;
    } else if (job.min_salary) {
      return `From $${job.min_salary.toLocaleString()}/yr ${job.currency}`;
    } else if (job.max_salary) {
      return `Up to $${job.max_salary.toLocaleString()}/yr ${job.currency}`;
    }
    return 'Not disclosed';
  };

  const match = currentMatch;
  const breakdown = match?.breakdown;
  const isProvisional = breakdown?.is_provisional || (breakdown?.evidence_coverage || 0) < 40;

  // Filter skills
  const skillsDetail = match?.skills_detail || [];
  const filteredSkills = skillsDetail.filter((item) => {
    if (skillFilter === 'all') return true;
    if (skillFilter === 'matched') return item.classification === 'MATCHED';
    if (skillFilter === 'partially_matched') return item.classification === 'PARTIALLY_MATCHED';
    if (skillFilter === 'missing') return item.classification === 'MISSING';
    if (skillFilter === 'unknown') return item.classification === 'UNKNOWN' || item.classification === 'INSUFFICIENT_EVIDENCE';
    if (skillFilter === 'mandatory') return item.is_mandatory;
    if (skillFilter === 'preferred') return !item.is_mandatory;
    return true;
  });

  const getClassificationBadge = (c: SkillMatchClassification) => {
    switch (c) {
      case 'MATCHED':
        return (
          <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-emerald-700 bg-emerald-50 dark:bg-emerald-950/60 dark:text-emerald-300 px-2 py-0.5 rounded-full border border-emerald-200/60 dark:border-emerald-800/60">
            <CheckCircle2 className="w-3 h-3 text-emerald-600 dark:text-emerald-400" />
            Verified Match
          </span>
        );
      case 'PARTIALLY_MATCHED':
        return (
          <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-amber-700 bg-amber-50 dark:bg-amber-950/60 dark:text-amber-300 px-2 py-0.5 rounded-full border border-amber-200/60 dark:border-amber-800/60">
            <Clock className="w-3 h-3 text-amber-600 dark:text-amber-400" />
            Partial Evidence
          </span>
        );
      case 'MISSING':
        return (
          <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-rose-700 bg-rose-50 dark:bg-rose-950/60 dark:text-rose-300 px-2 py-0.5 rounded-full border border-rose-200/60 dark:border-rose-800/60">
            <XCircle className="w-3 h-3 text-rose-600 dark:text-rose-400" />
            Missing Evidence
          </span>
        );
      case 'UNKNOWN':
      case 'INSUFFICIENT_EVIDENCE':
      default:
        return (
          <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-slate-600 bg-slate-100 dark:bg-slate-800 dark:text-slate-300 px-2 py-0.5 rounded-full border border-slate-200 dark:border-slate-700">
            <HelpCircle className="w-3 h-3 text-slate-500" />
            Unverified
          </span>
        );
    }
  };

  const getProvenanceBadge = (source?: string, score?: number, tier?: string) => {
    if (!source || source === 'none') {
      return (
        <span className="inline-flex items-center gap-1 text-[10px] text-slate-400 dark:text-slate-500">
          No profile record
        </span>
      );
    }
    if (source === 'assessment') {
      return (
        <span className="inline-flex items-center gap-1 text-[11px] font-medium text-emerald-700 dark:text-emerald-300 bg-emerald-50 dark:bg-emerald-950/50 px-2 py-0.5 rounded-md border border-emerald-200 dark:border-emerald-900/60">
          <Award className="w-3 h-3 text-emerald-600" />
          Assessment {score ? `${Math.round(score)}%` : ''} {tier ? `(${tier})` : ''}
        </span>
      );
    }
    if (source === 'project_evidence') {
      return (
        <span className="inline-flex items-center gap-1 text-[11px] font-medium text-purple-700 dark:text-purple-300 bg-purple-50 dark:bg-purple-950/50 px-2 py-0.5 rounded-md border border-purple-200 dark:border-purple-900/60">
          <FolderGit2 className="w-3 h-3 text-purple-600" />
          Project Artifact
        </span>
      );
    }
    if (source === 'extracted') {
      return (
        <span className="inline-flex items-center gap-1 text-[11px] font-medium text-blue-700 dark:text-blue-300 bg-blue-50 dark:bg-blue-950/50 px-2 py-0.5 rounded-md border border-blue-200 dark:border-blue-900/60">
          <FileText className="w-3 h-3 text-blue-600" />
          Approved Resume
        </span>
      );
    }
    return (
      <span className="inline-flex items-center gap-1 text-[11px] font-medium text-slate-700 dark:text-slate-300 bg-slate-100 dark:bg-slate-800 px-2 py-0.5 rounded-md border border-slate-200 dark:border-slate-700">
        <UserCheck className="w-3 h-3 text-slate-500" />
        Self Reported
      </span>
    );
  };

  return (
    <div className="fixed inset-0 z-50 overflow-hidden" role="dialog" aria-modal="true">
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-slate-900/60 backdrop-blur-sm transition-opacity"
        onClick={onClose}
        aria-hidden="true"
      />

      <div className="fixed inset-y-0 right-0 max-w-full flex pl-10 z-50">
        <div className="w-screen max-w-2xl bg-white dark:bg-slate-900 shadow-2xl flex flex-col border-l border-slate-200 dark:border-slate-800">
          {/* Header */}
          <div className="px-6 py-5 border-b border-slate-200 dark:border-slate-800 bg-slate-50/60 dark:bg-slate-900/60 space-y-4">
            <div className="flex items-start justify-between gap-4">
              <div>
                <div className="flex items-center gap-2">
                  <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-brand-700 dark:text-brand-300 bg-brand-50 dark:bg-brand-950/60 px-2.5 py-0.5 rounded-full border border-brand-200/60 dark:border-brand-800/60">
                    <Sparkles className="w-3 h-3 text-brand-600 dark:text-brand-400" />
                    Match Explainability Drawer
                  </span>
                  {match?.is_stale && (
                    <Badge variant="action" size="sm">
                      Stale Result
                    </Badge>
                  )}
                </div>
                <h2 className="text-xl font-bold text-slate-900 dark:text-white mt-1.5 leading-snug">
                  {job.title}
                </h2>
                <div className="flex flex-wrap items-center gap-3 text-xs text-slate-600 dark:text-slate-400 mt-1">
                  <span className="font-semibold text-slate-800 dark:text-slate-200 flex items-center gap-1">
                    <Building2 className="w-3.5 h-3.5 text-slate-500" />
                    {job.company_name}
                  </span>
                  <span>•</span>
                  <span className="flex items-center gap-1">
                    <MapPin className="w-3.5 h-3.5 text-slate-500" />
                    {job.location} ({job.remote_type})
                  </span>
                  <span>•</span>
                  <span className="flex items-center gap-1">
                    <DollarSign className="w-3.5 h-3.5 text-slate-500" />
                    {formatSalary()}
                  </span>
                </div>
              </div>

              <button
                onClick={onClose}
                className="rounded-lg p-2 text-slate-400 hover:text-slate-700 hover:bg-slate-200/60 dark:hover:bg-slate-800 dark:hover:text-slate-200 transition-colors"
                aria-label="Close explainability drawer"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Score & Coverage Top Hero Banner */}
            {match && (
              <div className="bg-white dark:bg-slate-800/80 rounded-xl p-4 border border-slate-200/80 dark:border-slate-700/80 shadow-sm flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div className="flex items-center gap-4">
                  <MatchScoreBadge
                    score={match.overall_score}
                    isProvisional={isProvisional}
                    size="lg"
                  />
                  <div className="space-y-1">
                    <p className="text-xs font-semibold text-slate-700 dark:text-slate-200">
                      Overall Recommendation Fit
                    </p>
                    <MatchEvidenceCoverage
                      coverage={match.breakdown?.evidence_coverage || 0}
                      isProvisional={isProvisional}
                      size="sm"
                    />
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={handleRecalculate}
                    disabled={isRecalculating}
                    className="flex items-center gap-1.5 text-xs"
                  >
                    <RefreshCw className={cn('w-3.5 h-3.5', isRecalculating && 'animate-spin')} />
                    <span>{isRecalculating ? 'Recalculating...' : 'Recalculate Fit'}</span>
                  </Button>
                </div>
              </div>
            )}

            {/* Stale Warning Banner */}
            {match?.is_stale && (
              <div className="bg-amber-50 dark:bg-amber-950/40 border border-amber-200 dark:border-amber-900/60 rounded-lg p-3 text-xs text-amber-800 dark:text-amber-200 flex items-start gap-2">
                <AlertTriangle className="w-4 h-4 text-amber-600 flex-shrink-0 mt-0.5" />
                <div className="flex-1">
                  <strong>Stale Match Result:</strong> Your profile, learning roadmap, or skill assessments have been updated since this match was evaluated.
                  <button
                    onClick={handleRecalculate}
                    className="ml-2 font-bold underline hover:text-amber-950 dark:hover:text-amber-100"
                  >
                    Recalculate now
                  </button>
                </div>
              </div>
            )}

            {/* Recalculate Error */}
            {recalcError && (
              <div className="bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-900/60 rounded-lg p-3 text-xs text-rose-800 dark:text-rose-200 flex items-start gap-2">
                <XCircle className="w-4 h-4 text-rose-600 flex-shrink-0 mt-0.5" />
                <div className="flex-1">{recalcError}</div>
              </div>
            )}

            {/* Tabs Nav */}
            <div className="flex items-center gap-1 border-b border-slate-200 dark:border-slate-800 pt-2 -mb-5">
              <button
                onClick={() => setActiveTab('breakdown')}
                className={cn(
                  'px-3 py-2 text-xs font-semibold border-b-2 transition-colors',
                  activeTab === 'breakdown'
                    ? 'border-brand-600 text-brand-600 dark:text-brand-400'
                    : 'border-transparent text-slate-500 hover:text-slate-800 dark:hover:text-slate-200'
                )}
              >
                Factor Breakdown
              </button>
              <button
                onClick={() => setActiveTab('skills')}
                className={cn(
                  'px-3 py-2 text-xs font-semibold border-b-2 transition-colors flex items-center gap-1.5',
                  activeTab === 'skills'
                    ? 'border-brand-600 text-brand-600 dark:text-brand-400'
                    : 'border-transparent text-slate-500 hover:text-slate-800 dark:hover:text-slate-200'
                )}
              >
                <span>Skill Matrix</span>
                <span className="text-[10px] bg-slate-200 dark:bg-slate-700 px-1.5 py-0.2 rounded-full font-bold">
                  {skillsDetail.length}
                </span>
              </button>
              <button
                onClick={() => setActiveTab('strengths_gaps')}
                className={cn(
                  'px-3 py-2 text-xs font-semibold border-b-2 transition-colors',
                  activeTab === 'strengths_gaps'
                    ? 'border-brand-600 text-brand-600 dark:text-brand-400'
                    : 'border-transparent text-slate-500 hover:text-slate-800 dark:hover:text-slate-200'
                )}
              >
                Strengths & Gaps
              </button>
              <button
                onClick={() => setActiveTab('actions')}
                className={cn(
                  'px-3 py-2 text-xs font-semibold border-b-2 transition-colors flex items-center gap-1.5',
                  activeTab === 'actions'
                    ? 'border-brand-600 text-brand-600 dark:text-brand-400'
                    : 'border-transparent text-slate-500 hover:text-slate-800 dark:hover:text-slate-200'
                )}
              >
                <span>Action Plan</span>
                <span className="text-[10px] bg-brand-100 text-brand-700 dark:bg-brand-950 dark:text-brand-300 px-1.5 py-0.2 rounded-full font-bold">
                  {match?.explanation?.recommended_actions?.length || 0}
                </span>
              </button>
            </div>
          </div>

          {/* Drawer Body */}
          <div className="flex-1 overflow-y-auto p-6 space-y-6">
            {isLoadingMatch && (
              <div className="py-12 text-center space-y-3">
                <RefreshCw className="w-8 h-8 animate-spin mx-auto text-brand-600" />
                <p className="text-sm text-slate-500">Calculating deterministic match factors...</p>
              </div>
            )}

            {!isLoadingMatch && match && (
              <>
                {/* TAB 1: FACTOR BREAKDOWN */}
                {activeTab === 'breakdown' && (
                  <div className="space-y-6">
                    {/* Disclaimer Note */}
                    <div className="bg-slate-50 dark:bg-slate-800/50 rounded-xl p-3.5 border border-slate-200/70 dark:border-slate-800 text-xs text-slate-600 dark:text-slate-400 flex items-start gap-2.5">
                      <Info className="w-4 h-4 text-slate-500 flex-shrink-0 mt-0.5" />
                      <div>
                        This match score is computed using CoachPath&apos;s authoritative 5-factor deterministic scoring algorithm. Factor weights are normalized against available data.
                      </div>
                    </div>

                    {/* Factor Progress Cards */}
                    <div className="space-y-4">
                      <h3 className="text-sm font-bold text-slate-900 dark:text-white flex items-center gap-2">
                        <Layers className="w-4 h-4 text-brand-600" />
                        5-Factor Mathematical Alignment
                      </h3>

                      {/* Factor 1: Skills (50%) */}
                      <div className="bg-white dark:bg-slate-800/60 rounded-xl p-4 border border-slate-200 dark:border-slate-700/80 space-y-2">
                        <div className="flex items-center justify-between">
                          <div>
                            <span className="text-xs font-bold text-slate-900 dark:text-white">
                              Skill Alignment
                            </span>
                            <span className="ml-2 text-[10px] text-slate-500 font-medium">
                              (Weight: 50%)
                            </span>
                          </div>
                          <span className="text-sm font-bold text-brand-600 dark:text-brand-400">
                            {Math.round(breakdown?.skill_score || 0)}%
                          </span>
                        </div>
                        <ProgressBar
                          value={breakdown?.skill_score || 0}
                          variant="brand"
                          size="md"
                        />
                        <p className="text-[11px] text-slate-500 dark:text-slate-400">
                          Evaluates mandatory skills ({match.matched_skills.length} verified of {match.matched_skills.length + match.missing_skills.length} required) plus preferred bonus.
                        </p>
                      </div>

                      {/* Factor 2: Experience (15%) */}
                      <div className="bg-white dark:bg-slate-800/60 rounded-xl p-4 border border-slate-200 dark:border-slate-700/80 space-y-2">
                        <div className="flex items-center justify-between">
                          <div>
                            <span className="text-xs font-bold text-slate-900 dark:text-white">
                              Professional Experience Match
                            </span>
                            <span className="ml-2 text-[10px] text-slate-500 font-medium">
                              (Weight: 15%)
                            </span>
                          </div>
                          <div className="flex items-center gap-2">
                            {breakdown?.unevaluated_factors?.includes('experience') && (
                              <span className="text-[10px] bg-slate-100 dark:bg-slate-700 text-slate-500 px-1.5 py-0.5 rounded">
                                Normalized
                              </span>
                            )}
                            <span className="text-sm font-bold text-brand-600 dark:text-brand-400">
                              {Math.round(breakdown?.experience_score || 0)}%
                            </span>
                          </div>
                        </div>
                        <ProgressBar
                          value={breakdown?.experience_score || 0}
                          variant="verified"
                          size="md"
                        />
                        <p className="text-[11px] text-slate-500 dark:text-slate-400">
                          Compares documented candidate tenure with role seniority requirements (
                          {job.experience_level || 'General'}).
                        </p>
                      </div>

                      {/* Factor 3: Project Evidence (15%) */}
                      <div className="bg-white dark:bg-slate-800/60 rounded-xl p-4 border border-slate-200 dark:border-slate-700/80 space-y-2">
                        <div className="flex items-center justify-between">
                          <div>
                            <span className="text-xs font-bold text-slate-900 dark:text-white">
                              Project Evidence & Artifacts
                            </span>
                            <span className="ml-2 text-[10px] text-slate-500 font-medium">
                              (Weight: 15%)
                            </span>
                          </div>
                          <div className="flex items-center gap-2">
                            {breakdown?.unevaluated_factors?.includes('projects') && (
                              <span className="text-[10px] bg-slate-100 dark:bg-slate-700 text-slate-500 px-1.5 py-0.5 rounded">
                                Normalized
                              </span>
                            )}
                            <span className="text-sm font-bold text-brand-600 dark:text-brand-400">
                              {Math.round(breakdown?.project_score || 0)}%
                            </span>
                          </div>
                        </div>
                        <ProgressBar
                          value={breakdown?.project_score || 0}
                          variant="intelligence"
                          size="md"
                        />
                        <p className="text-[11px] text-slate-500 dark:text-slate-400">
                          Validates practical engineering projects and repository deliverables tagged with required skills.
                        </p>
                      </div>

                      {/* Factor 4: Location & Work Mode (10%) */}
                      <div className="bg-white dark:bg-slate-800/60 rounded-xl p-4 border border-slate-200 dark:border-slate-700/80 space-y-2">
                        <div className="flex items-center justify-between">
                          <div>
                            <span className="text-xs font-bold text-slate-900 dark:text-white">
                              Location & Work Preference
                            </span>
                            <span className="ml-2 text-[10px] text-slate-500 font-medium">
                              (Weight: 10%)
                            </span>
                          </div>
                          <div className="flex items-center gap-2">
                            {breakdown?.unevaluated_factors?.includes('location') && (
                              <span className="text-[10px] bg-slate-100 dark:bg-slate-700 text-slate-500 px-1.5 py-0.5 rounded">
                                Normalized
                              </span>
                            )}
                            <span className="text-sm font-bold text-brand-600 dark:text-brand-400">
                              {Math.round(breakdown?.location_score || 0)}%
                            </span>
                          </div>
                        </div>
                        <ProgressBar
                          value={breakdown?.location_score || 0}
                          variant="action"
                          size="md"
                        />
                        <p className="text-[11px] text-slate-500 dark:text-slate-400">
                          Matches work arrangement ({job.remote_type}) and geographical preference against your profile.
                        </p>
                      </div>

                      {/* Factor 5: Candidate Preferences (10%) */}
                      <div className="bg-white dark:bg-slate-800/60 rounded-xl p-4 border border-slate-200 dark:border-slate-700/80 space-y-2">
                        <div className="flex items-center justify-between">
                          <div>
                            <span className="text-xs font-bold text-slate-900 dark:text-white">
                              Role & Compensation Preferences
                            </span>
                            <span className="ml-2 text-[10px] text-slate-500 font-medium">
                              (Weight: 10%)
                            </span>
                          </div>
                          <div className="flex items-center gap-2">
                            {breakdown?.unevaluated_factors?.includes('preference') && (
                              <span className="text-[10px] bg-slate-100 dark:bg-slate-700 text-slate-500 px-1.5 py-0.5 rounded">
                                Normalized
                              </span>
                            )}
                            <span className="text-sm font-bold text-brand-600 dark:text-brand-400">
                              {Math.round(breakdown?.preference_score || 0)}%
                            </span>
                          </div>
                        </div>
                        <ProgressBar
                          value={breakdown?.preference_score || 0}
                          variant="brand"
                          size="md"
                        />
                        <p className="text-[11px] text-slate-500 dark:text-slate-400">
                          Evaluates target role alignment, industry sectors, and expected salary brackets.
                        </p>
                      </div>
                    </div>
                  </div>
                )}

                {/* TAB 2: SKILL MATRIX */}
                {activeTab === 'skills' && (
                  <div className="space-y-4">
                    {/* Filter Pills */}
                    <div className="flex flex-wrap items-center gap-1.5 pb-2 border-b border-slate-200 dark:border-slate-800">
                      {[
                        { id: 'all', label: `All (${skillsDetail.length})` },
                        { id: 'matched', label: `Matched (${match.matched_skills.length})` },
                        { id: 'missing', label: `Missing (${match.missing_skills.length})` },
                        { id: 'mandatory', label: 'Mandatory' },
                        { id: 'preferred', label: 'Preferred' },
                      ].map((f) => (
                        <button
                          key={f.id}
                          onClick={() => setSkillFilter(f.id)}
                          className={cn(
                            'text-xs px-2.5 py-1 rounded-full font-medium transition-colors',
                            skillFilter === f.id
                              ? 'bg-slate-900 text-white dark:bg-white dark:text-slate-900'
                              : 'bg-slate-100 text-slate-600 hover:bg-slate-200 dark:bg-slate-800 dark:text-slate-300'
                          )}
                        >
                          {f.label}
                        </button>
                      ))}
                    </div>

                    {/* Skill List */}
                    {filteredSkills.length === 0 ? (
                      <p className="text-xs text-slate-500 py-6 text-center">
                        No skills match the selected filter.
                      </p>
                    ) : (
                      <div className="space-y-3">
                        {filteredSkills.map((item) => (
                          <div
                            key={item.skill_id}
                            className={cn(
                              'p-3.5 rounded-xl border bg-white dark:bg-slate-800/80 space-y-2 transition-all',
                              item.classification === 'MATCHED'
                                ? 'border-emerald-200/80 dark:border-emerald-900/50'
                                : item.classification === 'MISSING' && item.is_mandatory
                                ? 'border-rose-200 dark:border-rose-900/50 bg-rose-50/20'
                                : 'border-slate-200 dark:border-slate-700/80'
                            )}
                          >
                            <div className="flex items-start justify-between gap-2">
                              <div>
                                <div className="flex items-center gap-2">
                                  <h4 className="text-xs font-bold text-slate-900 dark:text-white">
                                    {item.name}
                                  </h4>
                                  <span className="text-[10px] text-slate-500 font-medium">
                                    ({item.category})
                                  </span>
                                  {item.is_mandatory ? (
                                    <span className="text-[10px] font-bold text-rose-600 bg-rose-50 dark:bg-rose-950/60 px-1.5 py-0.2 rounded">
                                      Required
                                    </span>
                                  ) : (
                                    <span className="text-[10px] font-medium text-slate-500 bg-slate-100 dark:bg-slate-700 px-1.5 py-0.2 rounded">
                                      Preferred
                                    </span>
                                  )}
                                </div>
                              </div>

                              <div>{getClassificationBadge(item.classification)}</div>
                            </div>

                            {/* Provenance and Explanation */}
                            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pt-1 border-t border-slate-100 dark:border-slate-800 text-xs">
                              <div className="text-[11px] text-slate-600 dark:text-slate-400">
                                {item.explanation}
                              </div>
                              <div className="flex-shrink-0">
                                {getProvenanceBadge(
                                  item.user_evidence_source,
                                  item.assessment_score,
                                  item.user_proficiency_tier
                                )}
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )}

                {/* TAB 3: STRENGTHS & GAPS */}
                {activeTab === 'strengths_gaps' && (
                  <div className="space-y-6">
                    {/* Grounded Summary */}
                    <div className="bg-slate-50 dark:bg-slate-800/60 rounded-xl p-4 border border-slate-200/80 dark:border-slate-700/80 space-y-2">
                      <h4 className="text-xs font-bold text-slate-900 dark:text-white flex items-center gap-1.5">
                        <Sparkles className="w-3.5 h-3.5 text-brand-600" />
                        Hiring Evaluation Rationale
                      </h4>
                      <p className="text-xs text-slate-600 dark:text-slate-300 leading-relaxed">
                        {match.explanation.summary}
                      </p>
                    </div>

                    {/* Strengths */}
                    <div className="space-y-3">
                      <h4 className="text-xs font-bold text-emerald-800 dark:text-emerald-300 flex items-center gap-1.5">
                        <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                        Key Candidate Strengths ({match.explanation.strengths.length})
                      </h4>
                      {match.explanation.strengths.length === 0 ? (
                        <p className="text-xs text-slate-500 italic pl-5">
                          No distinct strengths identified yet. Take diagnostic assessments to verify core competencies.
                        </p>
                      ) : (
                        <div className="space-y-2 pl-2">
                          {match.explanation.strengths.map((str, idx) => (
                            <div
                              key={idx}
                              className="flex items-start gap-2.5 text-xs text-slate-700 dark:text-slate-300 bg-emerald-50/40 dark:bg-emerald-950/20 p-2.5 rounded-lg border border-emerald-100 dark:border-emerald-900/30"
                            >
                              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 mt-1.5 flex-shrink-0" />
                              <span>{str}</span>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>

                    {/* Gaps */}
                    <div className="space-y-3">
                      <h4 className="text-xs font-bold text-rose-800 dark:text-rose-300 flex items-center gap-1.5">
                        <AlertTriangle className="w-4 h-4 text-rose-600" />
                        Identified Skill Gaps & Deficits ({match.explanation.gaps.length})
                      </h4>
                      {match.explanation.gaps.length === 0 ? (
                        <p className="text-xs text-emerald-600 italic pl-5">
                          Excellent: No critical mandatory skill deficits identified for this posting.
                        </p>
                      ) : (
                        <div className="space-y-2 pl-2">
                          {match.explanation.gaps.map((gap, idx) => (
                            <div
                              key={idx}
                              className="flex items-start gap-2.5 text-xs text-slate-700 dark:text-slate-300 bg-rose-50/40 dark:bg-rose-950/20 p-2.5 rounded-lg border border-rose-100 dark:border-rose-900/30"
                            >
                              <span className="w-1.5 h-1.5 rounded-full bg-rose-500 mt-1.5 flex-shrink-0" />
                              <span>{gap}</span>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {/* TAB 4: ACTION PLAN */}
                {activeTab === 'actions' && (
                  <div className="space-y-6">
                    <div className="space-y-2">
                      <h4 className="text-sm font-bold text-slate-900 dark:text-white flex items-center gap-2">
                        <Award className="w-4 h-4 text-brand-600" />
                        Targeted Actions to Maximize Your Match
                      </h4>
                      <p className="text-xs text-slate-500">
                        Follow these grounded CoachPath recommendations to resolve skill gaps and increase your score.
                      </p>
                    </div>

                    {/* Actions List */}
                    <div className="space-y-3">
                      {(match.explanation.recommended_actions || []).map((action, idx) => (
                        <div
                          key={idx}
                          className="p-3.5 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-800/80 space-y-2"
                        >
                          <div className="flex items-start gap-2.5">
                            <span className="w-5 h-5 rounded-full bg-brand-100 dark:bg-brand-950 text-brand-700 dark:text-brand-300 text-xs font-bold flex items-center justify-center flex-shrink-0 mt-0.5">
                              {idx + 1}
                            </span>
                            <p className="text-xs text-slate-800 dark:text-slate-200 font-medium">
                              {action}
                            </p>
                          </div>
                        </div>
                      ))}
                    </div>

                    {/* CoachPath Deep-Links */}
                    <div className="space-y-3 pt-4 border-t border-slate-200 dark:border-slate-800">
                      <h5 className="text-xs font-bold text-slate-700 dark:text-slate-300">
                        CoachPath Ecosystem Deep-Links
                      </h5>
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
                        <Link
                          href="/assessments"
                          className="p-3 rounded-lg border border-slate-200 dark:border-slate-800 hover:border-brand-500 dark:hover:border-brand-500 bg-slate-50/50 dark:bg-slate-800/40 flex items-center justify-between text-xs font-semibold text-slate-800 dark:text-slate-200 transition-colors group"
                        >
                          <div className="flex items-center gap-2">
                            <Award className="w-4 h-4 text-brand-600" />
                            <span>Verify in Assessments</span>
                          </div>
                          <ChevronRight className="w-4 h-4 text-slate-400 group-hover:text-brand-600 transition-colors" />
                        </Link>

                        <Link
                          href="/roadmap"
                          className="p-3 rounded-lg border border-slate-200 dark:border-slate-800 hover:border-brand-500 dark:hover:border-brand-500 bg-slate-50/50 dark:bg-slate-800/40 flex items-center justify-between text-xs font-semibold text-slate-800 dark:text-slate-200 transition-colors group"
                        >
                          <div className="flex items-center gap-2">
                            <BookOpen className="w-4 h-4 text-emerald-600" />
                            <span>Add to Learning Roadmap</span>
                          </div>
                          <ChevronRight className="w-4 h-4 text-slate-400 group-hover:text-emerald-600 transition-colors" />
                        </Link>

                        <Link
                          href="/skills"
                          className="p-3 rounded-lg border border-slate-200 dark:border-slate-800 hover:border-brand-500 dark:hover:border-brand-500 bg-slate-50/50 dark:bg-slate-800/40 flex items-center justify-between text-xs font-semibold text-slate-800 dark:text-slate-200 transition-colors group"
                        >
                          <div className="flex items-center gap-2">
                            <ShieldCheck className="w-4 h-4 text-purple-600" />
                            <span>Skill Gap Analysis</span>
                          </div>
                          <ChevronRight className="w-4 h-4 text-slate-400 group-hover:text-purple-600 transition-colors" />
                        </Link>

                        <Link
                          href="/profile"
                          className="p-3 rounded-lg border border-slate-200 dark:border-slate-800 hover:border-brand-500 dark:hover:border-brand-500 bg-slate-50/50 dark:bg-slate-800/40 flex items-center justify-between text-xs font-semibold text-slate-800 dark:text-slate-200 transition-colors group"
                        >
                          <div className="flex items-center gap-2">
                            <UserCheck className="w-4 h-4 text-amber-600" />
                            <span>Update Career Profile</span>
                          </div>
                          <ChevronRight className="w-4 h-4 text-slate-400 group-hover:text-amber-600 transition-colors" />
                        </Link>
                      </div>
                    </div>
                  </div>
                )}
              </>
            )}
          </div>

          {/* Drawer Footer Actions */}
          <div className="px-6 py-4 border-t border-slate-200 dark:border-slate-800 bg-slate-50/80 dark:bg-slate-900 flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3">
            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={handleRecalculate}
                disabled={isRecalculating}
                className="flex items-center gap-1.5"
              >
                <RefreshCw className={cn('w-3.5 h-3.5', isRecalculating && 'animate-spin')} />
                <span>Recalculate Fit</span>
              </Button>
            </div>

            <div className="flex items-center gap-2">
              {onViewFullJob && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => {
                    onViewFullJob(job);
                  }}
                  className="flex items-center gap-1.5"
                >
                  <FileText className="w-3.5 h-3.5" />
                  <span>Full Job Details</span>
                </Button>
              )}

              {job.source_url && (
                <a
                  href={job.source_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex"
                >
                  <Button size="sm" variant="primary" className="flex items-center gap-1.5">
                    <span>Apply on Site</span>
                    <ExternalLink className="w-3.5 h-3.5" />
                  </Button>
                </a>
              )}

              <Button variant="ghost" size="sm" onClick={onClose}>
                Close
              </Button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
