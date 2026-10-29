'use client';

import * as React from 'react';
import { JobOpportunity, ManualJobImportPayload } from '@/types';
import { Modal } from '@/components/ui/modal';
import { Button } from '@/components/ui/button';
import { jobClient } from '@/lib/job-client';
import {
  Upload,
  AlertCircle,
  CheckCircle2,
  Building2,
  FileText,
  DollarSign,
  Link as LinkIcon,
  Sparkles,
} from 'lucide-react';

export interface ManualJobImportModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: (imported: JobOpportunity) => void;
}

const CANONICAL_ROLES = [
  { id: '', label: 'Auto-Detect Role from Text' },
  { id: 'backend-developer', label: 'Backend Developer' },
  { id: 'frontend-developer', label: 'Frontend Developer' },
  { id: 'fullstack-developer', label: 'Fullstack Developer' },
  { id: 'data-engineer', label: 'Data Engineer' },
  { id: 'mobile-engineer', label: 'Mobile Engineer' },
  { id: 'data-scientist', label: 'Data Scientist' },
  { id: 'machine-learning-engineer', label: 'ML Engineer' },
  { id: 'ai-engineer', label: 'AI Engineer' },
  { id: 'devops-cloud-engineer', label: 'DevOps & Cloud' },
  { id: 'software-engineer', label: 'Software Engineer' },
  { id: 'data-analyst', label: 'Data Analyst' },
];

export function ManualJobImportModal({
  isOpen,
  onClose,
  onSuccess,
}: ManualJobImportModalProps) {
  const [formData, setFormData] = React.useState<ManualJobImportPayload>({
    title: '',
    company_name: '',
    location: 'Remote',
    remote_type: 'remote',
    experience_level: 'entry_level',
    role_id: '',
    min_salary: undefined,
    max_salary: undefined,
    currency: 'USD',
    application_url: '',
    source_url: '',
    description_text: '',
  });

  const [isSubmitting, setIsSubmitting] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (formData.title.trim().length < 2) {
      setError('Job title must be at least 2 characters.');
      return;
    }
    if (formData.company_name.trim().length < 2) {
      setError('Company name must be at least 2 characters.');
      return;
    }
    if (formData.description_text.trim().length < 20) {
      setError('Job description must be at least 20 characters.');
      return;
    }

    try {
      setIsSubmitting(true);
      const payload: ManualJobImportPayload = {
        title: formData.title.trim(),
        company_name: formData.company_name.trim(),
        location: formData.location?.trim() || 'Remote',
        remote_type: formData.remote_type || 'remote',
        experience_level: formData.experience_level || 'entry_level',
        role_id: formData.role_id || undefined,
        min_salary: formData.min_salary ? Number(formData.min_salary) : undefined,
        max_salary: formData.max_salary ? Number(formData.max_salary) : undefined,
        currency: formData.currency || 'USD',
        application_url: formData.application_url?.trim() || undefined,
        source_url: formData.source_url?.trim() || undefined,
        description_text: formData.description_text.trim(),
      };

      const result = await jobClient.importJob(payload);
      onSuccess(result);
      onClose();
    } catch (err: any) {
      setError(err?.message || 'Failed to import job posting. Please check your inputs.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      maxWidth="2xl"
      title="Import Job Posting for Parsing"
      description="Paste an external job listing to automatically extract canonical skills, normalize role requirements, and add it to your search catalog."
      footer={
        <div className="flex items-center justify-end gap-3 w-full">
          <Button variant="ghost" size="sm" onClick={onClose} disabled={isSubmitting}>
            Cancel
          </Button>
          <Button
            variant="primary"
            size="sm"
            onClick={handleSubmit}
            disabled={isSubmitting}
            className="flex items-center gap-1.5"
          >
            {isSubmitting ? (
              'Parsing & Ingesting...'
            ) : (
              <>
                <Sparkles className="w-3.5 h-3.5" /> Ingest & Extract Skills
              </>
            )}
          </Button>
        </div>
      }
    >
      <form onSubmit={handleSubmit} className="space-y-4 text-xs sm:text-sm">
        {error && (
          <div className="p-3 rounded-xl border border-rose-200 bg-rose-50 dark:border-rose-900/50 dark:bg-rose-950/30 text-rose-700 dark:text-rose-300 text-xs flex items-center gap-2">
            <AlertCircle className="w-4 h-4 shrink-0 text-rose-500" />
            <span>{error}</span>
          </div>
        )}

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div className="space-y-1">
            <label className="text-[11px] font-semibold text-slate-700 dark:text-slate-300">
              Job Title <span className="text-rose-500">*</span>
            </label>
            <input
              type="text"
              required
              placeholder="e.g. Junior Backend Engineer"
              value={formData.title}
              onChange={(e) => setFormData({ ...formData, title: e.target.value })}
              className="w-full px-3 py-2 text-xs rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900 text-slate-900 dark:text-white focus:ring-1 focus:ring-brand-500"
            />
          </div>

          <div className="space-y-1">
            <label className="text-[11px] font-semibold text-slate-700 dark:text-slate-300">
              Company Name <span className="text-rose-500">*</span>
            </label>
            <input
              type="text"
              required
              placeholder="e.g. Stripe, Linear, Acme Corp"
              value={formData.company_name}
              onChange={(e) => setFormData({ ...formData, company_name: e.target.value })}
              className="w-full px-3 py-2 text-xs rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900 text-slate-900 dark:text-white focus:ring-1 focus:ring-brand-500"
            />
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          <div className="space-y-1">
            <label className="text-[11px] font-semibold text-slate-700 dark:text-slate-300">
              Location
            </label>
            <input
              type="text"
              placeholder="e.g. Remote, Seattle, WA"
              value={formData.location}
              onChange={(e) => setFormData({ ...formData, location: e.target.value })}
              className="w-full px-3 py-2 text-xs rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900 text-slate-900 dark:text-white"
            />
          </div>

          <div className="space-y-1">
            <label className="text-[11px] font-semibold text-slate-700 dark:text-slate-300">
              Workplace Type
            </label>
            <select
              value={formData.remote_type}
              onChange={(e) => setFormData({ ...formData, remote_type: e.target.value })}
              className="w-full px-3 py-2 text-xs rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900 text-slate-900 dark:text-white"
            >
              <option value="remote">Remote</option>
              <option value="hybrid">Hybrid</option>
              <option value="onsite">On-Site</option>
            </select>
          </div>

          <div className="space-y-1">
            <label className="text-[11px] font-semibold text-slate-700 dark:text-slate-300">
              Seniority Level
            </label>
            <select
              value={formData.experience_level}
              onChange={(e) => setFormData({ ...formData, experience_level: e.target.value })}
              className="w-full px-3 py-2 text-xs rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900 text-slate-900 dark:text-white"
            >
              <option value="entry_level">Entry Level</option>
              <option value="junior">Junior</option>
              <option value="mid">Mid Level</option>
              <option value="internship">Internship</option>
            </select>
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          <div className="space-y-1">
            <label className="text-[11px] font-semibold text-slate-700 dark:text-slate-300">
              Benchmark Target Role
            </label>
            <select
              value={formData.role_id || ''}
              onChange={(e) => setFormData({ ...formData, role_id: e.target.value })}
              className="w-full px-3 py-2 text-xs rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900 text-slate-900 dark:text-white"
            >
              {CANONICAL_ROLES.map((r) => (
                <option key={r.id} value={r.id}>
                  {r.label}
                </option>
              ))}
            </select>
          </div>

          <div className="space-y-1">
            <label className="text-[11px] font-semibold text-slate-700 dark:text-slate-300">
              Min Annual Salary ($)
            </label>
            <input
              type="number"
              placeholder="e.g. 100000"
              value={formData.min_salary || ''}
              onChange={(e) =>
                setFormData({
                  ...formData,
                  min_salary: e.target.value ? Number(e.target.value) : undefined,
                })
              }
              className="w-full px-3 py-2 text-xs rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900 text-slate-900 dark:text-white"
            />
          </div>

          <div className="space-y-1">
            <label className="text-[11px] font-semibold text-slate-700 dark:text-slate-300">
              Max Annual Salary ($)
            </label>
            <input
              type="number"
              placeholder="e.g. 130000"
              value={formData.max_salary || ''}
              onChange={(e) =>
                setFormData({
                  ...formData,
                  max_salary: e.target.value ? Number(e.target.value) : undefined,
                })
              }
              className="w-full px-3 py-2 text-xs rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900 text-slate-900 dark:text-white"
            />
          </div>
        </div>

        <div className="space-y-1">
          <label className="text-[11px] font-semibold text-slate-700 dark:text-slate-300">
            Original Application or Careers Page URL
          </label>
          <input
            type="url"
            placeholder="https://company.com/jobs/role-123"
            value={formData.application_url || ''}
            onChange={(e) => setFormData({ ...formData, application_url: e.target.value })}
            className="w-full px-3 py-2 text-xs rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900 text-slate-900 dark:text-white"
          />
        </div>

        <div className="space-y-1">
          <label className="text-[11px] font-semibold text-slate-700 dark:text-slate-300 flex items-center justify-between">
            <span>Job Description Content <span className="text-rose-500">*</span></span>
            <span className="text-[10px] text-slate-400">Min 20 characters</span>
          </label>
          <textarea
            required
            rows={7}
            placeholder="Paste full job description including responsibilities, requirements, and qualifications here..."
            value={formData.description_text}
            onChange={(e) => setFormData({ ...formData, description_text: e.target.value })}
            className="w-full px-3 py-2 text-xs font-mono rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900 text-slate-900 dark:text-white focus:ring-1 focus:ring-brand-500"
          />
        </div>
      </form>
    </Modal>
  );
}
