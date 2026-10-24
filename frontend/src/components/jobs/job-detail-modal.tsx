'use client';

import * as React from 'react';
import { JobOpportunity } from '@/types';
import { Modal } from '@/components/ui/modal';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  Building2,
  MapPin,
  DollarSign,
  Calendar,
  ExternalLink,
  ShieldCheck,
  CheckCircle2,
  AlertCircle,
  Copy,
  Check,
  Briefcase,
  FileText,
  ListChecks,
  Sparkles,
} from 'lucide-react';

export interface JobDetailModalProps {
  job: JobOpportunity | null;
  isOpen: boolean;
  onClose: () => void;
}

export function JobDetailModal({ job, isOpen, onClose }: JobDetailModalProps) {
  const [copied, setCopied] = React.useState(false);

  if (!job) return null;

  const handleCopyLink = () => {
    const url = window.location.origin + `/jobs?selected=${job.id}`;
    navigator.clipboard.writeText(url);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const formatSalary = () => {
    if (job.min_salary && job.max_salary) {
      return `$${job.min_salary.toLocaleString()} – $${job.max_salary.toLocaleString()} / year ${job.currency}`;
    } else if (job.min_salary) {
      return `From $${job.min_salary.toLocaleString()} / year ${job.currency}`;
    } else if (job.max_salary) {
      return `Up to $${job.max_salary.toLocaleString()} / year ${job.currency}`;
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

  const requiredSkills = (job.skills || []).filter((s) => s.is_mandatory);
  const preferredSkills = (job.skills || []).filter((s) => !s.is_mandatory);

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      maxWidth="4xl"
      title={job.title}
      description={`${job.company_name} • ${job.location}`}
      footer={
        <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between w-full gap-3">
          <Button
            variant="outline"
            size="sm"
            onClick={handleCopyLink}
            className="flex items-center gap-1.5"
          >
            {copied ? (
              <>
                <Check className="w-3.5 h-3.5 text-emerald-600" />
                Copied Link
              </>
            ) : (
              <>
                <Copy className="w-3.5 h-3.5" />
                Share Position
              </>
            )}
          </Button>

          <div className="flex items-center gap-2">
            <Button variant="ghost" size="sm" onClick={onClose}>
              Close
            </Button>
            {job.application_url && (
              <a
                href={job.application_url}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center justify-center font-medium rounded-xl transition-all focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 text-xs px-3.5 py-2 shadow-subtle bg-slate-900 text-white hover:bg-slate-800 focus:ring-slate-900 dark:bg-white dark:text-slate-900 dark:hover:bg-slate-100 dark:focus:ring-white"
              >
                Apply on Official Site
                <ExternalLink className="w-3.5 h-3.5 ml-1.5" />
              </a>
            )}
          </div>
        </div>
      }
    >
      <div className="space-y-6 text-xs sm:text-sm">
        {/* Key Metadata Grid */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 p-3.5 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200/80 dark:border-slate-800">
          <div>
            <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider block">
              Compensation
            </span>
            <span className="font-semibold text-slate-900 dark:text-white mt-0.5 block truncate">
              {formatSalary()}
            </span>
          </div>

          <div>
            <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider block">
              Workplace Type
            </span>
            <span className="font-semibold text-slate-900 dark:text-white mt-0.5 block capitalize">
              {job.remote_type} ({job.employment_type?.replace('_', ' ') || 'Full Time'})
            </span>
          </div>

          <div>
            <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider block">
              Seniority Tier
            </span>
            <span className="font-semibold text-slate-900 dark:text-white mt-0.5 block capitalize">
              {job.experience_level.replace('_', ' ')}
            </span>
          </div>

          <div>
            <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider block">
              Listing Freshness
            </span>
            <span className="font-semibold text-emerald-600 dark:text-emerald-400 mt-0.5 block capitalize">
              {job.freshness_status} (Posted {formatDate(job.posted_at)})
            </span>
          </div>
        </div>

        {/* Source & Freshness Transparency Banner */}
        <div className="p-3 rounded-xl border border-blue-100 bg-blue-50/60 dark:border-blue-900/50 dark:bg-blue-950/30 text-xs flex items-start gap-2.5">
          <ShieldCheck className="w-4 h-4 text-blue-600 dark:text-blue-400 shrink-0 mt-0.5" />
          <div className="space-y-0.5">
            <span className="font-semibold text-blue-900 dark:text-blue-300">
              Verified Source Lineage: {job.source.toUpperCase()}
            </span>
            <p className="text-blue-700 dark:text-blue-400 text-[11px] leading-relaxed">
              Ingested from {job.source === 'seed' ? 'Curated Industry Benchmark Catalog' : job.source === 'manual' ? 'Candidate-Imported Listing' : 'Permitted Developer API'}.
              {job.last_verified_at && ` Last verified alive on ${formatDate(job.last_verified_at)}.`}
              {job.data_quality_score && ` Data completeness score: ${Math.round(job.data_quality_score * 100)}%.`}
            </p>
          </div>
        </div>

        {/* Responsibilities Section */}
        {job.responsibilities && job.responsibilities.length > 0 && (
          <div className="space-y-2">
            <h4 className="font-bold text-slate-900 dark:text-white text-xs sm:text-sm flex items-center gap-1.5">
              <Briefcase className="w-4 h-4 text-brand-500" /> Key Responsibilities
            </h4>
            <ul className="space-y-1.5 pl-4 list-disc text-slate-700 dark:text-slate-300 text-xs leading-relaxed">
              {job.responsibilities.map((r, i) => (
                <li key={i}>{r}</li>
              ))}
            </ul>
          </div>
        )}

        {/* Required Qualifications Section */}
        {job.required_qualifications && job.required_qualifications.length > 0 && (
          <div className="space-y-2">
            <h4 className="font-bold text-slate-900 dark:text-white text-xs sm:text-sm flex items-center gap-1.5">
              <ListChecks className="w-4 h-4 text-emerald-600" /> Mandatory Qualifications
            </h4>
            <ul className="space-y-1.5 pl-4 list-disc text-slate-700 dark:text-slate-300 text-xs leading-relaxed">
              {job.required_qualifications.map((q, i) => (
                <li key={i}>{q}</li>
              ))}
            </ul>
          </div>
        )}

        {/* Preferred Qualifications Section */}
        {job.preferred_qualifications && job.preferred_qualifications.length > 0 && (
          <div className="space-y-2">
            <h4 className="font-bold text-slate-900 dark:text-white text-xs sm:text-sm flex items-center gap-1.5">
              <Sparkles className="w-4 h-4 text-indigo-500" /> Preferred Qualifications
            </h4>
            <ul className="space-y-1.5 pl-4 list-disc text-slate-700 dark:text-slate-300 text-xs leading-relaxed">
              {job.preferred_qualifications.map((p, i) => (
                <li key={i}>{p}</li>
              ))}
            </ul>
          </div>
        )}

        {/* Canonical Skill Tagging */}
        <div className="space-y-3 pt-2 border-t border-slate-100 dark:border-slate-800">
          <h4 className="font-bold text-slate-900 dark:text-white text-xs sm:text-sm">
            Standardized Canonical Skills Tagged
          </h4>

          {requiredSkills.length > 0 && (
            <div className="space-y-1.5">
              <span className="text-[11px] font-semibold text-slate-500 block uppercase tracking-wider">
                Mandatory Technical Skills:
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
              <span className="text-[11px] font-semibold text-slate-500 block uppercase tracking-wider">
                Preferred / Nice-to-Have Skills:
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

        {/* Full Job Description */}
        <div className="space-y-2 pt-2 border-t border-slate-100 dark:border-slate-800">
          <h4 className="font-bold text-slate-900 dark:text-white text-xs sm:text-sm flex items-center gap-1.5">
            <FileText className="w-4 h-4 text-slate-400" /> Full Job Description
          </h4>
          <div className="prose prose-xs dark:prose-invert max-w-none text-slate-700 dark:text-slate-300 whitespace-pre-line leading-relaxed p-4 rounded-xl bg-slate-50/50 dark:bg-slate-900/50 border border-slate-100 dark:border-slate-800">
            {job.description_markdown}
          </div>
        </div>

        {/* External Link Safety Advisory */}
        {job.application_url && (
          <div className="p-3 rounded-xl border border-amber-200/80 bg-amber-50/50 dark:border-amber-900/40 dark:bg-amber-950/20 text-xs flex items-start gap-2.5">
            <AlertCircle className="w-4 h-4 text-amber-600 shrink-0 mt-0.5" />
            <p className="text-amber-800 dark:text-amber-300 text-[11px] leading-relaxed">
              <strong>External Application Notice:</strong> Clicking &quot;Apply on Official Site&quot; opens an external career page ({job.application_url}). CoachPath does not collect fees, control recruitment pipelines, or solicit candidate credentials on behalf of third-party employers.
            </p>
          </div>
        )}
      </div>
    </Modal>
  );
}
