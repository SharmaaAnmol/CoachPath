'use client';

import * as React from 'react';
import { Modal } from '@/components/ui/modal';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { RefreshCw, Clock, Calendar, AlertTriangle, Loader2 } from 'lucide-react';

interface RegenerateRoadmapModalProps {
  isOpen: boolean;
  onClose: () => void;
  currentWeeklyHours: number;
  onRegenerate: (payload: { weekly_hours: number; target_timeline_months: number; force_regenerate: boolean }) => Promise<void>;
  targetRoleTitle: string;
}

export function RegenerateRoadmapModal({
  isOpen,
  onClose,
  currentWeeklyHours,
  onRegenerate,
  targetRoleTitle,
}: RegenerateRoadmapModalProps) {
  const [weeklyHours, setWeeklyHours] = React.useState<number>(currentWeeklyHours || 10);
  const [timelineMonths, setTimelineMonths] = React.useState<number>(6);
  const [isSubmitting, setIsSubmitting] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);

  React.useEffect(() => {
    if (currentWeeklyHours) {
      setWeeklyHours(currentWeeklyHours);
    }
  }, [currentWeeklyHours]);

  const handleConfirm = async () => {
    if (weeklyHours < 1 || weeklyHours > 60) {
      setError('Weekly study hours must be between 1 and 60 hours.');
      return;
    }
    if (timelineMonths < 1 || timelineMonths > 36) {
      setError('Target timeline must be between 1 and 36 months.');
      return;
    }

    try {
      setIsSubmitting(true);
      setError(null);
      await onRegenerate({
        weekly_hours: Number(weeklyHours),
        target_timeline_months: Number(timelineMonths),
        force_regenerate: true,
      });
      onClose();
    } catch (err: any) {
      setError(err?.message || 'Failed to regenerate roadmap. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Regenerate Learning Roadmap"
      description={`Recalculate personalized curriculum for ${targetRoleTitle}`}
      footer={
        <div className="flex justify-end gap-2">
          <Button size="sm" variant="outline" onClick={onClose} disabled={isSubmitting}>
            Cancel
          </Button>
          <Button
            size="sm"
            variant="primary"
            onClick={handleConfirm}
            disabled={isSubmitting}
          >
            {isSubmitting ? (
              <>
                <Loader2 className="w-3.5 h-3.5 mr-1.5 animate-spin" /> Generating v2...
              </>
            ) : (
              'Confirm & Regenerate'
            )}
          </Button>
        </div>
      }
    >
      <div className="space-y-4 text-xs">
        {/* Warning callout */}
        <div className="p-3.5 rounded-lg bg-amber-50 dark:bg-amber-950/30 border border-amber-200 dark:border-amber-800 flex items-start gap-2.5 text-amber-900 dark:text-amber-300">
          <AlertTriangle className="w-4 h-4 shrink-0 text-amber-600 mt-0.5" />
          <div className="space-y-1">
            <p className="font-bold">Roadmap Versioning & Progress Retention</p>
            <p className="text-[11px] text-amber-800 dark:text-amber-400 leading-relaxed">
              Generating a fresh roadmap will archive your current version and create a new version calibrated to your latest diagnostic test results and skill gaps. Completed milestones will remain archived in your historical audit logs.
            </p>
          </div>
        </div>

        {/* Weekly Hours Input */}
        <div className="space-y-1.5">
          <label className="font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider text-[10px] flex items-center gap-1.5">
            <Clock className="w-3.5 h-3.5 text-brand-600" />
            Available Study Hours Per Week (1 – 60 hrs)
          </label>
          <Input
            type="number"
            min={1}
            max={60}
            value={weeklyHours}
            onChange={(e) => setWeeklyHours(Math.max(1, Number(e.target.value)))}
            className="w-full text-xs h-9"
          />
          <p className="text-[11px] text-slate-400">
            Recommended: 10–15 hours/week for steady progression alongside full-time work or study.
          </p>
        </div>

        {/* Timeline Months Input */}
        <div className="space-y-1.5">
          <label className="font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider text-[10px] flex items-center gap-1.5">
            <Calendar className="w-3.5 h-3.5 text-brand-600" />
            Target Completion Deadline (Months)
          </label>
          <Input
            type="number"
            min={1}
            max={36}
            value={timelineMonths}
            onChange={(e) => setTimelineMonths(Math.max(1, Number(e.target.value)))}
            className="w-full text-xs h-9"
          />
          <p className="text-[11px] text-slate-400">
            CoachPath will mathematically validate whether the curriculum can be completed within this timeframe.
          </p>
        </div>

        {error && (
          <div className="p-2.5 rounded bg-red-50 dark:bg-red-950/30 border border-red-200 dark:border-red-800 text-red-700 dark:text-red-300 text-[11px]">
            {error}
          </div>
        )}
      </div>
    </Modal>
  );
}
