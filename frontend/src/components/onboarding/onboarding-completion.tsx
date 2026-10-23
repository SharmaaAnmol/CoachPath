'use client';

import * as React from 'react';
import Link from 'next/link';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  CheckCircle2,
  Sparkles,
  ArrowRight,
  User,
  LayoutDashboard,
  MessageSquare,
  ChevronDown,
  ChevronUp,
} from 'lucide-react';
import { ConversationTurn } from '@/types';
import { ConversationMessage } from './conversation-message';

export interface OnboardingCompletionProps {
  turns: ConversationTurn[];
  targetRole?: string | null;
  careerStage?: string | null;
  completedAt?: string | null;
}

export function OnboardingCompletion({
  turns,
  targetRole,
  careerStage,
  completedAt,
}: OnboardingCompletionProps) {
  const [showHistory, setShowHistory] = React.useState(false);

  const formattedDate = React.useMemo(() => {
    if (!completedAt) return 'Recently';
    try {
      return new Date(completedAt).toLocaleDateString(undefined, {
        month: 'short',
        day: 'numeric',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      });
    } catch {
      return 'Recently';
    }
  }, [completedAt]);

  const answeredTurns = turns.filter((t) => t.user_response !== null);

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      {/* Celebration Header Card */}
      <Card className="border-emerald-200 dark:border-emerald-900 bg-gradient-to-b from-emerald-50/50 via-white to-white dark:from-emerald-950/20 dark:via-slate-900 dark:to-slate-900 shadow-elevated">
        <CardContent className="p-8 sm:p-10 flex flex-col items-center text-center space-y-5">
          <div className="h-16 w-16 rounded-3xl bg-gradient-to-tr from-emerald-500 to-teal-400 text-white flex items-center justify-center shadow-lg shadow-emerald-500/20 animate-bounce-subtle">
            <CheckCircle2 className="w-9 h-9" />
          </div>

          <div className="space-y-2 max-w-lg">
            <Badge variant="verified" size="md" className="px-3 py-1">
              <Sparkles className="w-3.5 h-3.5 mr-1.5" /> Discovery Completed
            </Badge>
            <h2 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-slate-900 dark:text-white">
              Your Career Blueprint is Established!
            </h2>
            <p className="text-sm text-slate-600 dark:text-slate-300 leading-relaxed">
              Your personalized career profile has been calibrated from your discovery interview.
              CoachPath now has the foundational baseline to power your skill assessment benchmarks, roadmap, and job matching.
            </p>
          </div>

          {/* Quick Metrics */}
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 w-full max-w-lg pt-2">
            <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/80 border border-slate-200/80 dark:border-slate-700/80 text-left">
              <span className="text-[11px] text-slate-500 dark:text-slate-400 block">Target Role</span>
              <span className="text-sm font-bold text-slate-900 dark:text-white truncate block">
                {targetRole || 'Software Engineer'}
              </span>
            </div>

            <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/80 border border-slate-200/80 dark:border-slate-700/80 text-left">
              <span className="text-[11px] text-slate-500 dark:text-slate-400 block">Career Stage</span>
              <span className="text-sm font-bold text-slate-900 dark:text-white capitalize truncate block">
                {careerStage?.replace(/_/g, ' ') || 'Calibrated'}
              </span>
            </div>

            <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/80 border border-slate-200/80 dark:border-slate-700/80 text-left col-span-2 sm:col-span-1">
              <span className="text-[11px] text-slate-500 dark:text-slate-400 block">Completed</span>
              <span className="text-sm font-bold text-slate-900 dark:text-white truncate block">
                {formattedDate}
              </span>
            </div>
          </div>

          {/* Action CTAs */}
          <div className="flex flex-col sm:flex-row items-center gap-3 pt-3 w-full max-w-md">
            <Link href="/career-profile" className="w-full sm:w-1/2">
              <Button variant="primary" size="lg" className="w-full">
                <User className="w-4 h-4 mr-2" />
                Career Profile
              </Button>
            </Link>

            <Link href="/dashboard" className="w-full sm:w-1/2">
              <Button variant="outline" size="lg" className="w-full">
                <LayoutDashboard className="w-4 h-4 mr-2" />
                Workspace Dashboard
              </Button>
            </Link>
          </div>
        </CardContent>
      </Card>

      {/* Expandable Conversation Transcript */}
      <Card className="border-slate-200/80 dark:border-slate-800">
        <CardHeader className="py-4 px-6 flex flex-row items-center justify-between cursor-pointer select-none" onClick={() => setShowHistory(!showHistory)}>
          <div className="flex items-center gap-2">
            <MessageSquare className="w-4 h-4 text-purple-600" />
            <CardTitle className="text-sm font-semibold">
              Interview Transcript ({answeredTurns.length} turns)
            </CardTitle>
          </div>
          <Button type="button" variant="ghost" size="sm" className="h-8 w-8 p-0">
            {showHistory ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
          </Button>
        </CardHeader>

        {showHistory && (
          <CardContent className="p-6 pt-2 space-y-4 border-t border-slate-100 dark:border-slate-800">
            {turns.map((turn) => (
              <div key={turn.turn_id} className="space-y-3 pb-3 border-b border-slate-100 dark:border-slate-800/60 last:border-0 last:pb-0">
                <ConversationMessage
                  type="ai"
                  content={turn.question}
                  category={turn.question_category}
                  timestamp={turn.created_at}
                  turnNumber={turn.turn_number}
                />
                {turn.user_response && (
                  <ConversationMessage
                    type="user"
                    content={turn.user_response}
                    timestamp={turn.responded_at}
                  />
                )}
              </div>
            ))}
          </CardContent>
        )}
      </Card>
    </div>
  );
}
