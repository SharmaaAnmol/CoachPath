'use client';

import * as React from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Alert } from '@/components/ui/alert';
import {
  Loader2,
  CheckCircle2,
  AlertTriangle,
  RotateCcw,
  FileText,
  Sparkles,
  Info,
  Clock,
} from 'lucide-react';
import { ResumeListItem, ResumeProcessingStatus } from '@/types';

interface ResumeProcessingStatusProps {
  resume: ResumeListItem;
  onRetry?: () => void;
  onReviewDraft?: () => void;
  isRetrying?: boolean;
}

export function ResumeProcessingStatusCard({
  resume,
  onRetry,
  onReviewDraft,
  isRetrying = false,
}: ResumeProcessingStatusProps) {
  const isProcessing = ['uploaded', 'processing', 'parsing'].includes(resume.status);
  const isParsed = ['parsed', 'needs_review'].includes(resume.status);
  const isFailed = resume.status === 'failed';

  const getStatusBadge = (status: ResumeProcessingStatus) => {
    switch (status) {
      case 'parsed':
        return (
          <Badge variant="verified" size="sm">
            <CheckCircle2 className="w-3.5 h-3.5 mr-1 text-emerald-600" /> Parsed & Ready for Review
          </Badge>
        );
      case 'needs_review':
        return (
          <Badge variant="action" size="sm">
            <Clock className="w-3.5 h-3.5 mr-1" /> Awaiting Review
          </Badge>
        );
      case 'parsing':
      case 'processing':
        return (
          <Badge variant="intelligence" size="sm">
            <Loader2 className="w-3.5 h-3.5 mr-1 animate-spin" /> AI Parsing Active
          </Badge>
        );
      case 'uploaded':
        return (
          <Badge variant="secondary" size="sm">
            <Clock className="w-3.5 h-3.5 mr-1" /> Queued for Extraction
          </Badge>
        );
      case 'failed':
        return (
          <Badge variant="gap" size="sm">
            <AlertTriangle className="w-3.5 h-3.5 mr-1" /> Parsing Failed
          </Badge>
        );
      default:
        return <Badge variant="secondary" size="sm">{status}</Badge>;
    }
  };

  const getCategorizedErrorMessage = () => {
    if (!resume.parsing_error_category) {
      return resume.parsing_error || 'An unexpected error occurred during resume processing.';
    }

    switch (resume.parsing_error_category) {
      case 'INSUFFICIENT_TEXT_OCR_REQUIRED':
        return 'The uploaded document appears to be an image-only or scanned PDF without selectable text. Text extraction could not retrieve sufficient character data. OCR is not currently configured.';
      case 'CORRUPTED_DOCUMENT':
        return 'The document structure is malformed or corrupted. Please verify the file opens locally and re-upload.';
      case 'DOCUMENT_ENCRYPTED':
        return 'This document is password protected or encrypted. Please remove password encryption before uploading.';
      case 'AI_PROVIDER_UNAVAILABLE':
        return 'The AI parsing provider is temporarily unavailable or unconfigured (OPENAI_API_KEY required). You can retry parsing once the provider is restored.';
      case 'AI_TIMEOUT':
        return 'AI extraction timed out while analyzing credentials. You can click retry to attempt processing again.';
      case 'EMPTY_DOCUMENT':
        return 'The document contains no readable text content.';
      default:
        return resume.parsing_error || 'Processing could not be completed.';
    }
  };

  return (
    <Card className="p-5 border-slate-200 dark:border-slate-800 space-y-4">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 flex items-center justify-center shrink-0">
            <FileText className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h4 className="font-semibold text-sm text-slate-900 dark:text-white truncate max-w-xs sm:max-w-md">
                {resume.file_name}
              </h4>
              {resume.is_primary && (
                <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full bg-brand-50 text-brand-700 dark:bg-brand-950/60 dark:text-brand-300 border border-brand-200 dark:border-brand-800">
                  Primary
                </span>
              )}
            </div>
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
              {(resume.file_size_bytes / 1024).toFixed(1)} KB &bull; Uploaded{' '}
              {new Date(resume.created_at).toLocaleDateString(undefined, {
                month: 'short',
                day: 'numeric',
                year: 'numeric',
                hour: '2-digit',
                minute: '2-digit',
              })}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          {getStatusBadge(resume.status)}
        </div>
      </div>

      {/* Processing State */}
      {isProcessing && (
        <div className="p-4 bg-purple-50/50 dark:bg-purple-950/20 border border-purple-200/80 dark:border-purple-800/60 rounded-xl flex items-center gap-3">
          <Loader2 className="w-5 h-5 text-purple-600 dark:text-purple-400 animate-spin shrink-0" />
          <div className="text-xs text-purple-900 dark:text-purple-200 space-y-0.5">
            <p className="font-medium">Extracting Text & Analyzing Career Credentials...</p>
            <p className="text-purple-700/80 dark:text-purple-300/70">
              Recovering education, work experiences, technical projects, and normalizing skills against CoachPath taxonomy.
            </p>
          </div>
        </div>
      )}

      {/* Failed State */}
      {isFailed && (
        <div className="space-y-3">
          <Alert variant="destructive" title="Extraction Notice">
            {getCategorizedErrorMessage()}
          </Alert>

          {onRetry && (
            <div className="flex justify-end">
              <Button
                variant="outline"
                size="sm"
                onClick={onRetry}
                isLoading={isRetrying}
                disabled={isRetrying}
              >
                <RotateCcw className="w-3.5 h-3.5 mr-1.5" /> Retry Parsing
              </Button>
            </div>
          )}
        </div>
      )}

      {/* Parsed & Ready State */}
      {isParsed && (
        <div className="p-4 bg-emerald-50/50 dark:bg-emerald-950/20 border border-emerald-200/80 dark:border-emerald-800/60 rounded-xl flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div className="flex items-center gap-2 text-xs text-emerald-900 dark:text-emerald-200">
            <Sparkles className="w-4 h-4 text-emerald-600 dark:text-emerald-400 shrink-0" />
            <span>
              Structured extraction complete. Information is preserved as a draft awaiting your review and approval.
            </span>
          </div>

          {onReviewDraft && (
            <Button
              variant="primary"
              size="sm"
              onClick={onReviewDraft}
              className="shrink-0"
            >
              Review Extracted Draft
            </Button>
          )}
        </div>
      )}
    </Card>
  );
}
