'use client';

import * as React from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Alert } from '@/components/ui/alert';
import { UploadCloud, FileText, CheckCircle2, AlertCircle, X, Loader2 } from 'lucide-react';
import { cn } from '@/lib/utils';
import { resumeClient } from '@/lib/resume-client';
import { ApiClientError } from '@/lib/api-client';
import { ResumeUploadResponse } from '@/types';

interface ResumeUploadProps {
  onUploadSuccess: (response: ResumeUploadResponse) => void;
  className?: string;
  disabled?: boolean;
}

const MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024; // 10 MB limit from backend settings

export function ResumeUpload({
  onUploadSuccess,
  className,
  disabled = false,
}: ResumeUploadProps) {
  const [isDragging, setIsDragging] = React.useState(false);
  const [selectedFile, setSelectedFile] = React.useState<File | null>(null);
  const [isUploading, setIsUploading] = React.useState(false);
  const [validationError, setValidationError] = React.useState<string | null>(null);
  const [apiError, setApiError] = React.useState<string | null>(null);

  const fileInputRef = React.useRef<HTMLInputElement | null>(null);

  const validateFile = (file: File): boolean => {
    setValidationError(null);
    setApiError(null);

    // 1. Check empty file
    if (file.size === 0) {
      setValidationError('The selected file is empty (0 bytes). Please select a valid resume document.');
      return false;
    }

    // 2. Check size ceiling (10MB)
    if (file.size > MAX_FILE_SIZE_BYTES) {
      const sizeMb = (file.size / (1024 * 1024)).toFixed(1);
      setValidationError(`File size (${sizeMb} MB) exceeds the 10 MB maximum limit.`);
      return false;
    }

    // 3. Check format extension
    const ext = file.name.split('.').pop()?.toLowerCase();
    if (!ext || !['pdf', 'docx'].includes(ext)) {
      setValidationError('Unsupported format. Only PDF (.pdf) and Word (.docx) documents are supported.');
      return false;
    }

    return true;
  };

  const handleFileSelect = (file: File) => {
    if (validateFile(file)) {
      setSelectedFile(file);
    } else {
      setSelectedFile(null);
    }
  };

  const onDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    if (disabled || isUploading) return;
    setIsDragging(true);
  };

  const onDragLeave = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const onDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
    if (disabled || isUploading) return;

    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFileSelect(e.dataTransfer.files[0]);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      handleFileSelect(e.target.files[0]);
    }
  };

  const handleUploadSubmit = async () => {
    if (!selectedFile || isUploading) return;

    setIsUploading(true);
    setApiError(null);
    try {
      const res = await resumeClient.uploadResume(selectedFile);
      setSelectedFile(null);
      if (fileInputRef.current) fileInputRef.current.value = '';
      onUploadSuccess(res);
    } catch (err: unknown) {
      if (err instanceof ApiClientError) {
        setApiError(err.message);
      } else if (err instanceof Error) {
        setApiError(err.message);
      } else {
        setApiError('Upload failed. Please check your network connection and try again.');
      }
    } finally {
      setIsUploading(false);
    }
  };

  const clearSelectedFile = () => {
    setSelectedFile(null);
    setValidationError(null);
    setApiError(null);
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  return (
    <Card className={cn('p-6 space-y-4', className)}>
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-base font-semibold text-slate-900 dark:text-white">
            Upload Master Resume
          </h3>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
            Supported formats: PDF (.pdf) or Word (.docx) &bull; Maximum file size: 10 MB
          </p>
        </div>
      </div>

      {/* Drag & Drop Area */}
      <div
        onDragOver={onDragOver}
        onDragLeave={onDragLeave}
        onDrop={onDrop}
        onClick={() => {
          if (!disabled && !isUploading && !selectedFile) {
            fileInputRef.current?.click();
          }
        }}
        className={cn(
          'relative border-2 border-dashed rounded-xl p-8 text-center transition-all cursor-pointer flex flex-col items-center justify-center gap-3',
          isDragging
            ? 'border-brand-500 bg-brand-50/50 dark:bg-brand-950/20'
            : 'border-slate-200 dark:border-slate-800 hover:border-brand-400 dark:hover:border-brand-600 bg-slate-50/50 dark:bg-slate-900/50',
          disabled && 'opacity-50 cursor-not-allowed pointer-events-none'
        )}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf,.docx,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
          className="hidden"
          onChange={handleInputChange}
          disabled={disabled || isUploading}
        />

        {!selectedFile ? (
          <>
            <div className="w-12 h-12 rounded-full bg-brand-100 dark:bg-brand-950/60 text-brand-600 dark:text-brand-400 flex items-center justify-center">
              <UploadCloud className="w-6 h-6" />
            </div>
            <div>
              <p className="text-sm font-medium text-slate-800 dark:text-slate-200">
                <span className="text-brand-600 dark:text-brand-400 underline underline-offset-2">
                  Click to choose a file
                </span>{' '}
                or drag and drop here
              </p>
              <p className="text-xs text-slate-400 dark:text-slate-500 mt-1">
                Your original document is securely preserved. Extracted draft requires your confirmation.
              </p>
            </div>
          </>
        ) : (
          <div className="w-full max-w-md bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg p-4 flex items-center justify-between gap-3 shadow-sm">
            <div className="flex items-center gap-3 min-w-0">
              <div className="w-10 h-10 rounded-lg bg-brand-50 dark:bg-brand-950/40 text-brand-600 dark:text-brand-400 flex items-center justify-center shrink-0">
                <FileText className="w-5 h-5" />
              </div>
              <div className="min-w-0 text-left">
                <p className="text-sm font-medium text-slate-900 dark:text-white truncate">
                  {selectedFile.name}
                </p>
                <p className="text-xs text-slate-500 dark:text-slate-400">
                  {(selectedFile.size / 1024).toFixed(1)} KB &bull;{' '}
                  {selectedFile.name.endsWith('.pdf') ? 'PDF Document' : 'Word Document'}
                </p>
              </div>
            </div>

            {!isUploading && (
              <Button
                variant="ghost"
                size="sm"
                className="h-8 w-8 p-0 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200"
                onClick={(e) => {
                  e.stopPropagation();
                  clearSelectedFile();
                }}
                aria-label="Remove selected file"
              >
                <X className="w-4 h-4" />
              </Button>
            )}
          </div>
        )}
      </div>

      {/* Validation / API Error Feedback */}
      {validationError && (
        <Alert variant="warning" title="File Validation Error">
          {validationError}
        </Alert>
      )}

      {apiError && (
        <Alert variant="destructive" title="Upload Failed">
          {apiError}
        </Alert>
      )}

      {/* Submit Action */}
      {selectedFile && (
        <div className="flex justify-end gap-3 pt-2">
          <Button
            variant="outline"
            size="sm"
            onClick={clearSelectedFile}
            disabled={isUploading}
          >
            Cancel
          </Button>
          <Button
            variant="primary"
            size="sm"
            onClick={handleUploadSubmit}
            isLoading={isUploading}
            disabled={isUploading}
          >
            {isUploading ? 'Uploading & Parsing...' : 'Upload & Parse Resume'}
          </Button>
        </div>
      )}
    </Card>
  );
}
