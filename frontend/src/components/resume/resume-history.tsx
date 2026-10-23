'use client';

import * as React from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { EmptyState } from '@/components/ui/empty-state';
import { Skeleton } from '@/components/ui/skeleton';
import { FileText, Upload } from 'lucide-react';
import { ResumeListItem } from '@/types';
import { ResumeCard } from './resume-card';

interface ResumeHistoryProps {
  resumes: ResumeListItem[];
  isLoading: boolean;
  onReviewDraft: (resumeId: string) => void;
  onRetry: (resumeId: string) => void;
  onDownload: (resumeId: string, filename: string) => void;
  onDelete: (resume: ResumeListItem) => void;
  onUploadClick: () => void;
  retryingId?: string | null;
  downloadingId?: string | null;
}

export function ResumeHistory({
  resumes,
  isLoading,
  onReviewDraft,
  onRetry,
  onDownload,
  onDelete,
  onUploadClick,
  retryingId,
  downloadingId,
}: ResumeHistoryProps) {
  if (isLoading) {
    return (
      <div className="space-y-3">
        <h3 className="text-sm font-semibold text-slate-900 dark:text-white">Uploaded Resumes</h3>
        <Card className="p-4 space-y-3">
          <Skeleton className="h-6 w-1/3" />
          <Skeleton className="h-4 w-1/2" />
        </Card>
        <Card className="p-4 space-y-3">
          <Skeleton className="h-6 w-1/4" />
          <Skeleton className="h-4 w-1/3" />
        </Card>
      </div>
    );
  }

  if (resumes.length === 0) {
    return (
      <EmptyState
        icon={<FileText className="w-6 h-6" />}
        title="No resumes uploaded yet"
        description="Upload your PDF or Word resume to extract your education, work history, projects, and skills into your career profile."
        actionLabel="Upload Master Resume"
        onAction={onUploadClick}
      />
    );
  }

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold text-slate-900 dark:text-white">
          Resume Documents ({resumes.length})
        </h3>
        <p className="text-xs text-slate-500 dark:text-slate-400">
          Click &ldquo;Review Draft&rdquo; on any parsed resume to inspect and merge credentials
        </p>
      </div>

      <div className="space-y-3">
        {resumes.map((resume) => (
          <ResumeCard
            key={resume.id}
            resume={resume}
            onReviewDraft={onReviewDraft}
            onRetry={onRetry}
            onDownload={onDownload}
            onDelete={onDelete}
            isRetrying={retryingId === resume.id}
            isDownloading={downloadingId === resume.id}
          />
        ))}
      </div>
    </div>
  );
}
