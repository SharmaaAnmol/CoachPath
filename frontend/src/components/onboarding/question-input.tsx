'use client';

import * as React from 'react';
import { Button } from '@/components/ui/button';
import { Send, CornerDownLeft, FastForward, Sparkles } from 'lucide-react';
import { cn } from '@/lib/utils';

export interface QuestionInputProps {
  onSubmit: (response: string) => Promise<void>;
  onSkip?: () => Promise<void>;
  isSubmitting: boolean;
  category?: string | null;
  placeholder?: string;
  className?: string;
}

const CATEGORY_SUGGESTIONS: Record<string, string[]> = {
  target_role: [
    'Backend Developer',
    'Full-Stack Engineer',
    'Frontend Developer',
    'Data Engineer',
    'Mobile Engineer',
    'Data Scientist',
    'DevOps / Cloud Engineer',
    'Machine Learning Engineer',
    'AI Engineer',
  ],
  career_stage: [
    'Current Computer Science student',
    'Recent College Graduate',
    'Self-taught developer transitioning careers',
    'Early Career Engineer (1-2 years experience)',
  ],
  education: [
    'B.Tech / B.S. in Computer Science',
    'B.S. in Engineering (Non-CS)',
    'Master of Science (M.S.) in CS',
    'Self-taught / Coding Bootcamp',
  ],
  learning_time: [
    '5 - 10 hours per week',
    '10 - 15 hours per week',
    '15 - 25 hours per week',
    'Full-time immersion (30+ hours/week)',
  ],
  timeline: [
    'Immediate (within 1-3 months)',
    'Targeting 3 to 6 months',
    'Targeting 6 to 12 months',
    'Long term career planning',
  ],
  preferences: [
    'Remote only',
    'Hybrid preferred',
    'Open to relocation / On-site',
    'Flexible with any mode',
  ],
  learning_resources: [
    'Official Documentation & GitHub',
    'Interactive platforms (LeetCode, NeetCode)',
    'Video courses & tutorials',
    'Books & technical whitepapers',
  ],
};

const MAX_CHARS = 2000;

export function QuestionInput({
  onSubmit,
  onSkip,
  isSubmitting,
  category,
  placeholder = 'Type your response here... (Press Cmd+Enter to send)',
  className,
}: QuestionInputProps) {
  const [text, setText] = React.useState('');
  const textareaRef = React.useRef<HTMLTextAreaElement>(null);

  const trimmedText = text.trim();
  const charCount = text.length;
  const isOverLimit = charCount > MAX_CHARS;
  const canSubmit = trimmedText.length > 0 && !isOverLimit && !isSubmitting;

  const suggestions = category ? CATEGORY_SUGGESTIONS[category] : undefined;

  const handleSubmit = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!canSubmit) return;
    const responseToSend = trimmedText;
    setText('');
    await onSubmit(responseToSend);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if ((e.metaKey || e.ctrlKey) && e.key === 'Enter') {
      e.preventDefault();
      if (canSubmit) {
        handleSubmit();
      }
    }
  };

  const handleApplySuggestion = (suggestion: string) => {
    if (isSubmitting) return;
    setText(suggestion);
    if (textareaRef.current) {
      textareaRef.current.focus();
    }
  };

  const handleSkipClick = async () => {
    if (isSubmitting) return;
    if (onSkip) {
      await onSkip();
    } else {
      await onSubmit('I would like to skip this question for now.');
    }
  };

  return (
    <div className={cn('space-y-3', className)}>
      {/* Quick Suggestion Chips */}
      {suggestions && suggestions.length > 0 && (
        <div className="flex flex-wrap items-center gap-1.5 px-1">
          <span className="text-[11px] font-semibold text-slate-500 dark:text-slate-400 flex items-center gap-1 mr-1">
            <Sparkles className="w-3 h-3 text-purple-500" /> Suggestions:
          </span>
          {suggestions.map((suggestion) => (
            <button
              key={suggestion}
              type="button"
              disabled={isSubmitting}
              onClick={() => handleApplySuggestion(suggestion)}
              className="text-xs px-2.5 py-1 rounded-full border border-slate-200 dark:border-slate-800 bg-slate-50/80 dark:bg-slate-800/80 text-slate-700 dark:text-slate-300 hover:bg-purple-50 hover:border-purple-200 dark:hover:bg-purple-950/40 dark:hover:border-purple-800 transition-colors disabled:opacity-50"
            >
              {suggestion}
            </button>
          ))}
        </div>
      )}

      {/* Main Input Box */}
      <div className="relative rounded-2xl border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900 shadow-sm focus-within:border-brand-500 focus-within:ring-2 focus-within:ring-brand-500/20 transition-all p-2.5 sm:p-3">
        <textarea
          ref={textareaRef}
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={isSubmitting}
          rows={3}
          placeholder={placeholder}
          className="w-full resize-none bg-transparent text-sm text-slate-900 dark:text-slate-100 placeholder:text-slate-400 focus:outline-none disabled:opacity-60 leading-relaxed"
          maxLength={MAX_CHARS}
          aria-label="Your response to the AI question"
        />

        {/* Input Footer Controls */}
        <div className="flex items-center justify-between gap-2 pt-2 border-t border-slate-100 dark:border-slate-800">
          <div className="flex items-center gap-2">
            <Button
              type="button"
              variant="ghost"
              size="sm"
              disabled={isSubmitting}
              onClick={handleSkipClick}
              className="text-xs text-slate-500 hover:text-slate-700 dark:hover:text-slate-300 h-8 px-2"
              title="Skip this question and move to next topic"
            >
              <FastForward className="w-3.5 h-3.5 mr-1" />
              Skip question
            </Button>

            <span
              className={cn(
                'text-[11px] font-mono transition-colors hidden sm:inline-block',
                isOverLimit
                  ? 'text-rose-600 font-bold'
                  : charCount > 1800
                  ? 'text-amber-500'
                  : 'text-slate-400'
              )}
            >
              {charCount}/{MAX_CHARS}
            </span>
          </div>

          <div className="flex items-center gap-2">
            <span className="text-[11px] text-slate-400 hidden md:inline-flex items-center gap-0.5">
              <span>Cmd</span>+<CornerDownLeft className="w-3 h-3 inline" />
            </span>

            <Button
              type="button"
              variant="intelligence"
              size="sm"
              disabled={!canSubmit}
              isLoading={isSubmitting}
              onClick={() => handleSubmit()}
              className="h-8 px-4"
            >
              <span>Send</span>
              <Send className="w-3.5 h-3.5 ml-1" />
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
