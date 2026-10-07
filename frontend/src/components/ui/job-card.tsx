'use client';

import * as React from 'react';
import { cn } from '@/lib/utils';
import { JobListing } from '@/types';
import { Card } from './card';
import { Button } from './button';
import { Badge } from './badge';
import { Building2, MapPin, DollarSign, ChevronDown, ChevronUp, Sparkles, Check, X } from 'lucide-react';

export interface JobCardProps {
  job: JobListing;
  onApplyOrOptimize?: (job: JobListing) => void;
  className?: string;
}

export function JobCard({ job, onApplyOrOptimize, className }: JobCardProps) {
  const [showBreakdown, setShowBreakdown] = React.useState(false);

  const getMatchColor = (score: number) => {
    if (score >= 90) return 'text-emerald-700 bg-emerald-50 border-emerald-300 dark:bg-emerald-950/50 dark:text-emerald-300 dark:border-emerald-800';
    if (score >= 75) return 'text-brand-700 bg-brand-50 border-brand-300 dark:bg-brand-950/50 dark:text-brand-300 dark:border-brand-800';
    return 'text-amber-700 bg-amber-50 border-amber-300 dark:bg-amber-950/50 dark:text-amber-300 dark:border-amber-800';
  };

  return (
    <Card className={cn('p-5 space-y-4 hover:border-slate-300 transition-all', className)}>
      <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <h3 className="text-lg font-bold text-slate-900 dark:text-white hover:text-brand-600 cursor-pointer">
              {job.title}
            </h3>
            <span className="rounded-full px-2 py-0.5 text-[11px] font-semibold bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300">
              {job.remoteType}
            </span>
          </div>

          <div className="flex flex-wrap items-center gap-3 text-xs text-slate-500 dark:text-slate-400">
            <span className="flex items-center gap-1 font-medium text-slate-700 dark:text-slate-200">
              <Building2 className="w-3.5 h-3.5" />
              {job.company}
            </span>
            <span className="flex items-center gap-1">
              <MapPin className="w-3.5 h-3.5" />
              {job.location}
            </span>
            <span className="flex items-center gap-1 text-emerald-700 dark:text-emerald-400 font-medium">
              <DollarSign className="w-3.5 h-3.5" />
              {job.salaryRange}
            </span>
          </div>
        </div>

        {/* Semantic Match Score Badge */}
        <div className="flex items-center gap-2 self-start sm:self-auto">
          <div className={cn('rounded-xl border px-3 py-1.5 flex items-center gap-1.5 font-bold text-sm shadow-subtle', getMatchColor(job.matchScore))}>
            <Sparkles className="w-4 h-4" />
            <span>{job.matchScore}% Match</span>
          </div>
        </div>
      </div>

      <p className="text-xs text-slate-600 dark:text-slate-300 line-clamp-2 leading-relaxed">
        {job.description}
      </p>

      {/* Skills Match vs Gap Preview */}
      <div className="space-y-2 pt-1">
        <div className="flex flex-wrap items-center gap-1.5">
          <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider mr-1">Matched:</span>
          {job.matchedSkills.slice(0, 4).map((s) => (
            <Badge key={s} variant="verified" size="sm">
              <Check className="w-3 h-3 text-emerald-600" />
              {s}
            </Badge>
          ))}
          {job.matchedSkills.length > 4 && (
            <span className="text-[11px] text-slate-400 font-medium">+{job.matchedSkills.length - 4} more</span>
          )}
        </div>

        {job.missingSkills.length > 0 && (
          <div className="flex flex-wrap items-center gap-1.5">
            <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider mr-1">Gaps:</span>
            {job.missingSkills.map((s) => (
              <Badge key={s} variant="gap" size="sm">
                <X className="w-3 h-3 text-rose-500" />
                {s}
              </Badge>
            ))}
          </div>
        )}
      </div>

      {/* Multi-factor Score Breakdown (Collapsible) */}
      {showBreakdown && (
        <div className="rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50/70 dark:bg-slate-900/60 p-4 space-y-3 text-xs animate-in fade-in">
          <div className="font-semibold text-slate-700 dark:text-slate-300 uppercase tracking-wider text-[10px]">
            AI Match Vector Factors
          </div>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <div className="bg-white dark:bg-slate-800 p-2.5 rounded-lg border border-slate-200/80 dark:border-slate-700 text-center">
              <div className="text-[10px] text-slate-400">Skills Weight</div>
              <div className="font-bold text-sm text-emerald-600">{job.breakdown.skillsScore}%</div>
            </div>
            <div className="bg-white dark:bg-slate-800 p-2.5 rounded-lg border border-slate-200/80 dark:border-slate-700 text-center">
              <div className="text-[10px] text-slate-400">Experience</div>
              <div className="font-bold text-sm text-brand-600">{job.breakdown.experienceScore}%</div>
            </div>
            <div className="bg-white dark:bg-slate-800 p-2.5 rounded-lg border border-slate-200/80 dark:border-slate-700 text-center">
              <div className="text-[10px] text-slate-400">Domain Match</div>
              <div className="font-bold text-sm text-purple-600">{job.breakdown.domainScore}%</div>
            </div>
            <div className="bg-white dark:bg-slate-800 p-2.5 rounded-lg border border-slate-200/80 dark:border-slate-700 text-center">
              <div className="text-[10px] text-slate-400">Role Similarity</div>
              <div className="font-bold text-sm text-slate-800 dark:text-slate-100">{job.breakdown.roleSimilarityScore}%</div>
            </div>
          </div>
        </div>
      )}

      {/* Action Footer */}
      <div className="flex items-center justify-between pt-2 border-t border-slate-100 dark:border-slate-800">
        <button
          onClick={() => setShowBreakdown(!showBreakdown)}
          className="flex items-center gap-1 text-xs font-medium text-slate-500 hover:text-slate-800 dark:hover:text-slate-200"
        >
          {showBreakdown ? (
            <>
              Hide Score Factors <ChevronUp className="w-3.5 h-3.5" />
            </>
          ) : (
            <>
              Explain Match Score <ChevronDown className="w-3.5 h-3.5" />
            </>
          )}
        </button>

        <div className="flex items-center gap-2">
          <Button
            size="sm"
            variant="outline"
            onClick={() => onApplyOrOptimize?.(job)}
          >
            Optimize Resume
          </Button>
          <Button
            size="sm"
            variant="primary"
            onClick={() => onApplyOrOptimize?.(job)}
          >
            Apply Now
          </Button>
        </div>
      </div>
    </Card>
  );
}
