'use client';

import * as React from 'react';
import Link from 'next/link';
import { mockReadinessData } from '@/lib/mock/data';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { ProgressBar } from '@/components/ui/progress-bar';
import { DemoPreviewBanner } from '@/components/ui/demo-preview-banner';
import {
  Gauge,
  ShieldCheck,
  Cpu,
  FolderGit2,
  Briefcase,
  MessageSquareCode,
  CheckCircle2,
  AlertCircle,
  ArrowRight,
  Sparkles,
} from 'lucide-react';

export default function CareerReadinessPage() {
  const { pillars, overallScore, keyMilestonesCompleted, totalKeyMilestones } = mockReadinessData;

  const pillarCards = [
    {
      key: 'skillVerification',
      pillar: pillars.skillVerification,
      icon: Cpu,
      color: 'emerald',
      barVariant: 'verified' as const,
    },
    {
      key: 'practicalProjects',
      pillar: pillars.practicalProjects,
      icon: FolderGit2,
      color: 'indigo',
      barVariant: 'brand' as const,
    },
    {
      key: 'marketRelevance',
      pillar: pillars.marketRelevance,
      icon: Briefcase,
      color: 'purple',
      barVariant: 'intelligence' as const,
    },
    {
      key: 'interviewFluency',
      pillar: pillars.interviewFluency,
      icon: MessageSquareCode,
      color: 'amber',
      barVariant: 'action' as const,
    },
  ];

  return (
    <div className="space-y-6">
      {/* Demo Preview Banner */}
      <DemoPreviewBanner
        plannedPhase="Phase 15"
        featureName="Real-time career readiness calculation"
      />

      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="font-display text-3xl font-semibold tracking-[-0.035em] text-slate-900 dark:text-ink-fg [text-wrap:balance] md:text-4xl">
              Career Readiness Index
            </h1>
            <Badge variant="verified" size="sm">
              <ShieldCheck className="w-3.5 h-3.5 mr-1" /> Calibrated
            </Badge>
          </div>
          <p className="text-xs text-slate-500 dark:text-ink-muted mt-1">
            Deterministic index calculated from 4 objective pillars for target role <strong className="text-purple-600 dark:text-lav">Full-Stack Engineer</strong>.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Link href="/roadmap">
            <Button size="sm" variant="primary">
              View Action Plan <ArrowRight className="w-3.5 h-3.5 ml-1" />
            </Button>
          </Link>
        </div>
      </div>

      {/* Hero Score Card */}
      <Card className="p-6 md:p-8 bg-gradient-to-r from-purple-900 via-slate-900 to-indigo-950 text-white border-slate-800 shadow-elevated">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="flex items-center gap-6">
            <div className="h-24 w-24 rounded-3xl bg-gradient-to-tr from-purple-600 to-brand-500 flex flex-col items-center justify-center font-extrabold shadow-lg shrink-0">
              <span className="text-4xl leading-none">{overallScore}%</span>
              <span className="text-[10px] uppercase font-mono tracking-wider text-purple-200 mt-1 dark:text-lav-light">
                Index
              </span>
            </div>

            <div className="space-y-1.5">
              <div className="flex items-center gap-2">
                <span className="text-xl font-bold">Tier 1 Market Qualified</span>
                <span className="text-xs font-mono px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 dark:bg-lime/20 dark:text-lime-soft dark:border-lime/50">
                  Top Quartile
                </span>
              </div>
              <p className="text-xs text-slate-300 max-w-xl leading-relaxed">
                Your profile demonstrates high verified proficiency in core full-stack competencies. Completing the remaining caching and event streaming tasks will elevate your index past 85%.
              </p>
              <div className="pt-1 text-xs font-mono text-purple-300 dark:text-lav-light">
                Key Milestones Achieved: <strong>{keyMilestonesCompleted} of {totalKeyMilestones}</strong>
              </div>
            </div>
          </div>
        </div>
      </Card>

      {/* 4 Constituent Pillars Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {pillarCards.map(({ key, pillar, icon: Icon, color, barVariant }) => (
          <Card key={key} className="p-6 space-y-4 hover:border-slate-300 transition-all">
            <div className="flex items-start justify-between gap-4 pb-3 border-b border-slate-100 dark:border-white/10">
              <div className="flex items-center gap-3">
                <div className={`p-2.5 rounded-xl bg-${color}-50 text-${color}-600 dark:bg-${color}-950/40 dark:text-${color}-400`}>
                  <Icon className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="text-base font-bold dark:font-display dark:font-semibold dark:tracking-[-0.02em] text-slate-900 dark:text-white">
                    {pillar.name}
                  </h3>
                  <span className="text-xs text-slate-400">
                    Formula Weight: <strong>{Math.round(pillar.weight * 100)}%</strong>
                  </span>
                </div>
              </div>

              <div className="text-right">
                <div className="text-2xl font-extrabold text-slate-900 dark:text-white">
                  {pillar.score}%
                </div>
                <Badge
                  variant={pillar.status === 'strong' ? 'verified' : 'action'}
                  size="sm"
                >
                  {pillar.status === 'strong' ? 'Strong' : 'Moderate'}
                </Badge>
              </div>
            </div>

            <ProgressBar value={pillar.score} variant={barVariant} size="sm" />

            <p className="text-xs text-slate-600 dark:text-ink-fg/80 leading-relaxed">
              {pillar.summary}
            </p>

            {/* Actionable Recommendations */}
            <div className="p-3.5 rounded-xl bg-slate-50 dark:bg-white/[0.07] border border-slate-200/80 dark:border-white/15 space-y-2 text-xs">
              <span className="font-bold text-slate-700 dark:text-ink-fg/80 uppercase tracking-wider text-[10px]">
                Recommended Actions to Maximize Score:
              </span>
              <ul className="space-y-1.5 text-slate-600 dark:text-ink-muted">
                {pillar.recommendations.map((rec, rIdx) => (
                  <li key={rIdx} className="flex items-start gap-2">
                    <CheckCircle2 className="w-3.5 h-3.5 text-brand-600 shrink-0 mt-0.5 dark:text-lav" />
                    <span>{rec}</span>
                  </li>
                ))}
              </ul>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
}
