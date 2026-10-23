'use client';

import * as React from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { ShieldCheck, CheckCircle2, RotateCcw, ArrowRight } from 'lucide-react';

interface ResumeApprovalSummaryProps {
  educationCount: number;
  experienceCount: number;
  projectsCount: number;
  certificationsCount: number;
  skillsCount: number;
  hasPersonalInfo: boolean;
  onConfirm: () => void;
  onDiscard: () => void;
  isConfirming: boolean;
}

export function ResumeApprovalSummary({
  educationCount,
  experienceCount,
  projectsCount,
  certificationsCount,
  skillsCount,
  hasPersonalInfo,
  onConfirm,
  onDiscard,
  isConfirming,
}: ResumeApprovalSummaryProps) {
  const totalItems =
    educationCount +
    experienceCount +
    projectsCount +
    certificationsCount +
    skillsCount +
    (hasPersonalInfo ? 1 : 0);

  return (
    <Card className="p-4 bg-gradient-to-r from-slate-900 via-brand-950 to-slate-900 text-white border-brand-800 shadow-lg">
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
        {/* Left: Tally and Explanation */}
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <div className="w-7 h-7 rounded-lg bg-brand-500/20 text-brand-300 flex items-center justify-center">
              <ShieldCheck className="w-4 h-4" />
            </div>
            <h4 className="font-semibold text-sm text-white">
              Candidate Approval Gate ({totalItems} items selected for merge)
            </h4>
          </div>

          <div className="flex flex-wrap items-center gap-2 text-xs text-slate-300 pt-1">
            {hasPersonalInfo && (
              <span className="bg-slate-800 px-2 py-0.5 rounded border border-slate-700">
                Contact Details
              </span>
            )}
            <span className="bg-slate-800 px-2 py-0.5 rounded border border-slate-700">
              {educationCount} Education
            </span>
            <span className="bg-slate-800 px-2 py-0.5 rounded border border-slate-700">
              {experienceCount} Experience
            </span>
            <span className="bg-slate-800 px-2 py-0.5 rounded border border-slate-700">
              {projectsCount} Projects
            </span>
            <span className="bg-slate-800 px-2 py-0.5 rounded border border-slate-700">
              {certificationsCount} Certifications
            </span>
            <span className="bg-slate-800 px-2 py-0.5 rounded border border-slate-700">
              {skillsCount} Skills
            </span>
          </div>

          <p className="text-[11px] text-slate-400 pt-0.5">
            Only approved items will be safely merged into your Career Profile in PostgreSQL. Existing unselected profile data remains preserved.
          </p>
        </div>

        {/* Right: Actions */}
        <div className="flex items-center gap-3 shrink-0">
          <Button
            variant="ghost"
            size="sm"
            onClick={onDiscard}
            disabled={isConfirming}
            className="text-slate-300 hover:text-white hover:bg-slate-800"
          >
            <RotateCcw className="w-3.5 h-3.5 mr-1.5" /> Discard Edits
          </Button>

          <Button
            variant="primary"
            size="md"
            onClick={onConfirm}
            isLoading={isConfirming}
            disabled={isConfirming || totalItems === 0}
            className="bg-emerald-600 hover:bg-emerald-700 text-white font-semibold shadow-md"
          >
            <CheckCircle2 className="w-4 h-4 mr-1.5" />
            Confirm & Merge into Career Profile
          </Button>
        </div>
      </div>
    </Card>
  );
}
