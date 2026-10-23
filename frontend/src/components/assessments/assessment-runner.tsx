'use client';

import * as React from 'react';
import {
  AttemptQuestionPublic,
  AttemptSession,
  AssessmentResultResponse,
} from '@/types';
import { assessmentClient } from '@/lib/assessment-client';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Modal } from '@/components/ui/modal';
import {
  Clock,
  ChevronLeft,
  ChevronRight,
  CheckCircle2,
  AlertCircle,
  HelpCircle,
  Flag,
  RotateCcw,
  Sparkles,
} from 'lucide-react';

interface AssessmentRunnerProps {
  session: AttemptSession;
  onComplete: (result: AssessmentResultResponse) => void;
  onExit: () => void;
}

export function AssessmentRunner({
  session,
  onComplete,
  onExit,
}: AssessmentRunnerProps) {
  const [currentIdx, setCurrentIdx] = React.useState(0);
  const [answers, setAnswers] = React.useState<Record<string, number>>(
    session.current_answers || {}
  );
  const [isSubmittingAnswer, setIsSubmittingAnswer] = React.useState(false);
  const [isCompleting, setIsCompleting] = React.useState(false);
  const [showConfirmModal, setShowConfirmModal] = React.useState(false);
  const [errorMessage, setErrorMessage] = React.useState<string | null>(null);

  // Time remaining calculation
  const totalMinutes = session.time_limit_minutes || 40;
  const startedTime = new Date(session.started_at).getTime();
  const [timeRemainingSeconds, setTimeRemainingSeconds] = React.useState(() => {
    const elapsed = Math.floor((Date.now() - startedTime) / 1000);
    const totalSecs = totalMinutes * 60;
    return Math.max(0, totalSecs - elapsed);
  });

  React.useEffect(() => {
    const timer = setInterval(() => {
      setTimeRemainingSeconds((prev) => {
        if (prev <= 1) {
          clearInterval(timer);
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  const formatTimer = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const questions = session.questions;
  const currentQuestion: AttemptQuestionPublic | undefined = questions[currentIdx];
  const totalQuestions = questions.length;
  const answeredCount = Object.keys(answers).length;
  const progressPercentage = Math.round((answeredCount / totalQuestions) * 100);

  const handleSelectOption = async (optionIndex: number) => {
    if (!currentQuestion || isCompleting) return;

    // Optimistically update local state
    setAnswers((prev) => ({
      ...prev,
      [currentQuestion.id]: optionIndex,
    }));
    setErrorMessage(null);

    // Save answer choice to server
    try {
      setIsSubmittingAnswer(true);
      await assessmentClient.submitAnswer(
        session.attempt_id,
        currentQuestion.id,
        optionIndex
      );
    } catch (err: any) {
      setErrorMessage(
        err?.message || 'Failed to sync answer with server. Please try again.'
      );
    } finally {
      setIsSubmittingAnswer(false);
    }
  };

  const handleFinalSubmit = async () => {
    try {
      setIsCompleting(true);
      setErrorMessage(null);
      setShowConfirmModal(false);
      const result = await assessmentClient.completeAttempt(session.attempt_id);
      onComplete(result);
    } catch (err: any) {
      setIsCompleting(false);
      setErrorMessage(
        err?.message || 'Failed to finalize assessment. Please try again.'
      );
    }
  };

  const difficultyVariant = (diff: string): 'default' | 'verified' | 'intelligence' | 'action' | 'gap' | 'secondary' | 'outline' => {
    switch (diff.toLowerCase()) {
      case 'basic':
        return 'default';
      case 'intermediate':
        return 'action';
      case 'advanced':
        return 'intelligence';
      default:
        return 'outline';
    }
  };

  if (!currentQuestion) {
    return (
      <Card className="p-8 text-center space-y-4">
        <AlertCircle className="w-10 h-10 text-amber-500 mx-auto" />
        <h3 className="text-lg font-bold">No Questions in Session</h3>
        <p className="text-sm text-slate-500">
          This attempt does not contain active questions.
        </p>
        <Button variant="outline" onClick={onExit}>
          Return to Assessments
        </Button>
      </Card>
    );
  }

  const currentSelectedOption = answers[currentQuestion.id];

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      {/* Top Header Card */}
      <Card className="p-5 shadow-sm border-slate-200 dark:border-slate-800">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xs font-semibold text-brand-600 dark:text-brand-400 uppercase tracking-wider">
                {session.skill_name}
              </span>
              <span className="text-slate-300 dark:text-slate-700">&bull;</span>
              <span className="text-xs text-slate-500 dark:text-slate-400">
                Diagnostic Assessment
              </span>
            </div>
            <h2 className="text-xl font-bold text-slate-900 dark:text-white mt-1">
              {session.assessment_title}
            </h2>
          </div>

          <div className="flex items-center gap-4">
            {/* Countdown Timer */}
            <div
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg border font-mono text-xs font-semibold ${
                timeRemainingSeconds < 300
                  ? 'border-rose-300 bg-rose-50 text-rose-700 dark:bg-rose-950/40 dark:text-rose-300 animate-pulse'
                  : 'border-slate-200 bg-slate-50 text-slate-700 dark:bg-slate-800 dark:border-slate-700 dark:text-slate-300'
              }`}
            >
              <Clock className="w-3.5 h-3.5" />
              <span>{formatTimer(timeRemainingSeconds)}</span>
            </div>

            <Button size="sm" variant="outline" onClick={onExit}>
              Save & Exit
            </Button>
          </div>
        </div>

        {/* Progress Tracker */}
        <div className="mt-5 space-y-2">
          <div className="flex justify-between text-xs text-slate-500 dark:text-slate-400 font-medium">
            <span>
              Progress: <strong className="text-slate-900 dark:text-white">{answeredCount}</strong> of {totalQuestions} answered ({progressPercentage}%)
            </span>
            <span>Question {currentIdx + 1} of {totalQuestions}</span>
          </div>
          <div className="w-full bg-slate-100 dark:bg-slate-800 rounded-full h-2 overflow-hidden">
            <div
              className="bg-brand-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${progressPercentage}%` }}
            />
          </div>
        </div>

        {/* Question Jump Palette (1 to 20) */}
        <div className="mt-4 pt-4 border-t border-slate-100 dark:border-slate-800/80">
          <div className="flex flex-wrap gap-1.5 sm:gap-2">
            {questions.map((q, idx) => {
              const isAnswered = answers[q.id] !== undefined;
              const isCurrent = idx === currentIdx;

              return (
                <button
                  key={q.id}
                  type="button"
                  onClick={() => setCurrentIdx(idx)}
                  className={`w-7 h-7 sm:w-8 sm:h-8 rounded-lg text-xs font-semibold transition-all flex items-center justify-center ${
                    isCurrent
                      ? 'bg-brand-600 text-white ring-2 ring-brand-400 ring-offset-1 dark:ring-offset-slate-900 shadow-sm'
                      : isAnswered
                      ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950/60 dark:text-emerald-300 border border-emerald-300 dark:border-emerald-800'
                      : 'bg-slate-50 text-slate-600 dark:bg-slate-800 dark:text-slate-400 border border-slate-200 dark:border-slate-700 hover:border-slate-300'
                  }`}
                  title={`Question ${idx + 1}: ${q.topic} (${q.difficulty})`}
                >
                  {idx + 1}
                </button>
              );
            })}
          </div>
        </div>
      </Card>

      {/* Error Alert */}
      {errorMessage && (
        <div className="p-4 rounded-xl bg-rose-50 border border-rose-200 text-rose-800 dark:bg-rose-950/40 dark:border-rose-800 dark:text-rose-200 text-xs sm:text-sm flex items-center gap-2">
          <AlertCircle className="w-4 h-4 shrink-0 text-rose-600" />
          <span>{errorMessage}</span>
        </div>
      )}

      {/* Question Card */}
      <Card className="p-6 space-y-6 shadow-sm border-slate-200 dark:border-slate-800">
        {/* Question Meta */}
        <div className="flex items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            <Badge variant={difficultyVariant(currentQuestion.difficulty)} size="sm">
              {currentQuestion.difficulty.toUpperCase()}
            </Badge>
            <Badge variant="outline" size="sm">
              {currentQuestion.topic}
            </Badge>
          </div>
          <span className="text-xs text-slate-400">
            Question #{currentIdx + 1} of {totalQuestions}
          </span>
        </div>

        {/* Prompt Text */}
        <div className="space-y-4">
          <h3 className="text-base sm:text-lg font-semibold text-slate-900 dark:text-white leading-relaxed">
            {currentQuestion.prompt_text}
          </h3>

          {/* Code Snippet Box */}
          {currentQuestion.code_snippet && (
            <div className="rounded-xl bg-slate-950 text-slate-100 p-4 font-mono text-xs overflow-x-auto border border-slate-800 shadow-inner">
              <pre className="leading-relaxed whitespace-pre-wrap">{currentQuestion.code_snippet}</pre>
            </div>
          )}
        </div>

        {/* Option Choices (A, B, C, D) */}
        <div className="space-y-3 pt-2">
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider block">
            Select the correct option:
          </span>

          {currentQuestion.options.map((optionText, optIdx) => {
            const isSelected = currentSelectedOption === optIdx;

            return (
              <button
                key={optIdx}
                type="button"
                onClick={() => handleSelectOption(optIdx)}
                className={`w-full p-4 rounded-xl border text-left text-xs sm:text-sm transition-all flex items-start gap-3.5 ${
                  isSelected
                    ? 'border-brand-600 bg-brand-50/80 text-brand-950 dark:bg-brand-950/40 dark:text-brand-100 font-medium ring-1 ring-brand-500'
                    : 'border-slate-200 hover:border-slate-300 hover:bg-slate-50/60 dark:border-slate-800 dark:hover:bg-slate-850 text-slate-700 dark:text-slate-300'
                }`}
              >
                <div
                  className={`w-6 h-6 rounded-full flex items-center justify-center font-mono font-bold text-xs shrink-0 transition-colors ${
                    isSelected
                      ? 'bg-brand-600 text-white'
                      : 'bg-slate-100 dark:bg-slate-800 text-slate-500'
                  }`}
                >
                  {String.fromCharCode(65 + optIdx)}
                </div>
                <div className="flex-1 leading-relaxed pt-0.5">{optionText}</div>
              </button>
            );
          })}
        </div>

        {/* Bottom Navigation Toolbar */}
        <div className="pt-6 border-t border-slate-100 dark:border-slate-800 flex items-center justify-between gap-3">
          <Button
            size="sm"
            variant="outline"
            disabled={currentIdx === 0}
            onClick={() => setCurrentIdx((prev) => Math.max(0, prev - 1))}
          >
            <ChevronLeft className="w-4 h-4 mr-1" />
            Previous
          </Button>

          <div className="flex items-center gap-2">
            {currentIdx < totalQuestions - 1 ? (
              <Button
                size="sm"
                variant="primary"
                onClick={() => setCurrentIdx((prev) => Math.min(totalQuestions - 1, prev + 1))}
              >
                Next
                <ChevronRight className="w-4 h-4 ml-1" />
              </Button>
            ) : (
              <Button
                size="sm"
                variant="primary"
                disabled={isCompleting}
                onClick={() => {
                  if (answeredCount < totalQuestions) {
                    setShowConfirmModal(true);
                  } else {
                    handleFinalSubmit();
                  }
                }}
              >
                {isCompleting ? 'Grading Answers...' : 'Submit Assessment'}
                <CheckCircle2 className="w-4 h-4 ml-1.5" />
              </Button>
            )}
          </div>
        </div>
      </Card>

      {/* Confirmation Modal when submitting with unanswered questions */}
      <Modal
        isOpen={showConfirmModal}
        onClose={() => setShowConfirmModal(false)}
        title="Unanswered Questions Detected"
        description={`You have answered ${answeredCount} of ${totalQuestions} questions. Unanswered questions will be scored as 0.`}
        maxWidth="md"
        footer={
          <div className="flex items-center justify-end gap-2 w-full">
            <Button
              size="sm"
              variant="outline"
              onClick={() => setShowConfirmModal(false)}
            >
              Continue Test
            </Button>
            <Button
              size="sm"
              variant="primary"
              disabled={isCompleting}
              onClick={handleFinalSubmit}
            >
              {isCompleting ? 'Evaluating...' : 'Confirm Submission'}
            </Button>
          </div>
        }
      >
        <div className="p-4 rounded-xl bg-amber-50 dark:bg-amber-950/40 border border-amber-200 dark:border-amber-800 text-xs text-amber-800 dark:text-amber-300 space-y-2">
          <p className="font-semibold">
            {totalQuestions - answeredCount} questions remain unanswered.
          </p>
          <p>
            You can return to the test using the numbered buttons above to answer all questions, or submit now to receive your calibrated score.
          </p>
        </div>
      </Modal>
    </div>
  );
}
