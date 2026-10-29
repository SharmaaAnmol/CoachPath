'use client';

import * as React from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  FileText,
  Briefcase,
  Sparkles,
  ShieldCheck,
  Search,
  Upload,
  AlertTriangle,
  Building2,
  MapPin,
  DollarSign,
  CheckCircle2,
  Tag,
  Loader2,
  Plus,
  X,
  FileCode,
} from 'lucide-react';
import { JobOpportunity, ResumeListItem, ResumeTailorRequest } from '@/types';
import { jobClient } from '@/lib/job-client';

interface ResumeTailoringWizardProps {
  resumes: ResumeListItem[];
  selectedResumeId: string | null;
  onSelectResume: (id: string) => void;
  onUploadClick: () => void;
  initialJobId?: string | null;
  onGenerate: (payload: {
    resumeId: string;
    request: ResumeTailorRequest;
  }) => Promise<void>;
  isGenerating: boolean;
  error?: string | null;
}

export function ResumeTailoringWizard({
  resumes,
  selectedResumeId,
  onSelectResume,
  onUploadClick,
  initialJobId,
  onGenerate,
  isGenerating,
  error,
}: ResumeTailoringWizardProps) {
  // Eligible source resumes
  const eligibleResumes = resumes.filter((r) =>
    ['parsed', 'needs_review'].includes(r.status)
  );

  // Auto-select primary or first eligible resume if none selected
  React.useEffect(() => {
    if (!selectedResumeId && eligibleResumes.length > 0) {
      const primary = eligibleResumes.find((r) => r.is_primary) || eligibleResumes[0];
      onSelectResume(primary.id);
    }
  }, [selectedResumeId, eligibleResumes, onSelectResume]);

  // Target Job State
  const [jobMode, setJobMode] = React.useState<'catalog' | 'custom'>('catalog');
  const [catalogJobs, setCatalogJobs] = React.useState<JobOpportunity[]>([]);
  const [isLoadingJobs, setIsLoadingJobs] = React.useState(false);
  const [jobSearchTerm, setJobSearchTerm] = React.useState('');
  const [selectedJob, setSelectedJob] = React.useState<JobOpportunity | null>(null);

  // Custom Job Input
  const [customTitle, setCustomTitle] = React.useState('');
  const [customCompany, setCustomCompany] = React.useState('');
  const [customDescription, setCustomDescription] = React.useState('');

  // Emphasis tags & Notes
  const [emphasisTags, setEmphasisTags] = React.useState<string[]>([]);
  const [emphasisInput, setEmphasisInput] = React.useState('');
  const [userNotes, setUserNotes] = React.useState('');

  // ─── Load Jobs ───────────────────────────────────────────────────────
  const fetchJobs = React.useCallback(async (search?: string) => {
    setIsLoadingJobs(true);
    try {
      const res = await jobClient.searchJobs({
        keyword: search || undefined,
        page_size: 20,
      });
      setCatalogJobs(res.items || []);

      // If initialJobId is provided, select it
      if (initialJobId && !selectedJob) {
        const found = res.items.find((j) => j.id === initialJobId);
        if (found) {
          setSelectedJob(found);
        } else {
          // Fetch directly
          try {
            const direct = await jobClient.getJobById(initialJobId);
            if (direct) setSelectedJob(direct);
          } catch {
            // Silently ignore if job not found
          }
        }
      }
    } catch {
      // Fallback empty
      setCatalogJobs([]);
    } finally {
      setIsLoadingJobs(false);
    }
  }, [initialJobId, selectedJob]);

  React.useEffect(() => {
    fetchJobs();
  }, [fetchJobs]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    fetchJobs(jobSearchTerm);
  };

  const handleAddEmphasis = () => {
    const trimmed = emphasisInput.trim();
    if (trimmed && !emphasisTags.includes(trimmed)) {
      setEmphasisTags([...emphasisTags, trimmed]);
      setEmphasisInput('');
    }
  };

  const handleRemoveEmphasis = (tag: string) => {
    setEmphasisTags(emphasisTags.filter((t) => t !== tag));
  };

  // Validation
  const hasValidResume = Boolean(selectedResumeId);
  const hasValidJob =
    jobMode === 'catalog'
      ? Boolean(selectedJob)
      : customDescription.trim().length >= 50 &&
        customTitle.trim().length > 0 &&
        customCompany.trim().length > 0;

  const canGenerate = hasValidResume && hasValidJob && !isGenerating;

  const handleStartGeneration = async () => {
    if (!selectedResumeId || !canGenerate) return;

    const request: ResumeTailorRequest = {
      target_emphasis: emphasisTags,
      user_notes: userNotes.trim() || undefined,
    };

    if (jobMode === 'catalog' && selectedJob) {
      request.job_id = selectedJob.id;
    } else {
      request.job_title = customTitle.trim();
      request.company_name = customCompany.trim();
      request.job_description_text = customDescription.trim();
    }

    await onGenerate({
      resumeId: selectedResumeId,
      request,
    });
  };

  return (
    <div className="space-y-8 max-w-5xl">
      {/* Wizard Header / Hero */}
      <div className="p-6 rounded-2xl bg-gradient-to-r from-purple-50/70 via-indigo-50/40 to-brand-50/40 dark:from-purple-950/20 dark:via-indigo-950/10 dark:to-brand-950/10 border border-purple-200/80 dark:border-purple-800/60 space-y-3">
        <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-purple-700 dark:text-purple-300">
          <Sparkles className="w-4 h-4" />
          <span>Tailoring Studio &bull; Grounded Anti-Fabrication</span>
        </div>
        <h2 className="text-xl font-bold text-slate-900 dark:text-white">
          Optimize Your Resume for a Specific Job Opportunity
        </h2>
        <p className="text-xs text-slate-600 dark:text-slate-300 max-w-3xl leading-relaxed">
          CoachPath rephrases your technical bullet points to directly address the target job requirements using our two-pass grounding engine. Your master resume remains completely immutable.
        </p>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-800 text-xs text-rose-700 dark:text-rose-300 flex items-start gap-3">
          <AlertTriangle className="w-5 h-5 shrink-0 text-rose-600 mt-0.5" />
          <div>
            <h4 className="font-bold text-rose-900 dark:text-rose-100">Generation Error</h4>
            <p className="mt-0.5">{error}</p>
          </div>
        </div>
      )}

      {/* ───────────────────────────────────────────────────────────── */}
      {/* STEP 1: SELECT SOURCE RESUME                                  */}
      {/* ───────────────────────────────────────────────────────────── */}
      <Card className="p-6 space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-7 h-7 rounded-lg bg-brand-100 dark:bg-brand-950/80 text-brand-700 dark:text-brand-300 flex items-center justify-center font-bold text-xs">
              1
            </div>
            <h3 className="text-sm font-bold text-slate-900 dark:text-white">
              Select Verified Source Resume
            </h3>
          </div>
          <Badge variant="verified" size="sm">
            <ShieldCheck className="w-3.5 h-3.5 mr-1" /> Immutable Source
          </Badge>
        </div>

        {eligibleResumes.length === 0 ? (
          <div className="p-6 rounded-xl bg-amber-50/60 dark:bg-amber-950/20 border border-amber-200 dark:border-amber-800 text-center space-y-3">
            <AlertTriangle className="w-8 h-8 mx-auto text-amber-600" />
            <div className="space-y-1">
              <h4 className="text-sm font-bold text-amber-900 dark:text-amber-100">
                No Eligible Master Resume Found
              </h4>
              <p className="text-xs text-amber-800/90 dark:text-amber-200/90 max-w-md mx-auto">
                You must have at least one successfully parsed resume document before you can generate tailored drafts.
              </p>
            </div>
            <Button size="sm" variant="primary" onClick={onUploadClick}>
              <Upload className="w-4 h-4 mr-1.5" /> Upload Master Resume
            </Button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {eligibleResumes.map((r) => {
              const isSelected = selectedResumeId === r.id;
              return (
                <div
                  key={r.id}
                  onClick={() => onSelectResume(r.id)}
                  className={`p-4 rounded-xl border text-left cursor-pointer transition-all flex items-start justify-between gap-3 ${
                    isSelected
                      ? 'border-brand-500 bg-brand-50/40 dark:bg-brand-950/30 shadow-subtle'
                      : 'border-slate-200 dark:border-slate-800 hover:border-slate-300 dark:hover:border-slate-700 bg-white dark:bg-slate-900'
                  }`}
                >
                  <div className="flex items-start gap-3 min-w-0">
                    <div
                      className={`w-9 h-9 rounded-lg flex items-center justify-center shrink-0 mt-0.5 ${
                        isSelected
                          ? 'bg-brand-600 text-white'
                          : 'bg-slate-100 dark:bg-slate-800 text-slate-500'
                      }`}
                    >
                      <FileText className="w-5 h-5" />
                    </div>
                    <div className="min-w-0 space-y-1">
                      <div className="flex items-center gap-2">
                        <span className="text-xs font-bold text-slate-900 dark:text-white truncate">
                          {r.file_name}
                        </span>
                        {r.is_primary && (
                          <span className="text-[10px] font-bold text-brand-700 bg-brand-100 dark:bg-brand-950 dark:text-brand-300 px-1.5 py-0.2 rounded">
                            Primary
                          </span>
                        )}
                      </div>
                      <p className="text-[11px] text-slate-500 dark:text-slate-400">
                        Parsed {new Date(r.created_at).toLocaleDateString()} &bull;{' '}
                        {(r.file_size_bytes / 1024).toFixed(0)} KB
                      </p>
                    </div>
                  </div>
                  {isSelected && (
                    <CheckCircle2 className="w-5 h-5 text-brand-600 shrink-0" />
                  )}
                </div>
              );
            })}
          </div>
        )}
      </Card>

      {/* ───────────────────────────────────────────────────────────── */}
      {/* STEP 2: SELECT TARGET JOB                                     */}
      {/* ───────────────────────────────────────────────────────────── */}
      <Card className="p-6 space-y-5">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-7 h-7 rounded-lg bg-indigo-100 dark:bg-indigo-950/80 text-indigo-700 dark:text-indigo-300 flex items-center justify-center font-bold text-xs">
              2
            </div>
            <h3 className="text-sm font-bold text-slate-900 dark:text-white">
              Select Target Job Opportunity
            </h3>
          </div>

          {/* Toggle Catalog vs Custom */}
          <div className="flex items-center rounded-lg bg-slate-100 dark:bg-slate-800 p-0.5 text-xs">
            <button
              type="button"
              onClick={() => setJobMode('catalog')}
              className={`px-3 py-1.5 rounded-md font-semibold transition-all ${
                jobMode === 'catalog'
                  ? 'bg-white dark:bg-slate-900 text-slate-900 dark:text-white shadow-sm'
                  : 'text-slate-500 hover:text-slate-900 dark:hover:text-white'
              }`}
            >
              Job Catalog
            </button>
            <button
              type="button"
              onClick={() => setJobMode('custom')}
              className={`px-3 py-1.5 rounded-md font-semibold transition-all ${
                jobMode === 'custom'
                  ? 'bg-white dark:bg-slate-900 text-slate-900 dark:text-white shadow-sm'
                  : 'text-slate-500 hover:text-slate-900 dark:hover:text-white'
              }`}
            >
              Paste Job Description
            </button>
          </div>
        </div>

        {/* Catalog Mode */}
        {jobMode === 'catalog' && (
          <div className="space-y-4">
            <form onSubmit={handleSearchSubmit} className="flex gap-2">
              <div className="relative flex-1">
                <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
                <input
                  type="text"
                  value={jobSearchTerm}
                  onChange={(e) => setJobSearchTerm(e.target.value)}
                  placeholder="Search catalog by title, company, or tech keywords (e.g. Stripe, Python, Backend)..."
                  className="w-full pl-9 pr-3 py-2 text-xs rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
                />
              </div>
              <Button size="sm" variant="outline" type="submit">
                Search
              </Button>
            </form>

            {isLoadingJobs ? (
              <div className="py-8 text-center text-xs text-slate-500 flex items-center justify-center gap-2">
                <Loader2 className="w-4 h-4 animate-spin text-indigo-600" />
                Loading job postings...
              </div>
            ) : catalogJobs.length === 0 ? (
              <div className="p-6 text-center text-xs text-slate-500 border border-dashed rounded-xl">
                No jobs match your search criteria. Try a broader search or paste the description directly.
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3 max-h-80 overflow-y-auto pr-1">
                {catalogJobs.map((job) => {
                  const isSelected = selectedJob?.id === job.id;
                  return (
                    <div
                      key={job.id}
                      onClick={() => setSelectedJob(job)}
                      className={`p-3.5 rounded-xl border text-left cursor-pointer transition-all flex flex-col justify-between gap-2 ${
                        isSelected
                          ? 'border-indigo-500 bg-indigo-50/40 dark:bg-indigo-950/30 shadow-subtle'
                          : 'border-slate-200 dark:border-slate-800 hover:border-slate-300 dark:hover:border-slate-700 bg-white dark:bg-slate-900'
                      }`}
                    >
                      <div className="space-y-1">
                        <div className="flex items-start justify-between gap-2">
                          <h4 className="text-xs font-bold text-slate-900 dark:text-white line-clamp-1">
                            {job.title}
                          </h4>
                          {isSelected && (
                            <CheckCircle2 className="w-4 h-4 text-indigo-600 shrink-0" />
                          )}
                        </div>
                        <div className="flex items-center gap-2 text-[11px] text-slate-600 dark:text-slate-400">
                          <Building2 className="w-3.5 h-3.5 shrink-0 text-slate-400" />
                          <span className="font-medium truncate">{job.company_name}</span>
                          {job.location && (
                            <>
                              <span>&bull;</span>
                              <span className="truncate">{job.location}</span>
                            </>
                          )}
                        </div>
                      </div>

                      <div className="flex flex-wrap gap-1.5 pt-1 text-[10px]">
                        {job.remote_type && (
                          <span className="px-2 py-0.5 rounded-md bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300">
                            {job.remote_type}
                          </span>
                        )}
                        {job.min_salary && job.max_salary && (
                          <span className="px-2 py-0.5 rounded-md bg-emerald-50 dark:bg-emerald-950/50 text-emerald-700 dark:text-emerald-300 font-medium">
                            ${job.min_salary.toLocaleString()} – ${job.max_salary.toLocaleString()}
                          </span>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        )}

        {/* Custom Text Mode */}
        {jobMode === 'custom' && (
          <div className="space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div>
                <label className="text-xs font-semibold text-slate-700 dark:text-slate-300 block mb-1">
                  Job Title <span className="text-rose-500">*</span>
                </label>
                <input
                  type="text"
                  value={customTitle}
                  onChange={(e) => setCustomTitle(e.target.value)}
                  placeholder="e.g. Senior Backend Engineer"
                  className="w-full px-3 py-2 text-xs rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
                />
              </div>
              <div>
                <label className="text-xs font-semibold text-slate-700 dark:text-slate-300 block mb-1">
                  Company Name <span className="text-rose-500">*</span>
                </label>
                <input
                  type="text"
                  value={customCompany}
                  onChange={(e) => setCustomCompany(e.target.value)}
                  placeholder="e.g. Stripe, Linear, Vercel"
                  className="w-full px-3 py-2 text-xs rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
                />
              </div>
            </div>

            <div>
              <div className="flex items-center justify-between mb-1">
                <label className="text-xs font-semibold text-slate-700 dark:text-slate-300 block">
                  Job Description Text <span className="text-rose-500">*</span>
                </label>
                <span
                  className={`text-[10px] font-mono ${
                    customDescription.trim().length >= 50
                      ? 'text-emerald-600 dark:text-emerald-400'
                      : 'text-slate-400'
                  }`}
                >
                  {customDescription.trim().length} / 50 min chars
                </span>
              </div>
              <textarea
                value={customDescription}
                onChange={(e) => setCustomDescription(e.target.value)}
                rows={6}
                placeholder="Paste the full job posting, responsibilities, and required qualifications here..."
                className="w-full px-3 py-2 text-xs rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
            </div>
          </div>
        )}
      </Card>

      {/* ───────────────────────────────────────────────────────────── */}
      {/* STEP 3: OPTIONAL EMPHASIS & NOTES                             */}
      {/* ───────────────────────────────────────────────────────────── */}
      <Card className="p-6 space-y-4">
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 rounded-lg bg-amber-100 dark:bg-amber-950/80 text-amber-700 dark:text-amber-300 flex items-center justify-center font-bold text-xs">
            3
          </div>
          <div>
            <h3 className="text-sm font-bold text-slate-900 dark:text-white">
              Target Emphasis & Candidate Notes (Optional)
            </h3>
            <p className="text-xs text-slate-500 dark:text-slate-400">
              Highlight specific technical themes or provide additional context for tailoring.
            </p>
          </div>
        </div>

        <div className="space-y-3">
          <div>
            <label className="text-xs font-semibold text-slate-700 dark:text-slate-300 block mb-1">
              Key Competencies to Emphasize
            </label>
            <div className="flex gap-2">
              <input
                type="text"
                value={emphasisInput}
                onChange={(e) => setEmphasisInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    e.preventDefault();
                    handleAddEmphasis();
                  }
                }}
                placeholder="e.g. Distributed Systems, Payment Processing, PostgreSQL Indexing"
                className="flex-1 px-3 py-2 text-xs rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
              />
              <Button
                size="sm"
                variant="outline"
                type="button"
                onClick={handleAddEmphasis}
                disabled={!emphasisInput.trim()}
              >
                <Plus className="w-3.5 h-3.5 mr-1" /> Add
              </Button>
            </div>

            {emphasisTags.length > 0 && (
              <div className="flex flex-wrap gap-1.5 pt-2">
                {emphasisTags.map((tag) => (
                  <span
                    key={tag}
                    className="inline-flex items-center gap-1 text-xs px-2.5 py-1 rounded-lg bg-purple-100 dark:bg-purple-950/60 text-purple-800 dark:text-purple-300 border border-purple-200 dark:border-purple-800 font-medium"
                  >
                    <Tag className="w-3 h-3 text-purple-600" />
                    <span>{tag}</span>
                    <button
                      type="button"
                      onClick={() => handleRemoveEmphasis(tag)}
                      className="hover:text-purple-950 dark:hover:text-white"
                    >
                      <X className="w-3 h-3" />
                    </button>
                  </span>
                ))}
              </div>
            )}
          </div>

          <div>
            <label className="text-xs font-semibold text-slate-700 dark:text-slate-300 block mb-1">
              Candidate Context / Directives
            </label>
            <textarea
              value={userNotes}
              onChange={(e) => setUserNotes(e.target.value)}
              maxLength={1000}
              rows={2}
              placeholder="e.g. Highlight high-throughput webhook ingestion experience over frontend work..."
              className="w-full px-3 py-2 text-xs rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
            />
          </div>
        </div>
      </Card>

      {/* ───────────────────────────────────────────────────────────── */}
      {/* SUMMARY & GENERATION TRIGGER                                  */}
      {/* ───────────────────────────────────────────────────────────── */}
      <div className="p-5 rounded-2xl bg-slate-900 text-white border border-slate-800 space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="space-y-1">
            <h4 className="text-sm font-bold flex items-center gap-2">
              <ShieldCheck className="w-4 h-4 text-emerald-400" />
              <span>Evidence-Grounded Resume Reconciler Ready</span>
            </h4>
            <p className="text-xs text-slate-400">
              Target:{' '}
              <strong className="text-white">
                {jobMode === 'catalog'
                  ? selectedJob?.title
                    ? `${selectedJob.title} (${selectedJob.company_name})`
                    : 'Select a job above'
                  : customTitle
                  ? `${customTitle} (${customCompany})`
                  : 'Enter job details above'}
              </strong>
            </p>
          </div>

          <Button
            size="lg"
            variant="primary"
            onClick={handleStartGeneration}
            disabled={!canGenerate}
            className="bg-purple-600 hover:bg-purple-700 shadow-elevated px-6 text-sm shrink-0"
          >
            {isGenerating ? (
              <>
                <Loader2 className="w-4 h-4 mr-2 animate-spin" /> Tailoring Resume...
              </>
            ) : (
              <>
                <Sparkles className="w-4 h-4 mr-2" /> Generate Tailored Draft
              </>
            )}
          </Button>
        </div>

        <div className="pt-2 border-t border-slate-800 text-[11px] text-slate-400 flex flex-wrap items-center gap-4">
          <span className="flex items-center gap-1.5">
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
            Original Resume Remains Untouched
          </span>
          <span className="flex items-center gap-1.5">
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
            Unevidenced Claims Automatically Pruned
          </span>
          <span className="flex items-center gap-1.5">
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
            Human Review Required Before Use
          </span>
        </div>
      </div>
    </div>
  );
}
