'use client';

import * as React from 'react';
import Link from 'next/link';
import { useSearchParams } from 'next/navigation';
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
  Layers,
  Split,
  Plus,
} from 'lucide-react';
import { resumeClient } from '@/lib/resume-client';
import { profileClient } from '@/lib/profile-client';
import { ApiClientError } from '@/lib/api-client';
import {
  MasterCareerProfile,
  ParsedResumePreview,
  ParsedResumeResponse,
  ResumeConfirmationPayload,
  ResumeConfirmationResponse,
  ResumeListItem,
  ResumeTailorRequest,
  ResumeUploadResponse,
  TailoredResumeListItem,
  TailoredResumeResponse,
} from '@/types';
import { ResumeUpload } from '@/components/resume/resume-upload';
import { ResumeHistory } from '@/components/resume/resume-history';
import { ResumeProcessingStatusCard } from '@/components/resume/resume-processing-status';
import { ResumeDeleteDialog } from '@/components/resume/resume-delete-dialog';
import { ParsedResumeReview } from '@/components/resume/parsed-resume-review';
import { ResumeTailoringWizard } from '@/components/resume/resume-tailoring-wizard';
import { TailoredResumeWorkspace } from '@/components/resume/tailored-resume-workspace';
import { TailoredVersionsList } from '@/components/resume/tailored-versions-list';
import { TailoredDeleteDialog } from '@/components/resume/tailored-delete-dialog';

type ResumeMainTab = 'master' | 'tailor' | 'versions';

export default function ResumePage() {
  const searchParams = useSearchParams();
  const urlTab = searchParams.get('tab');
  const urlJobId = searchParams.get('job_id') || searchParams.get('jobId');
  const urlVersionId = searchParams.get('version_id') || searchParams.get('versionId');

  // Active Main Tab: master resumes, tailoring studio, or version history
  const [activeTab, setActiveTab] = React.useState<ResumeMainTab>(() => {
    if (urlTab === 'tailor' || urlTab === 'tailoring' || urlJobId || urlVersionId) {
      return 'tailor';
    }
    if (urlTab === 'versions') {
      return 'versions';
    }
    return 'master';
  });

  const [resumes, setResumes] = React.useState<ResumeListItem[]>([]);
  const [isLoading, setIsLoading] = React.useState(true);
  const [existingProfile, setExistingProfile] = React.useState<MasterCareerProfile | null>(null);

  // Review state (master parsed resume)
  const [activeReviewResumeId, setActiveReviewResumeId] = React.useState<string | null>(null);
  const [parsedDraft, setParsedDraft] = React.useState<ParsedResumeResponse | null>(null);
  const [isLoadingDraft, setIsLoadingDraft] = React.useState(false);
  const [isConfirming, setIsConfirming] = React.useState(false);

  // Master resume deletion dialog state
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

  // ─── Phase 10B: Tailored Resumes State ──────────────────────────────
  const [tailoredVersions, setTailoredVersions] = React.useState<TailoredResumeListItem[]>([]);
  const [isLoadingTailoredVersions, setIsLoadingTailoredVersions] = React.useState(false);

  // Active tailored version loaded in workspace
  const [activeTailoredVersion, setActiveTailoredVersion] = React.useState<TailoredResumeResponse | null>(null);
  const [isLoadingTailoredVersion, setIsLoadingTailoredVersion] = React.useState(false);

  // Tailoring wizard selection
  const [selectedSourceResumeId, setSelectedSourceResumeId] = React.useState<string | null>(null);
  const [isGeneratingTailored, setIsGeneratingTailored] = React.useState(false);
  const [tailoringError, setTailoringError] = React.useState<string | null>(null);
  const [isSavingTailored, setIsSavingTailored] = React.useState(false);
  const [isApprovingTailored, setIsApprovingTailored] = React.useState(false);

  // Tailored version deletion dialog state
  const [deleteTailoredCandidate, setDeleteTailoredCandidate] = React.useState<TailoredResumeListItem | null>(null);
  const [isDeletingTailored, setIsDeletingTailored] = React.useState(false);
  const [deleteTailoredError, setDeleteTailoredError] = React.useState<string | null>(null);

  // ─── Initial Data Loading ──────────────────────────────────────────

  const loadData = React.useCallback(async () => {
    try {
      const [resumesRes, profileRes] = await Promise.all([
        resumeClient.listResumes(),
        profileClient.getMasterProfile().catch(() => null),
      ]);
      setResumes(resumesRes.resumes);
      if (profileRes) setExistingProfile(profileRes);

      // Pre-select primary resume for wizard
      const primary = resumesRes.resumes.find((r) => r.is_primary) || resumesRes.resumes[0];
      if (primary && ['parsed', 'needs_review'].includes(primary.status)) {
        setSelectedSourceResumeId(primary.id);
      }
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

  const loadTailoredVersions = React.useCallback(async () => {
    setIsLoadingTailoredVersions(true);
    try {
      const res = await resumeClient.listTailoredVersions({ page_size: 50 });
      setTailoredVersions(res.items || []);
    } catch {
      setTailoredVersions([]);
    } finally {
      setIsLoadingTailoredVersions(false);
    }
  }, []);

  React.useEffect(() => {
    loadData();
    loadTailoredVersions();
  }, [loadData, loadTailoredVersions]);

  // Load version directly if urlVersionId is specified
  React.useEffect(() => {
    if (urlVersionId) {
      setIsLoadingTailoredVersion(true);
      resumeClient
        .getTailoredVersion(urlVersionId)
        .then((ver) => {
          setActiveTailoredVersion(ver);
          setActiveTab('tailor');
        })
        .catch((err: unknown) => {
          const msg = err instanceof Error ? err.message : 'Could not load requested version.';
          setNotification({
            type: 'destructive',
            message: 'Version Load Error',
            details: msg,
          });
        })
        .finally(() => {
          setIsLoadingTailoredVersion(false);
        });
    }
  }, [urlVersionId]);

  // ─── Polling for Processing Master Resumes ──────────────────────────

  React.useEffect(() => {
    const processingResumes = resumes.filter((r) =>
      ['uploaded', 'processing', 'parsing'].includes(r.status)
    );
    if (processingResumes.length === 0) return;

    const interval = setInterval(async () => {
      try {
        const updatedList = await resumeClient.listResumes();
        setResumes(updatedList.resumes);

        if (activeReviewResumeId) {
          const matching = updatedList.resumes.find((r) => r.id === activeReviewResumeId);
          if (matching && matching.status === 'parsed' && !parsedDraft) {
            const draft = await resumeClient.getParsedResume(activeReviewResumeId);
            setParsedDraft(draft);
          }
        }
      } catch {
        // Silently tolerate temporary polling errors
      }
    }, 3000);

    return () => clearInterval(interval);
  }, [resumes, activeReviewResumeId, parsedDraft]);

  // ─── Master Resume Handlers ─────────────────────────────────────────

  const handleUploadSuccess = async (uploadRes: ResumeUploadResponse) => {
    setNotification({
      type: 'success',
      message: `Resume "${uploadRes.file_name}" uploaded successfully.`,
      details: uploadRes.message,
    });
    setMergeResult(null);

    const res = await resumeClient.listResumes();
    setResumes(res.resumes);

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

      const updatedProfile = await profileClient.getMasterProfile();
      setExistingProfile(updatedProfile);

      const updatedList = await resumeClient.listResumes();
      setResumes(updatedList.resumes);

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

  // ─── Phase 10B: Tailored Resume Handlers ────────────────────────────

  const handleGenerateTailored = async ({
    resumeId,
    request,
  }: {
    resumeId: string;
    request: ResumeTailorRequest;
  }) => {
    setIsGeneratingTailored(true);
    setTailoringError(null);
    setNotification(null);

    try {
      const tailored = await resumeClient.tailorResume(resumeId, request);
      setActiveTailoredVersion(tailored);
      loadTailoredVersions();

      setNotification({
        type: 'success',
        message: `Tailored Resume Draft v${tailored.version_number} Created`,
        details: 'Review the tailored wording and grounded changes below before explicit candidate approval.',
      });
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Tailoring generation failed.';
      setTailoringError(msg);
      setNotification({
        type: 'destructive',
        message: 'Tailoring Failed',
        details: msg,
      });
    } finally {
      setIsGeneratingTailored(false);
    }
  };

  const handleSaveTailored = async (updatedContent: ParsedResumePreview, notes?: string) => {
    if (!activeTailoredVersion) return;
    setIsSavingTailored(true);
    setNotification(null);

    try {
      const saved = await resumeClient.updateTailoredVersion(activeTailoredVersion.id, {
        tailored_content: updatedContent,
        user_notes: notes,
      });
      setActiveTailoredVersion(saved);
      loadTailoredVersions();

      setNotification({
        type: 'success',
        message: 'Tailored Changes Persisted',
        details: `Version ${saved.version_number} content successfully saved.`,
      });
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to save changes.';
      setNotification({
        type: 'destructive',
        message: 'Save Failed',
        details: msg,
      });
    } finally {
      setIsSavingTailored(false);
    }
  };

  const handleApproveTailored = async (acceptedSections: string[]) => {
    if (!activeTailoredVersion) return;
    setIsApprovingTailored(true);
    setNotification(null);

    try {
      const approved = await resumeClient.approveTailoredVersion(activeTailoredVersion.id, {
        user_confirmation: true,
        accepted_sections: acceptedSections,
      });
      setActiveTailoredVersion(approved);
      loadTailoredVersions();

      setNotification({
        type: 'success',
        message: `Tailored Resume v${approved.version_number} Approved & Locked`,
        details: 'Version marked as user-approved. Further edits are locked to preserve version integrity.',
      });
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Approval failed.';
      setNotification({
        type: 'destructive',
        message: 'Approval Error',
        details: msg,
      });
      throw err;
    } finally {
      setIsApprovingTailored(false);
    }
  };

  const handleOpenTailoredVersion = async (versionId: string) => {
    setIsLoadingTailoredVersion(true);
    setNotification(null);

    try {
      const ver = await resumeClient.getTailoredVersion(versionId);
      setActiveTailoredVersion(ver);
      setActiveTab('tailor');
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Could not load version details.';
      setNotification({
        type: 'destructive',
        message: 'Load Failed',
        details: msg,
      });
    } finally {
      setIsLoadingTailoredVersion(false);
    }
  };

  const handleDeleteTailoredConfirm = async () => {
    if (!deleteTailoredCandidate) return;
    setIsDeletingTailored(true);
    setDeleteTailoredError(null);

    try {
      await resumeClient.deleteTailoredVersion(deleteTailoredCandidate.id);
      if (activeTailoredVersion?.id === deleteTailoredCandidate.id) {
        setActiveTailoredVersion(null);
      }
      setDeleteTailoredCandidate(null);
      setNotification({
        type: 'info',
        message: `Tailored Version v${deleteTailoredCandidate.version_number} deleted.`,
      });
      loadTailoredVersions();
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to delete version.';
      setDeleteTailoredError(msg);
    } finally {
      setIsDeletingTailored(false);
    }
  };

  const primaryResume = resumes.find((r) => r.is_primary) || resumes[0] || null;

  return (
    <div className="space-y-6">
      {/* ───────────────────────────────────────────────────────────── */}
      {/* PAGE HEADER & TOP NAVIGATION TABS                             */}
      {/* ───────────────────────────────────────────────────────────── */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-bold text-slate-900 dark:text-white">
              Resume Intelligence & Tailoring
            </h1>
            <Badge variant="verified" size="sm">
              <ShieldCheck className="w-3.5 h-3.5 mr-1" /> Two-Pass Grounded AI
            </Badge>
          </div>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
            Manage your master source documents, extract verified career credentials, and optimize tailored resume variants for target engineering roles.
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

      {/* Main Feature Tabs */}
      <div className="flex items-center rounded-xl bg-slate-100 dark:bg-slate-800/80 p-1 text-xs font-semibold w-full sm:w-fit overflow-x-auto">
        <button
          type="button"
          onClick={() => setActiveTab('master')}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-all ${
            activeTab === 'master'
              ? 'bg-white dark:bg-slate-900 text-slate-900 dark:text-white shadow-sm'
              : 'text-slate-500 hover:text-slate-900 dark:hover:text-white'
          }`}
        >
          <FileText className="w-4 h-4 text-brand-600" />
          <span>Master Resumes</span>
          <span className="text-[10px] font-mono px-1.5 py-0.2 rounded-full bg-slate-200 dark:bg-slate-700">
            {resumes.length}
          </span>
        </button>

        <button
          type="button"
          onClick={() => setActiveTab('tailor')}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-all ${
            activeTab === 'tailor'
              ? 'bg-white dark:bg-slate-900 text-purple-600 dark:text-purple-400 shadow-sm'
              : 'text-slate-500 hover:text-purple-600 dark:hover:text-purple-400'
          }`}
        >
          <Sparkles className="w-4 h-4 text-purple-600" />
          <span>Job Tailoring Studio</span>
          {activeTailoredVersion && (
            <span className="w-2 h-2 rounded-full bg-purple-500 animate-pulse" />
          )}
        </button>

        <button
          type="button"
          onClick={() => setActiveTab('versions')}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-all ${
            activeTab === 'versions'
              ? 'bg-white dark:bg-slate-900 text-slate-900 dark:text-white shadow-sm'
              : 'text-slate-500 hover:text-slate-900 dark:hover:text-white'
          }`}
        >
          <Layers className="w-4 h-4 text-indigo-600" />
          <span>Tailored Versions</span>
          <span className="text-[10px] font-mono px-1.5 py-0.2 rounded-full bg-slate-200 dark:bg-slate-700">
            {tailoredVersions.length}
          </span>
        </button>
      </div>

      {/* Notifications */}
      {notification && (
        <Alert
          variant={
            notification.type === 'destructive'
              ? 'destructive'
              : notification.type === 'success'
              ? 'success'
              : 'info'
          }
          title={notification.message}
        >
          {notification.details}
        </Alert>
      )}

      {/* Merge Success Banner with Direct Profile Link */}
      {mergeResult && activeTab === 'master' && (
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
      {/* TAB 1: MASTER RESUMES & PARSED EXTRACTION                     */}
      {/* ───────────────────────────────────────────────────────────── */}
      {activeTab === 'master' && (
        <>
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
            <div className="space-y-6">
              {primaryResume && (
                <ResumeProcessingStatusCard
                  resume={primaryResume}
                  onRetry={() => handleRetry(primaryResume.id)}
                  onReviewDraft={() => handleReviewDraft(primaryResume.id)}
                  isRetrying={retryingId === primaryResume.id}
                />
              )}

              <ResumeUpload onUploadSuccess={handleUploadSuccess} />

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
        </>
      )}

      {/* ───────────────────────────────────────────────────────────── */}
      {/* TAB 2: JOB TAILORING STUDIO & WORKSPACE                       */}
      {/* ───────────────────────────────────────────────────────────── */}
      {activeTab === 'tailor' && (
        <>
          {isLoadingTailoredVersion ? (
            <Card className="p-12 space-y-4 text-center">
              <Skeleton className="w-12 h-12 rounded-xl mx-auto" />
              <div className="space-y-2 max-w-sm mx-auto">
                <Skeleton className="h-4 w-2/3 mx-auto" />
                <Skeleton className="h-3 w-full" />
              </div>
            </Card>
          ) : activeTailoredVersion ? (
            <TailoredResumeWorkspace
              version={activeTailoredVersion}
              jobTitle={
                tailoredVersions.find((v) => v.id === activeTailoredVersion.id)?.job_title ||
                'Target Engineering Position'
              }
              companyName={
                tailoredVersions.find((v) => v.id === activeTailoredVersion.id)?.company_name
              }
              onBack={() => setActiveTailoredVersion(null)}
              onSave={handleSaveTailored}
              onApprove={handleApproveTailored}
              onDelete={() => {
                const found = tailoredVersions.find((v) => v.id === activeTailoredVersion.id);
                if (found) setDeleteTailoredCandidate(found);
              }}
              isSaving={isSavingTailored}
              isApproving={isApprovingTailored}
            />
          ) : (
            <ResumeTailoringWizard
              resumes={resumes}
              selectedResumeId={selectedSourceResumeId}
              onSelectResume={(id) => setSelectedSourceResumeId(id)}
              onUploadClick={() => setActiveTab('master')}
              initialJobId={urlJobId}
              onGenerate={handleGenerateTailored}
              isGenerating={isGeneratingTailored}
              error={tailoringError}
            />
          )}
        </>
      )}

      {/* ───────────────────────────────────────────────────────────── */}
      {/* TAB 3: TAILORED VERSIONS HISTORY                              */}
      {/* ───────────────────────────────────────────────────────────── */}
      {activeTab === 'versions' && (
        <TailoredVersionsList
          versions={tailoredVersions}
          isLoading={isLoadingTailoredVersions}
          onOpenVersion={handleOpenTailoredVersion}
          onDeleteVersion={(v) => setDeleteTailoredCandidate(v)}
          onCreateNewClick={() => {
            setActiveTailoredVersion(null);
            setActiveTab('tailor');
          }}
        />
      )}

      {/* Master Resume Deletion Dialog */}
      <ResumeDeleteDialog
        isOpen={Boolean(deleteCandidate)}
        resume={deleteCandidate}
        onClose={() => setDeleteCandidate(null)}
        onConfirmDelete={handleDeleteConfirm}
        isDeleting={isDeleting}
        error={deleteError}
      />

      {/* Tailored Version Deletion Dialog */}
      <TailoredDeleteDialog
        isOpen={Boolean(deleteTailoredCandidate)}
        versionNumber={deleteTailoredCandidate?.version_number}
        jobTitle={deleteTailoredCandidate?.job_title}
        companyName={deleteTailoredCandidate?.company_name}
        onClose={() => setDeleteTailoredCandidate(null)}
        onConfirmDelete={handleDeleteTailoredConfirm}
        isDeleting={isDeletingTailored}
        error={deleteTailoredError}
      />
    </div>
  );
}
