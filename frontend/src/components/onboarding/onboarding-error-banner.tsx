'use client';

import * as React from 'react';
import { AlertCircle, RotateCcw, X, KeyRound, WifiOff } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

export interface OnboardingErrorBannerProps {
  error: Error | string | null;
  status?: number;
  onRetry?: () => void;
  onDismiss?: () => void;
  className?: string;
}

export function OnboardingErrorBanner({
  error,
  status,
  onRetry,
  onDismiss,
  className,
}: OnboardingErrorBannerProps) {
  if (!error) return null;

  const rawMessage = typeof error === 'string' ? error : error.message;

  // Determine error classification
  const is503 = status === 503 || rawMessage.toLowerCase().includes('not configured') || rawMessage.toLowerCase().includes('unavailable');
  const isNetwork = rawMessage.toLowerCase().includes('network') || rawMessage.toLowerCase().includes('failed to fetch');

  let title = 'Something went wrong';
  let description = rawMessage;
  let Icon = AlertCircle;

  if (is503) {
    title = 'AI Provider Key Required';
    description =
      'The AI service is currently not configured on the backend server. To enable real-time personalized career discovery, set your OPENAI_API_KEY (or ANTHROPIC_API_KEY) in backend/.env.';
    Icon = KeyRound;
  } else if (isNetwork) {
    title = 'Connection Interrupted';
    description = 'Unable to reach the CoachPath backend server. Please check your network connection and retry.';
    Icon = WifiOff;
  }

  return (
    <div
      role="alert"
      className={cn(
        'rounded-xl p-4 border transition-all animate-shake-subtle',
        is503
          ? 'bg-amber-50 dark:bg-amber-950/40 border-amber-200 dark:border-amber-800 text-amber-900 dark:text-amber-200'
          : 'bg-rose-50 dark:bg-rose-950/40 border-rose-200 dark:border-rose-800 text-rose-900 dark:text-rose-200',
        className
      )}
    >
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-start gap-3">
          <Icon
            className={cn(
              'w-5 h-5 shrink-0 mt-0.5',
              is503 ? 'text-amber-600 dark:text-amber-400' : 'text-rose-600 dark:text-rose-400'
            )}
          />
          <div className="space-y-1">
            <h4 className="text-sm font-semibold leading-tight">{title}</h4>
            <p className="text-xs opacity-90 leading-relaxed">{description}</p>
          </div>
        </div>

        <div className="flex items-center gap-2 shrink-0">
          {onRetry && (
            <Button
              type="button"
              variant="outline"
              size="sm"
              onClick={onRetry}
              className={cn(
                'h-7 px-2.5 text-xs',
                is503
                  ? 'border-amber-300 dark:border-amber-700 hover:bg-amber-100 dark:hover:bg-amber-900/40'
                  : 'border-rose-300 dark:border-rose-700 hover:bg-rose-100 dark:hover:bg-rose-900/40'
              )}
            >
              <RotateCcw className="w-3 h-3 mr-1" />
              Retry
            </Button>
          )}

          {onDismiss && (
            <button
              type="button"
              onClick={onDismiss}
              className="p-1 rounded-md text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 transition-colors"
              aria-label="Dismiss error"
            >
              <X className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
