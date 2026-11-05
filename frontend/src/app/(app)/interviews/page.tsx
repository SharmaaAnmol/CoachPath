'use client';

import * as React from 'react';
import { mockScheduledInterviews } from '@/lib/mock/data';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { ProgressBar } from '@/components/ui/progress-bar';
import { DemoPreviewBanner } from '@/components/ui/demo-preview-banner';
import {
  MessageSquareCode,
  Calendar,
  Clock,
  Sparkles,
  ChevronDown,
  ChevronUp,
  CheckCircle2,
  Building2,
  HelpCircle,
} from 'lucide-react';

export default function InterviewsPage() {
  const activeInterview = mockScheduledInterviews[0];
  const [expandedQuestionId, setExpandedQuestionId] = React.useState<string | null>(
    activeInterview?.questions[0]?.id || null
  );

  return (
    <div className="space-y-6">
      {/* Demo Preview Banner */}
      <DemoPreviewBanner
        plannedPhase="Phase 14"
        featureName="Interactive interview preparation"
      />

      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="font-display text-3xl font-semibold tracking-[-0.035em] text-slate-900 dark:text-ink-fg [text-wrap:balance] md:text-4xl">
            Interview Preparation & STAR Question Bank
          </h1>
          <p className="text-xs text-slate-500 dark:text-ink-muted mt-1">
            Structured drills with verifiable talking points grounded in your actual engineering achievements.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Badge variant="verified" size="md">
            <Calendar className="w-3.5 h-3.5 mr-1" /> Round Active
          </Badge>
        </div>
      </div>

      {/* Scheduled Interview Target Banner */}
      {activeInterview && (
        <Card className="p-6 bg-slate-900 text-white border-slate-800 space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div className="space-y-1">
              <div className="flex items-center gap-2">
                <span className="text-xs font-mono px-2 py-0.5 rounded-full bg-purple-500/20 text-purple-300 border border-purple-500/40 font-bold dark:bg-lav-violet dark:text-lav-light dark:border-lav/50">
                  {activeInterview.roundType} Round
                </span>
                <span className="text-xs text-slate-400">{activeInterview.dateTime}</span>
              </div>
              <h3 className="text-xl font-bold">{activeInterview.company} – {activeInterview.role}</h3>
              <p className="text-xs text-slate-400">
                Interviewers: <strong className="text-white">{activeInterview.interviewerName}</strong> ({activeInterview.interviewerTitle})
              </p>
            </div>

            <div className="w-full sm:w-48 space-y-1">
              <div className="flex justify-between text-xs text-slate-400">
                <span>STAR Preparation</span>
                <span className="font-mono font-bold text-emerald-400 dark:text-lime-soft">{activeInterview.prepCompletedPercentage}%</span>
              </div>
              <ProgressBar value={activeInterview.prepCompletedPercentage} variant="verified" size="sm" />
            </div>
          </div>
        </Card>
      )}

      {/* Question Bank List */}
      <div className="space-y-4">
        <h3 className="text-base font-bold dark:font-display dark:font-semibold dark:tracking-[-0.02em] text-slate-900 dark:text-white">
          Role-Specific Question Bank ({activeInterview.questions.length} Diagnostic Prompts)
        </h3>

        {activeInterview.questions.map((q, idx) => {
          const isExpanded = expandedQuestionId === q.id;
          return (
            <Card key={q.id} className="p-5 space-y-4 transition-all hover:border-slate-300">
              <div
                className="flex items-start justify-between gap-4 cursor-pointer"
                onClick={() => setExpandedQuestionId(isExpanded ? null : q.id)}
              >
                <div className="space-y-1 flex-1">
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-xs font-bold text-purple-600 dark:text-lav">Q{idx + 1}</span>
                    <Badge variant="default" size="sm">
                      {q.category}
                    </Badge>
                    <Badge
                      variant={q.difficulty === 'Staff-Level' ? 'intelligence' : 'action'}
                      size="sm"
                    >
                      {q.difficulty}
                    </Badge>
                  </div>
                  <h4 className="text-base font-bold text-slate-900 dark:text-white pt-0.5 leading-snug">
                    {q.question}
                  </h4>
                </div>

                <button
                  className="p-1 rounded-lg text-slate-400 hover:text-slate-700 dark:hover:text-ink-fg"
                  aria-label="Toggle question drill"
                >
                  {isExpanded ? <ChevronUp className="w-5 h-5" /> : <ChevronDown className="w-5 h-5" />}
                </button>
              </div>

              {/* Expanded STAR details */}
              {isExpanded && (
                <div className="space-y-4 pt-4 border-t border-slate-100 dark:border-white/10 animate-in fade-in duration-200">
                  {/* STAR Structure Grid if available */}
                  {q.suggestedSTAR && (
                    <div className="space-y-2">
                      <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
                        Tailored STAR Story (Situation &bull; Task &bull; Action &bull; Result)
                      </div>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
                        <div className="p-3 rounded-xl bg-slate-50 dark:bg-white/[0.07] border border-slate-200/80 dark:border-white/15 space-y-1">
                          <strong className="text-purple-600 uppercase text-[10px] tracking-wider block dark:text-lav">
                            Situation
                          </strong>
                          <p className="text-slate-700 dark:text-ink-fg/80 leading-relaxed">
                            {q.suggestedSTAR.situation}
                          </p>
                        </div>
                        <div className="p-3 rounded-xl bg-slate-50 dark:bg-white/[0.07] border border-slate-200/80 dark:border-white/15 space-y-1">
                          <strong className="text-indigo-600 uppercase text-[10px] tracking-wider block dark:text-lav">
                            Task
                          </strong>
                          <p className="text-slate-700 dark:text-ink-fg/80 leading-relaxed">
                            {q.suggestedSTAR.task}
                          </p>
                        </div>
                        <div className="p-3 rounded-xl bg-slate-50 dark:bg-white/[0.07] border border-slate-200/80 dark:border-white/15 space-y-1">
                          <strong className="text-emerald-600 uppercase text-[10px] tracking-wider block dark:text-lime">
                            Action Taken
                          </strong>
                          <p className="text-slate-700 dark:text-ink-fg/80 leading-relaxed">
                            {q.suggestedSTAR.action}
                          </p>
                        </div>
                        <div className="p-3 rounded-xl bg-slate-50 dark:bg-white/[0.07] border border-slate-200/80 dark:border-white/15 space-y-1">
                          <strong className="text-amber-600 uppercase text-[10px] tracking-wider block">
                            Measurable Result
                          </strong>
                          <p className="text-slate-700 dark:text-ink-fg/80 leading-relaxed">
                            {q.suggestedSTAR.result}
                          </p>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Key Talking Points */}
                  <div className="p-4 rounded-xl bg-purple-50/50 dark:bg-lav/10 border border-purple-200/80 dark:border-lav/30 space-y-2 text-xs">
                    <div className="font-bold text-purple-900 dark:text-lav-light uppercase tracking-wider text-[11px]">
                      Essential Talking Points & Rubric Items:
                    </div>
                    <ul className="list-disc list-inside space-y-1 text-slate-700 dark:text-ink-fg/80 leading-relaxed">
                      {q.keyTalkingPoints.map((pt, pidx) => (
                        <li key={pidx}>{pt}</li>
                      ))}
                    </ul>
                  </div>
                </div>
              )}
            </Card>
          );
        })}
      </div>
    </div>
  );
}
