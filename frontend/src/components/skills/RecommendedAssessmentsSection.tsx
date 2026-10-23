'use client';

import * as React from 'react';
import { RecommendedAssessmentItem } from '@/types';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  ClipboardCheck,
  Clock,
  HelpCircle,
  ArrowRight,
  Sparkles,
  Award,
} from 'lucide-react';
import Link from 'next/link';

interface RecommendedAssessmentsSectionProps {
  assessments: RecommendedAssessmentItem[];
}

export function RecommendedAssessmentsSection({
  assessments,
}: RecommendedAssessmentsSectionProps) {
  if (assessments.length === 0) {
    return null;
  }

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="p-1 rounded-lg bg-indigo-50 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-400">
            <ClipboardCheck className="w-4 h-4" />
          </span>
          <div>
            <h3 className="text-sm font-bold text-slate-900 dark:text-white uppercase tracking-wider">
              Recommended Diagnostic Assessments
            </h3>
            <p className="text-xs text-slate-500 dark:text-slate-400">
              Objective examinations designed to calibrate your baseline evidence and verify unassessed skills.
            </p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
        {assessments.map((asmt) => (
          <Card
            key={asmt.assessment_id}
            className="p-4 border-slate-200 dark:border-slate-800 hover:border-indigo-300 dark:hover:border-indigo-800 transition-all flex flex-col justify-between space-y-3 bg-white dark:bg-slate-900 shadow-sm"
          >
            <div className="space-y-1.5">
              <div className="flex items-center justify-between">
                <Badge variant="outline" className="text-[10px] bg-indigo-50 dark:bg-indigo-950/40 text-indigo-700 dark:text-indigo-300 border-indigo-200">
                  Diagnostic Exam
                </Badge>
                <div className="flex items-center gap-1 text-[11px] text-slate-400">
                  <Clock className="w-3 h-3" />
                  <span>{asmt.estimated_minutes} min</span>
                </div>
              </div>

              <h4 className="text-sm font-bold text-slate-900 dark:text-white">
                {asmt.title}
              </h4>

              <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed">
                {asmt.reason}
              </p>
            </div>

            <div className="pt-2 border-t border-slate-100 dark:border-slate-800 flex items-center justify-between">
              <span className="text-[11px] text-slate-400">
                20 Multiple Choice Questions
              </span>

              <Link href="/assessments">
                <Button size="sm" variant="intelligence" className="text-xs h-7.5">
                  Start Test <ArrowRight className="w-3 h-3 ml-1" />
                </Button>
              </Link>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
}
