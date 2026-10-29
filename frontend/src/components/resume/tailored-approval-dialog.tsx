'use client';

import * as React from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  ShieldCheck,
  CheckCircle2,
  X,
  AlertTriangle,
  Lock,
  Loader2,
} from 'lucide-react';

interface TailoredApprovalDialogProps {
  isOpen: boolean;
  versionNumber: number;
  jobTitle?: string | null;
  companyName?: string | null;
  onClose: () => void;
  onConfirmApprove: (acceptedSections: string[]) => Promise<void>;
  isApproving: boolean;
  error?: string | null;
}

const ALL_SECTIONS = [
  { id: 'executive_summary', label: 'Executive Summary' },
  { id: 'skills', label: 'Technical Skills & Competencies' },
  { id: 'experience', label: 'Work Experience & Impact Bullets' },
  { id: 'projects', label: 'Projects & Demonstrable Deliverables' },
  { id: 'education', label: 'Education & Certifications' },
];

export function TailoredApprovalDialog({
  isOpen,
  versionNumber,
  jobTitle,
  companyName,
  onClose,
  onConfirmApprove,
  isApproving,
  error,
}: TailoredApprovalDialogProps) {
  const [confirmed, setConfirmed] = React.useState(false);
  const [selectedSections, setSelectedSections] = React.useState<string[]>(
    ALL_SECTIONS.map((s) => s.id)
  );

  React.useEffect(() => {
    if (isOpen) {
      setConfirmed(false);
      setSelectedSections(ALL_SECTIONS.map((s) => s.id));
    }
  }, [isOpen]);

  if (!isOpen) return null;

  const toggleSection = (id: string) => {
    setSelectedSections((prev) =>
      prev.includes(id) ? prev.filter((s) => s !== id) : [...prev, id]
    );
  };

  const handleApprove = async () => {
    if (!confirmed || selectedSections.length === 0) return;
    await onConfirmApprove(selectedSections);
  };

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="approval-dialog-title"
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm animate-in fade-in duration-200"
    >
      <Card className="w-full max-w-lg p-6 bg-white dark:bg-slate-900 border-slate-200 dark:border-slate-800 shadow-2xl space-y-6">
        {/* Header */}
        <div className="flex items-start justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-purple-100 dark:bg-purple-950/60 text-purple-700 dark:text-purple-300 flex items-center justify-center shrink-0">
              <ShieldCheck className="w-5 h-5" />
            </div>
            <div>
              <h3 id="approval-dialog-title" className="text-base font-bold text-slate-900 dark:text-white">
                Human Approval Gateway
              </h3>
              <p className="text-xs text-slate-500 dark:text-slate-400">
                Review & Approve Tailored Resume v{versionNumber} for {jobTitle || 'Target Role'}{' '}
                {companyName ? `at ${companyName}` : ''}
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            disabled={isApproving}
            aria-label="Close dialog"
            className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Informative notice */}
        <div className="p-3.5 rounded-xl bg-purple-50/70 dark:bg-purple-950/30 border border-purple-200/80 dark:border-purple-800/60 text-xs text-purple-900 dark:text-purple-200 space-y-1.5 leading-relaxed">
          <div className="flex items-center gap-1.5 font-bold">
            <Lock className="w-3.5 h-3.5 text-purple-600 dark:text-purple-400" />
            <span>Integrity & Approval Notice</span>
          </div>
          <p className="text-[11px] text-purple-800/90 dark:text-purple-300">
            Explicit approval locks this tailored draft from accidental editing. CoachPath records this approved variant for your job applications. This operation will <strong>never auto-submit applications</strong> or send messages to recruiters without your manual action.
          </p>
        </div>

        {/* Accepted sections checklist */}
        <div className="space-y-2">
          <label className="text-xs font-semibold text-slate-800 dark:text-slate-200 block">
            Approved Resume Sections:
          </label>
          <div className="space-y-1.5 max-h-40 overflow-y-auto pr-1">
            {ALL_SECTIONS.map((sec) => (
              <label
                key={sec.id}
                className="flex items-center gap-2.5 p-2 rounded-lg border border-slate-200 dark:border-slate-800 hover:bg-slate-50 dark:hover:bg-slate-800/50 cursor-pointer text-xs"
              >
                <input
                  type="checkbox"
                  checked={selectedSections.includes(sec.id)}
                  onChange={() => toggleSection(sec.id)}
                  disabled={isApproving}
                  className="rounded border-slate-300 text-purple-600 focus:ring-purple-500 h-4 w-4"
                />
                <span className="font-medium text-slate-700 dark:text-slate-300">
                  {sec.label}
                </span>
              </label>
            ))}
          </div>
        </div>

        {/* Explicit confirmation checkbox */}
        <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-800 space-y-2">
          <label className="flex items-start gap-2.5 cursor-pointer text-xs">
            <input
              type="checkbox"
              checked={confirmed}
              onChange={(e) => setConfirmed(e.target.checked)}
              disabled={isApproving}
              className="mt-0.5 rounded border-slate-300 text-purple-600 focus:ring-purple-500 h-4 w-4 shrink-0"
            />
            <span className="text-slate-700 dark:text-slate-300 leading-normal">
              <strong>I verify that I have reviewed the tailored content.</strong> All bullet points, skills, and metrics accurately reflect my authentic experience and contain zero fabricated claims.
            </span>
          </label>
        </div>

        {error && (
          <div className="p-3 rounded-xl bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-800 text-xs text-rose-700 dark:text-rose-300 flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 shrink-0 text-rose-600" />
            <span>{error}</span>
          </div>
        )}

        {/* Footer actions */}
        <div className="flex items-center justify-end gap-3 pt-2 border-t border-slate-100 dark:border-slate-800">
          <Button
            variant="ghost"
            size="sm"
            onClick={onClose}
            disabled={isApproving}
          >
            Cancel
          </Button>
          <Button
            variant="primary"
            size="sm"
            onClick={handleApprove}
            disabled={!confirmed || selectedSections.length === 0 || isApproving}
            className="bg-purple-600 hover:bg-purple-700"
          >
            {isApproving ? (
              <>
                <Loader2 className="w-4 h-4 mr-1.5 animate-spin" /> Approving Draft...
              </>
            ) : (
              <>
                <CheckCircle2 className="w-4 h-4 mr-1.5" /> Approve & Lock Version
              </>
            )}
          </Button>
        </div>
      </Card>
    </div>
  );
}
