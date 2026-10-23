'use client';

import * as React from 'react';
import { Modal } from '@/components/ui/modal';
import { Button } from '@/components/ui/button';
import {
  ShieldCheck,
  Target,
  AlertCircle,
  HelpCircle,
  CheckCircle2,
  FileText,
  ClipboardCheck,
} from 'lucide-react';

interface ScoreExplanationModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export function ScoreExplanationModal({ isOpen, onClose }: ScoreExplanationModalProps) {
  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Understanding Skill Gap Engine Scores"
      description="How CoachPath deterministically calibrates alignment, coverage, and verification."
      maxWidth="2xl"
    >
      <div className="space-y-5 py-2 text-xs text-slate-600 dark:text-slate-300">
        {/* Core Distinction Alert */}
        <div className="p-3.5 rounded-xl bg-slate-50 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700 space-y-2">
          <div className="flex items-center gap-2 text-slate-900 dark:text-white font-bold text-sm">
            <ShieldCheck className="w-4 h-4 text-indigo-600 dark:text-indigo-400" />
            <span>Mathematical Determinism & Anti-Hallucination Standards</span>
          </div>
          <p className="leading-relaxed">
            All scores are calculated using deterministic weighted mathematical formulas on the server.
            No live LLM hallucinations are involved in scoring. Claims made on resumes or profiles are categorized as{' '}
            <strong className="text-amber-600 dark:text-amber-400">NOT_ASSESSED</strong> until validated through objective diagnostic tests.
          </p>
        </div>

        {/* Score 1: Role Alignment */}
        <div className="space-y-2 p-3.5 rounded-xl border border-indigo-100 dark:border-indigo-900/40 bg-indigo-50/30 dark:bg-indigo-950/20">
          <div className="flex items-center gap-2 text-indigo-900 dark:text-indigo-200 font-bold text-sm">
            <Target className="w-4 h-4 text-indigo-600 dark:text-indigo-400" />
            <span>1. Documented Role Alignment Score (0 – 100%)</span>
          </div>
          <p className="leading-relaxed">
            Measures how closely your <em>validated competency levels</em> match the benchmark expectations of your selected target role.
          </p>
          <ul className="list-disc list-inside space-y-1 text-slate-500 dark:text-slate-400 pl-1">
            <li>Weighted by requirement importance (Mandatory &gt; Preferred &gt; Bonus).</li>
            <li>Calculated as: <code className="px-1.5 py-0.5 rounded bg-white dark:bg-slate-800 text-indigo-600 dark:text-indigo-300 font-mono text-[11px]">Σ (coverage_ratio × weight) / Σ (weight) × 100</code></li>
            <li><strong>Important:</strong> Role alignment is an educational benchmark readiness indicator. It is <em>not</em> an employment guarantee or hiring probability.</li>
          </ul>
        </div>

        {/* Score 2: Evidence Coverage */}
        <div className="space-y-2 p-3.5 rounded-xl border border-emerald-100 dark:border-emerald-900/40 bg-emerald-50/30 dark:bg-emerald-950/20">
          <div className="flex items-center gap-2 text-emerald-900 dark:text-emerald-200 font-bold text-sm">
            <ClipboardCheck className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />
            <span>2. Evidence Coverage Score (0 – 100%)</span>
          </div>
          <p className="leading-relaxed">
            Measures the percentage of the role’s required skills that have <em>sufficient supporting evidence</em> (diagnostic assessments or verified projects).
          </p>
          <ul className="list-disc list-inside space-y-1 text-slate-500 dark:text-slate-400 pl-1">
            <li>High alignment requires high evidence coverage for true confidence.</li>
            <li>Unassessed skills (claimed without a test) receive partial or zero coverage credit.</li>
            <li>A high coverage score means your profile has been thoroughly evaluated, but does not imply all skills are strengths.</li>
          </ul>
        </div>

        {/* 4-Level Proficiency Standard */}
        <div className="space-y-2">
          <h4 className="font-bold text-slate-900 dark:text-white text-xs uppercase tracking-wider">
            Standard 4-Level Proficiency Framework
          </h4>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
            <div className="p-2.5 rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800">
              <span className="font-bold text-slate-800 dark:text-slate-200 block text-xs">Level 1: Foundational</span>
              <span className="text-[10px] text-slate-500 block mt-0.5">Basic conceptual familiarity; test score &lt;50%</span>
            </div>
            <div className="p-2.5 rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800">
              <span className="font-bold text-slate-800 dark:text-slate-200 block text-xs">Level 2: Developing</span>
              <span className="text-[10px] text-slate-500 block mt-0.5">Demonstrated working knowledge; test score 50–69%</span>
            </div>
            <div className="p-2.5 rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800">
              <span className="font-bold text-slate-800 dark:text-slate-200 block text-xs">Level 3: Proficient</span>
              <span className="text-[10px] text-slate-500 block mt-0.5">Production-ready autonomy; passed test 70–84%</span>
            </div>
            <div className="p-2.5 rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800">
              <span className="font-bold text-slate-800 dark:text-slate-200 block text-xs">Level 4: Advanced</span>
              <span className="text-[10px] text-slate-500 block mt-0.5">Deep architectural mastery; passed test ≥85%</span>
            </div>
          </div>
        </div>

        {/* 5 Distinct Classifications */}
        <div className="space-y-2">
          <h4 className="font-bold text-slate-900 dark:text-white text-xs uppercase tracking-wider">
            Five Authoritative Competency Statuses
          </h4>
          <div className="space-y-1.5">
            <div className="flex items-start gap-2">
              <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300 shrink-0">STRENGTH</span>
              <span className="text-[11px]">Validated evidence meets or exceeds the role requirement level.</span>
            </div>
            <div className="flex items-start gap-2">
              <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-300 shrink-0">DEVELOPING</span>
              <span className="text-[11px]">Demonstrated competency is exactly one level below the role requirement.</span>
            </div>
            <div className="flex items-start gap-2">
              <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-rose-100 text-rose-800 dark:bg-rose-950 dark:text-rose-300 shrink-0">GAP</span>
              <span className="text-[11px]">Validated competency falls two or more levels below benchmark.</span>
            </div>
            <div className="flex items-start gap-2">
              <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-purple-100 text-purple-800 dark:bg-purple-950 dark:text-purple-300 shrink-0">NOT_ASSESSED</span>
              <span className="text-[11px]">Claimed in your resume or profile, but not yet verified with an objective diagnostic test.</span>
            </div>
            <div className="flex items-start gap-2">
              <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-slate-200 text-slate-800 dark:bg-slate-800 dark:text-slate-300 shrink-0">NOT_IN_PROFILE</span>
              <span className="text-[11px]">Required by the role benchmark, but currently unmentioned in your profile or test records.</span>
            </div>
          </div>
        </div>

        <div className="pt-2 flex justify-end">
          <Button size="sm" onClick={onClose}>
            Understood
          </Button>
        </div>
      </div>
    </Modal>
  );
}
