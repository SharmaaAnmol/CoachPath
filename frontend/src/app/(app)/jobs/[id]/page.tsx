'use client';

import * as React from 'react';
import { useRouter } from 'next/navigation';
import { JobOpportunity } from '@/types';
import { jobClient } from '@/lib/job-client';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card } from '@/components/ui/card';
import { EmptyState } from '@/components/ui/empty-state';
import {
  ArrowLeft,
  Building2,
  MapPin,
  DollarSign,
  Calendar,
  ExternalLink,
  ShieldCheck,
  CheckCircle2,
  Briefcase,
  ListChecks,
  Sparkles,
  FileText,
  AlertCircle,
  Copy,
  Check,
} from 'lucide-react';

export default function JobDetailPage({ params }: { params: { id: string } }) {
  const router = useRouter();
  const [job, setJob] = React.useState<JobOpportunity | null>(null);
  const [isLoading, setIsLoading] = React.useState(true);
  const [error, setError] = React.useState<string | null>(null);
  const [copied, setCopied] = React.useState(false);

  React.useEffect(() => {
    async function loadJob() {
      setIsLoading(true);
      setError(null);
      try {
        const data = await jobClient.getJobById(params.id);
        setJob(data);
      } catch (err: any) {
        setError(err?.message || 'Job opportunity not found or has been archived.');
      } finally {
        setIsLoading(false);
      }
    }
    loadJob();
  }, [params.id]);

  const handleCopyLink = () => {
    if (typeof window !== 'undefined') {
      navigator.clipboard.writeText(window.location.href);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const formatSalary = (j: JobOpportunity) => {
    if (j.min_salary && j.max_salary) {
      return `$${j.min_salary.toLocaleString()} – $${j.max_salary.toLocaleString()} / year ${j.currency}`;
    } else if (j.min_salary) {
      return `From $${j.min_salary.toLocaleString()} / year ${j.currency}`;
    } else if (j.max_salary) {
      return `Up to $${j.max_salary.toLocaleString()} / year ${j.currency}`;
    }
    return 'Salary not disclosed by employer';
  };

  const formatDate = (dateString?: string) => {
    if (!dateString) return 'Unknown';
    try {
      return new Date(dateString).toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric',
      });
    } catch {
      return dateString;
    }
  };

  if (isLoading) {
    return (
      <div className="max-w-4xl mx-auto space-y-6 animate-pulse py-8">
        <div className="h-6 bg-slate-200 dark:bg-slate-700 rounded-md w-24" />
        <Card className="p-6 space-y-4">
          <div className="h-8 bg-slate-200 dark:bg-slate-700 rounded-md w-1/2" />
          <div className="h-4 bg-slate-100 dark:bg-slate-800 rounded-md w-1/3" />
          <div className="h-24 bg-slate-100 dark:bg-slate-800 rounded-md w-full" />
        </Card>
      </div>
    );
  }

  if (error || !job) {
    return (
      <div className="max-w-2xl mx-auto py-12">
        <EmptyState
          icon={<AlertCircle className="w-8 h-8 text-rose-500" />}
          title="Position Not Found"
          description={error || 'This job opportunity may have been removed, archived, or is unavailable.'}
          actionLabel="Back to Jobs Search"
          onAction={() => router.push('/jobs')}
        />
      </div>
    );
  }

  const requiredSkills = (job.skills || []).filter((s) => s.is_mandatory);
  const preferredSkills = (job.skills || []).filter((s) => !s.is_mandatory);

  return (
    <div className="max-w-4xl mx-auto space-y-6 pb-16">
      {/* Back Button */}
      <div>
        <Button
          variant="ghost"
          size="sm"
          onClick={() => router.push('/jobs')}
          className="flex items-center gap-1.5 text-xs text-slate-500 hover:text-slate-800 dark:hover:text-slate-200"
        >
          <ArrowLeft className="w-4 h-4" /> Back to Job Catalog
        </Button>
      </div>

      {/* Main Detail Header Card */}
      <Card className="p-6 space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4">
          <div className="space-y-2">
            <div className="flex flex-wrap items-center gap-2">
              <h1 className="text-xl sm:text-2xl font-extrabold text-slate-900 dark:text-white">
                {job.title}
              </h1>
              <span className="rounded-full px-2.5 py-0.5 text-xs font-semibold bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300 uppercase">
                {job.remote_type}
              </span>
              <span className="rounded-full px-2.5 py-0.5 text-xs font-medium bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300 capitalize">
                {job.experience_level.replace('_', ' ')}
              </span>
            </div>

            <div className="flex flex-wrap items-center gap-x-4 gap-y-1.5 text-xs sm:text-sm text-slate-600 dark:text-slate-400">
              <span className="flex items-center gap-1 font-semibold text-slate-900 dark:text-white">
                <Building2 className="w-4 h-4 text-slate-400" />
                {job.company_name}
              </span>
              <span className="flex items-center gap-1">
                <MapPin className="w-4 h-4 text-slate-400" />
                {job.location}
              </span>
              <span className="flex items-center gap-1 text-slate-400">
                <Calendar className="w-4 h-4" />
                Posted {formatDate(job.posted_at)}
              </span>
            </div>
          </div>

          {/* Action CTAs */}
          <div className="flex items-center gap-2.5 shrink-0">
            <Button variant="outline" size="sm" onClick={handleCopyLink} className="text-xs flex items-center gap-1.5">
              {copied ? (
                <>
                  <Check className="w-3.5 h-3.5 text-emerald-600" /> Copied
                </>
              ) : (
                <>
                  <Copy className="w-3.5 h-3.5" /> Share
                </>
              )}
            </Button>

            {job.application_url && (
              <a
                href={job.application_url}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center justify-center font-medium rounded-xl transition-all text-xs px-4 py-2 shadow-subtle bg-slate-900 text-white hover:bg-slate-800 dark:bg-white dark:text-slate-900 dark:hover:bg-slate-100"
              >
                Apply on Official Site
                <ExternalLink className="w-3.5 h-3.5 ml-1.5" />
              </a>
            )}
          </div>
        </div>

        {/* Compensation and Metadata Grid */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 p-4 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200/80 dark:border-slate-800 text-xs">
          <div>
            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">
              Compensation
            </span>
            <span className="font-semibold text-slate-900 dark:text-white mt-0.5 block truncate">
              {formatSalary(job)}
            </span>
          </div>

          <div>
            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">
              Workplace Modality
            </span>
            <span className="font-semibold text-slate-900 dark:text-white mt-0.5 block capitalize">
              {job.remote_type} • {job.employment_type?.replace('_', ' ') || 'Full-time'}
            </span>
          </div>

          <div>
            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">
              Experience Level
            </span>
            <span className="font-semibold text-slate-900 dark:text-white mt-0.5 block capitalize">
              {job.experience_level.replace('_', ' ')}
            </span>
          </div>

          <div>
            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">
              Listing Status
            </span>
            <span className="font-semibold text-emerald-600 dark:text-emerald-400 mt-0.5 block capitalize">
              {job.freshness_status}
            </span>
          </div>
        </div>

        {/* Source Lineage */}
        <div className="p-3.5 rounded-xl border border-blue-100 bg-blue-50/60 dark:border-blue-900/50 dark:bg-blue-950/30 text-xs flex items-start gap-2.5">
          <ShieldCheck className="w-4 h-4 text-blue-600 dark:text-blue-400 shrink-0 mt-0.5" />
          <div className="space-y-0.5">
            <span className="font-semibold text-blue-900 dark:text-blue-200">
              Data Lineage & Provenance: {job.source.toUpperCase()}
            </span>
            <p className="text-blue-700 dark:text-blue-300 text-[11px] leading-relaxed">
              Ingested from {job.source === 'seed' ? 'Curated Benchmark Catalog' : job.source === 'manual' ? 'Candidate-Imported Listing' : 'Permitted Developer API'}.
              {job.last_verified_at && ` Confirmed available on ${formatDate(job.last_verified_at)}.`}
              {job.data_quality_score && ` Data completeness score: ${Math.round(job.data_quality_score * 100)}%.`}
            </p>
          </div>
        </div>

        {/* Responsibilities */}
        {job.responsibilities && job.responsibilities.length > 0 && (
          <div className="space-y-2">
            <h3 className="font-bold text-slate-900 dark:text-white text-sm sm:text-base flex items-center gap-1.5">
              <Briefcase className="w-4 h-4 text-brand-500" /> Key Responsibilities
            </h3>
            <ul className="space-y-1.5 pl-4 list-disc text-slate-700 dark:text-slate-300 text-xs sm:text-sm leading-relaxed">
              {job.responsibilities.map((r, i) => (
                <li key={i}>{r}</li>
              ))}
            </ul>
          </div>
        )}

        {/* Required Qualifications */}
        {job.required_qualifications && job.required_qualifications.length > 0 && (
          <div className="space-y-2">
            <h3 className="font-bold text-slate-900 dark:text-white text-sm sm:text-base flex items-center gap-1.5">
              <ListChecks className="w-4 h-4 text-emerald-600" /> Mandatory Qualifications
            </h3>
            <ul className="space-y-1.5 pl-4 list-disc text-slate-700 dark:text-slate-300 text-xs sm:text-sm leading-relaxed">
              {job.required_qualifications.map((q, i) => (
                <li key={i}>{q}</li>
              ))}
            </ul>
          </div>
        )}

        {/* Preferred Qualifications */}
        {job.preferred_qualifications && job.preferred_qualifications.length > 0 && (
          <div className="space-y-2">
            <h3 className="font-bold text-slate-900 dark:text-white text-sm sm:text-base flex items-center gap-1.5">
              <Sparkles className="w-4 h-4 text-indigo-500" /> Preferred Qualifications
            </h3>
            <ul className="space-y-1.5 pl-4 list-disc text-slate-700 dark:text-slate-300 text-xs sm:text-sm leading-relaxed">
              {job.preferred_qualifications.map((p, i) => (
                <li key={i}>{p}</li>
              ))}
            </ul>
          </div>
        )}

        {/* Canonical Skills Breakdown */}
        <div className="space-y-3 pt-3 border-t border-slate-100 dark:border-slate-800">
          <h3 className="font-bold text-slate-900 dark:text-white text-sm sm:text-base">
            Canonical Technical Skills Tagged
          </h3>

          {requiredSkills.length > 0 && (
            <div className="space-y-1.5">
              <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider block">
                Mandatory Skills:
              </span>
              <div className="flex flex-wrap gap-1.5">
                {requiredSkills.map((s) => (
                  <Badge key={s.skill_id} variant="verified" size="md">
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 mr-1" />
                    {s.name}
                    {s.source_phrase && (
                      <span className="text-[10px] text-slate-400 font-normal ml-1">
                        ({s.source_phrase})
                      </span>
                    )}
                  </Badge>
                ))}
              </div>
            </div>
          )}

          {preferredSkills.length > 0 && (
            <div className="space-y-1.5 pt-1">
              <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider block">
                Preferred Skills:
              </span>
              <div className="flex flex-wrap gap-1.5">
                {preferredSkills.map((s) => (
                  <Badge key={s.skill_id} variant="default" size="md">
                    {s.name}
                    {s.source_phrase && (
                      <span className="text-[10px] text-slate-400 font-normal ml-1">
                        ({s.source_phrase})
                      </span>
                    )}
                  </Badge>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Full Markdown Description */}
        <div className="space-y-2 pt-3 border-t border-slate-100 dark:border-slate-800">
          <h3 className="font-bold text-slate-900 dark:text-white text-sm sm:text-base flex items-center gap-1.5">
            <FileText className="w-4 h-4 text-slate-400" /> Full Description
          </h3>
          <div className="prose prose-sm dark:prose-invert max-w-none text-slate-700 dark:text-slate-300 whitespace-pre-line leading-relaxed p-5 rounded-xl bg-slate-50/50 dark:bg-slate-900/50 border border-slate-100 dark:border-slate-800">
            {job.description_markdown}
          </div>
        </div>

        {/* External Safety Notice */}
        {job.application_url && (
          <div className="p-3.5 rounded-xl border border-amber-200/80 bg-amber-50/50 dark:border-amber-900/40 dark:bg-amber-950/20 text-xs flex items-start gap-2.5">
            <AlertCircle className="w-4 h-4 text-amber-600 shrink-0 mt-0.5" />
            <p className="text-amber-800 dark:text-amber-300 text-[11px] leading-relaxed">
              <strong>External Application Notice:</strong> Clicking &quot;Apply on Official Site&quot; opens an external career page ({job.application_url}). CoachPath does not collect recruitment fees, control employer hiring decisions, or solicit candidate credentials on behalf of third-party employers.
            </p>
          </div>
        )}
      </Card>
    </div>
  );
}
