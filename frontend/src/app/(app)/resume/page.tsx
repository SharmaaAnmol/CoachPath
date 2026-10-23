'use client';

import * as React from 'react';
import Link from 'next/link';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Alert } from '@/components/ui/alert';
import { Skeleton } from '@/components/ui/skeleton';
import {
  FileText,
  Upload,
  CheckCircle2,
  AlertTriangle,
  RotateCcw,
  Sparkles,
  ArrowRight,
  ShieldCheck,
  Download,
  Trash2,
  Clock,
  Briefcase,
  GraduationCap,
  Award,
  ExternalLink,
} from 'lucide-react';
import { resumeClient } from '@/lib/resume-client';
import { profileClient } from '@/lib/profile-client';
import { ApiClientError } from '@/lib/api-client';
import {
  MasterCareerProfile,
  ParsedResumeResponse,
  ResumeConfirmationPayload,
  ResumeConfirmationResponse,
  ResumeListItem,
  ResumeUploadResponse,
} from '@/types';
import { ResumeUpload } from '@/components/resume/resume-upload';
import { ResumeHistory } from '@/components/resume/resume-history';
import { ResumeProcessingStatusCard } from '@/components/resume/resume-processing-status';
import { ResumeDeleteDialog } from '@/components/resume/resume-delete-dialog';
import { ParsedResumeReview } from '@/components/resume/parsed-resume-review';

export default function ResumePage() {
  const [resumes, setResumes] = React.useState<ResumeListItem[]>([]);
  const [isLoading, setIsLoading] = React.useState(true);
  const [existingProfile, setExistingProfile] = React.useState<MasterCareerProfile | null>(null);

  // Review state
  const [activeReviewResumeId, setActiveReviewResumeId] = React.useState<string | null>(null);
  const [parsedDraft, setParsedDraft] = React.useState<ParsedResumeResponse | null>(null);
  const [isLoadingDraft, setIsLoadingDraft] = React.useState(false);
  const [isConfirming, setIsConfirming] = React.useState(false);

  // Deletion dialog state
  const [deleteCandidate, setDeleteCandidate] = React.useState<ResumeListItem | null>(null);
  const [isDeleting, setIsDeleting] = React.useState(false);
  const [deleteError, setDeleteError] = React.useState<string | null>(null);

  // Retry / download state
  const [retryingId, setRetryingId] = React.useState<string | null>(null);
  const [downloadingId, setDownloadingId] = React.useState<string | null>(null);

  // Notifications
  const [notification, setNotification] = React.useState<{
    type: 'success' | 'destructive' | 'info';
    message: string;
    details?: string;
  } | null>(null);

  // Merge success banner state
  const [mergeResult, setMergeResult] = React.useState<ResumeConfirmationResponse | null>(null);

  // ─── Initial Data Loading ──────────────────────────────────────────

  const loadData = React.useCallback(async () => {
    try {
      const [resumesRes, profileRes] = await Promise.all([
        resumeClient.listResumes(),
        profileClient.getMasterProfile().catch(() => null),
      ]);
      setResumes(resumesRes.resumes);
      if (profileRes) setExistingProfile(profileRes);
    } catch (err: unknown) {
      if (err instanceof ApiClientError) {
        setNotification({
          type: 'destructive',
          message: err.message,
        });
      }
    } finally {
      setIsLoading(false);
    }
  }, []);

  React.useEffect(() => {
    loadData();
  }, [loadData]);

  // ─── Polling for Processing Resumes ─────────────────────────────────

  React.useEffect(() => {
    const processingResumes = resumes.filter((r) =>
      ['uploaded', 'processing', 'parsing'].includes(r.status)
    );
    if (processingResumes.length === 0) return;

    const interval = setInterval(async () => {
      try {
        const updatedList = await resumeClient.listResumes();
        setResumes(updatedList.resumes);

        // If the one being reviewed or uploaded just finished, refresh draft if active
        if (activeReviewResumeId) {
          const matching = updatedList.resumes.find((r) => r.id === activeReviewResumeId);
          if (matching && matching.status === 'parsed' && !parsedDraft) {
            const draft = await resumeClient.getParsedResume(activeReviewResumeId);
            setParsedDraft(draft);
          }
        }
      } catch (err) {
        // Silently tolerate temporary polling errors
      }
    }, 3000);

    return () => clearInterval(interval);
  }, [resumes, activeReviewResumeId, parsedDraft]);

  // ─── Handlers ──────────────────────────────────────────────────────

  const handleUploadSuccess = async (uploadRes: ResumeUploadResponse) => {
    setNotification({
      type: 'success',
      message: `Resume "${uploadRes.file_name}" uploaded successfully.`,
      details: uploadRes.message,
    });
    setMergeResult(null);

    // Refresh list
    const res = await resumeClient.listResumes();
    setResumes(res.resumes);

    // If already parsed (synchronous parse in backend), open review immediately
    if (uploadRes.status === 'parsed') {
      handleReviewDraft(uploadRes.resume_id);
    }
  };

  const handleReviewDraft = async (resumeId: string) => {
    setActiveReviewResumeId(resumeId);
    setIsLoadingDraft(true);
    setNotification(null);
    setMergeResult(null);

    try {
      const draft = await resumeClient.getParsedResume(resumeId);
      setParsedDraft(draft);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Could not load parsed draft.';
      setNotification({
        type: 'destructive',
        message: 'Draft Loading Error',
        details: msg,
      });
      setActiveReviewResumeId(null);
    } finally {
      setIsLoadingDraft(false);
    }
  };

  const handleRetry = async (resumeId: string) => {
    setRetryingId(resumeId);
    setNotification(null);
    try {
      const res = await resumeClient.retryParsing(resumeId);
      setNotification({
        type: res.status === 'parsed' ? 'success' : 'info',
        message: res.message,
      });
      const list = await resumeClient.listResumes();
      setResumes(list.resumes);

      if (res.status === 'parsed') {
        handleReviewDraft(resumeId);
      }
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to retry parsing.';
      setNotification({
        type: 'destructive',
        message: 'Retry Failed',
        details: msg,
      });
    } finally {
      setRetryingId(null);
    }
  };

  const handleDownload = async (resumeId: string, filename: string) => {
    setDownloadingId(resumeId);
    try {
      await resumeClient.downloadResume(resumeId, filename);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Download failed.';
      setNotification({
        type: 'destructive',
        message: 'Download Error',
        details: msg,
      });
    } finally {
      setDownloadingId(null);
    }
  };

  const handleDeleteConfirm = async () => {
    if (!deleteCandidate) return;
    setIsDeleting(true);
    setDeleteError(null);
    try {
      await resumeClient.deleteResume(deleteCandidate.id);
      if (activeReviewResumeId === deleteCandidate.id) {
        setActiveReviewResumeId(null);
        setParsedDraft(null);
      }
      setDeleteCandidate(null);
      setNotification({
        type: 'info',
        message: `Resume "${deleteCandidate.file_name}" was permanently deleted.`,
      });
      const list = await resumeClient.listResumes();
      setResumes(list.resumes);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to delete resume.';
      setDeleteError(msg);
    } finally {
      setIsDeleting(false);
    }
  };

  const handleConfirmMerge = async (payload: ResumeConfirmationPayload) => {
    if (!activeReviewResumeId) return;
    setIsConfirming(true);
    setNotification(null);

    try {
      const result = await resumeClient.confirmResume(activeReviewResumeId, payload);
      setMergeResult(result);

      // Re-fetch authoritative profile from backend
      const updatedProfile = await profileClient.getMasterProfile();
      setExistingProfile(updatedProfile);

      // Refresh resumes list to update primary indicators
      const updatedList = await resumeClient.listResumes();
      setResumes(updatedList.resumes);

      // Exit review mode
      setActiveReviewResumeId(null);
      setParsedDraft(null);

      setNotification({
        type: 'success',
        message: 'Resume Credentials Approved & Merged',
        details: `Successfully merged ${result.merged_summary.education_added} education, ${result.merged_summary.experience_added} experience, ${result.merged_summary.projects_added} projects, ${result.merged_summary.certifications_added} certifications, and ${result.merged_summary.skills_added} skills into your Career Profile.`,
      });
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Confirmation and profile merge failed.';
      setNotification({
        type: 'destructive',
        message: 'Approval Failed',
        details: msg,
      });
    } finally {
      setIsConfirming(false);
    }
  };

  // Find primary or latest resume for Overview
  const primaryResume = resumes.find((r) => r.is_primary) || resumes[0] || null;

  // ─── Render ────────────────────────────────────────────────────────

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-bold text-slate-900 dark:text-white">
              Resume Intelligence & Parsing
            </h1>
            <Badge variant="verified" size="sm">
              <ShieldCheck className="w-3.5 h-3.5 mr-1" /> Human Approval Gate
            </Badge>
          </div>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
            Upload your master resume to extract career credentials. You retain absolute control to review and edit all extracted data before committing changes.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Link href="/career-profile">
            <Button variant="outline" size="sm">
              <Briefcase className="w-3.5 h-3.5 mr-1.5" /> View Career Profile
            </Button>
          </Link>
        </div>
      </div>

      {/* Notifications */}
      {notification && (
        <Alert
          variant={notification.type === 'destructive' ? 'destructive' : notification.type === 'success' ? 'success' : 'info'}
          title={notification.message}
        >
          {notification.details}
        </Alert>
      )}

      {/* Merge Success Banner with Direct Profile Link */}
      {mergeResult && (
        <Card className="p-5 bg-emerald-50/60 dark:bg-emerald-950/30 border border-emerald-200 dark:border-emerald-800 space-y-3">
          <div className="flex items-start justify-between gap-3">
            <div className="flex items-start gap-3">
              <div className="w-10 h-10 rounded-xl bg-emerald-100 dark:bg-emerald-900/60 text-emerald-700 dark:text-emerald-300 flex items-center justify-center shrink-0">
                <CheckCircle2 className="w-6 h-6" />
              </div>
              <div className="space-y-1">
                <h3 className="text-sm font-bold text-emerald-900 dark:text-emerald-100">
                  Profile Synchronization Complete!
                </h3>
                <p className="text-xs text-emerald-800/90 dark:text-emerald-200/90">
                  Your approved credentials have been committed to PostgreSQL. Your updated profile completeness is{' '}
                  <strong className="font-bold text-emerald-950 dark:text-emerald-50">
                    {mergeResult.completeness_score}%
                  </strong>.
                </p>
                <div className="flex flex-wrap gap-2 pt-2 text-[11px] text-emerald-900 dark:text-emerald-200 font-medium">
                  <span className="bg-emerald-100 dark:bg-emerald-900/80 px-2.5 py-0.5 rounded-full border border-emerald-300/60">
                    +{mergeResult.merged_summary.education_added} Education
                  </span>
                  <span className="bg-emerald-100 dark:bg-emerald-900/80 px-2.5 py-0.5 rounded-full border border-emerald-300/60">
                    +{mergeResult.merged_summary.experience_added} Experience
                  </span>
                  <span className="bg-emerald-100 dark:bg-emerald-900/80 px-2.5 py-0.5 rounded-full border border-emerald-300/60">
                    +{mergeResult.merged_summary.projects_added} Projects
                  </span>
                  <span className="bg-emerald-100 dark:bg-emerald-900/80 px-2.5 py-0.5 rounded-full border border-emerald-300/60">
                    +{mergeResult.merged_summary.certifications_added} Certifications
                  </span>
                  <span className="bg-emerald-100 dark:bg-emerald-900/80 px-2.5 py-0.5 rounded-full border border-emerald-300/60">
                    +{mergeResult.merged_summary.skills_added} Skills
                  </span>
                </div>
              </div>
            </div>

            <div className="flex items-center gap-2 shrink-0">
              <Link href="/career-profile">
                <Button variant="primary" size="sm" className="bg-emerald-600 hover:bg-emerald-700">
                  Inspect Career Profile <ArrowRight className="w-3.5 h-3.5 ml-1" />
                </Button>
              </Link>
            </div>
          </div>
        </Card>
      )}

      {/* ───────────────────────────────────────────────────────────── */}
      {/* WORKBENCH: PARSED RESUME REVIEW & EDIT                        */}
      {/* ───────────────────────────────────────────────────────────── */}
      {activeReviewResumeId && parsedDraft ? (
        <ParsedResumeReview
          parsedData={parsedDraft}
          existingProfile={existingProfile}
          onConfirm={handleConfirmMerge}
          onBack={() => {
            setActiveReviewResumeId(null);
            setParsedDraft(null);
          }}
          isConfirming={isConfirming}
        />
      ) : activeReviewResumeId && isLoadingDraft ? (
        <Card className="p-8 space-y-4">
          <div className="flex items-center gap-3">
            <Skeleton className="w-8 h-8 rounded-lg" />
            <div className="space-y-1 flex-1">
              <Skeleton className="h-4 w-1/3" />
              <Skeleton className="h-3 w-1/2" />
            </div>
          </div>
          <Skeleton className="h-48 w-full" />
        </Card>
      ) : (
        /* ───────────────────────────────────────────────────────────── */
        /* STANDARD VIEW: OVERVIEW, UPLOAD & HISTORY                     */
        /* ───────────────────────────────────────────────────────────── */
        <div className="space-y-6">
          {/* Section A: Current Resume Overview */}
          {primaryResume && (
            <ResumeProcessingStatusCard
              resume={primaryResume}
              onRetry={() => handleRetry(primaryResume.id)}
              onReviewDraft={() => handleReviewDraft(primaryResume.id)}
              isRetrying={retryingId === primaryResume.id}
            />
          )}

          {/* Section B: Upload Master Resume */}
          <ResumeUpload onUploadSuccess={handleUploadSuccess} />

          {/* Section C: Resume History */}
          <ResumeHistory
            resumes={resumes}
            isLoading={isLoading}
            onReviewDraft={handleReviewDraft}
            onRetry={handleRetry}
            onDownload={handleDownload}
            onDelete={(r) => setDeleteCandidate(r)}
            onUploadClick={() => window.scrollTo({ top: 200, behavior: 'smooth' })}
            retryingId={retryingId}
            downloadingId={downloadingId}
          />
        </div>
      )}

      {/* Deletion Dialog */}
      <ResumeDeleteDialog
        isOpen={Boolean(deleteCandidate)}
        resume={deleteCandidate}
        onClose={() => setDeleteCandidate(null)}
        onConfirmDelete={handleDeleteConfirm}
        isDeleting={isDeleting}
        error={deleteError}
      />
    </div>
  );
}
