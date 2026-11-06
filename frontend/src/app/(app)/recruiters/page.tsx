'use client';

import * as React from 'react';
import { useSearchParams } from 'next/navigation';
import { AlertCircle, Check, Copy, ExternalLink, Mail, MessageSquare, Trash2, X } from 'lucide-react';
import { AIThinking, GlassButton, GlassEmptyState, GlassPanel, PageHeader, StatusChip } from '@/components/glass';
import type { ChipTone } from '@/components/glass/status-chip';
import {
  applicationClient,
  outreachClient,
  type ApplicationPackage,
  type OutreachDraft,
  type OutreachHandoff,
  type OutreachStatus,
} from '@/lib/application-client';
import { ApiClientError } from '@/lib/api-client';
import { cn } from '@/lib/utils';

const MAX_WORDS = 90; // same cap the backend enforces
const STATUS: Record<OutreachStatus, { label: string; tone: ChipTone }> = {
  draft: { label: 'Draft', tone: 'neutral' },
  awaiting_approval: { label: 'Edited, needs approval', tone: 'neutral' },
  approved: { label: 'Approved', tone: 'active' },
  handoff_initiated: { label: 'Ready to send', tone: 'active' },
  sent: { label: 'Sent by you', tone: 'done' },
  cancelled: { label: 'Cancelled', tone: 'alert' },
};

const errorText = (e: unknown) => (e instanceof ApiClientError ? e.message : 'Something went wrong. Please try again.');
const countWords = (s: string) => s.trim().split(/\s+/).filter(Boolean).length;
const field =
  'w-full rounded-2xl border border-white/10 bg-black/40 px-4 py-3 text-sm leading-relaxed text-ink-fg placeholder:text-ink-dim focus:border-lav/60 focus:outline-none disabled:opacity-60';

function RecruitersInner() {
  const params = useSearchParams();
  const [drafts, setDrafts] = React.useState<OutreachDraft[]>([]);
  const [packages, setPackages] = React.useState<ApplicationPackage[]>([]);
  const [selectedId, setSelectedId] = React.useState<string | null>(null);
  const [loading, setLoading] = React.useState(true);
  const [creating, setCreating] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);
  const [form, setForm] = React.useState({ packageId: '', channel: 'recruiter_inmail', name: '', role: '', profile: '', contact: '' });

  React.useEffect(() => {
    Promise.all([
      outreachClient.list().catch((e) => { setError(errorText(e)); return { drafts: [] as OutreachDraft[] }; }),
      applicationClient.listPackages().catch(() => ({ packages: [] as ApplicationPackage[] })),
    ]).then(([d, p]) => {
      setDrafts(d.drafts);
      setSelectedId(d.drafts[0]?.id ?? null);
      setPackages(p.packages);
      const wanted = params.get('package');
      setForm((f) => ({ ...f, packageId: (wanted && p.packages.some((x) => x.id === wanted) ? wanted : p.packages[0]?.id) || '' }));
      setLoading(false);
    });
  }, [params]);

  const replace = (d: OutreachDraft) => setDrafts((list) => list.map((x) => (x.id === d.id ? d : x)));

  const create = async () => {
    const pkg = packages.find((p) => p.id === form.packageId);
    if (!pkg) return;
    setCreating(true);
    setError(null);
    try {
      const d = await outreachClient.create({
        job_id: pkg.job_id,
        application_package_id: pkg.id,
        outreach_channel: form.channel,
        recruiter_name: form.name || undefined,
        recruiter_role_type: form.role || undefined,
        recruiter_profile_url: form.profile || undefined,
        recruiter_contact_info: form.contact || undefined,
      });
      setDrafts((list) => [d, ...list]);
      setSelectedId(d.id);
    } catch (e) {
      setError(errorText(e));
    } finally {
      setCreating(false);
    }
  };

  const selected = drafts.find((d) => d.id === selectedId) ?? null;
  const set = (k: keyof typeof form) => (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => setForm((f) => ({ ...f, [k]: e.target.value }));

  return (
    <div className="flex flex-col gap-6 pb-10">
      <PageHeader
        title="Recruiter outreach"
        description="Short messages grounded in your verified work. CoachPath never sends anything: you copy the message, send it yourself, then mark it sent."
      />

      {error && (
        <div role="alert" className="flex items-start gap-3 rounded-2xl border border-crimson/30 bg-crimson/10 px-4 py-3 text-sm text-crimson-tint">
          <AlertCircle className="mt-0.5 h-4 w-4 shrink-0" />
          {error}
        </div>
      )}

      {!loading && packages.length === 0 ? (
        <GlassEmptyState
          icon={<MessageSquare className="h-5 w-5" />}
          title="Prepare an application first"
          description="Outreach messages are written for a specific job, using the application you prepared for it."
          action={<GlassButton href="/applications">Go to applications</GlassButton>}
        />
      ) : (
        <GlassPanel className="flex flex-col gap-4 p-5 sm:p-6">
          <div>
            <h2 className="font-display text-lg font-semibold tracking-[-0.02em]">Write a new message</h2>
            <p className="mt-1 text-sm text-ink-muted">Recruiter details are optional. Add a name if you know who you are writing to.</p>
          </div>
          <div className="grid gap-3 sm:grid-cols-2">
            <label className="flex flex-col gap-1.5 text-sm sm:col-span-2">
              Job
              <select value={form.packageId} onChange={set('packageId')} disabled={loading || creating} className={cn(field, 'h-11 py-0')}>
                {packages.map((p) => (
                  <option key={p.id} value={p.id} className="bg-ink-900">{p.job_title || 'Untitled job'}{p.company_name ? ` · ${p.company_name}` : ''}</option>
                ))}
              </select>
            </label>
            <label className="flex flex-col gap-1.5 text-sm">
              Send it as
              <select value={form.channel} onChange={set('channel')} className={cn(field, 'h-11 py-0')}>
                <option value="recruiter_inmail" className="bg-ink-900">LinkedIn message</option>
                <option value="email" className="bg-ink-900">Email</option>
              </select>
            </label>
            <label className="flex flex-col gap-1.5 text-sm">
              Recruiter name
              <input value={form.name} onChange={set('name')} placeholder="e.g. Priya Nair" className={cn(field, 'h-11 py-0')} />
            </label>
            <label className="flex flex-col gap-1.5 text-sm">
              Their role
              <input value={form.role} onChange={set('role')} placeholder="e.g. Technical recruiter" className={cn(field, 'h-11 py-0')} />
            </label>
            <label className="flex flex-col gap-1.5 text-sm">
              {form.channel === 'email' ? 'Their email' : 'Their profile link'}
              {form.channel === 'email' ? (
                <input type="email" value={form.contact} onChange={set('contact')} placeholder="name@company.com" className={cn(field, 'h-11 py-0')} />
              ) : (
                <input type="url" value={form.profile} onChange={set('profile')} placeholder="https://linkedin.com/in/…" className={cn(field, 'h-11 py-0')} />
              )}
            </label>
          </div>
          <GlassButton className="w-fit" onClick={create} isLoading={creating} disabled={!form.packageId || loading}>
            Write message
          </GlassButton>
          {creating && <AIThinking label="Writing a short message from your verified work" hint="Usually 5–15 seconds" />}
        </GlassPanel>
      )}

      {!loading && drafts.length > 0 && (
        <div className="grid gap-4 lg:grid-cols-[320px_1fr]">
          <GlassPanel className="h-fit p-2">
            <h2 className="px-3 pb-1 pt-3 font-display text-base font-semibold tracking-[-0.02em]">Your messages</h2>
            <ul>
              {drafts.map((d) => (
                <li key={d.id}>
                  <button
                    type="button"
                    onClick={() => setSelectedId(d.id)}
                    aria-current={d.id === selectedId ? 'true' : undefined}
                    className={cn('w-full rounded-xl px-3 py-3 text-left transition-colors hover:bg-white/[0.04]', d.id === selectedId && 'bg-lav/[0.12]')}
                  >
                    <span className="block truncate text-sm text-ink-fg">{d.recruiter_name || d.company_name || 'Recruiter'}</span>
                    <span className="mt-0.5 flex items-center justify-between gap-2 text-xs text-ink-dim">
                      <span className="truncate">{d.job_title || '—'}</span>
                      <span className={d.status === 'sent' ? 'text-lime' : 'text-ink-muted'}>{STATUS[d.status]?.label ?? d.status}</span>
                    </span>
                  </button>
                </li>
              ))}
            </ul>
          </GlassPanel>
          {selected && (
            <DraftDetail
              key={selected.id}
              draft={selected}
              onChange={replace}
              onRemove={(id) => {
                setDrafts((list) => list.filter((x) => x.id !== id));
                setSelectedId(null);
              }}
              onError={setError}
            />
          )}
        </div>
      )}

      {loading && <AIThinking label="Loading your messages" />}
    </div>
  );
}

function DraftDetail({
  draft,
  onChange,
  onRemove,
  onError,
}: {
  draft: OutreachDraft;
  onChange: (d: OutreachDraft) => void;
  onRemove: (id: string) => void;
  onError: (m: string | null) => void;
}) {
  const [subject, setSubject] = React.useState(draft.subject_line);
  const [body, setBody] = React.useState(draft.message_body);
  const [confirmed, setConfirmed] = React.useState(false);
  const [busy, setBusy] = React.useState<string | null>(null);
  const [handoff, setHandoff] = React.useState<OutreachHandoff | null>(null);
  const [copied, setCopied] = React.useState(false);
  const [confirmDelete, setConfirmDelete] = React.useState(false);

  const words = countWords(body);
  const tooLong = words > MAX_WORDS;
  const closed = draft.status === 'sent' || draft.status === 'cancelled';
  const dirty = subject !== draft.subject_line || body !== draft.message_body;
  const needsApproval = draft.status === 'draft' || draft.status === 'awaiting_approval';

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

  const copyText = handoff?.clipboard_text || handoff?.copy_text || `${draft.subject_line}\n\n${draft.message_body}`;
  const mailto = handoff?.mailto_uri || handoff?.mailto_url;
  const profile = handoff?.recruiter_profile_url || handoff?.profile_url || draft.recruiter_profile_url;

  return (
    <GlassPanel className="flex flex-col gap-5 p-5 sm:p-7">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div className="min-w-0">
          <h2 className="font-display text-xl font-semibold tracking-[-0.02em]">{draft.recruiter_name || 'Recruiter'}{draft.company_name ? ` · ${draft.company_name}` : ''}</h2>
          <p className="text-sm text-ink-muted">{[draft.recruiter_role_type, draft.job_title].filter(Boolean).join(' · ') || 'Role not set'}</p>
        </div>
        <StatusChip tone={STATUS[draft.status]?.tone ?? 'neutral'}>{STATUS[draft.status]?.label ?? draft.status}</StatusChip>
      </div>

      <label className="flex flex-col gap-1.5 text-sm font-medium">
        Subject
        <input value={subject} onChange={(e) => setSubject(e.target.value)} disabled={closed} className={cn(field, 'h-11 py-0 font-normal')} />
      </label>
      <div className="flex flex-col gap-1.5">
        <div className="flex items-baseline justify-between text-sm">
          <label htmlFor={`body-${draft.id}`} className="font-medium">Message</label>
          <span className={cn('tabular-nums', tooLong ? 'text-crimson-soft' : 'text-ink-dim')} aria-live="polite">
            {words} / {MAX_WORDS} words{tooLong ? ' (too long)' : ''}
          </span>
        </div>
        <textarea id={`body-${draft.id}`} value={body} onChange={(e) => setBody(e.target.value)} disabled={closed} rows={8} className={field} />
      </div>

      <div className="flex flex-col gap-4 border-t border-white/10 pt-5">
        {dirty && !closed && (
          <div className="flex flex-wrap items-center gap-3">
            <GlassButton
              variant="glass"
              disabled={tooLong}
              isLoading={busy === 'save'}
              onClick={() => run('save', async () => { onChange(await outreachClient.update(draft.id, { subject_line: subject, message_body: body })); setConfirmed(false); })}
            >
              Save changes
            </GlassButton>
            <span className="text-sm text-ink-dim">Saving asks you to approve the new version.</span>
          </div>
        )}

        {!dirty && needsApproval && (
          <>
            <label className="flex items-start gap-3 text-sm">
              <input type="checkbox" checked={confirmed} onChange={(e) => setConfirmed(e.target.checked)} className="mt-0.5 h-4 w-4 accent-[#C4B5FD]" />
              I read this message and everything in it is true.
            </label>
            <GlassButton className="w-fit" disabled={!confirmed} isLoading={busy === 'approve'} onClick={() => run('approve', async () => { onChange(await outreachClient.approve(draft.id)); setConfirmed(false); })}>
              <Check className="h-4 w-4" /> Approve message
            </GlassButton>
          </>
        )}

        {!dirty && (draft.status === 'approved' || draft.status === 'handoff_initiated') && (
          <>
            {!handoff ? (
              <GlassButton
                className="w-fit"
                isLoading={busy === 'handoff'}
                onClick={() => run('handoff', async () => { const h = await outreachClient.handoff(draft.id); setHandoff(h); onChange({ ...draft, status: h.status }); })}
              >
                Get ready to send
              </GlassButton>
            ) : (
              <div className="flex flex-col gap-3">
                {(handoff.handoff_instructions || handoff.instructions) && (
                  <p className="text-sm text-ink-muted">{handoff.handoff_instructions || handoff.instructions}</p>
                )}
                <div className="flex flex-wrap gap-2">
                  <GlassButton
                    variant="glass"
                    size="sm"
                    onClick={async () => {
                      try { await navigator.clipboard.writeText(copyText); setCopied(true); } catch { onError('Copy failed. Select the message and copy it by hand.'); }
                    }}
                  >
                    {copied ? <Check className="h-4 w-4" /> : <Copy className="h-4 w-4" />} {copied ? 'Copied' : 'Copy message'}
                  </GlassButton>
                  {mailto && (
                    <a href={mailto} className="inline-flex h-9 items-center gap-2 rounded-full border border-white/10 px-4 text-[13px] text-ink-fg hover:bg-white/5">
                      <Mail className="h-4 w-4" /> Open in email
                    </a>
                  )}
                  {profile && (
                    <a href={profile} target="_blank" rel="noopener noreferrer" className="inline-flex h-9 items-center gap-2 rounded-full border border-white/10 px-4 text-[13px] text-ink-fg hover:bg-white/5">
                      <ExternalLink className="h-4 w-4" /> Open their profile
                    </a>
                  )}
                </div>
              </div>
            )}
            <label className="flex items-start gap-3 text-sm">
              <input type="checkbox" checked={confirmed} onChange={(e) => setConfirmed(e.target.checked)} className="mt-0.5 h-4 w-4 accent-[#C6F432]" />
              I sent this message myself.
            </label>
            <GlassButton variant="lime" className="w-fit" disabled={!confirmed} isLoading={busy === 'sent'} onClick={() => run('sent', async () => onChange(await outreachClient.confirmSent(draft.id)))}>
              <Check className="h-4 w-4" /> Mark as sent
            </GlassButton>
          </>
        )}

        {draft.status === 'sent' && (
          <p className="flex items-center gap-2 text-sm text-lime">
            <Check className="h-4 w-4" /> Sent{draft.sent_at ? ` on ${new Date(draft.sent_at).toLocaleDateString()}` : ''}.
          </p>
        )}

        <div className="flex flex-wrap gap-2 pt-1">
          {!closed && (
            <GlassButton variant="ghost" size="sm" isLoading={busy === 'cancel'} onClick={() => run('cancel', async () => onChange(await outreachClient.cancel(draft.id)))}>
              <X className="h-4 w-4" /> Cancel message
            </GlassButton>
          )}
          {draft.status !== 'sent' &&
            (confirmDelete ? (
              <GlassButton variant="ghost" size="sm" className="text-crimson-soft" isLoading={busy === 'delete'} onClick={() => run('delete', async () => { await outreachClient.remove(draft.id); onRemove(draft.id); })}>
                <Trash2 className="h-4 w-4" /> Yes, delete it
              </GlassButton>
            ) : (
              <GlassButton variant="ghost" size="sm" onClick={() => setConfirmDelete(true)}>
                <Trash2 className="h-4 w-4" /> Delete
              </GlassButton>
            ))}
        </div>
      </div>
    </GlassPanel>
  );
}

export default function RecruitersPage() {
  return (
    <React.Suspense fallback={<AIThinking label="Loading your messages" />}>
      <RecruitersInner />
    </React.Suspense>
  );
}
