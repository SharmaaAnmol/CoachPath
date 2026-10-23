'use client';

import * as React from 'react';
import { Modal } from '@/components/ui/modal';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { skillGapClient } from '@/lib/skill-gap-client';
import { SkillGapAnalysisSummaryItem } from '@/types';
import {
  History,
  Calendar,
  CheckCircle2,
  TrendingUp,
  ShieldCheck,
  AlertCircle,
  FileQuestion,
  RotateCcw,
} from 'lucide-react';

interface AnalysisHistoryModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export function AnalysisHistoryModal({
  isOpen,
  onClose,
}: AnalysisHistoryModalProps) {
  const [historyItems, setHistoryItems] = React.useState<SkillGapAnalysisSummaryItem[]>([]);
  const [isLoading, setIsLoading] = React.useState(false);
  const [errorMessage, setErrorMessage] = React.useState<string | null>(null);

  React.useEffect(() => {
    if (!isOpen) return;

    let isMounted = true;
    const fetchHistory = async () => {
      try {
        setIsLoading(true);
        setErrorMessage(null);
        const data = await skillGapClient.getAnalysisHistory();
        if (isMounted) {
          setHistoryItems(data.items);
        }
      } catch (err: any) {
        if (isMounted) {
          setErrorMessage(err?.message || 'Failed to load analysis history.');
        }
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    };

    fetchHistory();
    return () => {
      isMounted = false;
    };
  }, [isOpen]);

  const formatDate = (isoString: string) => {
    try {
      const d = new Date(isoString);
      return d.toLocaleDateString(undefined, {
        month: 'short',
        day: 'numeric',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      });
    } catch {
      return isoString;
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Skill Gap Snapshot History"
      description="Timeline of immutable point-in-time gap analysis evaluations."
      maxWidth="xl"
    >
      <div className="space-y-4 py-2">
        {isLoading && (
          <div className="py-8 flex flex-col items-center justify-center space-y-3">
            <div className="w-8 h-8 rounded-full border-2 border-indigo-600 border-t-transparent animate-spin" />
            <p className="text-xs text-slate-500">Retrieving evaluation snapshot timeline...</p>
          </div>
        )}

        {errorMessage && (
          <div className="p-3.5 rounded-xl bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-800 text-xs text-rose-700 dark:text-rose-300 flex items-start gap-2">
            <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
            <p>{errorMessage}</p>
          </div>
        )}

        {!isLoading && !errorMessage && historyItems.length === 0 && (
          <div className="p-6 text-center text-xs text-slate-500 border border-dashed rounded-xl border-slate-200 dark:border-slate-800">
            No previous evaluation snapshots found.
          </div>
        )}

        {!isLoading && !errorMessage && historyItems.length > 0 && (
          <div className="space-y-2.5 max-h-80 overflow-y-auto pr-1">
            {historyItems.map((snap) => (
              <div
                key={snap.id}
                className={`p-3.5 rounded-xl border transition-all ${
                  snap.is_current
                    ? 'border-indigo-300 bg-indigo-50/20 dark:border-indigo-800 dark:bg-indigo-950/20'
                    : 'border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900'
                } space-y-2 shadow-sm`}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-xs text-slate-900 dark:text-white">
                      {snap.role_title}
                    </span>
                    {snap.is_current ? (
                      <Badge className="bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300 border-emerald-300 text-[10px] font-bold">
                        ACTIVE CURRENT
                      </Badge>
                    ) : (
                      <Badge variant="outline" className="text-[10px] text-slate-500">
                        ARCHIVED
                      </Badge>
                    )}
                  </div>
                  <div className="flex items-center gap-1 text-[11px] text-slate-400">
                    <Calendar className="w-3 h-3" />
                    <span>{formatDate(snap.calculated_at)}</span>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-3 pt-1 border-t border-slate-100 dark:border-slate-800/80 text-xs">
                  <div>
                    <span className="text-[11px] text-slate-400 block">Role Alignment</span>
                    <span className="font-black text-indigo-600 dark:text-indigo-400 text-sm">
                      {snap.role_alignment_score.toFixed(1)}%
                    </span>
                  </div>
                  <div>
                    <span className="text-[11px] text-slate-400 block">Evidence Coverage</span>
                    <span className="font-black text-emerald-600 dark:text-emerald-400 text-sm">
                      {snap.evidence_coverage_score.toFixed(1)}%
                    </span>
                  </div>
                </div>

                <div className="flex items-center gap-3 text-[11px] text-slate-500 pt-1 border-t border-slate-100 dark:border-slate-800/80">
                  <span>{snap.strongest_skills_count} Strengths</span>
                  <span>•</span>
                  <span>{snap.developing_skills_count} Developing</span>
                  <span>•</span>
                  <span>{snap.skill_gaps_count} Gaps</span>
                  <span>•</span>
                  <span>{snap.unassessed_skills_count} Unassessed</span>
                </div>
              </div>
            ))}
          </div>
        )}

        <div className="pt-2 flex justify-end">
          <Button size="sm" variant="outline" onClick={onClose}>
            Close
          </Button>
        </div>
      </div>
    </Modal>
  );
}
