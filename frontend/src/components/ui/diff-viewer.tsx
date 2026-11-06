'use client';

import * as React from 'react';
import { cn } from '@/lib/utils';
import { ResumeDiffChange } from '@/types';
import { Card } from './card';
import { Button } from './button';
import { Check, X, ShieldCheck, Sparkles } from 'lucide-react';

export interface DiffViewerProps {
  change: ResumeDiffChange;
  onAccept?: (id: string) => void;
  onReject?: (id: string) => void;
  className?: string;
}

export function DiffViewer({ change, onAccept, onReject, className }: DiffViewerProps) {
  const [currentStatus, setCurrentStatus] = React.useState(change.status);

  const handleAccept = () => {
    setCurrentStatus('accepted');
    onAccept?.(change.id);
  };

  const handleReject = () => {
    setCurrentStatus('rejected');
    onReject?.(change.id);
  };

  return (
    <Card className={cn('overflow-hidden border-slate-200 dark:border-white/10', className)}>
      {/* Header with section and approval status */}
      <div className="bg-slate-50 dark:bg-white/[0.07] px-4 py-3 border-b border-slate-200 dark:border-white/10 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Sparkles className="w-4 h-4 text-purple-600 dark:text-lav" />
          <span className="text-xs font-bold uppercase tracking-wider text-slate-700 dark:text-ink-fg/80">
            {change.section}
          </span>
        </div>

        <div className="flex items-center gap-2">
          {currentStatus === 'accepted' && (
            <span className="flex items-center gap-1 text-xs font-semibold text-emerald-700 bg-emerald-100/80 dark:bg-lime/10 dark:text-lime-soft px-2.5 py-0.5 rounded-full">
              <Check className="w-3.5 h-3.5" /> Accepted
            </span>
          )}
          {currentStatus === 'rejected' && (
            <span className="flex items-center gap-1 text-xs font-semibold text-rose-700 bg-rose-100/80 dark:bg-crimson/10 dark:text-crimson-tint px-2.5 py-0.5 rounded-full">
              <X className="w-3.5 h-3.5" /> Discarded
            </span>
          )}
          {currentStatus === 'pending' && (
            <span className="text-xs font-medium text-amber-700 bg-amber-100/80 dark:bg-amber-950/60 dark:text-amber-300 px-2.5 py-0.5 rounded-full">
              Pending Review
            </span>
          )}
        </div>
      </div>

      {/* Side-by-side or stacked diff */}
      <div className="p-4 space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs font-mono">
          {/* Original */}
          <div className="rounded-lg p-3 bg-rose-50/50 dark:bg-crimson/10 border border-rose-200 dark:border-crimson/30">
            <div className="text-[10px] font-bold uppercase text-rose-700 dark:text-crimson-soft mb-1">
              Current Baseline
            </div>
            <div className="text-slate-700 dark:text-ink-fg/80 whitespace-pre-line leading-relaxed">
              {change.originalText}
            </div>
          </div>

          {/* Suggested */}
          <div className="rounded-lg p-3 bg-emerald-50/50 dark:bg-lime/10 border border-emerald-200 dark:border-lime/30">
            <div className="text-[10px] font-bold uppercase text-emerald-700 dark:text-lime mb-1">
              AI Tailored Version (Verified Evidence)
            </div>
            <div className="text-slate-900 dark:text-ink-fg font-medium whitespace-pre-line leading-relaxed">
              {change.suggestedText}
            </div>
          </div>
        </div>

        {/* Explainability & Grounded Evidence Callout */}
        <div className="rounded-lg bg-slate-50 dark:bg-white/[0.07] p-3 space-y-1.5 border border-slate-200/80 dark:border-white/15 text-xs">
          <div className="flex items-center gap-1.5 font-semibold text-slate-800 dark:text-ink-fg">
            <ShieldCheck className="w-4 h-4 text-emerald-600 dark:text-lime" />
            <span>Anti-Hallucination Evidence Proof:</span>
            <span className="font-mono text-purple-700 dark:text-lav-light font-normal">
              {change.evidenceReference}
            </span>
          </div>
          <p className="text-slate-600 dark:text-ink-muted pl-5">
            <strong className="text-slate-700 dark:text-ink-fg/80">Why this improves score:</strong> {change.rationale}
          </p>
        </div>

        {/* Human Approval Gate Controls */}
        <div className="flex items-center justify-end gap-2 pt-2 border-t border-slate-100 dark:border-white/10">
          <Button
            size="sm"
            variant="ghost"
            onClick={handleReject}
            disabled={currentStatus === 'rejected'}
            className="text-slate-600 hover:text-rose-600 hover:bg-rose-50 dark:hover:text-crimson-soft dark:hover:bg-crimson/10"
          >
            <X className="w-3.5 h-3.5 mr-1" />
            Reject Change
          </Button>
          <Button
            size="sm"
            variant="primary"
            onClick={handleAccept}
            disabled={currentStatus === 'accepted'}
            className="bg-emerald-600 hover:bg-emerald-700 dark:bg-lime/20 dark:hover:bg-lime/20"
          >
            <Check className="w-3.5 h-3.5 mr-1" />
            Accept & Update Resume
          </Button>
        </div>
      </div>
    </Card>
  );
}
