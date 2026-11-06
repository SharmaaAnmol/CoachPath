import { ArrowRight, Building2, MapPin } from 'lucide-react';
import { GlassButton, GlassPanel, PageHeader, StatusChip } from '@/components/glass';

const pillars = [
  { name: 'Skills verified', value: 82 },
  { name: 'Roadmap progress', value: 64 },
  { name: 'Resume strength', value: 88 },
  { name: 'Interview prep', value: 71 },
];

const matches = [
  { role: 'Backend Engineer', company: 'Razorpay', place: 'Bengaluru', fit: 91 },
  { role: 'Platform Engineer', company: 'Zerodha', place: 'Remote, India', fit: 86 },
  { role: 'Software Engineer II', company: 'Swiggy', place: 'Bengaluru', fit: 79 },
];

function Stat({ label, value, note }: { label: string; value: string; note: string }) {
  return (
    <GlassPanel interactive className="p-5">
      <p className="text-xs text-ink-dim">{label}</p>
      <p className="mt-2 font-display text-3xl font-semibold tabular-nums tracking-[-0.03em]">{value}</p>
      <p className="mt-1 text-sm text-ink-muted">{note}</p>
    </GlassPanel>
  );
}

export default function DashboardSample() {
  return (
    <div className="flex flex-col gap-6">
      <PageHeader
        title="Welcome back, Priya"
        description="Backend Engineer track. Three things moved since Monday: two skills verified and one new match above 90%."
        actions={<GlassButton variant="glass" href="/design-system/samples/jobs">See job matches</GlassButton>}
      />

      <div className="grid gap-4 lg:grid-cols-[1.25fr_1fr]">
        {/* The one next step, always first */}
        <GlassPanel className="relative overflow-hidden p-6 sm:p-7">
          <span aria-hidden className="pointer-events-none absolute -right-16 -top-16 h-56 w-56 rounded-full bg-crimson/20 blur-3xl" />
          <StatusChip tone="alert">Next step</StatusChip>
          <h2 className="mt-4 max-w-md font-display text-2xl font-semibold leading-tight tracking-[-0.03em] sm:text-[28px]">
            Finish Kafka basics to close your last skill gap.
          </h2>
          <p className="mt-2 max-w-md text-sm leading-relaxed text-ink-muted">
            Module 3 of 4 · about 40 minutes left. Passing the check moves your readiness from 78% to about 84%.
          </p>
          <div className="mt-6 flex flex-wrap gap-3">
            <GlassButton variant="lime">Continue roadmap <ArrowRight className="h-4 w-4" aria-hidden /></GlassButton>
            <GlassButton variant="ghost">Skip for today</GlassButton>
          </div>
        </GlassPanel>

        {/* Readiness */}
        <GlassPanel className="p-6 sm:p-7">
          <div className="flex items-baseline justify-between">
            <h2 className="font-display text-lg font-semibold tracking-[-0.02em]">Career readiness</h2>
            <StatusChip tone="done">Up 6 this week</StatusChip>
          </div>
          <p className="mt-3 font-display text-6xl font-semibold tabular-nums tracking-[-0.05em]">78<span className="text-3xl text-ink-dim">%</span></p>
          <ul className="mt-5 flex flex-col gap-3">
            {pillars.map((p) => (
              <li key={p.name}>
                <div className="flex justify-between text-sm"><span className="text-ink-muted">{p.name}</span><span className="tabular-nums">{p.value}%</span></div>
                <div className="mt-1.5 h-1.5 overflow-hidden rounded-full bg-white/10">
                  <div className="h-full rounded-full bg-gradient-to-r from-lav to-lime" style={{ width: `${p.value}%` }} />
                </div>
              </li>
            ))}
          </ul>
        </GlassPanel>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <Stat label="Verified skills" value="9 of 12" note="3 gaps left: Kafka, Redis, system design" />
        <Stat label="Roadmap" value="14 of 22" note="Tasks done · on track for 18 Dec" />
        <Stat label="Job matches" value="18" note="5 above 85% fit" />
      </div>

      <GlassPanel className="p-2 sm:p-3">
        <div className="flex items-center justify-between px-4 pb-2 pt-3">
          <h2 className="font-display text-lg font-semibold tracking-[-0.02em]">Top matches</h2>
          <GlassButton variant="ghost" size="sm" href="/design-system/samples/jobs">All matches</GlassButton>
        </div>
        <ul>
          {matches.map((m) => (
            <li key={m.company}>
              <a href="/design-system/samples/jobs" className="flex items-center gap-4 rounded-2xl px-4 py-4 transition-colors duration-200 hover:bg-white/[0.04]">
                <span className="grid h-10 w-10 shrink-0 place-items-center rounded-xl border border-white/10 bg-white/5"><Building2 className="h-4 w-4 text-ink-muted" aria-hidden /></span>
                <span className="min-w-0 flex-1">
                  <span className="block font-medium">{m.role} · {m.company}</span>
                  <span className="flex items-center gap-1 text-sm text-ink-dim"><MapPin className="h-3.5 w-3.5" aria-hidden />{m.place}</span>
                </span>
                <span className="text-right">
                  <span className="block font-display text-xl font-semibold tabular-nums text-lime">{m.fit}%</span>
                  <span className="block text-xs text-ink-dim">fit</span>
                </span>
              </a>
            </li>
          ))}
        </ul>
      </GlassPanel>
    </div>
  );
}
