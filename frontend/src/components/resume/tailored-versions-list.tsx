'use client';

import * as React from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import {
  FileText,
  Briefcase,
  Sparkles,
  ShieldCheck,
  CheckCircle2,
  Clock,
  Trash2,
  ArrowRight,
  ExternalLink,
  Layers,
  Search,
  Plus,
} from 'lucide-react';
import { TailoredResumeListItem, TailoredResumeStatus } from '@/types';

interface TailoredVersionsListProps {
  versions: TailoredResumeListItem[];
  isLoading: boolean;
  onOpenVersion: (versionId: string) => void;
  onDeleteVersion: (version: TailoredResumeListItem) => void;
  onCreateNewClick: () => void;
}

export function TailoredVersionsList({
  versions,
  isLoading,
  onOpenVersion,
  onDeleteVersion,
  onCreateNewClick,
}: TailoredVersionsListProps) {
  const [filterStatus, setFilterStatus] = React.useState<'all' | TailoredResumeStatus>('all');
  const [searchTerm, setSearchTerm] = React.useState('');

  const filtered = versions.filter((v) => {
    if (filterStatus !== 'all' && v.status !== filterStatus) return false;
    if (searchTerm) {
      const term = searchTerm.toLowerCase();
      const matchTitle = (v.job_title || '').toLowerCase().includes(term);
      const matchComp = (v.company_name || '').toLowerCase().includes(term);
      if (!matchTitle && !matchComp) return false;
    }
    return true;
  });

  return (
    <div className="space-y-6">
      {/* Header with Search and Filters */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h3 className="text-lg font-bold text-slate-900 dark:text-white flex items-center gap-2">
            <Layers className="w-5 h-5 text-purple-600" />
            <span>Tailored Resume Versions</span>
            <span className="text-xs font-mono font-normal px-2 py-0.5 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400">
              {versions.length}
            </span>
          </h3>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
            Historical versions created for specific target roles and job opportunities.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Button size="sm" variant="primary" onClick={onCreateNewClick} className="bg-purple-600 hover:bg-purple-700">
            <Plus className="w-4 h-4 mr-1.5" /> Tailor for New Job
          </Button>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-3">
        <div className="flex items-center rounded-lg bg-slate-100 dark:bg-slate-800 p-0.5 text-xs w-full sm:w-auto">
          <button
            type="button"
            onClick={() => setFilterStatus('all')}
            className={`px-3 py-1.5 rounded-md font-semibold transition-all ${
              filterStatus === 'all'
                ? 'bg-white dark:bg-slate-900 text-slate-900 dark:text-white shadow-sm'
                : 'text-slate-500 hover:text-slate-900 dark:hover:text-white'
            }`}
          >
            All ({versions.length})
          </button>
          <button
            type="button"
            onClick={() => setFilterStatus('draft')}
            className={`px-3 py-1.5 rounded-md font-semibold transition-all ${
              filterStatus === 'draft'
                ? 'bg-white dark:bg-slate-900 text-amber-700 dark:text-amber-400 shadow-sm'
                : 'text-slate-500 hover:text-slate-900 dark:hover:text-white'
            }`}
          >
            Drafts ({versions.filter((v) => v.status === 'draft').length})
          </button>
          <button
            type="button"
            onClick={() => setFilterStatus('approved')}
            className={`px-3 py-1.5 rounded-md font-semibold transition-all ${
              filterStatus === 'approved'
                ? 'bg-white dark:bg-slate-900 text-emerald-700 dark:text-emerald-400 shadow-sm'
                : 'text-slate-500 hover:text-slate-900 dark:hover:text-white'
            }`}
          >
            Approved ({versions.filter((v) => v.status === 'approved').length})
          </button>
        </div>

        <div className="relative w-full sm:w-64">
          <Search className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Filter by job or company..."
            className="w-full pl-8 pr-3 py-1.5 text-xs rounded-lg border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
          />
        </div>
      </div>

      {/* Loading Skeleton */}
      {isLoading ? (
        <div className="space-y-3">
          {[1, 2, 3].map((i) => (
            <Card key={i} className="p-4 space-y-2">
              <Skeleton className="h-4 w-1/3" />
              <Skeleton className="h-3 w-1/2" />
            </Card>
          ))}
        </div>
      ) : filtered.length === 0 ? (
        <div className="p-12 text-center rounded-2xl border border-dashed border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-900/50 space-y-3">
          <div className="w-12 h-12 rounded-2xl bg-purple-100 dark:bg-purple-950/60 text-purple-600 flex items-center justify-center mx-auto">
            <FileText className="w-6 h-6" />
          </div>
          <div className="space-y-1 max-w-sm mx-auto">
            <h4 className="text-sm font-bold text-slate-900 dark:text-white">
              {versions.length === 0
                ? 'No Tailored Versions Yet'
                : 'No Matching Versions Found'}
            </h4>
            <p className="text-xs text-slate-500 dark:text-slate-400">
              {versions.length === 0
                ? 'Select a target job and create your first evidence-grounded tailored resume variant.'
                : 'Try clearing your search term or changing your status filter.'}
            </p>
          </div>
          {versions.length === 0 && (
            <Button size="sm" variant="primary" onClick={onCreateNewClick} className="bg-purple-600 hover:bg-purple-700">
              <Sparkles className="w-4 h-4 mr-1.5" /> Start Tailoring Now
            </Button>
          )}
        </div>
      ) : (
        <div className="space-y-3">
          {filtered.map((ver) => (
            <Card
              key={ver.id}
              className="p-4 hover:border-slate-300 dark:hover:border-slate-700 transition-all shadow-sm"
            >
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                {/* Left details */}
                <div className="space-y-1.5 min-w-0">
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="font-mono text-xs font-bold px-2 py-0.5 rounded bg-purple-100 dark:bg-purple-950/60 text-purple-800 dark:text-purple-300">
                      v{ver.version_number}
                    </span>
                    <h4 className="text-sm font-bold text-slate-900 dark:text-white truncate">
                      {ver.job_title || 'Target Job Opportunity'}
                    </h4>
                    {ver.company_name && (
                      <span className="text-xs text-slate-500 dark:text-slate-400">
                        at <strong className="text-slate-700 dark:text-slate-300">{ver.company_name}</strong>
                      </span>
                    )}
                  </div>

                  <div className="flex items-center gap-3 text-xs text-slate-500 dark:text-slate-400 flex-wrap">
                    {ver.status === 'approved' ? (
                      <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-emerald-700 bg-emerald-100 dark:bg-emerald-950/60 dark:text-emerald-300 px-2 py-0.5 rounded-full">
                        <CheckCircle2 className="w-3.5 h-3.5" />
                        Approved {ver.approved_at ? new Date(ver.approved_at).toLocaleDateString() : ''}
                      </span>
                    ) : (
                      <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-amber-700 bg-amber-100 dark:bg-amber-950/60 dark:text-amber-300 px-2 py-0.5 rounded-full">
                        <Clock className="w-3.5 h-3.5" />
                        Draft Review
                      </span>
                    )}

                    {ver.anti_hallucination_verified && (
                      <span className="inline-flex items-center gap-1 text-[11px] text-emerald-600 dark:text-emerald-400 font-medium">
                        <ShieldCheck className="w-3.5 h-3.5" /> Grounded Audit Passed
                      </span>
                    )}

                    {ver.keyword_coverage !== null && ver.keyword_coverage !== undefined && (
                      <span className="font-mono text-[11px]">
                        Coverage: <strong>{ver.keyword_coverage.toFixed(1)}%</strong>
                      </span>
                    )}

                    <span className="text-[11px]">
                      {ver.changes_count} changes
                    </span>

                    <span className="text-[11px] text-slate-400">
                      Updated {new Date(ver.updated_at).toLocaleDateString()}
                    </span>
                  </div>
                </div>

                {/* Right actions */}
                <div className="flex items-center gap-2 shrink-0">
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => onOpenVersion(ver.id)}
                  >
                    Inspect & Edit <ArrowRight className="w-3.5 h-3.5 ml-1" />
                  </Button>
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={() => onDeleteVersion(ver)}
                    className="text-slate-400 hover:text-rose-600 hover:bg-rose-50 dark:hover:bg-rose-950/40 p-2"
                  >
                    <Trash2 className="w-4 h-4" />
                  </Button>
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
