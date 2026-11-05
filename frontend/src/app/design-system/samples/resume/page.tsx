import { Check, Download, X } from 'lucide-react';
import { AIThinking, AppWindow, GlassButton, GlassPanel, PageHeader, StatusChip } from '@/components/glass';

const changes = [
  {
    section: 'Experience · Payments API', state: 'accepted' as const,
    from: 'Worked on backend services for payments.',
    to: 'Built a payments reconciliation API in Python and FastAPI handling 40k transactions a day.',
  },
  {
    section: 'Experience · Data pipeline', state: 'pending' as const,
    from: 'Helped move reports to a new database.',
    to: 'Moved 120 daily reports from MySQL to PostgreSQL, cutting report time from 9 minutes to 40 seconds.',
  },
  {
    section: 'Skills', state: 'pending' as const,
    from: 'Python, SQL, Git',
    to: 'Python, FastAPI, PostgreSQL, Docker, REST API design, Git',
  },
];

const versions = [
  { name: 'Razorpay · Backend Engineer', note: 'Version 2 · today', current: true },
  { name: 'Zerodha · Platform Engineer', note: 'Version 1 · 3 Nov', current: false },
  { name: 'Master resume', note: 'Uploaded 28 Oct', current: false },
];

export default function ResumeSample() {
  return (
    <div className="flex flex-col gap-6">
      <PageHeader
        title="Resume optimizer"
        description="Every change is shown before it is saved. Nothing is invented: each line comes from your profile."
        actions={<GlassButton variant="glass"><Download className="h-4 w-4" aria-hidden />Download PDF</GlassButton>}
      />

      <div className="grid gap-4 lg:grid-cols-[1fr_300px]">
        <AppWindow title="Tailoring · Backend Engineer at Razorpay">
          <div className="flex flex-col gap-4 p-4 sm:p-6">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <p className="text-sm text-ink-muted">3 changes suggested · 1 accepted</p>
              <GlassButton variant="lime" size="sm">Accept all</GlassButton>
            </div>
            {changes.map((c) => (
              <div key={c.section} className="overflow-hidden rounded-2xl border border-ink-line bg-black/35 text-sm">
                <div className="flex flex-wrap items-center justify-between gap-2 border-b border-ink-line px-4 py-3">
                  <span className="font-medium">{c.section}</span>
                  {c.state === 'accepted' ? (
                    <StatusChip tone="done">Accepted</StatusChip>
                  ) : (
                    <span className="flex gap-2">
                      <button type="button" aria-label={`Reject change in ${c.section}`} className="grid h-9 w-9 place-items-center rounded-full border border-white/10 text-ink-muted transition-colors hover:border-crimson/50 hover:text-crimson-soft"><X className="h-4 w-4" aria-hidden /></button>
                      <button type="button" aria-label={`Accept change in ${c.section}`} className="grid h-9 w-9 place-items-center rounded-full bg-lime text-lime-ink transition-transform hover:-translate-y-0.5 active:scale-95"><Check className="h-4 w-4" aria-hidden /></button>
                    </span>
                  )}
                </div>
                <p className="bg-crimson/10 px-4 py-3 text-crimson-tint"><span aria-hidden>− </span><span className="sr-only">Removed: </span>{c.from}</p>
                <p className="bg-lime/[0.07] px-4 py-3 text-lime-soft"><span aria-hidden>+ </span><span className="sr-only">Added: </span>{c.to}</p>
              </div>
            ))}
            <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-4">
              <AIThinking label="Checking the summary against the job description" hint="Usually 10–20 seconds" />
            </div>
          </div>
        </AppWindow>

        <div className="flex flex-col gap-4">
          <GlassPanel className="p-5">
            <p className="text-xs text-ink-dim">Match after changes</p>
            <p className="mt-1 font-display text-5xl font-semibold tabular-nums tracking-[-0.04em] text-lime">91%</p>
            <p className="mt-1 text-sm text-ink-muted">Up from 74% with your master resume.</p>
          </GlassPanel>
          <GlassPanel className="p-2">
            <h2 className="px-3 pb-1 pt-3 font-display text-base font-semibold tracking-[-0.02em]">Versions</h2>
            <ul>
              {versions.map((v) => (
                <li key={v.name}>
                  <a href="#" aria-current={v.current ? 'true' : undefined} className={`block rounded-xl px-3 py-3 transition-colors hover:bg-white/[0.04] ${v.current ? 'bg-lav/[0.12]' : ''}`}>
                    <span className="block truncate text-sm">{v.name}</span>
                    <span className="block text-xs text-ink-dim">{v.note}</span>
                  </a>
                </li>
              ))}
            </ul>
          </GlassPanel>
        </div>
      </div>
    </div>
  );
}
