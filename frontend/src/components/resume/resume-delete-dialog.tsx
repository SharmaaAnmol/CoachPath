'use client';

import * as React from 'react';
import { Modal } from '@/components/ui/modal';
import { Button } from '@/components/ui/button';
import { Alert } from '@/components/ui/alert';
import { AlertTriangle, Trash2 } from 'lucide-react';
import { ResumeListItem } from '@/types';

interface ResumeDeleteDialogProps {
  isOpen: boolean;
  resume: ResumeListItem | null;
  onClose: () => void;
  onConfirmDelete: () => Promise<void>;
  isDeleting: boolean;
  error?: string | null;
}

export function ResumeDeleteDialog({
  isOpen,
  resume,
  onClose,
  onConfirmDelete,
  isDeleting,
  error,
}: ResumeDeleteDialogProps) {
  if (!resume) return null;

  return (
    <Modal
      isOpen={isOpen}
      onClose={() => {
        if (!isDeleting) onClose();
      }}
      title="Delete Resume Document"
      description="Permanent removal from storage and database."
      maxWidth="md"
      footer={
        <div className="flex justify-end gap-3 w-full">
          <Button
            variant="outline"
            size="sm"
            onClick={onClose}
            disabled={isDeleting}
          >
            Cancel
          </Button>
          <Button
            variant="destructive"
            size="sm"
            onClick={onConfirmDelete}
            isLoading={isDeleting}
            disabled={isDeleting}
          >
            <Trash2 className="w-3.5 h-3.5 mr-1.5" />
            Delete Document
          </Button>
        </div>
      }
    >
      <div className="space-y-4">
        <div className="flex items-start gap-3 p-3 bg-rose-50/50 dark:bg-rose-950/20 border border-rose-200 dark:border-rose-900 rounded-lg text-rose-900 dark:text-rose-200 text-xs">
          <AlertTriangle className="w-5 h-5 text-rose-600 dark:text-rose-400 shrink-0 mt-0.5" />
          <div className="space-y-1">
            <p className="font-semibold text-sm">Are you sure you want to delete this resume?</p>
            <p>
              This action will permanently delete <strong className="font-semibold text-slate-900 dark:text-white">{resume.file_name}</strong>, its stored file on disk, and any associated parsed draft records.
            </p>
            <p className="text-[11px] opacity-90">
              Note: Any details already merged into your Career Profile in previous sessions will remain untouched.
            </p>
          </div>
        </div>

        {error && (
          <Alert variant="destructive" title="Deletion Error">
            {error}
          </Alert>
        )}
      </div>
    </Modal>
  );
}
