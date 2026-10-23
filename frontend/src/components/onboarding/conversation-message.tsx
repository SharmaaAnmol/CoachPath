'use client';

import * as React from 'react';
import { Sparkles, User, Loader2 } from 'lucide-react';
import { cn } from '@/lib/utils';
import { Badge } from '@/components/ui/badge';

export interface ConversationMessageProps {
  type: 'ai' | 'user';
  content: string;
  category?: string | null;
  timestamp?: string | null;
  turnNumber?: number;
}

const CATEGORY_NAMES: Record<string, string> = {
  target_role: 'Target Role',
  career_stage: 'Career Stage',
  education: 'Education',
  skills: 'Skills',
  technologies: 'Technologies',
  projects: 'Projects',
  experience: 'Work Experience',
  learning_time: 'Learning Time',
  learning_resources: 'Learning Resources',
  timeline: 'Timeline',
  industries: 'Industries',
  companies: 'Target Companies',
  salary: 'Salary Range',
  goals: 'Career Goals',
  preferences: 'Work Preferences',
  wrap_up: 'Summary Prep',
};

export function ConversationMessage({
  type,
  content,
  category,
  timestamp,
  turnNumber,
}: ConversationMessageProps) {
  const isAI = type === 'ai';

  const formattedTime = React.useMemo(() => {
    if (!timestamp) return null;
    try {
      const date = new Date(timestamp);
      return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    } catch {
      return null;
    }
  }, [timestamp]);

  const categoryLabel = category ? CATEGORY_NAMES[category] || category : null;

  return (
    <div
      className={cn(
        'flex gap-3 sm:gap-4 w-full transition-opacity duration-300',
        isAI ? 'justify-start' : 'justify-end'
      )}
    >
      {/* AI Avatar */}
      {isAI && (
        <div className="h-8 w-8 sm:h-9 sm:w-9 rounded-xl bg-gradient-to-tr from-purple-600 to-indigo-600 text-white flex items-center justify-center shrink-0 shadow-sm mt-0.5">
          <Sparkles className="w-4 h-4 sm:w-4.5 sm:h-4.5 text-white" />
        </div>
      )}

      {/* Message Bubble Container */}
      <div
        className={cn(
          'flex flex-col max-w-[88%] sm:max-w-[78%] md:max-w-[72%]',
          isAI ? 'items-start' : 'items-end'
        )}
      >
        {/* Metadata Header */}
        <div className="flex items-center gap-2 mb-1 px-1">
          <span className="text-xs font-semibold text-slate-800 dark:text-slate-200">
            {isAI ? 'CoachPath AI' : 'You'}
          </span>

          {isAI && categoryLabel && (
            <Badge variant="intelligence" size="sm" className="text-[10px] py-0 px-1.5 h-4">
              {categoryLabel}
            </Badge>
          )}

          {isAI && turnNumber && (
            <span className="text-[10px] text-slate-400">
              Q#{turnNumber}
            </span>
          )}

          {formattedTime && (
            <span className="text-[10px] text-slate-400 ml-1">
              {formattedTime}
            </span>
          )}
        </div>

        {/* Bubble Body */}
        <div
          className={cn(
            'rounded-2xl px-4 py-3 text-sm leading-relaxed whitespace-pre-wrap transition-all shadow-sm',
            isAI
              ? 'bg-white dark:bg-slate-900 border border-slate-200/90 dark:border-slate-800 text-slate-900 dark:text-slate-100 rounded-tl-sm'
              : 'bg-brand-600 text-white dark:bg-brand-600 rounded-tr-sm'
          )}
        >
          {content}
        </div>
      </div>

      {/* User Avatar */}
      {!isAI && (
        <div className="h-8 w-8 sm:h-9 sm:w-9 rounded-xl bg-slate-800 dark:bg-slate-700 text-slate-200 flex items-center justify-center shrink-0 shadow-sm mt-0.5">
          <User className="w-4 h-4" />
        </div>
      )}
    </div>
  );
}

export function AIMessageThinking({ category }: { category?: string | null }) {
  const categoryLabel = category ? CATEGORY_NAMES[category] || category : null;

  return (
    <div className="flex gap-3 sm:gap-4 w-full justify-start animate-fade-in">
      <div className="h-8 w-8 sm:h-9 sm:w-9 rounded-xl bg-gradient-to-tr from-purple-600 to-indigo-600 text-white flex items-center justify-center shrink-0 shadow-sm animate-pulse">
        <Sparkles className="w-4 h-4 text-white" />
      </div>

      <div className="flex flex-col items-start max-w-[80%]">
        <div className="flex items-center gap-2 mb-1 px-1">
          <span className="text-xs font-semibold text-slate-800 dark:text-slate-200">
            CoachPath AI
          </span>
          {categoryLabel && (
            <Badge variant="intelligence" size="sm" className="text-[10px] py-0 px-1.5 h-4">
              {categoryLabel}
            </Badge>
          )}
        </div>

        <div className="rounded-2xl rounded-tl-sm px-4 py-3 bg-white dark:bg-slate-900 border border-slate-200/90 dark:border-slate-800 shadow-sm flex items-center gap-2 text-xs text-slate-500 dark:text-slate-400">
          <Loader2 className="w-3.5 h-3.5 animate-spin text-purple-600" />
          <span>Analyzing response & determining next question...</span>
        </div>
      </div>
    </div>
  );
}
