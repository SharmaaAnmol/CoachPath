'use client';

import * as React from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { onboardingClient } from '@/lib/onboarding-client';
import { ApiClientError } from '@/lib/api-client';
import {
  ConversationTurn,
  OnboardingProgressData,
  OnboardingSessionData,
  OnboardingSummary,
} from '@/types';
import { OnboardingProgress } from '@/components/onboarding/onboarding-progress';
import {
  ConversationMessage,
  AIMessageThinking,
} from '@/components/onboarding/conversation-message';
import { QuestionInput } from '@/components/onboarding/question-input';
import { CareerSummaryReview } from '@/components/onboarding/career-summary-review';
import { OnboardingCompletion } from '@/components/onboarding/onboarding-completion';
import { OnboardingErrorBanner } from '@/components/onboarding/onboarding-error-banner';
import { Button } from '@/components/ui/button';
import { Sparkles, ArrowLeft, RefreshCw, Loader2 } from 'lucide-react';

export default function OnboardingPage() {
  const router = useRouter();

  // Primary State
  const [session, setSession] = React.useState<OnboardingSessionData | null>(null);
  const [progress, setProgress] = React.useState<OnboardingProgressData | null>(null);
  const [turns, setTurns] = React.useState<ConversationTurn[]>([]);
  const [summary, setSummary] = React.useState<OnboardingSummary | null>(null);

  // Loading States
  const [isLoadingSession, setIsLoadingSession] = React.useState(true);
  const [isSubmitting, setIsSubmitting] = React.useState(false);
  const [isConfirming, setIsConfirming] = React.useState(false);

  // Error State & Retry Tracking
  const [errorInfo, setErrorInfo] = React.useState<{ message: string; status?: number } | null>(null);
  const [lastFailedResponse, setLastFailedResponse] = React.useState<string | null>(null);

  // Chat scroll anchor
  const chatBottomRef = React.useRef<HTMLDivElement>(null);

  const scrollToBottom = (smooth = true) => {
    chatBottomRef.current?.scrollIntoView({ behavior: smooth ? 'smooth' : 'auto' });
  };

  // Helper to load complete session data and history
  const loadFullSessionState = React.useCallback(async () => {
    try {
      setErrorInfo(null);
      // 1. Fetch Session
      const sessionData = await onboardingClient.getSession();
      setSession(sessionData);

      // 2. Fetch Turns History
      const historyData = await onboardingClient.getHistory();
      setTurns(historyData);

      // 3. Fetch Progress
      try {
        const progressData = await onboardingClient.getProgress();
        setProgress(progressData);
      } catch {
        // Non-blocking if progress fetch has hiccup
      }

      // 4. If session is awaiting confirmation or completed, fetch summary
      if (sessionData.status === 'awaiting_confirmation' || sessionData.status === 'completed') {
        try {
          const summaryData = await onboardingClient.getSummary();
          setSummary(summaryData.summary);
        } catch {
          // Non-blocking
        }
      }
    } catch (err: unknown) {
      if (err instanceof ApiClientError) {
        setErrorInfo({ message: err.message, status: err.status });
      } else {
        setErrorInfo({ message: 'Failed to synchronize onboarding session.' });
      }
    }
  }, []);

  // Initialization: Start or Resume Session
  React.useEffect(() => {
    let isMounted = true;

    const initialize = async () => {
      setIsLoadingSession(true);
      setErrorInfo(null);

      try {
        // Attempt start / resume
        const startRes = await onboardingClient.startOnboarding();
        if (!isMounted) return;

        // Load complete history and state
        await loadFullSessionState();
      } catch (err: unknown) {
        if (!isMounted) return;

        if (err instanceof ApiClientError) {
          // If 409: session already completed, load state to show completion
          if (err.status === 409) {
            await loadFullSessionState();
          } else {
            setErrorInfo({ message: err.message, status: err.status });
          }
        } else {
          setErrorInfo({ message: 'Unable to initialize onboarding session.' });
        }
      } finally {
        if (isMounted) {
          setIsLoadingSession(false);
        }
      }
    };

    initialize();

    return () => {
      isMounted = false;
    };
  }, [loadFullSessionState]);

  // Scroll to bottom when turns update or while thinking
  React.useEffect(() => {
    if (!isLoadingSession) {
      scrollToBottom();
    }
  }, [turns.length, isSubmitting, isLoadingSession]);

  // Response Submission Handler
  const handleSubmitResponse = async (responseText: string) => {
    if (!responseText.trim() || isSubmitting) return;

    setIsSubmitting(true);
    setErrorInfo(null);
    setLastFailedResponse(null);

    // Optimistically record user response in local turns for snappy feedback
    const activeUnansweredIndex = turns.findIndex((t) => t.user_response === null);
    if (activeUnansweredIndex !== -1) {
      const updatedTurns = [...turns];
      updatedTurns[activeUnansweredIndex] = {
        ...updatedTurns[activeUnansweredIndex],
        user_response: responseText,
        responded_at: new Date().toISOString(),
      };
      setTurns(updatedTurns);
    }

    try {
      const result = await onboardingClient.respond(responseText);

      // Re-fetch complete official state from server
      await loadFullSessionState();

      // If transition to awaiting confirmation, fetch summary
      if (result.session_status === 'awaiting_confirmation' || result.ready_to_summarize) {
        try {
          const summaryData = await onboardingClient.getSummary();
          setSummary(summaryData.summary);
        } catch {
          // Handled in full session state reload
        }
      }
    } catch (err: unknown) {
      setLastFailedResponse(responseText);

      if (err instanceof ApiClientError) {
        setErrorInfo({ message: err.message, status: err.status });
      } else {
        setErrorInfo({ message: 'Failed to process your response with the AI service.' });
      }
      // Reload official history to correct any optimistic divergence
      await loadFullSessionState();
    } finally {
      setIsSubmitting(false);
    }
  };

  // Skip Current Question Handler
  const handleSkipQuestion = async () => {
    await handleSubmitResponse("I would like to skip this question for now.");
  };

  // Retry Last Failed Submission
  const handleRetryLastSubmission = async () => {
    if (lastFailedResponse) {
      const retryText = lastFailedResponse;
      setLastFailedResponse(null);
      setErrorInfo(null);
      await handleSubmitResponse(retryText);
    } else {
      await loadFullSessionState();
    }
  };

  // Summary Confirmation Handler
  const handleConfirmSummary = async (edits?: OnboardingSummary | null) => {
    setIsConfirming(true);
    setErrorInfo(null);

    try {
      const result = await onboardingClient.confirmSummary({
        confirmed: true,
        edits: edits || null,
      });

      setSession(result);

      // Reload history to ensure everything is synced
      await loadFullSessionState();
    } catch (err: unknown) {
      if (err instanceof ApiClientError) {
        setErrorInfo({ message: err.message, status: err.status });
      } else {
        setErrorInfo({ message: 'Failed to confirm and apply career summary.' });
      }
    } finally {
      setIsConfirming(false);
    }
  };

  // Initial Loading Screen
  if (isLoadingSession) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] space-y-4">
        <div className="h-12 w-12 rounded-2xl bg-gradient-to-tr from-brand-600 to-purple-600 flex items-center justify-center text-white shadow-lg shadow-purple-500/20 animate-pulse">
          <Sparkles className="h-6 w-6" />
        </div>
        <div className="text-center space-y-1">
          <h3 className="text-base font-bold text-slate-900 dark:text-white">
            Connecting to AI Career Advisor
          </h3>
          <p className="text-xs text-slate-500 dark:text-slate-400">
            Restoring your personalized onboarding session...
          </p>
        </div>
      </div>
    );
  }

  // 1. COMPLETED STATE VIEW
  if (session?.status === 'completed') {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <Link
            href="/dashboard"
            className="inline-flex items-center text-xs font-semibold text-slate-500 hover:text-slate-900 dark:hover:text-slate-200 transition-colors"
          >
            <ArrowLeft className="w-3.5 h-3.5 mr-1" />
            Back to Dashboard
          </Link>
        </div>

        <OnboardingCompletion
          turns={turns}
          targetRole={summary?.target_role}
          careerStage={summary?.career_stage}
          completedAt={session.completed_at}
        />
      </div>
    );
  }

  // 2. AWAITING CONFIRMATION STATE VIEW
  if (session?.status === 'awaiting_confirmation') {
    return (
      <div className="space-y-6 max-w-4xl mx-auto">
        <div className="flex items-center justify-between">
          <Link
            href="/dashboard"
            className="inline-flex items-center text-xs font-semibold text-slate-500 hover:text-slate-900 dark:hover:text-slate-200 transition-colors"
          >
            <ArrowLeft className="w-3.5 h-3.5 mr-1" />
            Save & Exit to Dashboard
          </Link>

          <Button
            type="button"
            variant="ghost"
            size="sm"
            onClick={loadFullSessionState}
            className="text-xs text-slate-500"
          >
            <RefreshCw className="w-3 h-3 mr-1" /> Refresh
          </Button>
        </div>

        {errorInfo && (
          <OnboardingErrorBanner
            error={errorInfo.message}
            status={errorInfo.status}
            onRetry={handleRetryLastSubmission}
            onDismiss={() => setErrorInfo(null)}
          />
        )}

        {summary ? (
          <CareerSummaryReview
            summary={summary}
            onConfirm={handleConfirmSummary}
            isConfirming={isConfirming}
          />
        ) : (
          <div className="p-8 text-center bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 space-y-3">
            <Loader2 className="w-6 h-6 animate-spin text-purple-600 mx-auto" />
            <p className="text-sm font-semibold text-slate-700 dark:text-slate-300">
              Generating your structured career summary...
            </p>
            <Button size="sm" variant="outline" onClick={loadFullSessionState}>
              Reload Summary
            </Button>
          </div>
        )}
      </div>
    );
  }

  // 3. IN_PROGRESS CONVERSATIONAL DISCOVERY VIEW
  const currentUnansweredTurn = turns.find((t) => t.user_response === null);
  const activeQuestionCategory =
    currentUnansweredTurn?.question_category || session?.current_question_category || 'target_role';

  return (
    <div className="space-y-4 max-w-4xl mx-auto">
      {/* Top Header & Navigation */}
      <div className="flex items-center justify-between">
        <Link
          href="/dashboard"
          className="inline-flex items-center text-xs font-semibold text-slate-500 hover:text-slate-900 dark:hover:text-slate-200 transition-colors"
        >
          <ArrowLeft className="w-3.5 h-3.5 mr-1" />
          Exit & Resume Later
        </Link>

        <div className="flex items-center gap-2">
          <Button
            type="button"
            variant="ghost"
            size="sm"
            onClick={loadFullSessionState}
            className="text-xs text-slate-500 hover:text-slate-800"
            title="Refresh session from server"
          >
            <RefreshCw className="w-3 h-3 mr-1" />
            Sync
          </Button>
        </div>
      </div>

      {/* Progress Card */}
      {progress && (
        <OnboardingProgress
          areasCovered={progress.areas_covered}
          areasRemaining={progress.areas_remaining}
          turnCount={progress.turn_count}
          currentCategory={activeQuestionCategory}
          readyToSummarize={progress.ready_to_summarize}
        />
      )}

      {/* Error Banner */}
      {errorInfo && (
        <OnboardingErrorBanner
          error={errorInfo.message}
          status={errorInfo.status}
          onRetry={handleRetryLastSubmission}
          onDismiss={() => setErrorInfo(null)}
        />
      )}

      {/* Conversation Stream Container */}
      <div className="rounded-2xl border border-slate-200/90 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-950/40 p-4 sm:p-6 min-h-[380px] max-h-[620px] overflow-y-auto space-y-5 shadow-inner">
        {turns.length === 0 ? (
          <div className="flex items-center justify-center h-48 text-xs text-slate-400">
            Initiating career discovery interview...
          </div>
        ) : (
          turns.map((turn) => (
            <div key={turn.turn_id} className="space-y-4">
              {/* AI Question */}
              <ConversationMessage
                type="ai"
                content={turn.question}
                category={turn.question_category}
                timestamp={turn.created_at}
                turnNumber={turn.turn_number}
              />

              {/* User Response if answered */}
              {turn.user_response && (
                <ConversationMessage
                  type="user"
                  content={turn.user_response}
                  timestamp={turn.responded_at}
                />
              )}
            </div>
          ))
        )}

        {/* AI Thinking Animation */}
        {isSubmitting && <AIMessageThinking category={activeQuestionCategory} />}

        {/* Scroll anchor */}
        <div ref={chatBottomRef} />
      </div>

      {/* Question Input Controls */}
      <QuestionInput
        onSubmit={handleSubmitResponse}
        onSkip={handleSkipQuestion}
        isSubmitting={isSubmitting}
        category={activeQuestionCategory}
      />
    </div>
  );
}
