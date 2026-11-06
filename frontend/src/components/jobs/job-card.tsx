'use client';

import * as React from 'react';
import { cn } from '@/lib/utils';
import { JobOpportunity, JobSkillItem } from '@/types';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  Building2,
  MapPin,
  DollarSign,
  Calendar,
  ExternalLink,
  ShieldCheck,
  CheckCircle2,
  Sparkles,
  ArrowRight,
  Clock,
  Briefcase,
} from 'lucide-react';

export interface JobCardProps {
  job: JobOpportunity;
  onSelect: (job: JobOpportunity) => void;
  className?: string;
}

export function JobCard({ job, onSelect, className }: JobCardProps) {
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

  // Format posted date
  const formatPostedDate = (dateString: string) => {
    try {
      const date = new Date(dateString);
      return date.toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric',
      });
    } catch {
      return 'Recently';
    }
  };

  // Source provider formatting
  const getSourceBadge = (source: string) => {
    switch (source.toLowerCase()) {
      case 'seed':
        return { label: 'Curated Benchmark', color: 'bg-indigo-50 text-indigo-700 border-indigo-200 dark:bg-lav/10 dark:text-lav-light dark:border-lav/30' };
      case 'manual':
        return { label: 'User Imported', color: 'bg-emerald-50 text-emerald-700 border-emerald-200 dark:bg-lime/10 dark:text-lime-soft dark:border-lime/30' };
      case 'arbeitnow':
        return { label: 'Arbeitnow API', color: 'bg-sky-50 text-sky-700 border-sky-200 dark:bg-lav/10 dark:text-lav-light dark:border-lav/30' };
      default:
        return { label: source.toUpperCase(), color: 'bg-slate-100 text-slate-700 border-slate-200 dark:bg-white/[0.07] dark:text-ink-fg/80 dark:border-white/15' };
    }
  };

  // Freshness formatting
  const getFreshnessBadge = (status: string) => {
    switch (status.toLowerCase()) {
      case 'active':
        return { label: 'Active', color: 'text-emerald-600 bg-emerald-50 dark:bg-lime/10 dark:text-lime' };
      case 'needs_refresh':
        return { label: 'Review Needed', color: 'text-amber-600 bg-amber-50 dark:bg-amber-950/50 dark:text-amber-400' };
      case 'expired':
        return { label: 'Expired', color: 'text-slate-500 bg-slate-100 dark:bg-white/[0.07] dark:text-ink-muted' };
      case 'closed':
        return { label: 'Listing Closed', color: 'text-rose-600 bg-rose-50 dark:bg-crimson/10 dark:text-crimson-soft' };
      default:
        return { label: status, color: 'text-slate-500 bg-slate-100 dark:bg-white/[0.07] dark:text-ink-muted' };
    }
  };

  // Split skills into mandatory and preferred
  const requiredSkills = (job.skills || []).filter((s) => s.is_mandatory);
  const preferredSkills = (job.skills || []).filter((s) => !s.is_mandatory);

  const sourceBadge = getSourceBadge(job.source);
  const freshness = getFreshnessBadge(job.freshness_status);

  return (
    <Card
      className={cn(
        'p-5 space-y-4 hover:border-slate-300 dark:hover:border-white/15 transition-all cursor-pointer group hover:shadow-subtle',
        className
      )}
      onClick={() => onSelect(job)}
    >
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-3">
        <div className="space-y-1.5 flex-1 min-w-0">
          <div className="flex flex-wrap items-center gap-2">
            <h3 className="text-base sm:text-lg font-bold text-slate-900 dark:text-white group-hover:text-brand-600 dark:group-hover:text-lav transition-colors truncate">
              {job.title}
            </h3>

            {/* Remote Flexibility Badge */}
            <span
              className={cn(
                'rounded-full px-2.5 py-0.5 text-[11px] font-semibold uppercase tracking-wider',
                job.remote_type === 'remote'
                  ? 'bg-emerald-100 text-emerald-800 dark:bg-lime/10 dark:text-lime-soft'
                  : job.remote_type === 'hybrid'
                  ? 'bg-blue-100 text-blue-800 dark:bg-lav/10 dark:text-lav-light'
                  : 'bg-slate-100 text-slate-800 dark:bg-white/[0.07] dark:text-ink-fg/80'
              )}
            >
              {job.remote_type}
            </span>

            {/* Seniority Badge */}
            <span className="rounded-full px-2 py-0.5 text-[11px] font-medium bg-slate-100 text-slate-700 dark:bg-white/[0.07] dark:text-ink-fg/80 capitalize">
              {job.experience_level.replace('_', ' ')}
            </span>
          </div>

          {/* Company & Location Row */}
          <div className="flex flex-wrap items-center gap-y-1 gap-x-3 text-xs text-slate-500 dark:text-ink-muted">
            <span className="flex items-center gap-1 font-semibold text-slate-800 dark:text-ink-fg">
              <Building2 className="w-3.5 h-3.5 text-slate-400" />
              {job.company_name}
            </span>
            <span className="flex items-center gap-1">
              <MapPin className="w-3.5 h-3.5 text-slate-400" />
              {job.location}
            </span>
            {salaryDisplay && (
              <span className="flex items-center gap-1 text-emerald-700 dark:text-lime font-semibold">
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

        {/* Source & Freshness Metadata Badges */}
        <div className="flex items-center gap-2 self-start sm:self-auto shrink-0">
          <span
            className={cn(
              'px-2 py-0.5 rounded-md text-[11px] font-medium border',
              sourceBadge.color
            )}
          >
            {sourceBadge.label}
          </span>
          <span
            className={cn(
              'px-2 py-0.5 rounded-md text-[11px] font-semibold',
              freshness.color
            )}
          >
            {freshness.label}
          </span>
        </div>
      </div>

      {/* Description Snippet */}
      <p className="text-xs text-slate-600 dark:text-ink-fg/80 line-clamp-2 leading-relaxed">
        {job.description_markdown.replace(/[#*`_]/g, '')}
      </p>

      {/* Canonical Skills Tagging (Required vs Preferred) */}
      <div className="space-y-1.5 pt-1">
        {requiredSkills.length > 0 && (
          <div className="flex flex-wrap items-center gap-1.5">
            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider mr-1">
              Required Skills:
            </span>
            {requiredSkills.slice(0, 5).map((s) => (
              <Badge key={s.skill_id} variant="verified" size="sm" className="font-medium text-[11px]">
                <CheckCircle2 className="w-3 h-3 text-emerald-600 mr-1 dark:text-lime" />
                {s.name}
              </Badge>
            ))}
            {requiredSkills.length > 5 && (
              <span className="text-[11px] text-slate-400 font-medium">
                +{requiredSkills.length - 5} more
              </span>
            )}
          </div>
        )}

        {preferredSkills.length > 0 && (
          <div className="flex flex-wrap items-center gap-1.5">
            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider mr-1">
              Preferred:
            </span>
            {preferredSkills.slice(0, 4).map((s) => (
              <Badge key={s.skill_id} variant="default" size="sm" className="font-normal text-[11px]">
                {s.name}
              </Badge>
            ))}
            {preferredSkills.length > 4 && (
              <span className="text-[11px] text-slate-400 font-medium">
                +{preferredSkills.length - 4} more
              </span>
            )}
          </div>
        )}
      </div>

      {/* Card Action Footer */}
      <div className="flex items-center justify-between pt-2 border-t border-slate-100 dark:border-white/10 text-xs">
        <div className="flex items-center gap-2 text-slate-400 text-[11px]">
          {job.last_verified_at && (
            <span className="flex items-center gap-1">
              <ShieldCheck className="w-3.5 h-3.5 text-slate-400" />
              Verified {formatPostedDate(job.last_verified_at)}
            </span>
          )}
        </div>

        <div className="flex items-center gap-3">
          <Button
            size="sm"
            variant="ghost"
            className="text-xs group-hover:text-brand-600 dark:group-hover:text-lav"
            onClick={(e) => {
              e.stopPropagation();
              onSelect(job);
            }}
          >
            View Details <ArrowRight className="w-3.5 h-3.5 ml-1" />
          </Button>
        </div>
      </div>
    </Card>
  );
}
