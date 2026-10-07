'use client';

import * as React from 'react';
import Link from 'next/link';
import {
  mockProfile,
  mockReadinessData,
  mockRoadmapPhases,
  mockJobs,
  mockScheduledInterviews,
  mockAssessments,
} from '@/lib/mock/data';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { StatCard } from '@/components/ui/stat-card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { ProgressBar } from '@/components/ui/progress-bar';
import { JobCard } from '@/components/ui/job-card';
import { Alert } from '@/components/ui/alert';
import {
  Gauge,
  Cpu,
  Compass,
  Briefcase,
  Sparkles,
  ArrowRight,
  Clock,
  Calendar,
  CheckCircle2,
  FileText,
  HelpCircle,
  ExternalLink,
} from 'lucide-react';

export default function DashboardPage() {
  const currentPhase = mockRoadmapPhases[0];
  const activeTask = currentPhase.tasks.find((t) => t.status === 'in_progress') || currentPhase.tasks[0];
  const upcomingInterview = mockScheduledInterviews[0];
  const topJobs = mockJobs.slice(0, 2);
  const nextAssessment = mockAssessments.find((a) => a.status === 'available');

  return (
    <div className="space-y-6">
      {/* Welcome Banner */}
      <div className="rounded-2xl bg-gradient-to-r from-brand-900 via-slate-900 to-purple-950 p-6 md:p-8 text-white shadow-elevated border border-slate-800 flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div className="space-y-2">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/10 text-purple-200 text-xs font-mono">
            <Sparkles className="w-3.5 h-3.5" />
            <span>Target Role: {mockProfile.targetRole}</span>
          </div>
          <h2 className="text-2xl sm:text-3xl font-extrabold tracking-tight">
            Welcome back, {mockProfile.name.split(' ')[0]}
          </h2>
          <p className="text-sm text-slate-300 max-w-xl leading-relaxed">
            Your career graph is calibrated at <strong className="text-white">{mockReadinessData.overallScore}% Readiness</strong>. You have 1 active milestone task and 1 scheduled interview.
          </p>
        </div>

        <div className="flex items-center gap-3 shrink-0">
          <Link href="/career-readiness">
            <Button variant="intelligence" size="md">
              <Gauge className="w-4 h-4 mr-1.5" /> View Readiness Breakdown
            </Button>
          </Link>
          <Link href="/roadmap">
            <Button variant="outline" size="md" className="bg-white/10 border-white/20 text-white hover:bg-white/20">
              Resume Sprint
            </Button>
          </Link>
        </div>
      </div>

      {/* High-Priority Alert: Scheduled Interview */}
      {upcomingInterview && (
        <Alert
          variant="intelligence"
          title={`Scheduled Interview Tomorrow: ${upcomingInterview.company} (${upcomingInterview.roundType})`}
        >
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mt-1">
            <span className="text-xs">
              Time: <strong>{upcomingInterview.dateTime}</strong> with {upcomingInterview.interviewerName} ({upcomingInterview.interviewerTitle}).
            </span>
            <Link href="/interviews">
              <Button size="sm" variant="intelligence">
                Review STAR Talking Points <ArrowRight className="w-3.5 h-3.5 ml-1" />
              </Button>
            </Link>
          </div>
        </Alert>
      )}

      {/* Top 4 Stat Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Career Readiness Index"
          value={`${mockReadinessData.overallScore}%`}
          subtitle="Tier 1 Qualified (4 Pillars)"
          icon={<Gauge className="w-5 h-5" />}
          iconColor="intelligence"
          trend={{ value: '+6%', isPositive: true, label: 'this month' }}
        />
        <StatCard
          title="Verified Skills"
          value="6 / 12"
          subtitle="Validated via diagnostic tests"
          icon={<Cpu className="w-5 h-5" />}
          iconColor="verified"
          trend={{ value: '3 Gaps', isPositive: false, label: 'to address' }}
        />
        <StatCard
          title="Roadmap Sprint"
          value={`${currentPhase.progressPercentage}%`}
          subtitle="Phase 1: High-Perf Caching"
          icon={<Compass className="w-5 h-5" />}
          iconColor="action"
          trend={{ value: 'Task 3 of 3', isPositive: true }}
        />
        <StatCard
          title="Top Match Rate"
          value="94%"
          subtitle="Stripe Connect Infrastructure"
          icon={<Briefcase className="w-5 h-5" />}
          iconColor="brand"
          trend={{ value: '4 matches', isPositive: true, label: 'active' }}
        />
      </div>

      {/* Main Grid: 2 Columns */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column (2 spans): Active Task & Top Jobs */}
        <div className="lg:col-span-2 space-y-6">
          {/* Active Roadmap Task Card */}
          <Card className="p-6 space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100 dark:border-slate-800">
              <div className="flex items-center gap-2">
                <Compass className="w-5 h-5 text-amber-600" />
                <h3 className="text-base font-bold text-slate-900 dark:text-white">
                  Current Roadmap Milestone: {currentPhase.title}
                </h3>
              </div>
              <Link href="/roadmap" className="text-xs font-semibold text-brand-600 hover:underline">
                View Roadmap &rarr;
              </Link>
            </div>

            <div className="p-4 rounded-xl bg-amber-50/50 dark:bg-amber-950/20 border border-amber-200/80 dark:border-amber-900/40 space-y-3">
              <div className="flex items-start justify-between gap-3">
                <div>
                  <Badge variant="action" size="sm" className="mb-1">
                    {activeTask.category} &bull; {activeTask.estimatedHours} hrs
                  </Badge>
                  <h4 className="text-sm font-bold text-slate-900 dark:text-white">
                    {activeTask.title}
                  </h4>
                  <p className="text-xs text-slate-600 dark:text-slate-300 mt-1 leading-relaxed">
                    {activeTask.description}
                  </p>
                </div>
              </div>

              <div className="pt-2 flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-t border-amber-200/50 dark:border-amber-900/30 text-xs">
                <div className="flex items-center gap-1.5 text-slate-600 dark:text-slate-300">
                  <ExternalLink className="w-3.5 h-3.5 text-amber-600" />
                  <span>Resource: <strong>{activeTask.resourceTitle}</strong></span>
                </div>
                <Link href={activeTask.resourceUrl}>
                  <Button size="sm" variant="primary">
                    Start Deliverable
                  </Button>
                </Link>
              </div>
            </div>

            <div className="space-y-1">
              <div className="flex justify-between text-xs text-slate-500">
                <span>Phase 1 Milestone Progress</span>
                <span className="font-semibold text-slate-700 dark:text-slate-200">{currentPhase.progressPercentage}%</span>
              </div>
              <ProgressBar value={currentPhase.progressPercentage} variant="action" size="sm" />
            </div>
          </Card>

          {/* Top Semantic Job Matches */}
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-base font-bold text-slate-900 dark:text-white">
                  High-Affinity Job Matches
                </h3>
                <p className="text-xs text-slate-500">
                  Ranked by semantic embeddings against your verified skills.
                </p>
              </div>
              <Link href="/jobs" className="text-xs font-semibold text-brand-600 hover:underline">
                Browse All 4 Matches &rarr;
              </Link>
            </div>

            <div className="space-y-4">
              {topJobs.map((job) => (
                <JobCard key={job.id} job={job} />
              ))}
            </div>
          </div>
        </div>

        {/* Right Column (1 span): Quick Action Panels */}
        <div className="space-y-6">
          {/* Diagnostic Assessment Prompt */}
          {nextAssessment && (
            <Card className="p-5 space-y-4 border-purple-200/80 bg-purple-50/20 dark:bg-purple-950/10">
              <div className="flex items-center gap-2 text-purple-700 dark:text-purple-300 font-bold text-sm">
                <Sparkles className="w-4 h-4" />
                <span>Next Diagnostic Assessment</span>
              </div>
              <div>
                <h4 className="text-sm font-bold text-slate-900 dark:text-white">
                  {nextAssessment.title}
                </h4>
                <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
                  Validates: <strong className="text-slate-700 dark:text-slate-300">{nextAssessment.skillName}</strong>
                </p>
              </div>
              <div className="flex items-center justify-between text-xs text-slate-500">
                <span>{nextAssessment.durationMinutes} mins</span>
                <span>{nextAssessment.questionCount} questions</span>
                <Badge variant="action" size="sm">{nextAssessment.difficulty}</Badge>
              </div>
              <Link href="/assessments">
                <Button size="sm" variant="intelligence" className="w-full">
                  Begin Diagnostic Test
                </Button>
              </Link>
            </Card>
          )}

          {/* 4 Pillars Mini-Summary */}
          <Card className="p-5 space-y-4">
            <div className="flex items-center justify-between pb-2 border-b border-slate-100 dark:border-slate-800">
              <h4 className="text-sm font-bold text-slate-900 dark:text-white flex items-center gap-2">
                <Gauge className="w-4 h-4 text-purple-600" />
                Readiness Pillars
              </h4>
              <Link href="/career-readiness" className="text-[11px] font-semibold text-brand-600 hover:underline">
                Details
              </Link>
            </div>

            <div className="space-y-3 text-xs">
              <div>
                <div className="flex justify-between mb-1">
                  <span className="text-slate-600 dark:text-slate-300">Skill Competency (35%)</span>
                  <span className="font-bold text-emerald-600">82%</span>
                </div>
                <ProgressBar value={82} variant="verified" size="sm" />
              </div>
              <div>
                <div className="flex justify-between mb-1">
                  <span className="text-slate-600 dark:text-slate-300">Project Evidence (25%)</span>
                  <span className="font-bold text-indigo-600">75%</span>
                </div>
                <ProgressBar value={75} variant="brand" size="sm" />
              </div>
              <div>
                <div className="flex justify-between mb-1">
                  <span className="text-slate-600 dark:text-slate-300">Market Relevance (25%)</span>
                  <span className="font-bold text-purple-600">85%</span>
                </div>
                <ProgressBar value={85} variant="intelligence" size="sm" />
              </div>
              <div>
                <div className="flex justify-between mb-1">
                  <span className="text-slate-600 dark:text-slate-300">Interview Fluency (15%)</span>
                  <span className="font-bold text-amber-600">70%</span>
                </div>
                <ProgressBar value={70} variant="action" size="sm" />
              </div>
            </div>
          </Card>

          {/* Recent Platform Activity */}
          <Card className="p-5 space-y-3">
            <h4 className="text-sm font-bold text-slate-900 dark:text-white">
              Recent Activity
            </h4>
            <div className="space-y-3 text-xs">
              <div className="flex items-start gap-2.5">
                <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
                <div>
                  <p className="font-semibold text-slate-800 dark:text-slate-200">
                    Passed PostgreSQL Assessment (84%)
                  </p>
                  <span className="text-[10px] text-slate-400">Sep 20, 2026</span>
                </div>
              </div>
              <div className="flex items-start gap-2.5">
                <FileText className="w-4 h-4 text-purple-600 shrink-0 mt-0.5" />
                <div>
                  <p className="font-semibold text-slate-800 dark:text-slate-200">
                    Tailored Resume v2 for Stripe (+12% Boost)
                  </p>
                  <span className="text-[10px] text-slate-400">Oct 5, 2026</span>
                </div>
              </div>
              <div className="flex items-start gap-2.5">
                <Briefcase className="w-4 h-4 text-blue-600 shrink-0 mt-0.5" />
                <div>
                  <p className="font-semibold text-slate-800 dark:text-slate-200">
                    Application Submitted to Linear (91% Match)
                  </p>
                  <span className="text-[10px] text-slate-400">Oct 5, 2026</span>
                </div>
              </div>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}
