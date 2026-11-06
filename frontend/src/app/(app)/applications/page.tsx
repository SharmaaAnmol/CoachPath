'use client';

import * as React from 'react';
import Link from 'next/link';
import { mockApplications } from '@/lib/mock/data';
import { ApplicationItem, ApplicationStage } from '@/types';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { DemoPreviewBanner } from '@/components/ui/demo-preview-banner';
import {
  Kanban,
  Building2,
  Calendar,
  Sparkles,
  Plus,
  ArrowRight,
  MoreVertical,
  CheckCircle2,
  Clock,
} from 'lucide-react';

export default function ApplicationsPage() {
  const [applications, setApplications] = React.useState<ApplicationItem[]>(mockApplications);

  const columns: { stage: ApplicationStage; title: string; color: string }[] = [
    { stage: 'saved', title: 'Saved Opportunities', color: 'border-slate-300 bg-slate-50/50 dark:bg-white/[0.04]' },
    { stage: 'applied', title: 'Submitted Applications', color: 'border-blue-300 bg-blue-50/20 dark:bg-lav/10 dark:border-lav/50' },
    { stage: 'interviewing', title: 'Active Interviewing', color: 'border-purple-300 bg-purple-50/20 dark:bg-lav/10 dark:border-lav/50' },
    { stage: 'offered', title: 'Offers Extended', color: 'border-emerald-300 bg-emerald-50/20 dark:bg-lime/10 dark:border-lime/50' },
  ];

  const moveStage = (appId: string, direction: 'next' | 'prev') => {
    const stageOrder: ApplicationStage[] = ['saved', 'applied', 'interviewing', 'offered'];
    setApplications((prev) =>
      prev.map((app) => {
        if (app.id !== appId) return app;
        const currentIndex = stageOrder.indexOf(app.stage);
        const nextIndex = direction === 'next' ? Math.min(currentIndex + 1, stageOrder.length - 1) : Math.max(currentIndex - 1, 0);
        return { ...app, stage: stageOrder[nextIndex] };
      })
    );
  };

  return (
    <div className="space-y-6">
      {/* Demo Preview Banner */}
      <DemoPreviewBanner
        plannedPhase="Phase 12"
        featureName="Live application tracking"
      />

      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="font-display text-3xl font-semibold tracking-[-0.035em] text-slate-900 dark:text-ink-fg [text-wrap:balance] md:text-4xl">
            Application Pipeline & Status Tracker
          </h1>
          <p className="text-xs text-slate-500 dark:text-ink-muted mt-1">
            Track active opportunities, interview scheduling, and next-action deadlines across target companies.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Button
            size="sm"
            variant="primary"
            disabled
            aria-disabled="true"
            title="Application creation is scheduled for Phase 12"
          >
            <Plus className="w-3.5 h-3.5 mr-1" /> Add Application (Phase 12)
          </Button>
        </div>
      </div>

      {/* Kanban Board Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 items-start">
        {columns.map((col) => {
          const items = applications.filter((a) => a.stage === col.stage);
          return (
            <div key={col.stage} className="space-y-3">
              {/* Column Header */}
              <div className="flex items-center justify-between px-2 py-1">
                <div className="flex items-center gap-2">
                  <h3 className="text-xs font-bold uppercase tracking-wider text-slate-700 dark:text-ink-fg/80">
                    {col.title}
                  </h3>
                  <span className="rounded-full px-2 py-0.5 text-[10px] font-bold bg-slate-200 dark:bg-white/[0.07] text-slate-700 dark:text-ink-fg/80">
                    {items.length}
                  </span>
                </div>
              </div>

              {/* Column Body Cards */}
              <div className={`p-3 rounded-2xl border min-h-[450px] space-y-3 ${col.color}`}>
                {items.map((app) => (
                  <Card key={app.id} className="p-4 space-y-3 bg-white dark:bg-white/[0.04] shadow-subtle hover:shadow-card transition-all">
                    <div className="space-y-1">
                      <div className="flex items-start justify-between gap-2">
                        <span className="text-xs font-bold text-slate-900 dark:text-white leading-tight">
                          {app.roleTitle}
                        </span>
                        <Badge variant="verified" size="sm">
                          {app.matchScore}%
                        </Badge>
                      </div>

                      <div className="flex items-center gap-2 text-xs font-semibold text-purple-700 dark:text-lav-light">
                        <Building2 className="w-3.5 h-3.5" />
                        <span>{app.company}</span>
                        <span className="text-slate-400 font-normal">&bull; {app.salary}</span>
                      </div>
                    </div>

                    {app.nextStep && (
                      <div className="p-2.5 rounded-lg bg-purple-50 dark:bg-lav/10 border border-purple-200 dark:border-lav/30 text-[11px] text-purple-900 dark:text-lav-light flex items-start gap-1.5">
                        <Clock className="w-3.5 h-3.5 shrink-0 mt-0.5 text-purple-600 dark:text-lav" />
                        <span className="leading-snug">{app.nextStep}</span>
                      </div>
                    )}

                    {app.notes && (
                      <p className="text-[11px] text-slate-500 dark:text-ink-muted line-clamp-2">
                        {app.notes}
                      </p>
                    )}

                    {/* Move controls */}
                    <div className="pt-2 border-t border-slate-100 dark:border-white/10 flex items-center justify-between text-xs">
                      {col.stage !== 'saved' ? (
                        <button
                          onClick={() => moveStage(app.id, 'prev')}
                          className="text-[11px] text-slate-400 hover:text-slate-700 font-medium"
                        >
                          &larr; Back
                        </button>
                      ) : <span />}

                      {col.stage !== 'offered' ? (
                        <button
                          onClick={() => moveStage(app.id, 'next')}
                          className="text-[11px] text-brand-600 font-bold hover:underline dark:text-lav"
                        >
                          Advance &rarr;
                        </button>
                      ) : (
                        <span className="text-[11px] font-bold text-emerald-600 dark:text-lime">Offer Active!</span>
                      )}
                    </div>
                  </Card>
                ))}

                {items.length === 0 && (
                  <div className="h-32 flex items-center justify-center text-xs text-slate-400 border border-dashed border-slate-300 dark:border-white/15 rounded-xl">
                    No active applications
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
