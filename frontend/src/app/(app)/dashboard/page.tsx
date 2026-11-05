'use client';

import * as React from 'react';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { GlassButton, GlassEmptyState, GlassPanel, PageHeader, StatusChip } from '@/components/glass';
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
import { staggerContainer, staggerItem } from '@/lib/motion';
import { ArrowRight, Briefcase, Building2, CheckCircle2, Circle, MapPin, Sparkles, Target } from 'lucide-react';

function Meter({ label, value }: { label: string; value: number }) {
  const v = Math.max(0, Math.min(100, Math.round(value)));
  return (
    <li>
      <div className="flex justify-between text-sm">
        <span className="text-ink-muted">{label}</span>
        <span className="tabular-nums">{v}%</span>
      </div>
      <div className="mt-1.5 h-1.5 overflow-hidden rounded-full bg-white/10" role="presentation">
        <div className="h-full rounded-full bg-gradient-to-r from-lav to-lime" style={{ width: `${v}%` }} />
      </div>
    </li>
  );
}

function Stat({ label, value, note, href }: { label: string; value: string; note: string; href: string }) {
  return (
    <Link href={href} className="block rounded-glass">
      <GlassPanel interactive className="h-full p-5">
        <p className="text-xs text-ink-dim">{label}</p>
        <p className="mt-2 font-display text-3xl font-semibold tabular-nums tracking-[-0.03em]">{value}</p>
        <p className="mt-1 text-sm text-ink-muted">{note}</p>
      </GlassPanel>
    </Link>
  );
}

function Check({ done, children }: { done: boolean; children: React.ReactNode }) {
  return (
    <li className="flex items-center gap-2.5 text-sm">
      {done ? <CheckCircle2 className="h-4 w-4 shrink-0 text-lime" /> : <Circle className="h-4 w-4 shrink-0 text-ink-dim" />}
      <span className={done ? 'text-ink-fg' : 'text-ink-muted'}>{children}</span>
      <span className="sr-only">{done ? '(done)' : '(not done)'}</span>
    </li>
  );
}

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

  const roadmapPct = roadmap?.progress_percentage || 0;
  const onboardingOpen = onboardingSession && onboardingSession.status !== 'completed';
  const awaiting = onboardingSession?.status === 'awaiting_confirmation';
  const inProgress = onboardingSession?.status === 'in_progress';

  return (
    <motion.div initial="hidden" animate="visible" variants={staggerContainer} className="flex flex-col gap-6 pb-10">
      <motion.div variants={staggerItem}>
        <PageHeader
          title={`Welcome back, ${firstName}`}
          description={
            readinessScore > 0
              ? `${targetRoleTitle} track. Your career readiness is ${readinessScore}% across skill tests and roadmap milestones.`
              : `${targetRoleTitle}. Take a skill test and generate your roadmap to calibrate your readiness.`
          }
          actions={
            <GlassButton variant="glass" href="/career-readiness">
              View Readiness Hub
            </GlassButton>
          }
        />
      </motion.div>

      {onboardingOpen && (
        <motion.div variants={staggerItem}>
          <GlassPanel className="flex flex-col gap-4 p-5 sm:flex-row sm:items-center sm:justify-between">
            <div className="min-w-0">
              <StatusChip tone={awaiting ? 'done' : 'active'}>{awaiting ? 'Ready to confirm' : 'AI onboarding'}</StatusChip>
              <h2 className="mt-3 font-display text-lg font-semibold tracking-[-0.02em]">
                {awaiting
                  ? 'AI Career Profile Summary Ready for Confirmation'
                  : inProgress
                  ? `AI Career Discovery In Progress (Turn ${onboardingSession?.turn_count || 1})`
                  : 'Complete Your AI Career Discovery Interview'}
              </h2>
              <p className="mt-1 text-sm text-ink-muted">
                {awaiting
                  ? 'Your personalized career summary is ready. Confirm it to update your master profile.'
                  : inProgress
                  ? 'Resume your adaptive conversation to identify your strengths and target career goals.'
                  : 'Set your target engineering path and experience baseline with a short AI interview.'}
              </p>
            </div>
            <GlassButton variant={awaiting ? 'lime' : 'primary'} href="/onboarding" className="shrink-0">
              <Sparkles className="h-4 w-4" />
              {awaiting ? 'Review & Confirm' : inProgress ? 'Resume Discovery' : 'Start Interview'}
            </GlassButton>
          </GlassPanel>
        </motion.div>
      )}

      <motion.div variants={staggerItem} className="grid gap-4 lg:grid-cols-[1.25fr_1fr]">
        {/* The one next step */}
        <GlassPanel className="relative overflow-hidden p-6 sm:p-7">
          <span aria-hidden className="pointer-events-none absolute -right-16 -top-16 h-56 w-56 rounded-full bg-crimson/20 blur-3xl" />
          {roadmap && activeTask ? (
            <>
              <StatusChip tone="alert">Next step</StatusChip>
              <h2 className="mt-4 max-w-lg font-display text-2xl font-semibold leading-tight tracking-[-0.03em] sm:text-[28px]">
                {activeTask.title}
              </h2>
              <p className="mt-2 max-w-lg text-sm leading-relaxed text-ink-muted">
                {[currentPhase?.title, activeTask.skill_name, `about ${activeTask.estimated_hours || 4} hours`].filter(Boolean).join(' · ')}
              </p>
              {activeTask.description && (
                <p className="mt-2 line-clamp-3 max-w-lg text-sm leading-relaxed text-ink-muted">{activeTask.description}</p>
              )}
              <div className="mt-6 flex flex-wrap gap-3">
                <GlassButton variant="lime" href="/roadmap">
                  Work on task <ArrowRight className="h-4 w-4" />
                </GlassButton>
              </div>
            </>
          ) : (
            <>
              <StatusChip tone="alert">Next step</StatusChip>
              <h2 className="mt-4 max-w-lg font-display text-2xl font-semibold leading-tight tracking-[-0.03em] sm:text-[28px]">
                Generate your milestone roadmap
              </h2>
              <p className="mt-2 max-w-lg text-sm leading-relaxed text-ink-muted">
                Get step-by-step milestones, vetted learning material and project deliverables built from your skill gaps.
              </p>
              <div className="mt-6">
                <GlassButton variant="lime" href="/roadmap">
                  Generate roadmap <ArrowRight className="h-4 w-4" />
                </GlassButton>
              </div>
            </>
          )}
        </GlassPanel>

        {/* Readiness */}
        <GlassPanel className="p-6 sm:p-7">
          <div className="flex items-baseline justify-between gap-3">
            <h2 className="font-display text-lg font-semibold tracking-[-0.02em]">Career readiness</h2>
            {gapSkillsCount > 0 && <StatusChip tone="alert">{gapSkillsCount} gaps</StatusChip>}
          </div>
          {readinessScore > 0 ? (
            <p className="mt-3 font-display text-6xl font-semibold tabular-nums tracking-[-0.05em]">
              {readinessScore}
              <span className="text-3xl text-ink-dim">%</span>
            </p>
          ) : (
            <p className="mt-3 font-display text-3xl font-semibold tracking-[-0.03em] text-ink-muted">Not calibrated yet</p>
          )}
          <ul className="mt-5 flex flex-col gap-3">
            <Meter label="Skill tests passed" value={totalAssessmentsCount ? (passedAssessmentsCount / totalAssessmentsCount) * 100 : 0} />
            <Meter label="Roadmap progress" value={roadmapPct} />
            <Meter label="Profile completeness" value={completeness} />
          </ul>
        </GlassPanel>
      </motion.div>

      <motion.div variants={staggerItem} className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <Stat
          label="Verified skills"
          value={`${verifiedSkillsCount}`}
          note={`${passedAssessmentsCount} of ${totalAssessmentsCount} tests passed`}
          href="/skills"
        />
        <Stat
          label="Roadmap"
          value={roadmap ? `${roadmap.completed_tasks || 0} of ${roadmap.total_tasks || 0}` : 'Not started'}
          note={roadmap ? `Tasks done · ${roadmapPct}% complete` : 'Generate a milestone plan'}
          href="/roadmap"
        />
        <Stat
          label="Job matches"
          value={jobMatches.length > 0 ? `${jobMatches[0]?.match?.overall_score ?? 0}%` : '0'}
          note={jobMatches.length > 0 ? `Best fit · ${jobMatches[0]?.job?.company_name || 'top match'}` : 'Matches against live tech roles'}
          href="/jobs"
        />
      </motion.div>

      <motion.div variants={staggerItem}>
        {jobMatches.length > 0 ? (
          <GlassPanel className="p-2 sm:p-3">
            <div className="flex items-center justify-between px-4 pb-2 pt-3">
              <h2 className="font-display text-lg font-semibold tracking-[-0.02em]">Top job matches</h2>
              <GlassButton variant="ghost" size="sm" href="/jobs">
                View all jobs
              </GlassButton>
            </div>
            <ul>
              {jobMatches.slice(0, 3).map((item, idx) => {
                const fit = item.match?.overall_score ?? 0;
                return (
                  <li key={item.job?.id || idx}>
                    <Link
                      href={`/jobs/${item.job?.id || ''}`}
                      className="flex items-center gap-4 rounded-2xl px-4 py-4 transition-colors duration-200 hover:bg-white/[0.04]"
                    >
                      <span className="grid h-10 w-10 shrink-0 place-items-center rounded-xl border border-white/10 bg-white/5">
                        <Building2 className="h-4 w-4 text-ink-muted" />
                      </span>
                      <span className="min-w-0 flex-1">
                        <span className="block font-medium">
                          {item.job?.title}
                          {item.job?.company_name ? ` · ${item.job.company_name}` : ''}
                        </span>
                        <span className="flex items-center gap-1 text-sm text-ink-dim">
                          <MapPin className="h-3.5 w-3.5 shrink-0" />
                          {[item.job?.location, item.job?.remote_type].filter(Boolean).join(' · ') || 'Location not listed'}
                        </span>
                      </span>
                      <span className="text-right">
                        <span className={`block font-display text-xl font-semibold tabular-nums ${fit >= 80 ? 'text-lime' : 'text-lav'}`}>
                          {fit}%
                        </span>
                        <span className="block text-xs text-ink-dim">fit</span>
                      </span>
                    </Link>
                  </li>
                );
              })}
            </ul>
          </GlassPanel>
        ) : (
          <GlassEmptyState
            icon={<Briefcase className="h-5 w-5" />}
            title="No job matches yet"
            description="Set your target role in Career Profile and take a skill test to get matches across live engineering listings."
            action={<GlassButton variant="glass" href="/jobs">Explore job feed</GlassButton>}
          />
        )}
      </motion.div>

      <motion.div variants={staggerItem} className="grid gap-4 md:grid-cols-2">
        <GlassPanel className="flex flex-col p-6">
          <div className="flex items-center justify-between">
            <h2 className="font-display text-lg font-semibold tracking-[-0.02em]">Skill tests</h2>
            <GlassButton variant="ghost" size="sm" href="/assessments">
              All tests
            </GlassButton>
          </div>
          <p className="mt-3 font-display text-4xl font-semibold tabular-nums tracking-[-0.04em]">
            {passedAssessmentsCount}
            <span className="text-xl text-ink-dim"> / {totalAssessmentsCount} passed</span>
          </p>
          <p className="mt-3 text-sm text-ink-muted">
            Recommended: System Design & Distributed Patterns, 20 questions. It calibrates your architecture score.
          </p>
          <div className="mt-auto pt-5">
            <GlassButton variant="primary" href="/assessments">
              <Target className="h-4 w-4" /> Start a test
            </GlassButton>
          </div>
        </GlassPanel>

        <GlassPanel className="flex flex-col p-6">
          <div className="flex items-center justify-between">
            <h2 className="font-display text-lg font-semibold tracking-[-0.02em]">Profile evidence</h2>
            <span className="text-sm tabular-nums text-ink-muted">{completeness.toFixed(0)}% complete</span>
          </div>
          <ul className="mt-4 flex flex-col gap-2.5">
            <Check done>Account verified</Check>
            <Check done={!!profile?.primary_role}>Target role set</Check>
            <Check done={passedAssessmentsCount > 0}>A skill test passed</Check>
          </ul>
          <div className="mt-auto flex flex-wrap gap-3 pt-5">
            <GlassButton variant="glass" href="/resume">
              Optimize resume
            </GlassButton>
            <GlassButton variant="ghost" href="/career-profile">
              Edit profile
            </GlassButton>
          </div>
        </GlassPanel>
      </motion.div>
    </motion.div>
  );
}
