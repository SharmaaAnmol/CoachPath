'use client';

import * as React from 'react';
import {
  AssessmentCategoryItem,
  AssessmentResultResponse,
  AttemptSession,
} from '@/types';
import { assessmentClient } from '@/lib/assessment-client';
import { AssessmentRunner } from '@/components/assessments/assessment-runner';
import { AssessmentResultView } from '@/components/assessments/assessment-result-view';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs } from '@/components/ui/tabs';
import {
  CheckCircle2,
  Clock,
  Award,
  Sparkles,
  HelpCircle,
  Play,
  RotateCcw,
  AlertCircle,
  Code2,
  Database,
  Layers,
  Brain,
  Cpu,
  Globe,
  Binary,
} from 'lucide-react';

export default function AssessmentsPage() {
  const [categories, setCategories] = React.useState<AssessmentCategoryItem[]>([]);
  const [isLoading, setIsLoading] = React.useState(true);
  const [errorMessage, setErrorMessage] = React.useState<string | null>(null);
  const [filter, setFilter] = React.useState('all');

  // View state: 'catalog' | 'runner' | 'result'
  const [viewState, setViewState] = React.useState<'catalog' | 'runner' | 'result'>('catalog');
  const [activeSession, setActiveSession] = React.useState<AttemptSession | null>(null);
  const [activeResult, setActiveResult] = React.useState<AssessmentResultResponse | null>(null);
  const [startingCategoryId, setStartingCategoryId] = React.useState<string | null>(null);

  const fetchCategories = React.useCallback(async () => {
    try {
      setIsLoading(true);
      setErrorMessage(null);
      const data = await assessmentClient.listAssessments();
      setCategories(data);
    } catch (err: any) {
      setErrorMessage(err?.message || 'Failed to load assessment catalog.');
    } finally {
      setIsLoading(false);
    }
  }, []);

  React.useEffect(() => {
    fetchCategories();
  }, [fetchCategories]);

  const handleStartOrResume = async (categoryId: string) => {
    try {
      setStartingCategoryId(categoryId);
      setErrorMessage(null);
      const session = await assessmentClient.startOrResumeAttempt(categoryId);
      setActiveSession(session);
      setViewState('runner');
    } catch (err: any) {
      setErrorMessage(err?.message || 'Failed to start assessment attempt.');
    } finally {
      setStartingCategoryId(null);
    }
  };

  const handleReviewResults = async (category: AssessmentCategoryItem) => {
    try {
      setStartingCategoryId(category.skill_id);
      setErrorMessage(null);
      const history = await assessmentClient.getHistory();
      const match = history.find(
        (h) => h.assessment_id === category.id && h.status === 'completed'
      );
      if (match) {
        const result = await assessmentClient.getAttemptResult(match.attempt_id);
        setActiveResult(result);
        setViewState('result');
      } else {
        // Fallback: start new attempt
        await handleStartOrResume(category.skill_id);
      }
    } catch (err: any) {
      setErrorMessage(err?.message || 'Failed to load assessment result.');
    } finally {
      setStartingCategoryId(null);
    }
  };

  const completed = categories.filter((c) => c.user_status === 'completed');
  const inProgress = categories.filter((c) => c.user_status === 'in_progress');
  const available = categories.filter((c) => c.user_status === 'available');

  const filteredCategories = categories.filter((c) => {
    if (filter === 'completed') return c.user_status === 'completed';
    if (filter === 'in_progress') return c.user_status === 'in_progress';
    if (filter === 'available') return c.user_status === 'available';
    return true;
  });

  const filterTabs = [
    { id: 'all', label: 'All Diagnostic Tests', badge: categories.length },
    { id: 'available', label: 'Ready to Take', badge: available.length },
    { id: 'in_progress', label: 'In Progress', badge: inProgress.length },
    { id: 'completed', label: 'Completed & Verified', badge: completed.length },
  ];

  // Helper icons per domain
  const getDomainIcon = (skillId: string) => {
    switch (skillId) {
      case 'python':
      case 'java':
      case 'c-cpp':
      case 'javascript-typescript':
        return <Code2 className="w-4 h-4 text-brand-600" />;
      case 'sql-databases':
        return <Database className="w-4 h-4 text-emerald-600" />;
      case 'dsa':
        return <Binary className="w-4 h-4 text-indigo-600" />;
      case 'web-development':
        return <Globe className="w-4 h-4 text-sky-600" />;
      case 'machine-learning':
        return <Brain className="w-4 h-4 text-purple-600" />;
      case 'ai-llm':
        return <Sparkles className="w-4 h-4 text-amber-500" />;
      default:
        return <Layers className="w-4 h-4 text-slate-500" />;
    }
  };

  // ─── RUNNER VIEW ─────────────────────────────────────────────────────
  if (viewState === 'runner' && activeSession) {
    return (
      <AssessmentRunner
        session={activeSession}
        onComplete={(result) => {
          setActiveResult(result);
          setViewState('result');
          fetchCategories();
        }}
        onExit={() => {
          setViewState('catalog');
          fetchCategories();
        }}
      />
    );
  }

  // ─── RESULT VIEW ─────────────────────────────────────────────────────
  if (viewState === 'result' && activeResult) {
    return (
      <AssessmentResultView
        result={activeResult}
        onRetake={async () => {
          await handleStartOrResume(activeResult.skill_id);
        }}
        onBackToCatalog={() => {
          setViewState('catalog');
          fetchCategories();
        }}
      />
    );
  }

  // ─── CATALOG VIEW (Default) ──────────────────────────────────────────
  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-slate-900 dark:text-white">
            Diagnostic Skill Assessments
          </h2>
          <p className="text-xs sm:text-sm text-slate-500 dark:text-slate-400 mt-1">
            Server-side deterministic evaluations calibrated across 9 core engineering domains with 20 questions per diagnostic attempt.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Badge variant="verified" size="md">
            <CheckCircle2 className="w-3.5 h-3.5 mr-1" />
            {completed.length} of 9 Domains Verified
          </Badge>
        </div>
      </div>

      {/* Error Alert */}
      {errorMessage && (
        <div className="p-4 rounded-xl bg-rose-50 border border-rose-200 text-rose-800 dark:bg-rose-950/40 dark:border-rose-800 dark:text-rose-200 text-xs sm:text-sm flex items-center justify-between">
          <div className="flex items-center gap-2">
            <AlertCircle className="w-4 h-4 shrink-0 text-rose-600" />
            <span>{errorMessage}</span>
          </div>
          <Button size="sm" variant="outline" onClick={fetchCategories}>
            Retry
          </Button>
        </div>
      )}

      {/* Tabs */}
      <Tabs tabs={filterTabs} activeTab={filter} onChange={setFilter} />

      {/* Loading Skeletons */}
      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[...Array(6)].map((_, i) => (
            <Card key={i} className="p-5 space-y-4 animate-pulse">
              <div className="h-4 bg-slate-200 dark:bg-slate-800 rounded-md w-1/3" />
              <div className="h-6 bg-slate-200 dark:bg-slate-800 rounded-md w-3/4" />
              <div className="h-12 bg-slate-100 dark:bg-slate-850 rounded-md w-full" />
              <div className="h-8 bg-slate-200 dark:bg-slate-800 rounded-md w-full" />
            </Card>
          ))}
        </div>
      ) : (
        /* Assessment Categories Grid */
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredCategories.map((asmt) => {
            const isCompleted = asmt.user_status === 'completed';
            const isInProgress = asmt.user_status === 'in_progress';
            const isStarting = startingCategoryId === asmt.skill_id;

            return (
              <Card
                key={asmt.id}
                className="p-5 flex flex-col justify-between hover:border-slate-300 dark:hover:border-slate-700 transition-all shadow-xs"
              >
                <div className="space-y-3">
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex items-center gap-1.5">
                      {getDomainIcon(asmt.skill_id)}
                      <span className="text-xs font-bold text-slate-700 dark:text-slate-300">
                        {asmt.skill_id.toUpperCase()}
                      </span>
                    </div>

                    {isCompleted ? (
                      <div className="flex items-center gap-1.5 text-xs font-bold text-emerald-700 bg-emerald-50 dark:bg-emerald-950/40 dark:text-emerald-300 px-2.5 py-1 rounded-full border border-emerald-200 dark:border-emerald-800">
                        <Award className="w-3.5 h-3.5" />
                        <span>Best: {asmt.user_best_score}%</span>
                      </div>
                    ) : isInProgress ? (
                      <Badge variant="action" size="sm" className="animate-pulse">
                        Resume Test
                      </Badge>
                    ) : (
                      <Badge variant="outline" size="sm">
                        Ready to Take
                      </Badge>
                    )}
                  </div>

                  <div>
                    <h4 className="text-base font-bold text-slate-900 dark:text-white leading-snug">
                      {asmt.title}
                    </h4>
                    <p className="text-xs text-slate-500 dark:text-slate-400 mt-1 line-clamp-2 leading-relaxed">
                      {asmt.description}
                    </p>
                  </div>

                  <div className="flex items-center gap-4 text-xs text-slate-500 dark:text-slate-400 pt-1">
                    <span className="flex items-center gap-1">
                      <Clock className="w-3.5 h-3.5" />
                      {asmt.time_limit_minutes} mins
                    </span>
                    <span className="flex items-center gap-1">
                      <HelpCircle className="w-3.5 h-3.5" />
                      20 of {asmt.question_count} questions
                    </span>
                  </div>
                </div>

                <div className="pt-4 mt-4 border-t border-slate-100 dark:border-slate-800 flex items-center justify-between">
                  {isCompleted ? (
                    <div className="flex items-center gap-1 text-xs text-emerald-600 font-medium">
                      <CheckCircle2 className="w-3.5 h-3.5" />
                      <span>{asmt.attempt_count} Attempt{asmt.attempt_count > 1 ? 's' : ''}</span>
                    </div>
                  ) : (
                    <span className="text-[11px] text-slate-400 font-medium">
                      7 Basic &bull; 7 Inter &bull; 6 Adv
                    </span>
                  )}

                  <div className="flex items-center gap-2">
                    {isCompleted ? (
                      <>
                        <Button
                          size="sm"
                          variant="outline"
                          disabled={isStarting}
                          onClick={() => handleReviewResults(asmt)}
                        >
                          Review
                        </Button>
                        <Button
                          size="sm"
                          variant="primary"
                          disabled={isStarting}
                          onClick={() => handleStartOrResume(asmt.skill_id)}
                        >
                          {isStarting ? 'Loading...' : 'Retake'}
                        </Button>
                      </>
                    ) : (
                      <Button
                        size="sm"
                        variant="primary"
                        disabled={isStarting}
                        onClick={() => handleStartOrResume(asmt.skill_id)}
                      >
                        {isStarting
                          ? 'Loading...'
                          : isInProgress
                          ? 'Resume Diagnostic'
                          : 'Start Diagnostic'}
                      </Button>
                    )}
                  </div>
                </div>
              </Card>
            );
          })}
        </div>
      )}
    </div>
  );
}
