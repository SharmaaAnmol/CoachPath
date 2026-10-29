'use client';

import * as React from 'react';
import { MarketIntelligenceData } from '@/types';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import {
  TrendingUp,
  BarChart3,
  DollarSign,
  Globe,
  Briefcase,
  AlertCircle,
  X,
  Sparkles,
} from 'lucide-react';

export interface MarketIntelligenceCardProps {
  data: MarketIntelligenceData | null;
  isLoading: boolean;
  selectedRoleId?: string;
  onRoleChange?: (roleId: string) => void;
  onClose?: () => void;
  className?: string;
}

const CANONICAL_ROLES = [
  { id: '', label: 'All Tech Roles' },
  { id: 'backend-developer', label: 'Backend Developer' },
  { id: 'frontend-developer', label: 'Frontend Developer' },
  { id: 'fullstack-developer', label: 'Fullstack Developer' },
  { id: 'data-engineer', label: 'Data Engineer' },
  { id: 'mobile-engineer', label: 'Mobile Engineer' },
  { id: 'data-scientist', label: 'Data Scientist' },
  { id: 'machine-learning-engineer', label: 'ML Engineer' },
  { id: 'ai-engineer', label: 'AI Engineer' },
  { id: 'devops-cloud-engineer', label: 'DevOps & Cloud' },
  { id: 'software-engineer', label: 'Software Engineer' },
  { id: 'data-analyst', label: 'Data Analyst' },
];

export function MarketIntelligenceCard({
  data,
  isLoading,
  selectedRoleId,
  onRoleChange,
  onClose,
  className,
}: MarketIntelligenceCardProps) {
  if (isLoading) {
    return (
      <Card className="p-6 space-y-4 animate-pulse">
        <div className="h-6 w-1/3 bg-slate-200 dark:bg-slate-700 rounded-lg" />
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="h-16 bg-slate-100 dark:bg-slate-800 rounded-xl" />
          ))}
        </div>
      </Card>
    );
  }

  if (!data) return null;

  const total = data.total_active_jobs || 0;
  const remotePercent = total > 0 && data.remote_distribution['remote']
    ? Math.round((data.remote_distribution['remote'] / total) * 100)
    : 0;
  const hybridPercent = total > 0 && data.remote_distribution['hybrid']
    ? Math.round((data.remote_distribution['hybrid'] / total) * 100)
    : 0;

  return (
    <Card className="p-5 sm:p-6 space-y-5 bg-gradient-to-br from-white via-slate-50/50 to-indigo-50/20 dark:from-slate-900 dark:via-slate-900/90 dark:to-indigo-950/20 border-slate-200/90 dark:border-slate-800">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-slate-100 dark:border-slate-800">
        <div className="space-y-0.5">
          <div className="flex items-center gap-2">
            <h3 className="text-base sm:text-lg font-bold text-slate-900 dark:text-white flex items-center gap-2">
              <BarChart3 className="w-5 h-5 text-brand-600 dark:text-brand-400" />
              Verified Market Intelligence & Skill Demand
            </h3>
            <Badge variant="intelligence" size="sm">
              Phase 8A Ground Truth
            </Badge>
          </div>
          <p className="text-xs text-slate-500 dark:text-slate-400">
            Real-time empirical aggregates computed across {total} verified catalog opportunities.
          </p>
        </div>

        <div className="flex items-center gap-2">
          {onRoleChange && (
            <select
              value={selectedRoleId || ''}
              onChange={(e) => onRoleChange(e.target.value)}
              className="text-xs px-2.5 py-1.5 rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900 text-slate-800 dark:text-slate-200"
            >
              {CANONICAL_ROLES.map((r) => (
                <option key={r.id} value={r.id}>
                  {r.label}
                </option>
              ))}
            </select>
          )}

          {onClose && (
            <button
              onClick={onClose}
              className="p-1.5 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 rounded-lg"
              aria-label="Close market intelligence view"
            >
              <X className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>

      {/* Provisional Sample Size Notice */}
      {data.is_provisional && (
        <div className="p-3 rounded-xl border border-amber-200 bg-amber-50/70 dark:border-amber-900/40 dark:bg-amber-950/20 text-xs flex items-start gap-2.5">
          <AlertCircle className="w-4 h-4 text-amber-600 shrink-0 mt-0.5" />
          <div className="space-y-0.5">
            <span className="font-semibold text-amber-900 dark:text-amber-200">
              Provisional Market Indicator (Sample Size: {total} Positions)
            </span>
            <p className="text-amber-800 dark:text-amber-300 text-[11px] leading-relaxed">
              {data.provisional_reason ||
                'This sample is actively developing as more permitted sources are ingested. Aggregates represent initial benchmark indicators rather than full market consensus.'}
            </p>
          </div>
        </div>
      )}

      {/* Overview Stat Metrics */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <div className="p-3.5 rounded-xl bg-white dark:bg-slate-800/80 border border-slate-200/80 dark:border-slate-700/80 shadow-xs">
          <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">
            Active Verified Jobs
          </span>
          <span className="text-xl sm:text-2xl font-extrabold text-slate-900 dark:text-white mt-1 block">
            {total}
          </span>
        </div>

        <div className="p-3.5 rounded-xl bg-white dark:bg-slate-800/80 border border-slate-200/80 dark:border-slate-700/80 shadow-xs">
          <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">
            Median Base Salary
          </span>
          <span className="text-xl sm:text-2xl font-extrabold text-emerald-600 dark:text-emerald-400 mt-1 block">
            {data.salary_insights.median_salary
              ? `$${Math.round(data.salary_insights.median_salary / 1000)}k`
              : 'N/A'}
          </span>
          <span className="text-[10px] text-slate-400 block mt-0.5">
            Sample: {data.salary_insights.sample_size} jobs
          </span>
        </div>

        <div className="p-3.5 rounded-xl bg-white dark:bg-slate-800/80 border border-slate-200/80 dark:border-slate-700/80 shadow-xs">
          <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">
            Remote & Hybrid Share
          </span>
          <span className="text-xl sm:text-2xl font-extrabold text-brand-600 dark:text-brand-400 mt-1 block">
            {remotePercent + hybridPercent}%
          </span>
          <span className="text-[10px] text-slate-400 block mt-0.5">
            {remotePercent}% Fully Remote
          </span>
        </div>

        <div className="p-3.5 rounded-xl bg-white dark:bg-slate-800/80 border border-slate-200/80 dark:border-slate-700/80 shadow-xs">
          <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">
            Top In-Demand Skill
          </span>
          <span className="text-lg sm:text-xl font-extrabold text-purple-600 dark:text-purple-400 mt-1 block truncate">
            {data.top_demanded_skills[0]?.name || 'Python'}
          </span>
          <span className="text-[10px] text-slate-400 block mt-0.5">
            In {data.top_demanded_skills[0]?.percentage || 0}% of listings
          </span>
        </div>
      </div>

      {/* In-Demand Technical Skills Leaderboard */}
      <div className="space-y-3 pt-2">
        <h4 className="text-xs font-bold text-slate-800 dark:text-slate-200 uppercase tracking-wider flex items-center justify-between">
          <span>Top Requested Canonical Skills</span>
          <span className="text-slate-400 font-normal">Ranked by listing frequency</span>
        </h4>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
          {data.top_demanded_skills.slice(0, 8).map((skill, index) => (
            <div
              key={skill.skill_id}
              className="p-3 rounded-xl bg-white dark:bg-slate-800/60 border border-slate-200/70 dark:border-slate-700/70 space-y-1.5"
            >
              <div className="flex items-center justify-between font-semibold">
                <span className="text-slate-900 dark:text-white flex items-center gap-1.5">
                  <span className="w-4 text-slate-400 text-[11px] font-mono">#{index + 1}</span>
                  {skill.name}
                </span>
                <span className="text-brand-600 dark:text-brand-400 font-mono text-[11px]">
                  {skill.percentage}% ({skill.job_count} jobs)
                </span>
              </div>
              <div className="w-full bg-slate-100 dark:bg-slate-700 h-2 rounded-full overflow-hidden">
                <div
                  className="bg-brand-500 h-full rounded-full transition-all duration-500"
                  style={{ width: `${Math.min(100, skill.percentage)}%` }}
                />
              </div>
            </div>
          ))}
        </div>
      </div>
    </Card>
  );
}
