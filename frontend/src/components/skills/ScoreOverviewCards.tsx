'use client';

import * as React from 'react';
import { SkillGapAnalysisData } from '@/types';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import {
  Target,
  ShieldCheck,
  HelpCircle,
  TrendingUp,
  CheckCircle2,
  Clock,
  AlertCircle,
  FileQuestion,
  HelpCircleIcon,
  RotateCcw,
  Sparkles,
} from 'lucide-react';

interface ScoreOverviewCardsProps {
  analysis: SkillGapAnalysisData;
  onOpenExplanation: () => void;
  onRecalculate?: () => void;
  isRecalculating?: boolean;
}

export function ScoreOverviewCards({
  analysis,
  onOpenExplanation,
  onRecalculate,
  isRecalculating = false,
}: ScoreOverviewCardsProps) {
  const alignment = analysis.role_alignment_score;
  const coverage = analysis.evidence_coverage_score;

  // Visual color for alignment score
  const getAlignmentColor = (score: number) => {
    if (score >= 75) return { stroke: '#10b981', text: 'text-emerald-600 dark:text-emerald-400', bg: 'bg-emerald-50 dark:bg-emerald-950/40', border: 'border-emerald-200 dark:border-emerald-800' };
    if (score >= 50) return { stroke: '#6366f1', text: 'text-indigo-600 dark:text-indigo-400', bg: 'bg-indigo-50 dark:bg-indigo-950/40', border: 'border-indigo-200 dark:border-indigo-800' };
    if (score >= 25) return { stroke: '#f59e0b', text: 'text-amber-600 dark:text-amber-400', bg: 'bg-amber-50 dark:bg-amber-950/40', border: 'border-amber-200 dark:border-amber-800' };
    return { stroke: '#f43f5e', text: 'text-rose-600 dark:text-rose-400', bg: 'bg-rose-50 dark:bg-rose-950/40', border: 'border-rose-200 dark:border-rose-800' };
  };

  const getCoverageColor = (score: number) => {
    if (score >= 75) return { stroke: '#10b981', text: 'text-emerald-600 dark:text-emerald-400', bg: 'bg-emerald-50 dark:bg-emerald-950/40', border: 'border-emerald-200 dark:border-emerald-800' };
    if (score >= 50) return { stroke: '#0ea5e9', text: 'text-sky-600 dark:text-sky-400', bg: 'bg-sky-50 dark:bg-sky-950/40', border: 'border-sky-200 dark:border-sky-800' };
    if (score >= 25) return { stroke: '#f59e0b', text: 'text-amber-600 dark:text-amber-400', bg: 'bg-amber-50 dark:bg-amber-950/40', border: 'border-amber-200 dark:border-amber-800' };
    return { stroke: '#94a3b8', text: 'text-slate-600 dark:text-slate-400', bg: 'bg-slate-50 dark:bg-slate-900', border: 'border-slate-200 dark:border-slate-800' };
  };

  const alignColors = getAlignmentColor(alignment);
  const covColors = getCoverageColor(coverage);

  // SVG circular gauge helper
  const radius = 38;
  const circumference = 2 * Math.PI * radius;
  const alignStrokeDashoffset = circumference - (alignment / 100) * circumference;
  const covStrokeDashoffset = circumference - (coverage / 100) * circumference;

  const totalRequired = Object.keys(analysis.skill_details).length;
  const strengthsCount = analysis.strongest_skills.length;
  const developingCount = analysis.developing_skills.length;
  const gapsCount = analysis.skill_gaps.length;
  const unassessedCount = analysis.unassessed_skills.length;
  const missingCount = analysis.missing_skills.length;

  return (
    <div className="space-y-4">
      {/* Primary Score Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* 1. Documented Role Alignment Card */}
        <Card className={`p-5 border transition-all ${alignColors.border} bg-white dark:bg-slate-900 relative overflow-hidden shadow-sm`}>
          <div className="flex items-start justify-between">
            <div className="space-y-1 pr-4">
              <div className="flex items-center gap-2">
                <span className="p-1.5 rounded-lg bg-indigo-50 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-400">
                  <Target className="w-4 h-4" />
                </span>
                <h3 className="text-xs font-bold tracking-wider uppercase text-slate-700 dark:text-slate-300">
                  Documented Role Alignment
                </h3>
                <button
                  type="button"
                  onClick={onOpenExplanation}
                  className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 transition-colors"
                  aria-label="Explain Role Alignment Score"
                >
                  <HelpCircle className="w-3.5 h-3.5" />
                </button>
              </div>
              <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed">
                Evaluates how thoroughly your verified proficiency matches benchmark standards for{' '}
                <strong className="text-slate-800 dark:text-slate-200">{analysis.role_title}</strong>.
              </p>
            </div>

            {/* Circular Gauge */}
            <div className="relative shrink-0 w-24 h-24 flex items-center justify-center">
              <svg className="w-24 h-24 transform -rotate-90" viewBox="0 0 96 96">
                <circle
                  cx="48"
                  cy="48"
                  r={radius}
                  className="stroke-slate-100 dark:stroke-slate-800"
                  strokeWidth="7"
                  fill="transparent"
                />
                <circle
                  cx="48"
                  cy="48"
                  r={radius}
                  stroke={alignColors.stroke}
                  strokeWidth="7"
                  strokeDasharray={circumference}
                  strokeDashoffset={alignStrokeDashoffset}
                  strokeLinecap="round"
                  fill="transparent"
                  className="transition-all duration-1000 ease-out"
                />
              </svg>
              <div className="absolute inset-0 flex flex-col items-center justify-center">
                <span className={`text-xl font-black ${alignColors.text}`}>
                  {alignment.toFixed(1)}%
                </span>
                <span className="text-[10px] uppercase font-bold text-slate-400">Alignment</span>
              </div>
            </div>
          </div>

          <div className="mt-4 pt-3 border-t border-slate-100 dark:border-slate-800 flex items-center justify-between text-xs">
            <span className="text-slate-500 dark:text-slate-400">
              {alignment >= 75
                ? 'High Benchmark Readiness'
                : alignment >= 50
                ? 'Moderate Alignment with Key Gaps'
                : alignment > 0
                ? 'Developing Foundational Competency'
                : 'Zero Validated Competencies'}
            </span>
            <span className="text-[11px] font-semibold text-indigo-600 dark:text-indigo-400">
              Deterministic Scale
            </span>
          </div>
        </Card>

        {/* 2. Evidence Coverage Card */}
        <Card className={`p-5 border transition-all ${covColors.border} bg-white dark:bg-slate-900 relative overflow-hidden shadow-sm`}>
          <div className="flex items-start justify-between">
            <div className="space-y-1 pr-4">
              <div className="flex items-center gap-2">
                <span className="p-1.5 rounded-lg bg-emerald-50 dark:bg-emerald-950/60 text-emerald-600 dark:text-emerald-400">
                  <ShieldCheck className="w-4 h-4" />
                </span>
                <h3 className="text-xs font-bold tracking-wider uppercase text-slate-700 dark:text-slate-300">
                  Evidence Coverage
                </h3>
                <button
                  type="button"
                  onClick={onOpenExplanation}
                  className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 transition-colors"
                  aria-label="Explain Evidence Coverage Score"
                >
                  <HelpCircle className="w-3.5 h-3.5" />
                </button>
              </div>
              <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed">
                Percentage of required competencies backed by objective diagnostic tests or verified projects.
              </p>
            </div>

            {/* Circular Gauge */}
            <div className="relative shrink-0 w-24 h-24 flex items-center justify-center">
              <svg className="w-24 h-24 transform -rotate-90" viewBox="0 0 96 96">
                <circle
                  cx="48"
                  cy="48"
                  r={radius}
                  className="stroke-slate-100 dark:stroke-slate-800"
                  strokeWidth="7"
                  fill="transparent"
                />
                <circle
                  cx="48"
                  cy="48"
                  r={radius}
                  stroke={covColors.stroke}
                  strokeWidth="7"
                  strokeDasharray={circumference}
                  strokeDashoffset={covStrokeDashoffset}
                  strokeLinecap="round"
                  fill="transparent"
                  className="transition-all duration-1000 ease-out"
                />
              </svg>
              <div className="absolute inset-0 flex flex-col items-center justify-center">
                <span className={`text-xl font-black ${covColors.text}`}>
                  {coverage.toFixed(1)}%
                </span>
                <span className="text-[10px] uppercase font-bold text-slate-400">Coverage</span>
              </div>
            </div>
          </div>

          <div className="mt-4 pt-3 border-t border-slate-100 dark:border-slate-800 flex items-center justify-between text-xs">
            <span className="text-slate-500 dark:text-slate-400">
              {unassessedCount > 0
                ? `${unassessedCount} skill${unassessedCount > 1 ? 's' : ''} require diagnostic testing`
                : 'All relevant skills assessed'}
            </span>
            <span className="text-[11px] font-semibold text-emerald-600 dark:text-emerald-400">
              Objective Backing
            </span>
          </div>
        </Card>
      </div>

      {/* Competency Distribution Metrics Bar */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2.5">
        <div className="p-3 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 flex flex-col justify-between">
          <span className="text-[11px] font-medium text-slate-500 dark:text-slate-400">Total Required</span>
          <span className="text-lg font-black text-slate-900 dark:text-white mt-1">{totalRequired}</span>
        </div>

        <div className="p-3 rounded-xl border border-emerald-200 dark:border-emerald-800/60 bg-emerald-50/20 dark:bg-emerald-950/20 flex flex-col justify-between">
          <div className="flex items-center gap-1.5 text-emerald-700 dark:text-emerald-300">
            <CheckCircle2 className="w-3.5 h-3.5" />
            <span className="text-[11px] font-semibold">Strengths</span>
          </div>
          <span className="text-lg font-black text-emerald-700 dark:text-emerald-300 mt-1">{strengthsCount}</span>
        </div>

        <div className="p-3 rounded-xl border border-amber-200 dark:border-amber-800/60 bg-amber-50/20 dark:bg-amber-950/20 flex flex-col justify-between">
          <div className="flex items-center gap-1.5 text-amber-700 dark:text-amber-300">
            <Clock className="w-3.5 h-3.5" />
            <span className="text-[11px] font-semibold">Developing</span>
          </div>
          <span className="text-lg font-black text-amber-700 dark:text-amber-300 mt-1">{developingCount}</span>
        </div>

        <div className="p-3 rounded-xl border border-rose-200 dark:border-rose-800/60 bg-rose-50/20 dark:bg-rose-950/20 flex flex-col justify-between">
          <div className="flex items-center gap-1.5 text-rose-700 dark:text-rose-300">
            <AlertCircle className="w-3.5 h-3.5" />
            <span className="text-[11px] font-semibold">Gaps</span>
          </div>
          <span className="text-lg font-black text-rose-700 dark:text-rose-300 mt-1">{gapsCount}</span>
        </div>

        <div className="p-3 rounded-xl border border-purple-200 dark:border-purple-800/60 bg-purple-50/20 dark:bg-purple-950/20 flex flex-col justify-between">
          <div className="flex items-center gap-1.5 text-purple-700 dark:text-purple-300">
            <FileQuestion className="w-3.5 h-3.5" />
            <span className="text-[11px] font-semibold">Unassessed</span>
          </div>
          <span className="text-lg font-black text-purple-700 dark:text-purple-300 mt-1">{unassessedCount}</span>
        </div>

        <div className="p-3 rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-800/40 flex flex-col justify-between">
          <div className="flex items-center gap-1.5 text-slate-600 dark:text-slate-400">
            <HelpCircleIcon className="w-3.5 h-3.5" />
            <span className="text-[11px] font-semibold">Missing</span>
          </div>
          <span className="text-lg font-black text-slate-700 dark:text-slate-300 mt-1">{missingCount}</span>
        </div>
      </div>
    </div>
  );
}
