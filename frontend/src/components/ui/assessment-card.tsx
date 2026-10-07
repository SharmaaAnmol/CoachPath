import * as React from 'react';
import { cn } from '@/lib/utils';
import { Assessment } from '@/types';
import { Card } from './card';
import { Button } from './button';
import { Badge } from './badge';
import { Clock, HelpCircle, CheckCircle2, Award } from 'lucide-react';

export interface AssessmentCardProps {
  assessment: Assessment;
  onStart?: (assessment: Assessment) => void;
  className?: string;
}

export function AssessmentCard({ assessment, onStart, className }: AssessmentCardProps) {
  const isCompleted = assessment.status === 'completed';

  const difficultyColors = {
    Beginner: 'default',
    Intermediate: 'action',
    Advanced: 'intelligence',
  } as const;

  return (
    <Card className={cn('p-5 flex flex-col justify-between hover:border-slate-300 transition-all', className)}>
      <div className="space-y-3">
        <div className="flex items-start justify-between gap-3">
          <Badge variant={difficultyColors[assessment.difficulty]} size="sm">
            {assessment.difficulty}
          </Badge>
          {isCompleted ? (
            <div className="flex items-center gap-1.5 text-xs font-bold text-emerald-700 bg-emerald-50 dark:bg-emerald-950/40 dark:text-emerald-300 px-2.5 py-1 rounded-full border border-emerald-200 dark:border-emerald-800">
              <Award className="w-3.5 h-3.5" />
              <span>Score: {assessment.score}%</span>
            </div>
          ) : (
            <Badge variant="outline" size="sm">
              Ready to take
            </Badge>
          )}
        </div>

        <div>
          <h4 className="text-base font-bold text-slate-900 dark:text-white leading-snug">
            {assessment.title}
          </h4>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
            Validates: <span className="font-semibold text-slate-700 dark:text-slate-300">{assessment.skillName}</span>
          </p>
        </div>

        <div className="flex items-center gap-4 text-xs text-slate-500 dark:text-slate-400 pt-1">
          <span className="flex items-center gap-1">
            <Clock className="w-3.5 h-3.5" />
            {assessment.durationMinutes} mins
          </span>
          <span className="flex items-center gap-1">
            <HelpCircle className="w-3.5 h-3.5" />
            {assessment.questionCount} diagnostic questions
          </span>
        </div>
      </div>

      <div className="pt-4 mt-4 border-t border-slate-100 dark:border-slate-800 flex items-center justify-between">
        {isCompleted ? (
          <div className="flex items-center gap-1.5 text-xs text-slate-500">
            <CheckCircle2 className="w-4 h-4 text-emerald-600" />
            <span>Passed & Verified</span>
          </div>
        ) : (
          <span className="text-xs text-slate-400 font-medium">Deterministic evaluation</span>
        )}

        <Button
          size="sm"
          variant={isCompleted ? 'outline' : 'primary'}
          onClick={() => onStart?.(assessment)}
        >
          {isCompleted ? 'Review Score' : 'Start Diagnostic'}
        </Button>
      </div>
    </Card>
  );
}
