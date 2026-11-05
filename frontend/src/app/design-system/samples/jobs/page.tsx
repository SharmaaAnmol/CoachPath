import { Building2, Check, MapPin, X } from 'lucide-react';
import { GlassButton, GlassPanel, PageHeader, StatusChip } from '@/components/glass';
import { cn } from '@/lib/utils';

const jobs = [
  { role: 'Backend Engineer', company: 'Razorpay', place: 'Bengaluru · Hybrid', pay: '₹28–36 LPA', fit: 91, have: ['Python', 'FastAPI', 'PostgreSQL'], gap: ['Kafka'] },
  { role: 'Platform Engineer', company: 'Zerodha', place: 'Remote, India', pay: '₹24–32 LPA', fit: 86, have: ['Python', 'Docker', 'Linux'], gap: ['Kubernetes'] },
  { role: 'Software Engineer II', company: 'Swiggy', place: 'Bengaluru · Onsite', pay: '₹30–40 LPA', fit: 79, have: ['Python', 'REST APIs'], gap: ['Redis', 'System design'] },
  { role: 'Backend Developer', company: 'Groww', place: 'Bengaluru · Hybrid', pay: '₹22–30 LPA', fit: 74, have: ['PostgreSQL', 'FastAPI'], gap: ['Go', 'Kafka'] },
];
const filters = ['All 18', 'Above 85%', 'Remote', 'Bengaluru', 'Saved'];

export default function JobsSample() {
  const top = jobs[0];
  return (
    <div className="flex flex-col gap-6">
      <PageHeader
        title="Job matches"
        description="Ranked by how well your verified skills cover each job. Updated 2 hours ago from 6 job boards."
        actions={<GlassButton variant="glass">Import a job link</GlassButton>}
      />

      <div className="flex flex-wrap gap-2" role="group" aria-label="Filters">
        {filters.map((f, i) => (
          <button key={f} type="button" aria-pressed={i === 0}
            className={cn('h-9 rounded-full border px-4 text-sm transition-colors duration-200',
              i === 0 ? 'border-lav/50 bg-lav/15 text-ink-fg' : 'border-white/10 text-ink-muted hover:border-white/20 hover:text-ink-fg')}>
            {f}
          </button>
        ))}
      </div>

      <div className="grid gap-4 lg:grid-cols-[1fr_380px]">
        <ul className="flex flex-col gap-3">
          {jobs.map((j, i) => (
            <li key={j.company}>
              <GlassPanel interactive className={cn('p-5', i === 0 && 'shadow-[inset_0_0_0_1px_rgba(196,181,253,.35)]')}>
                <div className="flex items-start gap-4">
                  <span className="grid h-11 w-11 shrink-0 place-items-center rounded-xl border border-white/10 bg-white/5"><Building2 className="h-4 w-4 text-ink-muted" aria-hidden /></span>
                  <div className="min-w-0 flex-1">
                    <h2 className="font-display text-lg font-semibold tracking-[-0.02em]">{j.role}</h2>
                    <p className="text-sm text-ink-muted">{j.company} · {j.pay}</p>
                    <p className="mt-0.5 flex items-center gap-1 text-sm text-ink-dim"><MapPin className="h-3.5 w-3.5" aria-hidden />{j.place}</p>
                  </div>
                  <div className="text-right">
                    <p className={cn('font-display text-2xl font-semibold tabular-nums', j.fit >= 85 ? 'text-lime' : 'text-lav')}>{j.fit}%</p>
                    <p className="text-xs text-ink-dim">fit</p>
                  </div>
                </div>
                <div className="mt-4 flex flex-wrap gap-2">
                  {j.have.map((s) => <StatusChip key={s} tone="done">{s}</StatusChip>)}
                  {j.gap.map((s) => <StatusChip key={s} tone="alert">{s} · gap</StatusChip>)}
                </div>
              </GlassPanel>
            </li>
          ))}
        </ul>

        {/* Why this match: evidence for the selected job */}
        <GlassPanel className="h-fit p-6 lg:sticky lg:top-10">
          <StatusChip tone="active">Selected</StatusChip>
          <h2 className="mt-3 font-display text-xl font-semibold tracking-[-0.02em]">{top.role} · {top.company}</h2>
          <p className="mt-1 text-sm text-ink-muted">You cover 11 of the 12 skills this job asks for.</p>
          <ul className="mt-5 flex flex-col gap-2.5 text-sm">
            {['Python, 4 years · verified', 'FastAPI · verified by test', 'PostgreSQL · on resume', 'REST API design · verified'].map((e) => (
              <li key={e} className="flex items-start gap-2.5"><Check className="mt-0.5 h-4 w-4 shrink-0 text-lime" aria-hidden />{e}</li>
            ))}
            <li className="flex items-start gap-2.5 text-crimson-soft"><X className="mt-0.5 h-4 w-4 shrink-0" aria-hidden />Kafka · not shown yet</li>
          </ul>
          <div className="mt-6 flex flex-col gap-2">
            <GlassButton href="/design-system/samples/resume">Tailor my resume for this job</GlassButton>
            <GlassButton variant="ghost">Save for later</GlassButton>
          </div>
        </GlassPanel>
      </div>
    </div>
  );
}
