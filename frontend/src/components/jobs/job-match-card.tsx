'use client';

import * as React from 'react';
import { cn } from '@/lib/utils';
import { JobOpportunity, JobMatchResponse } from '@/types';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { MatchScoreBadge } from './match-score-badge';
import { MatchEvidenceCoverage } from './match-evidence-coverage';
import {
  Building2,
  MapPin,
  DollarSign,
  Calendar,
  ShieldCheck,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  HelpCircle,
  ArrowRight,
  Sparkles,
  RefreshCw,
  ExternalLink,
} from 'lucide-react';

export interface JobMatchCardProps {
  job: JobOpportunity;
  match: JobMatchResponse;
  onSelectBreakdown: (job: JobOpportunity, match: JobMatchResponse) => void;
  onSelectJob: (job: JobOpportunity) => void;
  className?: string;
}

export function JobMatchCard({
  job,
  match,
  onSelectBreakdown,
  onSelectJob,
  className,
}: JobMatchCardProps) {
  // Format salary honestly
  const formatSalary = () => {
    if (job.min_salary && job.max_salary) {
      return `$${job.min_salary.toLocaleString()} – $${job.max_salary.toLocaleString()}/yr ${job.currency}`;
    } else if (job.min_salary) {
      return `From $${job.min_salary.toLocaleString()}/yr ${job.currency}`;
    } else if (job.max_salary) {
      return `Up to $${job.max_salary.toLocaleString()}/yr ${job.currency}`;
    }
    return null;
  };

  const salaryDisplay = formatSalary();

  const formatPostedDate = (dateString: string) => {
    try {
      const date = new Date(dateString);
      return date.toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
      });
    } catch {
      return 'Recent';
    }
  };

  // Freshness badge
  const getFreshnessBadge = (status: string) => {
    switch (status.toLowerCase()) {
      case 'active':
        return { label: 'Active', color: 'text-emerald-600 bg-emerald-50 dark:bg-emerald-950/50 dark:text-emerald-400' };
      case 'needs_refresh':
        return { label: 'Review Needed', color: 'text-amber-600 bg-amber-50 dark:bg-amber-950/50 dark:text-amber-400' };
      case 'expired':
        return { label: 'Expired', color: 'text-slate-500 bg-slate-100 dark:bg-slate-800 dark:text-slate-400' };
      case 'closed':
        return { label: 'Listing Closed', color: 'text-rose-600 bg-rose-50 dark:bg-rose-950/50 dark:text-rose-400' };
      default:
        return { label: status, color: 'text-slate-500 bg-slate-100 dark:bg-slate-800 dark:text-slate-400' };
    }
  };

  const freshness = getFreshnessBadge(job.freshness_status);

  // Skill categorization
  const matchedRequired = match.matched_skills || [];
  const missingRequired = match.missing_skills || [];
  const matchedPreferred = match.matched_preferred_skills || [];
  const unknownSkills = match.unknown_skills || [];

  return (
    <Card
      className={cn(
        'p-5 space-y-4 hover:border-brand-300/80 dark:hover:border-brand-800/80 transition-all cursor-pointer group hover:shadow-subtle',
        match.is_stale && 'border-amber-200 dark:border-amber-900/50',
        className
      )}
      onClick={() => onSelectBreakdown(job, match)}
    >
      {/* Top Header Row: Match Score + Job Title & Meta */}
      <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-3">
        <div className="space-y-1.5 flex-1 min-w-0">
          <div className="flex flex-wrap items-center gap-2">
            <h3 className="text-base sm:text-lg font-bold text-slate-900 dark:text-white group-hover:text-brand-600 dark:group-hover:text-brand-400 transition-colors truncate">
              {job.title}
            </h3>

            {/* Workplace flexibility */}
            <span
              className={cn(
                'rounded-full px-2.5 py-0.5 text-[11px] font-semibold uppercase tracking-wider',
                job.remote_type === 'remote'
                  ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300'
                  : job.remote_type === 'hybrid'
                  ? 'bg-blue-100 text-blue-800 dark:bg-blue-950 dark:text-blue-300'
                  : 'bg-slate-100 text-slate-800 dark:bg-slate-800 dark:text-slate-300'
              )}
            >
              {job.remote_type}
            </span>

            {/* Experience level */}
            <span className="rounded-full px-2 py-0.5 text-[11px] font-medium bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300 capitalize">
              {job.experience_level.replace('_', ' ')}
            </span>
          </div>

          {/* Company, Location, Salary */}
          <div className="flex flex-wrap items-center gap-y-1 gap-x-3 text-xs text-slate-500 dark:text-slate-400">
            <span className="flex items-center gap-1 font-semibold text-slate-800 dark:text-slate-200">
              <Building2 className="w-3.5 h-3.5 text-slate-400" />
              {job.company_name}
            </span>
            <span className="flex items-center gap-1">
              <MapPin className="w-3.5 h-3.5 text-slate-400" />
              {job.location}
            </span>
            {salaryDisplay && (
              <span className="flex items-center gap-1 text-emerald-700 dark:text-emerald-400 font-semibold">
                <DollarSign className="w-3.5 h-3.5" />
                {salaryDisplay}
              </span>
            )}
            <span className="flex items-center gap-1 text-slate-400">
              <Calendar className="w-3.5 h-3.5" />
              {formatPostedDate(job.posted_at)}
            </span>
          </div>
        </div>

        {/* Right Badge Cluster: Match Score + Confidence */}
        <div className="flex flex-col sm:items-end gap-1.5 shrink-0">
          <MatchScoreBadge
            score={match.overall_score}
            isProvisional={match.breakdown?.is_provisional}
            size="md"
          />
          <MatchEvidenceCoverage coverage={match.breakdown?.evidence_coverage || 0} />
        </div>
      </div>

      {/* Stale Match Warning Banner */}
      {match.is_stale && (
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-md bg-amber-50 text-amber-800 border border-amber-200/80 dark:bg-amber-950/40 dark:text-amber-300 dark:border-amber-800 text-xs font-medium">
          <RefreshCw className="w-3.5 h-3.5 text-amber-600 shrink-0" />
          <span>Profile or assessment evidence updated. Recalculation recommended.</span>
        </div>
      )}

      {/* Summary Narrative Snippet */}
      {match.explanation?.summary && (
        <p className="text-xs text-slate-600 dark:text-slate-300 leading-relaxed line-clamp-2">
          {match.explanation.summary}
        </p>
      )}

      {/* Skills Matrix Pill Row (Matched vs Missing vs Preferred) */}
      <div className="space-y-2 pt-1">
        {/* Matched Required Skills */}
        {matchedRequired.length > 0 && (
          <div className="flex flex-wrap items-center gap-1.5">
            <span className="text-[10px] font-bold text-emerald-700 dark:text-emerald-400 uppercase tracking-wider flex items-center gap-1 mr-1">
              <CheckCircle2 className="w-3 h-3 text-emerald-600" /> Matched Required:
            </span>
            {matchedRequired.slice(0, 4).map((s) => (
              <Badge key={s} variant="verified" size="sm" className="font-medium text-[11px]">
                {s}
              </Badge>
            ))}
            {matchedRequired.length > 4 && (
              <span className="text-[11px] text-slate-400 font-medium">
                +{matchedRequired.length - 4} more
              </span>
            )}
          </div>
        )}

        {/* Missing Required Skills */}
        {missingRequired.length > 0 && (
          <div className="flex flex-wrap items-center gap-1.5">
            <span className="text-[10px] font-bold text-rose-700 dark:text-rose-400 uppercase tracking-wider flex items-center gap-1 mr-1">
              <XCircle className="w-3 h-3 text-rose-500" /> Missing Required:
            </span>
            {missingRequired.slice(0, 3).map((s) => (
              <Badge key={s} variant="gap" size="sm" className="font-medium text-[11px]">
                {s}
              </Badge>
            ))}
            {missingRequired.length > 3 && (
              <span className="text-[11px] text-slate-400 font-medium">
                +{missingRequired.length - 3} more
              </span>
            )}
          </div>
        )}

        {/* Preferred Skills */}
        {(matchedPreferred.length > 0 || unknownSkills.length > 0) && (
          <div className="flex flex-wrap items-center gap-1.5 text-slate-500 dark:text-slate-400">
            <span className="text-[10px] font-bold uppercase tracking-wider mr-1">
              Preferred:
            </span>
            {matchedPreferred.slice(0, 2).map((s) => (
              <span
                key={s}
                className="px-2 py-0.5 rounded-full text-[11px] font-medium bg-emerald-50 text-emerald-700 border border-emerald-200 dark:bg-emerald-950/40 dark:text-emerald-300"
              >
                ✓ {s}
              </span>
            ))}
            {unknownSkills.slice(0, 2).map((s) => (
              <span
                key={s}
                className="px-2 py-0.5 rounded-full text-[11px] font-normal bg-slate-100 text-slate-600 border border-slate-200 dark:bg-slate-800 dark:text-slate-400 dark:border-slate-700"
              >
                ? {s}
              </span>
            ))}
          </div>
        )}
      </div>

      {/* Card Footer with Explanatory Actions */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pt-3 border-t border-slate-100 dark:border-slate-800 text-xs gap-2">
        <div className="flex items-center gap-2 text-slate-400 text-[11px]">
          <span
            className={cn(
              'px-2 py-0.5 rounded-md text-[10px] font-semibold',
              freshness.color
            )}
          >
            {freshness.label}
          </span>
          {match.calculated_at && (
            <span>Calculated {formatPostedDate(match.calculated_at)}</span>
          )}
        </div>

        <div className="flex items-center gap-2 self-end sm:self-auto">
          <Button
            size="sm"
            variant="outline"
            className="text-xs"
            onClick={(e) => {
              e.stopPropagation();
              onSelectJob(job);
            }}
          >
            Posting Details
          </Button>

          <Button
            size="sm"
            variant="primary"
            className="text-xs flex items-center gap-1.5 shadow-xs"
            onClick={(e) => {
              e.stopPropagation();
              onSelectBreakdown(job, match);
            }}
          >
            <Sparkles className="w-3.5 h-3.5 text-brand-200" />
            Match Breakdown <ArrowRight className="w-3.5 h-3.5 ml-0.5" />
          </Button>
        </div>
      </div>
    </Card>
  );
}
