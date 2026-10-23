'use client';

import * as React from 'react';
import { PrioritizedGapItem } from '@/types';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import {
  AlertTriangle,
  ArrowRight,
  ClipboardCheck,
  BookOpen,
  Code,
  CheckCircle2,
  HelpCircle,
} from 'lucide-react';
import Link from 'next/link';

interface GapPriorityListProps {
  gaps: PrioritizedGapItem[];
  roleTitle: string;
}

export function GapPriorityList({ gaps, roleTitle }: GapPriorityListProps) {
  if (gaps.length === 0) {
    return (
      <Card className="p-6 text-center space-y-2 border-emerald-200 bg-emerald-50/20 dark:bg-emerald-950/20">
        <CheckCircle2 className="w-8 h-8 text-emerald-600 mx-auto" />
        <h4 className="text-sm font-bold text-slate-900 dark:text-white">
          No Outstanding Benchmark Gaps!
        </h4>
        <p className="text-xs text-slate-600 dark:text-slate-400 max-w-md mx-auto">
          All required skills for {roleTitle} currently meet or exceed required competency thresholds.
        </p>
      </Card>
    );
  }

  const getPriorityBadge = (priority: string) => {
    switch (priority) {
      case 'CRITICAL':
        return (
          <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider bg-rose-100 text-rose-800 border border-rose-300 dark:bg-rose-950 dark:text-rose-300 dark:border-rose-800">
            Critical Priority
          </span>
        );
      case 'HIGH':
        return (
          <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider bg-amber-100 text-amber-800 border border-amber-300 dark:bg-amber-950 dark:text-amber-300 dark:border-amber-800">
            High Priority
          </span>
        );
      case 'MEDIUM':
        return (
          <span className="px-2 py-0.5 rounded text-[10px] font-semibold uppercase tracking-wider bg-sky-100 text-sky-800 border border-sky-300 dark:bg-sky-950 dark:text-sky-300 dark:border-sky-800">
            Medium Priority
          </span>
        );
      default:
        return (
          <span className="px-2 py-0.5 rounded text-[10px] font-medium uppercase tracking-wider bg-slate-100 text-slate-700 border border-slate-200 dark:bg-slate-800 dark:text-slate-300 dark:border-slate-700">
            Low Priority
          </span>
        );
    }
  };

  const getActionBadge = (actionType: string) => {
    if (actionType === 'TAKE_ASSESSMENT') {
      return (
        <span className="px-2 py-0.5 rounded text-[10px] font-bold tracking-wider bg-purple-50 text-purple-700 border border-purple-200 dark:bg-purple-950/40 dark:text-purple-300 flex items-center gap-1">
          <ClipboardCheck className="w-3 h-3" /> ASSESS FIRST
        </span>
      );
    }
    return (
      <span className="px-2 py-0.5 rounded text-[10px] font-bold tracking-wider bg-indigo-50 text-indigo-700 border border-indigo-200 dark:bg-indigo-950/40 dark:text-indigo-300 flex items-center gap-1">
        <BookOpen className="w-3 h-3" /> LEARN & IMPROVE
      </span>
    );
  };

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-sm font-bold text-slate-900 dark:text-white uppercase tracking-wider">
            Prioritized Remedial Action Plan
          </h3>
          <p className="text-xs text-slate-500 dark:text-slate-400">
            Deterministically ranked by requirement weight, deficit severity, and assessment readiness.
          </p>
        </div>
        <span className="text-xs font-semibold text-slate-500">
          {gaps.length} Action Item{gaps.length > 1 ? 's' : ''}
        </span>
      </div>

      <div className="grid grid-cols-1 gap-3">
        {gaps.map((gap) => {
          const isAssessmentAction = gap.action_type === 'TAKE_ASSESSMENT';

          return (
            <Card
              key={`${gap.rank}-${gap.skill_id}`}
              className="p-4 border-slate-200 dark:border-slate-800 hover:border-slate-300 dark:hover:border-slate-700 transition-all bg-white dark:bg-slate-900 shadow-sm space-y-3"
            >
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                <div className="flex items-center gap-2.5">
                  <span className="w-6 h-6 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 text-xs font-black flex items-center justify-center shrink-0">
                    {gap.rank}
                  </span>
                  <div className="flex items-center gap-2">
                    <h4 className="text-sm font-bold text-slate-900 dark:text-white">
                      {gap.skill_name}
                    </h4>
                    {getPriorityBadge(gap.priority)}
                    {getActionBadge(gap.action_type)}
                  </div>
                </div>

                <div className="text-xs font-medium text-slate-500 self-end sm:self-center">
                  Level {gap.current_level} <span className="text-slate-300 dark:text-slate-700 mx-1">→</span> Level {gap.required_level} Required
                </div>
              </div>

              {/* Rationale and Details */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs pt-1">
                <div className="md:col-span-2 space-y-1">
                  <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
                    Why This Matters for {roleTitle}:
                  </span>
                  <p className="text-slate-600 dark:text-slate-300 leading-relaxed">
                    {gap.reason}
                  </p>
                </div>

                <div className="space-y-1">
                  <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
                    Recommended Action:
                  </span>
                  <p className="text-slate-700 dark:text-slate-200 font-medium">
                    {gap.action_description}
                  </p>
                </div>
              </div>

              {/* CTA footer */}
              <div className="pt-2 border-t border-slate-100 dark:border-slate-800 flex items-center justify-between">
                <span className="text-[11px] text-slate-400 capitalize">
                  Requirement Tier: <strong className="text-slate-700 dark:text-slate-300">{gap.importance}</strong>
                </span>

                <Link href="/assessments">
                  <Button size="sm" variant={isAssessmentAction ? 'intelligence' : 'outline'} className="text-xs h-7.5">
                    {isAssessmentAction ? (
                      <>
                        <ClipboardCheck className="w-3.5 h-3.5 mr-1" />
                        Take Diagnostic Test
                      </>
                    ) : (
                      <>
                        <BookOpen className="w-3.5 h-3.5 mr-1" />
                        Explore Assessment Topics
                      </>
                    )}
                  </Button>
                </Link>
              </div>
            </Card>
          );
        })}
      </div>
    </div>
  );
}
