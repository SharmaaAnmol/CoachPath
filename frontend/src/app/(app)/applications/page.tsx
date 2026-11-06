'use client';

import * as React from 'react';
import Link from 'next/link';
import { useSearchParams } from 'next/navigation';
import { AlertCircle, Check, ExternalLink, FileText, Send } from 'lucide-react';
import { AIThinking, GlassButton, GlassEmptyState, GlassPanel, PageHeader, StatusChip } from '@/components/glass';
import type { ChipTone } from '@/components/glass/status-chip';
import { applicationClient, type ApplicationPackage, type PackageHandoff, type PackageStatus } from '@/lib/application-client';
import { resumeClient } from '@/lib/resume-client';
import { ApiClientError } from '@/lib/api-client';
import { cn } from '@/lib/utils';

const STATUS: Record<PackageStatus, { label: string; tone: ChipTone }> = {
  draft: { label: 'Draft', tone: 'neutral' },
  approved: { label: 'Approved', tone: 'active' },
  handoff_initiated: { label: 'Opened on company site', tone: 'active' },
  submitted: { label: 'Submitted', tone: 'done' },
};
const STEPS: PackageStatus[] = ['draft', 'approved', 'handoff_initiated', 'submitted'];

const errorText = (e: unknown) => (e instanceof ApiClientError ? e.message : 'Something went wrong. Please try again.');
const field =
  'w-full rounded-2xl border border-white/10 bg-black/40 px-4 py-3 text-sm leading-relaxed text-ink-fg placeholder:text-ink-dim focus:border-lav/60 focus:outline-none disabled:opacity-60';

interface TailoredOption {
  id: string;
  target_job_id: string;
  label: string;
}

function ApplicationsInner() {
  const params = useSearchParams();
  const [packages, setPackages] = React.useState<ApplicationPackage[]>([]);
  const [versions, setVersions] = React.useState<TailoredOption[]>([]);
  const [selectedId, setSelectedId] = React.useState<string | null>(null);
  const [versionId, setVersionId] = React.useState('');
  const [loading, setLoading] = React.useState(true);
  const [preparing, setPreparing] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);

  React.useEffect(() => {
    Promise.all([
      applicationClient.listPackages().catch((e) => { setError(errorText(e)); return { packages: [] as ApplicationPackage[] }; }),
      resumeClient.listTailoredVersions({ page_size: 50 }).catch(() => null),
    ]).then(([pk, vs]) => {
      setPackages(pk.packages);
      setSelectedId(pk.packages[0]?.id ?? null);
      const items = ((vs as { items?: unknown[] } | null)?.items ?? []) as Array<{
        id: string; target_job_id: string; job_title?: string | null; company_name?: string | null; status: string; version_number?: number;
      }>;
      const opts = items.map((v) => ({
        id: v.id,
        target_job_id: v.target_job_id,
        label: `${v.job_title || 'Untitled job'}${v.company_name ? ` · ${v.company_name}` : ''} · ${v.status === 'approved' ? 'approved resume' : 'draft resume'}`,
      }));
      setVersions(opts);
      const wanted = params.get('job');
      setVersionId((wanted && opts.find((o) => o.target_job_id === wanted)?.id) || opts[0]?.id || '');
      setLoading(false);
    });
  }, [params]);

  const replace = (p: ApplicationPackage) => setPackages((list) => list.map((x) => (x.id === p.id ? p : x)));

  const prepare = async () => {
    const v = versions.find((o) => o.id === versionId);
    if (!v) return;
    setPreparing(true);
    setError(null);
    try {
      const p = await applicationClient.preparePackage({ job_id: v.target_job_id, tailored_resume_version_id: v.id });
      setPackages((list) => [p, ...list.filter((x) => x.id !== p.id)]);
      setSelectedId(p.id);
    } catch (e) {
      setError(errorText(e));
    } finally {
      setPreparing(false);
    }
  };

  const selected = packages.find((p) => p.id === selectedId) ?? null;

  return (
    <div className="flex flex-col gap-6 pb-10">
      <PageHeader
        title="Applications"
        description="Prepare each application from a tailored resume, review every answer, then submit it yourself on the company's site. CoachPath never submits for you."
      />

      {error && (
        <div role="alert" className="flex items-start gap-3 rounded-2xl border border-crimson/30 bg-crimson/10 px-4 py-3 text-sm text-crimson-tint">
          <AlertCircle className="mt-0.5 h-4 w-4 shrink-0" />
          {error}
        </div>
      )}

      {/* Prepare */}
      {!loading && versions.length === 0 ? (
        <GlassEmptyState
          icon={<FileText className="h-5 w-5" />}
          title="Tailor your resume for a job first"
          description="An application is built from a resume you tailored for that job, so every answer comes from your own verified experience."
          action={<GlassButton href="/resume">Open resume optimizer</GlassButton>}
        />
      ) : (
        <GlassPanel className="flex flex-col gap-4 p-5 sm:p-6">
          <div>
            <h2 className="font-display text-lg font-semibold tracking-[-0.02em]">Prepare a new application</h2>
            <p className="mt-1 text-sm text-ink-muted">Pick a job you tailored your resume for. The AI drafts a cover note and answers; you review them before anything is used.</p>
          </div>
          <div className="flex flex-col gap-3 sm:flex-row">
            <label className="sr-only" htmlFor="version">Tailored resume</label>
            <select id="version" value={versionId} onChange={(e) => setVersionId(e.target.value)} disabled={loading || preparing} className={cn(field, 'h-11 py-0 sm:flex-1')}>
              {versions.map((v) => (
                <option key={v.id} value={v.id} className="bg-ink-900">{v.label}</option>
              ))}
            </select>
            <GlassButton onClick={prepare} isLoading={preparing} disabled={!versionId || loading}>
              Prepare application
            </GlassButton>
          </div>
          {preparing && <AIThinking label="Drafting your cover note and answers" hint="Usually 10–20 seconds" />}
        </GlassPanel>
      )}

      {/* List + detail */}
      {!loading && packages.length > 0 && (
        <div className="grid gap-4 lg:grid-cols-[320px_1fr]">
          <GlassPanel className="h-fit p-2">
            <h2 className="px-3 pb-1 pt-3 font-display text-base font-semibold tracking-[-0.02em]">Your applications</h2>
            <ul>
              {packages.map((p) => (
                <li key={p.id}>
                  <button
                    type="button"
                    onClick={() => setSelectedId(p.id)}
                    aria-current={p.id === selectedId ? 'true' : undefined}
                    className={cn('w-full rounded-xl px-3 py-3 text-left transition-colors hover:bg-white/[0.04]', p.id === selectedId && 'bg-lav/[0.12]')}
                  >
                    <span className="block truncate text-sm text-ink-fg">{p.job_title || 'Untitled job'}</span>
                    <span className="mt-0.5 flex items-center justify-between gap-2 text-xs text-ink-dim">
                      <span className="truncate">{p.company_name || '—'}</span>
                      <span className={p.status === 'submitted' ? 'text-lime' : 'text-ink-muted'}>{STATUS[p.status]?.label ?? p.status}</span>
                    </span>
                  </button>
                </li>
              ))}
            </ul>
          </GlassPanel>
          {selected && <PackageDetail key={selected.id} pkg={selected} onChange={replace} onError={setError} />}
        </div>
      )}

      {loading && <AIThinking label="Loading your applications" />}
    </div>
  );
}

function PackageDetail({ pkg, onChange, onError }: { pkg: ApplicationPackage; onChange: (p: ApplicationPackage) => void; onError: (m: string | null) => void }) {
  const [cover, setCover] = React.useState(pkg.cover_note);
  const [answers, setAnswers] = React.useState(pkg.application_questions.map((q) => q.answer));
  const [confirmed, setConfirmed] = React.useState(false);
  const [busy, setBusy] = React.useState<string | null>(null);
  const [handoff, setHandoff] = React.useState<PackageHandoff | null>(null);

  const locked = pkg.status === 'submitted';
  const dirty = cover !== pkg.cover_note || answers.some((a, i) => a !== pkg.application_questions[i]?.answer);
  const step = STEPS.indexOf(pkg.status);

  const run = async (name: string, fn: () => Promise<void>) => {
    setBusy(name);
    onError(null);
    try {
      await fn();
    } catch (e) {
      onError(errorText(e));
    } finally {
      setBusy(null);
    }
  };

  const save = () =>
    run('save', async () => {
      const p = await applicationClient.updatePackage(pkg.id, {
        cover_note: cover,
        application_questions: pkg.application_questions.map((q, i) => ({ ...q, answer: answers[i] })),
      });
      onChange(p);
      setConfirmed(false);
    });

  return (
    <GlassPanel className="flex flex-col gap-6 p-5 sm:p-7">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div className="min-w-0">
          <h2 className="font-display text-xl font-semibold tracking-[-0.02em]">{pkg.job_title || 'Untitled job'}</h2>
          <p className="text-sm text-ink-muted">{pkg.company_name || 'Company not listed'}</p>
        </div>
        <StatusChip tone={STATUS[pkg.status]?.tone ?? 'neutral'}>{STATUS[pkg.status]?.label ?? pkg.status}</StatusChip>
      </div>

      {/* Progress */}
      <ol className="grid grid-cols-4 gap-2 text-xs" aria-label="Application progress">
        {['Review', 'Approve', 'Open site', 'Submitted'].map((label, i) => (
          <li key={label} className="flex flex-col gap-1.5">
            <span className={cn('h-1 rounded-full', i <= step ? (i === 3 ? 'bg-lime' : 'bg-lav') : 'bg-white/10')} />
            <span className={i <= step ? 'text-ink-fg' : 'text-ink-dim'}>{label}{i <= step ? <span className="sr-only"> (done)</span> : null}</span>
          </li>
        ))}
      </ol>

      <div className="flex flex-col gap-2">
        <label htmlFor={`cover-${pkg.id}`} className="text-sm font-medium">Cover note</label>
        <textarea id={`cover-${pkg.id}`} value={cover} onChange={(e) => setCover(e.target.value)} disabled={locked} rows={7} className={field} />
      </div>

      {pkg.application_questions.length > 0 && (
        <div className="flex flex-col gap-4">
          <h3 className="text-sm font-medium">Application answers</h3>
          {pkg.application_questions.map((q, i) => {
            const unclear = q.needs_clarification || q.requires_clarification;
            return (
              <div key={q.id || i} className="flex flex-col gap-2 rounded-2xl border border-white/10 bg-white/[0.02] p-4">
                <label htmlFor={`q-${pkg.id}-${i}`} className="text-sm text-ink-fg">{q.question}</label>
                <textarea
                  id={`q-${pkg.id}-${i}`}
                  value={answers[i]}
                  onChange={(e) => setAnswers((a) => a.map((x, j) => (j === i ? e.target.value : x)))}
                  disabled={locked}
                  rows={4}
                  className={field}
                />
                {unclear && (
                  <p className="text-sm text-crimson-soft">
                    Needs your input{q.clarification_prompt ? `: ${q.clarification_prompt}` : '. The AI could not find evidence for this in your profile.'}
                  </p>
                )}
                {!!q.evidence_citations?.length && (
                  <p className="text-xs text-ink-dim">Based on: {q.evidence_citations.join(' · ')}</p>
                )}
              </div>
            );
          })}
        </div>
      )}

      {/* Actions by stage */}
      <div className="flex flex-col gap-4 border-t border-white/10 pt-5">
        {dirty && !locked && (
          <div className="flex flex-wrap items-center gap-3">
            <GlassButton variant="glass" onClick={save} isLoading={busy === 'save'}>Save changes</GlassButton>
            <span className="text-sm text-ink-dim">Saving resets approval, so you review the new version.</span>
          </div>
        )}

        {!dirty && pkg.status === 'draft' && (
          <>
            <label className="flex items-start gap-3 text-sm">
              <input type="checkbox" checked={confirmed} onChange={(e) => setConfirmed(e.target.checked)} className="mt-0.5 h-4 w-4 accent-[#C4B5FD]" />
              I read the cover note and every answer, and they are accurate.
            </label>
            <GlassButton className="w-fit" disabled={!confirmed} isLoading={busy === 'approve'} onClick={() => run('approve', async () => onChange(await applicationClient.approvePackage(pkg.id)))}>
              <Check className="h-4 w-4" /> Approve application
            </GlassButton>
          </>
        )}

        {!dirty && pkg.status === 'approved' && (
          <GlassButton
            className="w-fit"
            isLoading={busy === 'handoff'}
            onClick={() =>
              run('handoff', async () => {
                const h = await applicationClient.handoffPackage(pkg.id);
                setHandoff(h);
                onChange({ ...pkg, status: h.status, application_url: h.application_url ?? pkg.application_url });
              })
            }
          >
            <ExternalLink className="h-4 w-4" /> Get ready to submit
          </GlassButton>
        )}

        {pkg.status === 'handoff_initiated' && (
          <>
            <p className="text-sm text-ink-muted">
              {handoff?.instructions || 'Paste your cover note and answers into the company application form, submit it there, then confirm below.'}
            </p>
            {(handoff?.application_url || pkg.application_url) && (
              <a href={(handoff?.application_url || pkg.application_url) as string} target="_blank" rel="noopener noreferrer" className="inline-flex w-fit items-center gap-2 text-sm text-lav underline-offset-4 hover:underline">
                Open the company application <ExternalLink className="h-3.5 w-3.5" />
              </a>
            )}
            <label className="flex items-start gap-3 text-sm">
              <input type="checkbox" checked={confirmed} onChange={(e) => setConfirmed(e.target.checked)} className="mt-0.5 h-4 w-4 accent-[#C6F432]" />
              I submitted this application on the company&apos;s site.
            </label>
            <GlassButton variant="lime" className="w-fit" disabled={!confirmed} isLoading={busy === 'submit'} onClick={() => run('submit', async () => onChange(await applicationClient.confirmSubmission(pkg.id)))}>
              <Check className="h-4 w-4" /> Mark as submitted
            </GlassButton>
          </>
        )}

        {pkg.status === 'submitted' && (
          <p className="flex items-center gap-2 text-sm text-lime">
            <Check className="h-4 w-4" /> Submitted{pkg.submitted_at ? ` on ${new Date(pkg.submitted_at).toLocaleDateString()}` : ''}.
          </p>
        )}

        <Link href={`/recruiters?package=${pkg.id}`} className="inline-flex w-fit items-center gap-2 text-sm text-ink-muted transition-colors hover:text-ink-fg">
          <Send className="h-4 w-4" /> Write a message to a recruiter for this job
        </Link>
      </div>
    </GlassPanel>
  );
}

export default function ApplicationsPage() {
  return (
    <React.Suspense fallback={<AIThinking label="Loading your applications" />}>
      <ApplicationsInner />
    </React.Suspense>
  );
}
