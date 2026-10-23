'use client';

import * as React from 'react';
import { Modal } from '@/components/ui/modal';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { RoadmapTaskItem } from '@/types';
import { FileCheck, ExternalLink, Loader2, AlertCircle } from 'lucide-react';

interface DeliverableModalProps {
  isOpen: boolean;
  onClose: () => void;
  task: RoadmapTaskItem | null;
  onSubmit: (taskId: string, submissionUrl: string) => Promise<void>;
}

export function DeliverableModal({
  isOpen,
  onClose,
  task,
  onSubmit,
}: DeliverableModalProps) {
  const [url, setUrl] = React.useState('');
  const [isSubmitting, setIsSubmitting] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);

  React.useEffect(() => {
    if (task) {
      setUrl(task.submission_url || '');
      setError(null);
    }
  }, [task]);

  if (!task) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!url.trim()) {
      setError('Please provide a valid GitHub repository, pull request, or project URL.');
      return;
    }

    try {
      // Basic URL format validation
      new URL(url.trim());
    } catch {
      setError('Please enter a valid URL starting with http:// or https://');
      return;
    }

    try {
      setIsSubmitting(true);
      setError(null);
      await onSubmit(task.id, url.trim());
      onClose();
    } catch (err: any) {
      setError(err?.message || 'Failed to submit deliverable proof. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Submit Milestone Deliverable Proof"
      description={`Task: ${task.title}`}
      footer={
        <div className="flex justify-end gap-2">
          <Button size="sm" variant="outline" onClick={onClose} disabled={isSubmitting}>
            Cancel
          </Button>
          <Button
            size="sm"
            variant="primary"
            onClick={handleSubmit}
            disabled={isSubmitting}
          >
            {isSubmitting ? (
              <>
                <Loader2 className="w-3.5 h-3.5 mr-1.5 animate-spin" /> Submitting...
              </>
            ) : (
              'Save & Complete Task'
            )}
          </Button>
        </div>
      }
    >
      <form onSubmit={handleSubmit} className="space-y-4 text-xs">
        {/* Deliverable Rubric */}
        <div className="p-3.5 rounded-lg bg-purple-50 dark:bg-purple-950/30 border border-purple-200 dark:border-purple-800 text-purple-900 dark:text-purple-300 space-y-1">
          <div className="flex items-center gap-1.5 font-bold">
            <FileCheck className="w-4 h-4 text-purple-600" />
            <span>Verification Rubric & Deliverable Requirement</span>
          </div>
          <p className="text-slate-600 dark:text-slate-300 text-[11px] leading-relaxed">
            {task.deliverable_requirement || 'Provide a public GitHub repository link verifying your implementation.'}
          </p>
        </div>

        {task.completion_criteria && (
          <div className="p-3 rounded-lg bg-slate-50 dark:bg-slate-800/60 border border-slate-200/80 dark:border-slate-700/60 text-slate-700 dark:text-slate-300 text-[11px] space-y-0.5">
            <span className="font-semibold text-slate-900 dark:text-white">Acceptance Criteria:</span>
            <p className="text-slate-500 dark:text-slate-400">{task.completion_criteria}</p>
          </div>
        )}

        {/* Input */}
        <div className="space-y-1.5">
          <label className="font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider text-[10px]">
            Public GitHub Repository or Live Demo URL <span className="text-red-500">*</span>
          </label>
          <Input
            type="url"
            value={url}
            onChange={(e) => {
              setUrl(e.target.value);
              if (error) setError(null);
            }}
            placeholder="https://github.com/your-username/project-repo"
            required
            className="w-full text-xs h-9"
          />
          <p className="text-[11px] text-slate-400">
            Submit a public repository URL containing code commits, documentation, and tests.
          </p>
        </div>

        {error && (
          <div className="p-2.5 rounded bg-red-50 dark:bg-red-950/30 border border-red-200 dark:border-red-800 flex items-center gap-2 text-red-700 dark:text-red-300 text-[11px]">
            <AlertCircle className="w-4 h-4 shrink-0 text-red-500" />
            <span>{error}</span>
          </div>
        )}
      </form>
    </Modal>
  );
}
