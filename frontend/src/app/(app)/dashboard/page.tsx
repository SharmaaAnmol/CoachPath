'use client';

import * as React from 'react';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { BentoGrid, BentoCard } from '@/components/ui/bento-grid';
import { StatCard } from '@/components/ui/stat-card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { ProgressBar } from '@/components/ui/progress-bar';
import { Alert } from '@/components/ui/alert';
import { NumberTicker } from '@/components/ui/number-ticker';
import { useAuth } from '@/hooks/use-auth';
import { profileClient } from '@/lib/profile-client';
import { onboardingClient } from '@/lib/onboarding-client';
import { roadmapClient } from '@/lib/roadmap-client';
import { jobMatchingClient } from '@/lib/job-matching-client';
import { assessmentClient } from '@/lib/assessment-client';
import { skillGapClient } from '@/lib/skill-gap-client';
import {
  MasterCareerProfile,
  OnboardingSessionData,
  RoadmapData,
  JobRecommendationItem,
  AssessmentCategoryItem,
  SkillGapAnalysisData,
} from '@/types';
import {
  fadeIn,
  slideUp,
  staggerContainer,
  staggerItem,
} from '@/lib/motion';
import {
  Gauge,
  Cpu,
  Compass,
  Briefcase,
  Sparkles,
  ArrowRight,
  CheckCircle2,
  Clock,
  ExternalLink,
  Target,
  Layers,
  ClipboardCheck,
  ChevronRight,
  ShieldCheck,
  Building2,
  MapPin,
  TrendingUp,
} from 'lucide-react';

export default function DashboardPage() {
  const { user } = useAuth();

  // State hooks for real data integration
  const [profile, setProfile] = React.useState<MasterCareerProfile | null>(null);
  const [onboardingSession, setOnboardingSession] = React.useState<OnboardingSessionData | null>(null);
  const [roadmap, setRoadmap] = React.useState<RoadmapData | null>(null);
  const [jobMatches, setJobMatches] = React.useState<JobRecommendationItem[]>([]);
  const [assessments, setAssessments] = React.useState<AssessmentCategoryItem[]>([]);
  const [skillGap, setSkillGap] = React.useState<SkillGapAnalysisData | null>(null);
  const [isLoading, setIsLoading] = React.useState(true);

  React.useEffect(() => {
    let isMounted = true;

    async function loadDashboardData() {
      setIsLoading(true);

      const promises = [
        profileClient.getMasterProfile().catch(() => null),
        onboardingClient.getSession().catch(() => null),
        roadmapClient.getActiveRoadmap().catch(() => null),
        jobMatchingClient.getRecommendations({ page_size: 3 }).catch(() => null),
        assessmentClient.listAssessments().catch(() => []),
        skillGapClient.getLatestAnalysis().catch(() => null),
      ];

      const [
        profileRes,
        onboardingRes,
        roadmapRes,
        jobsRes,
        assessmentsRes,
        skillGapRes,
      ] = await Promise.all(promises);

      if (isMounted) {
        if (profileRes) setProfile(profileRes as MasterCareerProfile);
        if (onboardingRes) setOnboardingSession(onboardingRes as OnboardingSessionData);
        if (roadmapRes) setRoadmap(roadmapRes as RoadmapData);
        if (jobsRes && (jobsRes as any).items) {
          setJobMatches((jobsRes as any).items);
        }
        if (Array.isArray(assessmentsRes)) {
          setAssessments(assessmentsRes as AssessmentCategoryItem[]);
        }
        if (skillGapRes) setSkillGap(skillGapRes as SkillGapAnalysisData);
        setIsLoading(false);
      }
    }

    loadDashboardData();

    return () => {
      isMounted = false;
    };
  }, []);

  // Derived candidate metrics from real data
  const candidateName = profile?.full_name || user?.full_name || 'Candidate';
  const firstName = candidateName.split(' ')[0];
  const targetRoleTitle =
    profile?.primary_role?.title ||
    roadmap?.target_role_title ||
    skillGap?.role_title ||
    'Target Role Pending';

  const completeness = profile?.completeness_score ?? 35;
  const passedAssessmentsCount = assessments.filter(
    (a) => a.user_status === 'completed' && (a.user_best_score ?? 0) >= a.passing_threshold
  ).length;
  const totalAssessmentsCount = assessments.length || 9;

  // Active roadmap task calculation
  const currentPhase = roadmap?.phases?.find((p) => !p.is_completed) || roadmap?.phases?.[0];
  const activeTask =
    currentPhase?.tasks?.find((t) => t.status === 'in_progress') ||
    currentPhase?.tasks?.find((t) => t.status === 'pending') ||
    currentPhase?.tasks?.[0];

  // Calculated readiness score
  const readinessScore = skillGap?.role_alignment_score ?? (passedAssessmentsCount > 0 ? Math.round((passedAssessmentsCount / totalAssessmentsCount) * 100) : 0);
  const verifiedSkillsCount = (skillGap?.strongest_skills?.length) ?? (profile?.verified_skills_count ?? passedAssessmentsCount);
  const gapSkillsCount = (skillGap?.missing_skills?.length) ?? 0;

  return (
    <motion.div
      initial="hidden"
      animate="visible"
      variants={staggerContainer}
      className="space-y-7 pb-10"
    >
      {/* 1. Hero Hub Banner */}
      <motion.div
        variants={slideUp}
        className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-slate-900 via-indigo-950 to-slate-900 p-6 md:p-8 text-white shadow-elevated border border-slate-800"
      >
        {/* Subtle decorative glow */}
        <div className="absolute top-0 right-0 -mt-10 -mr-10 h-64 w-64 rounded-full bg-brand-500/10 blur-3xl pointer-events-none" />
        <div className="absolute bottom-0 left-1/3 -mb-10 h-48 w-48 rounded-full bg-purple-500/10 blur-3xl pointer-events-none" />

        <div className="relative z-10 flex flex-col lg:flex-row lg:items-center justify-between gap-6">
          <div className="space-y-3 max-w-2xl">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/10 backdrop-blur-md text-indigo-200 text-xs font-mono border border-white/10">
              <Sparkles className="w-3.5 h-3.5 text-indigo-400" />
              <span>{targetRoleTitle}</span>
            </div>
            <h2 className="text-2xl sm:text-3xl lg:text-4xl font-extrabold tracking-tight text-white">
              Welcome back, {firstName}
            </h2>
            <p className="text-sm text-slate-300 leading-relaxed">
              {readinessScore > 0 ? (
                <>
                  Your career readiness is calibrated at{' '}
                  <strong className="text-white font-semibold">
                    <NumberTicker value={readinessScore} suffix="%" />
                  </strong>{' '}
                  across diagnostic skill benchmarks and roadmap milestones.
                </>
              ) : (
                <>
                  Ready to calibrate your engineering profile? Complete your diagnostic assessments and generate your milestone roadmap below.
                </>
              )}
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-3 shrink-0">
            <Link href="/career-readiness">
              <Button variant="intelligence" size="md">
                <Gauge className="w-4 h-4 mr-2" /> View Readiness Hub
              </Button>
            </Link>
            <Link href="/roadmap">
              <Button
                variant="outline"
                size="md"
                className="bg-white/10 border-white/20 text-white hover:bg-white/20"
              >
                <Compass className="w-4 h-4 mr-2" />
                {roadmap ? 'Resume Roadmap' : 'Generate Roadmap'}
              </Button>
            </Link>
          </div>
        </div>
      </motion.div>

      {/* 2. Onboarding Status Banner (if unconfirmed or in-progress) */}
      {onboardingSession && onboardingSession.status !== 'completed' && (
        <motion.div variants={slideUp}>
          <Alert
            variant={onboardingSession.status === 'awaiting_confirmation' ? 'success' : 'intelligence'}
            title={
              onboardingSession.status === 'awaiting_confirmation'
                ? 'AI Career Profile Summary Ready for Confirmation'
                : onboardingSession.status === 'in_progress'
                ? `AI Career Discovery In Progress (Turn ${onboardingSession.turn_count || 1})`
                : 'Complete Your AI Career Discovery Interview'
            }
          >
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mt-1.5">
              <span className="text-xs text-slate-600 dark:text-slate-300">
                {onboardingSession.status === 'awaiting_confirmation'
                  ? 'Your personalized career summary is synthesized and awaiting your confirmation to update your master profile.'
                  : onboardingSession.status === 'in_progress'
                  ? 'Resume your adaptive conversation to identify your strengths and target career goals.'
                  : 'Establish your target engineering path and experience baseline with our adaptive AI interview.'}
              </span>
              <Link href="/onboarding">
                <Button
                  size="sm"
                  variant={onboardingSession.status === 'awaiting_confirmation' ? 'primary' : 'intelligence'}
                >
                  <Sparkles className="w-3.5 h-3.5 mr-1.5" />
                  {onboardingSession.status === 'awaiting_confirmation'
                    ? 'Review & Confirm'
                    : onboardingSession.status === 'in_progress'
                    ? 'Resume Discovery'
                    : 'Start Interview'}
                </Button>
              </Link>
            </div>
          </Alert>
        </motion.div>
      )}

      {/* 3. Top 4 Metric Stat Cards */}
      <motion.div variants={staggerItem} className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Career Readiness"
          value={readinessScore > 0 ? `${readinessScore}%` : 'Pending'}
          subtitle={readinessScore > 0 ? '4-Pillar Calibrated Score' : 'Take assessments to calibrate'}
          icon={<Gauge className="w-5 h-5" />}
          iconColor="intelligence"
          trend={readinessScore > 0 ? { value: `${readinessScore}%`, isPositive: true, label: 'overall' } : undefined}
        />
        <StatCard
          title="Verified Skills"
          value={`${verifiedSkillsCount}`}
          subtitle={`${passedAssessmentsCount} of ${totalAssessmentsCount} tests passed`}
          icon={<Cpu className="w-5 h-5" />}
          iconColor="verified"
          trend={gapSkillsCount > 0 ? { value: `${gapSkillsCount} Gaps`, isPositive: false, label: 'to address' } : undefined}
        />
        <StatCard
          title="Roadmap Sprint"
          value={roadmap ? `${roadmap.progress_percentage || 0}%` : 'Not Started'}
          subtitle={roadmap ? `${roadmap.completed_tasks || 0} of ${roadmap.total_tasks || 0} tasks done` : 'Dynamic milestone plan'}
          icon={<Compass className="w-5 h-5" />}
          iconColor="action"
          trend={roadmap ? { value: `Phase ${roadmap.phases?.filter(p => p.is_completed).length + 1 || 1}`, isPositive: true } : undefined}
        />
        <StatCard
          title="Semantic Job Matches"
          value={jobMatches.length > 0 ? `${jobMatches[0]?.match?.overall_score || 0}%` : `${jobMatches.length} Active`}
          subtitle={jobMatches.length > 0 ? jobMatches[0]?.job?.company_name || 'Top Fit' : 'Matches against live tech roles'}
          icon={<Briefcase className="w-5 h-5" />}
          iconColor="brand"
          trend={jobMatches.length > 0 ? { value: `${jobMatches.length} Matches`, isPositive: true } : undefined}
        />
      </motion.div>

      {/* 4. Bento Grid: High Impact Modular Layout */}
      <motion.div variants={staggerItem}>
        <BentoGrid>
          {/* Bento Card 1: Active Milestone / Roadmap Action (colSpan 2) */}
          <BentoCard colSpan={2} gradient className="space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100 dark:border-slate-800">
              <div className="flex items-center gap-2">
                <div className="p-2 rounded-xl bg-amber-50 dark:bg-amber-950/40 text-amber-600">
                  <Compass className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="text-base font-bold text-slate-900 dark:text-white">
                    {roadmap ? `Current Milestone: ${currentPhase?.title || 'Active Sprint'}` : 'Personalized Milestone Roadmap'}
                  </h3>
                  <p className="text-xs text-slate-500 dark:text-slate-400">
                    {roadmap ? `${roadmap.progress_percentage || 0}% overall sprint completion` : 'AI-structured curriculum tailored to your gap matrix'}
                  </p>
                </div>
              </div>
              <Link href="/roadmap" className="text-xs font-semibold text-brand-600 dark:text-brand-400 hover:underline inline-flex items-center gap-1">
                <span>View Roadmap</span>
                <ChevronRight className="w-3.5 h-3.5" />
              </Link>
            </div>

            {roadmap && activeTask ? (
              <div className="p-4 rounded-2xl bg-amber-50/60 dark:bg-amber-950/20 border border-amber-200/80 dark:border-amber-900/40 space-y-3">
                <div className="flex items-start justify-between gap-3">
                  <div className="space-y-1">
                    <Badge variant="action" size="sm">
                      {activeTask.skill_name || activeTask.task_type || 'Deliverable'} • {activeTask.estimated_hours || 4} hrs
                    </Badge>
                    <h4 className="text-sm font-bold text-slate-900 dark:text-white">
                      {activeTask.title}
                    </h4>
                    <p className="text-xs text-slate-600 dark:text-slate-300 leading-relaxed">
                      {activeTask.description}
                    </p>
                  </div>
                </div>

                <div className="pt-2 flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-t border-amber-200/50 dark:border-amber-900/30 text-xs">
                  <div className="flex items-center gap-1.5 text-slate-600 dark:text-slate-300 truncate">
                    <ExternalLink className="w-3.5 h-3.5 text-amber-600 shrink-0" />
                    <span className="truncate">Deliverable: <strong>{activeTask.title}</strong></span>
                  </div>
                  <Link href="/roadmap">
                    <Button size="sm" variant="primary">
                      Work on Task
                    </Button>
                  </Link>
                </div>
              </div>
            ) : (
              /* Meaningful Zero-Mock Empty State */
              <div className="p-6 rounded-2xl bg-slate-50 dark:bg-slate-900/50 border border-dashed border-slate-200 dark:border-slate-800 text-center space-y-3">
                <div className="h-12 w-12 rounded-2xl bg-brand-50 dark:bg-brand-950/40 text-brand-600 flex items-center justify-center mx-auto">
                  <Target className="w-6 h-6" />
                </div>
                <div className="space-y-1 max-w-md mx-auto">
                  <h4 className="text-sm font-bold text-slate-900 dark:text-white">
                    No active roadmap sprint generated yet
                  </h4>
                  <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed">
                    Generate an adaptive roadmap to receive step-by-step milestones, vetted documentation, and verifiable repository deliverables.
                  </p>
                </div>
                <Link href="/roadmap" className="inline-block pt-1">
                  <Button size="sm" variant="primary">
                    <Sparkles className="w-3.5 h-3.5 mr-1.5" /> Generate Milestone Sprint
                  </Button>
                </Link>
              </div>
            )}
          </BentoCard>

          {/* Bento Card 2: Diagnostic Skill Assessments (colSpan 1) */}
          <BentoCard colSpan={1} className="space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100 dark:border-slate-800">
              <div className="flex items-center gap-2">
                <div className="p-2 rounded-xl bg-purple-50 dark:bg-purple-950/40 text-purple-600">
                  <ClipboardCheck className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="text-sm font-bold text-slate-900 dark:text-white">
                    Skill Diagnostics
                  </h3>
                  <p className="text-[11px] text-slate-500 dark:text-slate-400">
                    Deterministic verification
                  </p>
                </div>
              </div>
              <Link href="/assessments" className="text-xs font-semibold text-brand-600 dark:text-brand-400 hover:underline">
                All Tests
              </Link>
            </div>

            <div className="space-y-2.5">
              <div className="flex items-center justify-between text-xs">
                <span className="text-slate-600 dark:text-slate-400 font-medium">Passed Benchmarks</span>
                <span className="font-bold text-slate-900 dark:text-white">
                  {passedAssessmentsCount} / {totalAssessmentsCount}
                </span>
              </div>
              <ProgressBar
                value={totalAssessmentsCount > 0 ? (passedAssessmentsCount / totalAssessmentsCount) * 100 : 0}
                color="intelligence"
                className="h-2"
              />
            </div>

            <div className="p-3.5 rounded-xl bg-slate-50 dark:bg-slate-800/40 border border-slate-100 dark:border-slate-800 space-y-2 text-xs">
              <div className="font-semibold text-slate-900 dark:text-white flex items-center justify-between">
                <span>Recommended Test</span>
                <Badge variant="intelligence" size="sm">20 Qs</Badge>
              </div>
              <p className="text-slate-500 dark:text-slate-400 text-[11px] leading-relaxed">
                System Design & Distributed Patterns — calibrates your technical architecture score.
              </p>
              <Link href="/assessments" className="block pt-1">
                <Button size="sm" variant="intelligence" className="w-full text-xs">
                  Start Diagnostic
                </Button>
              </Link>
            </div>
          </BentoCard>

          {/* Bento Card 3: Top Semantic Job Matches (colSpan 2) */}
          <BentoCard colSpan={2} className="space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100 dark:border-slate-800">
              <div className="flex items-center gap-2">
                <div className="p-2 rounded-xl bg-indigo-50 dark:bg-indigo-950/40 text-indigo-600">
                  <Briefcase className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="text-base font-bold text-slate-900 dark:text-white">
                    Personalized Job Matches
                  </h3>
                  <p className="text-xs text-slate-500 dark:text-slate-400">
                    Ranked by multi-factor semantic embeddings and verified skill alignment
                  </p>
                </div>
              </div>
              <Link href="/jobs" className="text-xs font-semibold text-brand-600 dark:text-brand-400 hover:underline inline-flex items-center gap-1">
                <span>View All Jobs</span>
                <ChevronRight className="w-3.5 h-3.5" />
              </Link>
            </div>

            {jobMatches.length > 0 ? (
              <div className="space-y-3">
                {jobMatches.slice(0, 2).map((item, idx) => (
                  <div
                    key={item.job?.id || idx}
                    className="p-4 rounded-2xl border border-slate-200/80 dark:border-slate-800/80 hover:border-slate-300 dark:hover:border-slate-700 transition-all flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-white dark:bg-slate-900"
                  >
                    <div className="space-y-1 min-w-0">
                      <div className="flex items-center gap-2 flex-wrap">
                        <span className="text-sm font-bold text-slate-900 dark:text-white truncate">
                          {item.job?.title}
                        </span>
                        <Badge
                          variant={
                            (item.match?.overall_score || 0) >= 80
                              ? 'verified'
                              : (item.match?.overall_score || 0) >= 60
                              ? 'action'
                              : 'default'
                          }
                          size="sm"
                        >
                          {item.match?.overall_score || 85}% Match
                        </Badge>
                      </div>
                      <div className="flex items-center gap-3 text-xs text-slate-500 dark:text-slate-400 flex-wrap">
                        <span className="flex items-center gap-1">
                          <Building2 className="w-3.5 h-3.5 text-slate-400" />
                          {item.job?.company_name}
                        </span>
                        <span className="flex items-center gap-1">
                          <MapPin className="w-3.5 h-3.5 text-slate-400" />
                          {item.job?.location} ({item.job?.remote_type || 'Hybrid'})
                        </span>
                      </div>
                    </div>

                    <Link href={`/jobs/${item.job?.id || ''}`} className="shrink-0">
                      <Button size="sm" variant="outline" className="w-full sm:w-auto">
                        Explain Match
                      </Button>
                    </Link>
                  </div>
                ))}
              </div>
            ) : (
              /* Zero-mock empty state for jobs */
              <div className="p-6 rounded-2xl bg-slate-50 dark:bg-slate-900/50 border border-dashed border-slate-200 dark:border-slate-800 text-center space-y-3">
                <div className="h-12 w-12 rounded-2xl bg-indigo-50 dark:bg-indigo-950/40 text-indigo-600 flex items-center justify-center mx-auto">
                  <Briefcase className="w-6 h-6" />
                </div>
                <div className="space-y-1 max-w-md mx-auto">
                  <h4 className="text-sm font-bold text-slate-900 dark:text-white">
                    No active job matches generated yet
                  </h4>
                  <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed">
                    Set your target role in Career Profile and take a diagnostic test to generate semantic job matches across live engineering listings.
                  </p>
                </div>
                <Link href="/jobs" className="inline-block pt-1">
                  <Button size="sm" variant="outline">
                    Explore Job Feed
                  </Button>
                </Link>
              </div>
            )}
          </BentoCard>

          {/* Bento Card 4: Career Profile Completeness & Action Steps (colSpan 1) */}
          <BentoCard colSpan={1} className="space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100 dark:border-slate-800">
              <div className="flex items-center gap-2">
                <div className="p-2 rounded-xl bg-emerald-50 dark:bg-emerald-950/40 text-emerald-600">
                  <ShieldCheck className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="text-sm font-bold text-slate-900 dark:text-white">
                    Profile Evidence
                  </h3>
                  <p className="text-[11px] text-slate-500 dark:text-slate-400">
                    Truthful career graph
                  </p>
                </div>
              </div>
              <Link href="/career-profile" className="text-xs font-semibold text-brand-600 dark:text-brand-400 hover:underline">
                Profile
              </Link>
            </div>

            <div className="space-y-2">
              <div className="flex items-center justify-between text-xs">
                <span className="text-slate-600 dark:text-slate-400 font-medium">Completeness</span>
                <span className="font-bold text-slate-900 dark:text-white">{completeness.toFixed(0)}%</span>
              </div>
              <ProgressBar value={completeness} color="verified" className="h-2" />
            </div>

            <div className="space-y-2 text-xs pt-1">
              <div className="flex items-center gap-2 text-slate-700 dark:text-slate-300">
                <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
                <span>Account Verified</span>
              </div>
              <div className="flex items-center gap-2 text-slate-700 dark:text-slate-300">
                {profile?.primary_role ? (
                  <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
                ) : (
                  <div className="w-4 h-4 rounded-full border border-slate-300 shrink-0" />
                )}
                <span>Target Role Configured</span>
              </div>
              <div className="flex items-center gap-2 text-slate-700 dark:text-slate-300">
                {passedAssessmentsCount > 0 ? (
                  <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
                ) : (
                  <div className="w-4 h-4 rounded-full border border-slate-300 shrink-0" />
                )}
                <span>Diagnostic Assessment Passed</span>
              </div>
            </div>

            <div className="pt-2">
              <Link href="/resume" className="block">
                <Button size="sm" variant="secondary" className="w-full text-xs">
                  Optimize Resume Diff &rarr;
                </Button>
              </Link>
            </div>
          </BentoCard>
        </BentoGrid>
      </motion.div>
    </motion.div>
  );
}
