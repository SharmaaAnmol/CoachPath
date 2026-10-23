'use client';

import * as React from 'react';
import { Card } from '@/components/ui/card';
import {
  FileText,
  Sparkles,
  Bot,
  ShieldCheck,
} from 'lucide-react';

interface DiagnosticNarrativeCardProps {
  narrative: string;
  roleTitle: string;
}

export function DiagnosticNarrativeCard({
  narrative,
  roleTitle,
}: DiagnosticNarrativeCardProps) {
  if (!narrative) {
    return null;
  }

  // Split narrative by double newlines into clean paragraphs
  const paragraphs = narrative
    .split(/\n\n+/)
    .map((p) => p.trim())
    .filter(Boolean);

  return (
    <Card className="p-4 sm:p-5 border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-sm space-y-3">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="p-1.5 rounded-lg bg-indigo-50 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-400">
            <FileText className="w-4 h-4" />
          </span>
          <div>
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-900 dark:text-white">
              Deterministic Diagnostic Evaluation Report
            </h3>
            <p className="text-[11px] text-slate-500 dark:text-slate-400">
              Objective benchmark synthesis for {roleTitle}
            </p>
          </div>
        </div>

        <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 flex items-center gap-1">
          <ShieldCheck className="w-3 h-3 text-indigo-500" /> Grounded Analysis
        </span>
      </div>

      <div className="space-y-2.5 pt-1 text-xs text-slate-600 dark:text-slate-300 leading-relaxed">
        {paragraphs.map((p, idx) => (
          <p key={idx} className="p-2.5 rounded-lg bg-slate-50/70 dark:bg-slate-800/40 border border-slate-100 dark:border-slate-800/80">
            {p}
          </p>
        ))}
      </div>
    </Card>
  );
}
