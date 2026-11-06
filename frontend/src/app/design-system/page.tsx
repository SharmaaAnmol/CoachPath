import { notFound } from 'next/navigation';
import { ArrowRight, FileText } from 'lucide-react';
import {
  AIThinking,
  AppWindow,
  GlassButton,
  GlassEmptyState,
  GlassPanel,
  LightField,
  PageHeader,
  StatusChip,
} from '@/components/glass';

export const metadata = { title: 'CoachPath design system' };

/** Dev-only gallery of the redesign foundation (phase 1). Hidden in production builds. */
export default function DesignSystemPage() {
  if (process.env.NODE_ENV === 'production') notFound();

  return (
    <div className="cp-dark relative min-h-screen shrink-0 overflow-x-clip">
      <LightField tone="violet" className="left-[10%] top-[18%] h-[420px] w-[620px]" />
      <LightField tone="lavender" className="right-[6%] top-[52%] h-[320px] w-[420px]" />
      <LightField tone="lime" className="right-[20%] top-[8%] h-[200px] w-[260px]" />
      <LightField tone="crimson" className="left-[30%] bottom-[6%] h-[200px] w-[260px]" />

      <main className="relative mx-auto flex max-w-[1200px] flex-col gap-16 px-4 py-20 sm:px-6">
        <PageHeader
          title="CoachPath design system"
          description="Look D foundation: black ground, lavender and violet lead, lime for done and verified, crimson for removed lines and the next step."
          actions={
            <>
              <GlassButton variant="glass" href="#buttons">Buttons</GlassButton>
              <GlassButton href="#window">
                See the app window <ArrowRight className="h-4 w-4" aria-hidden />
              </GlassButton>
            </>
          }
        />

        <section id="buttons" className="flex flex-col gap-5">
          <h2 className="font-display text-2xl font-semibold tracking-[-0.03em]">Buttons and status chips</h2>
          <GlassPanel className="flex flex-col gap-6 p-8">
            <div className="flex flex-wrap items-center gap-3">
              <GlassButton size="lg">Upload your resume</GlassButton>
              <GlassButton variant="glass" size="lg">See the six steps</GlassButton>
              <GlassButton variant="lime">Continue roadmap</GlassButton>
              <GlassButton variant="ghost">Skip for now</GlassButton>
              <GlassButton isLoading>Tailoring</GlassButton>
              <GlassButton disabled>Disabled</GlassButton>
            </div>
            <div className="flex flex-wrap items-center gap-3">
              <StatusChip>Suggested</StatusChip>
              <StatusChip tone="active">In progress</StatusChip>
              <StatusChip tone="done">Verified</StatusChip>
              <StatusChip tone="alert">Skill gap</StatusChip>
            </div>
          </GlassPanel>
        </section>

        <section id="window" className="flex flex-col gap-5">
          <h2 className="font-display text-2xl font-semibold tracking-[-0.03em]">App window and AI waiting state</h2>
          <AppWindow title="coachpath.app / tailoring">
            <div className="grid gap-8 p-6 md:grid-cols-[1fr_320px]">
              <div className="flex flex-col gap-4">
                <div>
                  <h3 className="font-display text-xl font-semibold tracking-[-0.02em]">Backend Engineer · Razorpay</h3>
                  <p className="text-sm text-ink-muted">Version 2 · 3 changes suggested</p>
                </div>
                <div className="overflow-hidden rounded-2xl border border-ink-line bg-black/35 text-sm">
                  <div className="flex items-center justify-between border-b border-ink-line px-4 py-3">
                    <span>Experience · Payments API</span>
                    <StatusChip tone="done">Accepted</StatusChip>
                  </div>
                  <p className="bg-crimson/10 px-4 py-3 text-crimson-tint">− Worked on backend services for payments.</p>
                  <p className="bg-lime/[0.07] px-4 py-3 text-lime-soft">
                    + Built a payments reconciliation API in Python and FastAPI handling 40k transactions a day.
                  </p>
                </div>
              </div>
              <div className="flex flex-col gap-6">
                <AIThinking label="Tailoring your resume for this job" hint="Usually 10–20 seconds" />
                <div className="rounded-2xl border border-crimson/30 bg-crimson/[0.06] p-4">
                  <p className="text-xs font-medium text-crimson-soft">Next step</p>
                  <p className="mt-1 font-medium">Finish the Kafka basics module to close your last gap.</p>
                  <GlassButton variant="lime" size="sm" className="mt-3">Continue roadmap</GlassButton>
                </div>
              </div>
            </div>
          </AppWindow>
        </section>

        <section className="flex flex-col gap-5">
          <h2 className="font-display text-2xl font-semibold tracking-[-0.03em]">Empty state</h2>
          <GlassEmptyState
            icon={<FileText className="h-5 w-5" />}
            title="No resume yet"
            description="Upload a PDF or DOCX. We read it in about a minute and you review everything before it is saved."
            action={<GlassButton>Upload your resume</GlassButton>}
          />
        </section>
      </main>
    </div>
  );
}
