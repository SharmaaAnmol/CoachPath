'use client';

import * as React from 'react';
import Link from 'next/link';
import { AssessmentResultResponse, GradedQuestionResult } from '@/types';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  Award,
  CheckCircle2,
  XCircle,
  HelpCircle,
  TrendingUp,
  AlertTriangle,
  RotateCcw,
  ArrowLeft,
  ChevronDown,
  ChevronUp,
  Sparkles,
  BookOpen,
  Cpu,
} from 'lucide-react';

interface AssessmentResultViewProps {
  result: AssessmentResultResponse;
  onRetake: () => void;
  onBackToCatalog: () => void;
}

export function AssessmentResultView({
  result,
  onRetake,
  onBackToCatalog,
}: AssessmentResultViewProps) {
  const [filterMode, setFilterMode] = React.useState<'all' | 'correct' | 'incorrect'>('all');
  const [expandedQuestions, setExpandedQuestions] = React.useState<Record<string, boolean>>({});

  const toggleExpand = (id: string) => {
    setExpandedQuestions((prev) => ({
      ...prev,
      [id]: !prev[id],
    }));
  };

  const filteredQuestions = result.questions.filter((q) => {
    if (filterMode === 'correct') return q.is_correct;
    if (filterMode === 'incorrect') return !q.is_correct;
    return true;
  });

  const proficiencyVariant = (band: string): 'default' | 'verified' | 'intelligence' | 'action' | 'gap' | 'secondary' | 'outline' => {
    switch (band.toLowerCase()) {
      case 'strong':
        return 'verified';
      case 'proficient':
        return 'intelligence';
      case 'developing':
        return 'action';
      default:
        return 'outline';
    }
  };

  return (
    <div className="space-y-8 max-w-4xl mx-auto">
      {/* Top Banner Card */}
      <Card className="p-6 sm:p-8 bg-gradient-to-br from-slate-900 to-slate-950 text-white border-slate-800 shadow-md">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-6">
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <Badge variant="outline" size="sm" className="border-slate-700 text-slate-300">
                {result.skill_name}
              </Badge>
              <Badge
                variant={result.passed ? 'verified' : 'outline'}
                size="sm"
              >
                {result.passed ? 'PASSED & VERIFIED' : 'CALIBRATED'}
              </Badge>
            </div>
            <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight">
              {result.assessment_title}
            </h1>
            <p className="text-xs sm:text-sm text-slate-400">
              Deterministic diagnostic evaluation calibrated into verified portfolio credentials.
            </p>
          </div>

          {/* Calibrated Score Radial / Box */}
          <div className="flex items-center gap-4 bg-slate-800/80 p-4 sm:p-5 rounded-2xl border border-slate-700/80 shrink-0">
            <div className="text-center">
              <span className="text-xs uppercase tracking-wider text-slate-400 font-semibold block">
                Calibrated Score
              </span>
              <div className="text-3xl sm:text-4xl font-black text-brand-400 mt-0.5">
                {result.score_percentage}%
              </div>
              <Badge variant={proficiencyVariant(result.proficiency_band)} size="sm" className="mt-1.5">
                {result.proficiency_band}
              </Badge>
            </div>
          </div>
        </div>

        {/* Quick Stats Grid */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mt-6 pt-6 border-t border-slate-800/80 text-xs">
          <div>
            <span className="text-slate-400 block">Total Questions</span>
            <span className="text-base font-bold text-slate-100">{result.total_questions}</span>
          </div>
          <div>
            <span className="text-slate-400 block">Correct Answers</span>
            <span className="text-base font-bold text-emerald-400">
              {result.correct_count} of {result.total_questions}
            </span>
          </div>
          <div>
            <span className="text-slate-400 block">Passing Target</span>
            <span className="text-base font-bold text-slate-100">{result.passing_threshold}%</span>
          </div>
          <div>
            <span className="text-slate-400 block">Proficiency Tier</span>
            <span className="text-base font-bold text-indigo-300">{result.proficiency_band}</span>
          </div>
        </div>
      </Card>

      {/* Pedagogical Feedback Summaries */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Strengths Card */}
        <Card className="p-5 border-emerald-200 dark:border-emerald-900/60 bg-emerald-50/40 dark:bg-emerald-950/20 space-y-3">
          <div className="flex items-center gap-2 text-emerald-800 dark:text-emerald-300 font-bold text-sm">
            <TrendingUp className="w-4 h-4 text-emerald-600" />
            <span>Demonstrated Strengths</span>
          </div>
          <p className="text-xs sm:text-sm text-slate-700 dark:text-slate-300 leading-relaxed">
            {result.strengths_summary}
          </p>
        </Card>

        {/* Focus Areas Card */}
        <Card className="p-5 border-amber-200 dark:border-amber-900/60 bg-amber-50/40 dark:bg-amber-950/20 space-y-3">
          <div className="flex items-center gap-2 text-amber-800 dark:text-amber-300 font-bold text-sm">
            <AlertTriangle className="w-4 h-4 text-amber-600" />
            <span>Targeted Focus Areas</span>
          </div>
          <p className="text-xs sm:text-sm text-slate-700 dark:text-slate-300 leading-relaxed">
            {result.weaknesses_summary}
          </p>
        </Card>
      </div>

      {/* Breakdowns: Topic & Difficulty */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Topic Breakdown */}
        <Card className="p-5 space-y-4">
          <h3 className="text-sm font-bold text-slate-900 dark:text-white flex items-center gap-2">
            <BookOpen className="w-4 h-4 text-brand-600" />
            <span>Subtopic Breakdown</span>
          </h3>

          <div className="space-y-3">
            {result.topic_breakdown.map((t, idx) => (
              <div key={idx} className="space-y-1 text-xs">
                <div className="flex justify-between items-center text-slate-600 dark:text-slate-300">
                  <span className="font-medium truncate max-w-[220px]">{t.topic}</span>
                  <span className="font-semibold">
                    {t.correct}/{t.total} ({Math.round(t.percentage)}%)
                  </span>
                </div>
                <div className="w-full bg-slate-100 dark:bg-slate-800 rounded-full h-1.5 overflow-hidden">
                  <div
                    className={`h-1.5 rounded-full ${
                      t.percentage >= 70
                        ? 'bg-emerald-500'
                        : t.percentage >= 50
                        ? 'bg-amber-500'
                        : 'bg-rose-500'
                    }`}
                    style={{ width: `${t.percentage}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </Card>

        {/* Difficulty Tier Performance */}
        <Card className="p-5 space-y-4">
          <h3 className="text-sm font-bold text-slate-900 dark:text-white flex items-center gap-2">
            <Award className="w-4 h-4 text-brand-600" />
            <span>Difficulty Breakdown</span>
          </h3>

          <div className="space-y-4 pt-1">
            {Object.entries(result.difficulty_breakdown).map(([diff, stats]) => (
              <div key={diff} className="space-y-1.5 text-xs">
                <div className="flex justify-between items-center">
                  <span className="capitalize font-bold text-slate-700 dark:text-slate-300">
                    {diff} Tier ({stats.total} questions)
                  </span>
                  <span className="font-semibold text-slate-900 dark:text-white">
                    {stats.correct}/{stats.total} ({Math.round(stats.percentage)}%)
                  </span>
                </div>
                <div className="w-full bg-slate-100 dark:bg-slate-800 rounded-full h-2 overflow-hidden">
                  <div
                    className={`h-2 rounded-full ${
                      stats.percentage >= 70
                        ? 'bg-emerald-500'
                        : stats.percentage >= 50
                        ? 'bg-amber-500'
                        : 'bg-rose-500'
                    }`}
                    style={{ width: `${stats.percentage}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </Card>
      </div>

      {/* Action Bar */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-4 p-4 rounded-2xl bg-slate-50 dark:bg-slate-850 border border-slate-200 dark:border-slate-800">
        <Button variant="outline" size="sm" onClick={onBackToCatalog}>
          <ArrowLeft className="w-4 h-4 mr-1.5" />
          Back to Assessments
        </Button>

        <div className="flex items-center gap-3">
          <Link href="/skills">
            <Button variant="intelligence" size="sm">
              <Cpu className="w-4 h-4 mr-1.5" />
              View Skill Gap Impact
            </Button>
          </Link>
          <Button variant="primary" size="sm" onClick={onRetake}>
            <RotateCcw className="w-4 h-4 mr-1.5" />
            Retake Diagnostic Test
          </Button>
        </div>
      </div>

      {/* Question Review Section */}
      <div className="space-y-4 pt-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-2 border-b border-slate-200 dark:border-slate-800">
          <div>
            <h3 className="text-lg font-bold text-slate-900 dark:text-white">
              Pedagogical Question Review
            </h3>
            <p className="text-xs text-slate-500 dark:text-slate-400">
              Review your selected choices, correct answers, and underlying technical explanations.
            </p>
          </div>

          {/* Filter Pills */}
          <div className="flex items-center gap-1.5 bg-slate-100 dark:bg-slate-800 p-1 rounded-xl text-xs font-semibold">
            <button
              type="button"
              onClick={() => setFilterMode('all')}
              className={`px-3 py-1 rounded-lg transition-colors ${
                filterMode === 'all'
                  ? 'bg-white dark:bg-slate-700 text-slate-900 dark:text-white shadow-xs'
                  : 'text-slate-500 hover:text-slate-800 dark:hover:text-slate-200'
              }`}
            >
              All ({result.questions.length})
            </button>
            <button
              type="button"
              onClick={() => setFilterMode('correct')}
              className={`px-3 py-1 rounded-lg transition-colors flex items-center gap-1 ${
                filterMode === 'correct'
                  ? 'bg-emerald-500 text-white shadow-xs'
                  : 'text-slate-500 hover:text-emerald-700 dark:hover:text-emerald-300'
              }`}
            >
              Correct ({result.correct_count})
            </button>
            <button
              type="button"
              onClick={() => setFilterMode('incorrect')}
              className={`px-3 py-1 rounded-lg transition-colors flex items-center gap-1 ${
                filterMode === 'incorrect'
                  ? 'bg-rose-500 text-white shadow-xs'
                  : 'text-slate-500 hover:text-rose-700 dark:hover:text-rose-300'
              }`}
            >
              Incorrect ({result.questions.length - result.correct_count})
            </button>
          </div>
        </div>

        {/* Questions List */}
        <div className="space-y-4">
          {filteredQuestions.map((q) => {
            const isExpanded = expandedQuestions[q.id] ?? true;

            return (
              <Card
                key={q.id}
                className={`p-5 transition-all border ${
                  q.is_correct
                    ? 'border-emerald-200/80 dark:border-emerald-900/40 bg-white dark:bg-slate-900'
                    : 'border-rose-200/80 dark:border-rose-900/40 bg-white dark:bg-slate-900'
                }`}
              >
                <div
                  className="flex items-start justify-between gap-4 cursor-pointer select-none"
                  onClick={() => toggleExpand(q.id)}
                >
                  <div className="flex items-start gap-3">
                    <div className="pt-0.5">
                      {q.is_correct ? (
                        <CheckCircle2 className="w-5 h-5 text-emerald-600 shrink-0" />
                      ) : (
                        <XCircle className="w-5 h-5 text-rose-600 shrink-0" />
                      )}
                    </div>
                    <div className="space-y-1">
                      <div className="flex items-center gap-2">
                        <span className="text-xs font-bold text-slate-400">
                          Question #{q.index}
                        </span>
                        <Badge variant="outline" size="sm">
                          {q.topic}
                        </Badge>
                        <Badge variant="outline" size="sm">
                          {q.difficulty}
                        </Badge>
                      </div>
                      <h4 className="text-sm font-semibold text-slate-900 dark:text-white leading-relaxed">
                        {q.prompt_text}
                      </h4>
                    </div>
                  </div>

                  <button type="button" className="text-slate-400 hover:text-slate-600 p-1">
                    {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                  </button>
                </div>

                {/* Expanded Details */}
                {isExpanded && (
                  <div className="mt-4 pt-4 border-t border-slate-100 dark:border-slate-800 space-y-4">
                    {/* Code Snippet if present */}
                    {q.code_snippet && (
                      <div className="rounded-xl bg-slate-950 text-slate-100 p-3 font-mono text-xs overflow-x-auto border border-slate-800">
                        <pre className="whitespace-pre-wrap">{q.code_snippet}</pre>
                      </div>
                    )}

                    {/* Options list */}
                    <div className="space-y-2">
                      {q.options.map((opt, optIdx) => {
                        const isChosen = q.selected_option_index === optIdx;
                        const isCorrectOption = q.correct_option_index === optIdx;

                        let style =
                          'border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-850/50 text-slate-700 dark:text-slate-300';
                        let badgeLabel = null;

                        if (isCorrectOption) {
                          style =
                            'border-emerald-500 bg-emerald-50/80 dark:bg-emerald-950/40 text-emerald-950 dark:text-emerald-200 font-semibold ring-1 ring-emerald-500';
                          badgeLabel = 'Correct Answer';
                        } else if (isChosen && !isCorrectOption) {
                          style =
                            'border-rose-400 bg-rose-50/80 dark:bg-rose-950/40 text-rose-950 dark:text-rose-200 font-medium';
                          badgeLabel = 'Your Selection';
                        }

                        return (
                          <div
                            key={optIdx}
                            className={`p-3 rounded-xl border text-xs flex items-start justify-between gap-3 ${style}`}
                          >
                            <div className="flex items-start gap-2.5">
                              <span className="font-mono font-bold">
                                {String.fromCharCode(65 + optIdx)}.
                              </span>
                              <span>{opt}</span>
                            </div>
                            {badgeLabel && (
                              <span
                                className={`text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full shrink-0 ${
                                  isCorrectOption
                                    ? 'bg-emerald-200 text-emerald-900 dark:bg-emerald-800 dark:text-emerald-100'
                                    : 'bg-rose-200 text-rose-900 dark:bg-rose-800 dark:text-rose-100'
                                }`}
                              >
                                {badgeLabel}
                              </span>
                            )}
                          </div>
                        );
                      })}
                    </div>

                    {/* Pedagogical Explanation Box */}
                    <div className="p-4 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 space-y-1.5 text-xs">
                      <div className="font-bold text-slate-900 dark:text-white flex items-center gap-1.5">
                        <Sparkles className="w-3.5 h-3.5 text-brand-600" />
                        <span>Pedagogical Feedback</span>
                      </div>
                      <p className="text-slate-600 dark:text-slate-300 leading-relaxed">
                        {q.explanation}
                      </p>
                    </div>
                  </div>
                )}
              </Card>
            );
          })}
        </div>
      </div>
    </div>
  );
}
