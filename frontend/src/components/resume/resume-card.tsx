'use client';

import * as React from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  FileText,
  Download,
  Trash2,
  RotateCcw,
  Sparkles,
  CheckCircle2,
  AlertTriangle,
  Clock,
  Loader2,
} from 'lucide-react';
import { ResumeListItem } from '@/types';

interface ResumeCardProps {
  resume: ResumeListItem;
  onReviewDraft?: (resumeId: string) => void;
  onRetry?: (resumeId: string) => void;
  onDownload?: (resumeId: string, filename: string) => void;
  onDelete?: (resume: ResumeListItem) => void;
  isRetrying?: boolean;
  isDownloading?: boolean;
}

export function ResumeCard({
  resume,
  onReviewDraft,
  onRetry,
  onDownload,
  onDelete,
  isRetrying = false,
  isDownloading = false,
}: ResumeCardProps) {
  const isParsed = ['parsed', 'needs_review'].includes(resume.status);
  const isFailed = resume.status === 'failed';
  const isProcessing = ['uploaded', 'processing', 'parsing'].includes(resume.status);

  return (
    <Card className="p-4 border-slate-200 dark:border-slate-800 hover:border-slate-300 dark:hover:border-slate-700 transition-all shadow-sm">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        {/* File Details */}
        <div className="flex items-start gap-3 min-w-0">
          <div className="w-10 h-10 rounded-xl bg-brand-50 dark:bg-brand-950/40 text-brand-600 dark:text-brand-400 flex items-center justify-center shrink-0 mt-0.5">
            <FileText className="w-5 h-5" />
          </div>

          <div className="min-w-0 space-y-1">
            <div className="flex items-center gap-2 flex-wrap">
              <h4 className="text-sm font-semibold text-slate-900 dark:text-white truncate max-w-sm">
                {resume.file_name}
              </h4>
              {resume.is_primary && (
                <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full bg-brand-100 text-brand-800 dark:bg-brand-950/80 dark:text-brand-300 border border-brand-200 dark:border-brand-800">
                  Primary Source
                </span>
              )}
              {resume.status === 'parsed' && (
                <Badge variant="verified" size="sm">
                  <CheckCircle2 className="w-3 h-3 mr-1" /> Parsed
                </Badge>
              )}
              {resume.status === 'needs_review' && (
                <Badge variant="action" size="sm">
                  <Clock className="w-3 h-3 mr-1" /> Needs Review
                </Badge>
              )}
              {isProcessing && (
                <Badge variant="intelligence" size="sm">
                  <Loader2 className="w-3 h-3 mr-1 animate-spin" /> Parsing...
                </Badge>
              )}
              {isFailed && (
                <Badge variant="gap" size="sm">
                  <AlertTriangle className="w-3 h-3 mr-1" /> Failed
                </Badge>
              )}
            </div>

            <div className="flex items-center gap-2 text-xs text-slate-500 dark:text-slate-400">
              <span>{(resume.file_size_bytes / 1024).toFixed(1)} KB</span>
              <span>&bull;</span>
              <span>
                Uploaded{' '}
                {new Date(resume.created_at).toLocaleDateString(undefined, {
                  month: 'short',
                  day: 'numeric',
                  year: 'numeric',
                })}
              </span>
              {resume.parsed_at && (
                <>
                  <span>&bull;</span>
                  <span className="text-emerald-600 dark:text-emerald-400">
                    Parsed{' '}
                    {new Date(resume.parsed_at).toLocaleDateString(undefined, {
                      month: 'short',
                      day: 'numeric',
                    })}
                  </span>
                </>
              )}
            </div>

            {isFailed && resume.parsing_error && (
              <p className="text-xs text-rose-600 dark:text-rose-400 line-clamp-1 pt-0.5">
                Error: {resume.parsing_error}
              </p>
            )}
          </div>
        </div>

        {/* Actions */}
        <div className="flex items-center gap-2 self-end md:self-center shrink-0">
          {isParsed && onReviewDraft && (
            <Button
              variant="primary"
              size="sm"
              onClick={() => onReviewDraft(resume.id)}
            >
              <Sparkles className="w-3.5 h-3.5 mr-1.5" /> Review Draft
            </Button>
          )}

          {isFailed && onRetry && (
            <Button
              variant="outline"
              size="sm"
              onClick={() => onRetry(resume.id)}
              isLoading={isRetrying}
              disabled={isRetrying}
            >
              <RotateCcw className="w-3.5 h-3.5 mr-1.5" /> Retry
            </Button>
          )}

          {onDownload && (
            <Button
              variant="outline"
              size="sm"
              onClick={() => onDownload(resume.id, resume.file_name)}
              isLoading={isDownloading}
              disabled={isDownloading}
              title="Download original file"
            >
              <Download className="w-3.5 h-3.5 mr-1.5" /> Download
            </Button>
          )}

          {onDelete && (
            <Button
              variant="ghost"
              size="sm"
              className="text-slate-400 hover:text-rose-600 dark:hover:text-rose-400"
              onClick={() => onDelete(resume)}
              title="Delete resume"
            >
              <Trash2 className="w-4 h-4" />
            </Button>
          )}
        </div>
      </div>
    </Card>
  );
}
