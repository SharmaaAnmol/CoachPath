import Link from 'next/link';
import type { Metadata } from 'next';
import { CheckCircle2 } from 'lucide-react';

export const metadata: Metadata = { title: 'Delete your account · CoachPath' };

const SUPPORT_EMAIL = process.env.NEXT_PUBLIC_SUPPORT_EMAIL;

// Public page Google Play links to: how a user deletes their CoachPath account and what is removed.
export default function DeleteAccountPage({ searchParams }: { searchParams: { done?: string } }) {
  if (searchParams.done) {
    return (
      <div className="mx-auto flex max-w-xl flex-col items-center gap-4 px-4 py-24 text-center">
        <CheckCircle2 className="h-10 w-10 text-lime" aria-hidden />
        <h1 className="font-display text-3xl font-semibold tracking-[-0.03em] text-ink-fg">Your account is deleted</h1>
        <p className="text-ink-muted">All your CoachPath data has been permanently removed. Thanks for trying CoachPath.</p>
        <Link href="/" className="mt-2 inline-flex min-h-11 items-center rounded-full bg-lav px-6 font-medium text-lav-ink">
          Back to home
        </Link>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-3xl px-4 py-16 sm:px-6">
      <h1 className="font-display text-4xl font-semibold tracking-[-0.03em] text-ink-fg">Delete your CoachPath account</h1>
      <p className="mt-6 text-base leading-relaxed text-ink-muted">
        You can delete your account and all of your data yourself, at any time, from the app or the website.
      </p>

      <section className="mt-10">
        <h2 className="font-display text-xl font-semibold tracking-[-0.02em] text-ink-fg">How to delete it</h2>
        <ol className="mt-3 list-decimal space-y-2 pl-5 text-[15px] leading-relaxed text-ink-muted">
          <li>Sign in to CoachPath in the app or at this website.</li>
          <li>Open <strong className="text-ink-fg">Settings</strong> and scroll to <strong className="text-ink-fg">Delete account</strong>.</li>
          <li>Enter your password, type <strong className="text-ink-fg">DELETE</strong>, and confirm.</li>
        </ol>
        <Link href="/settings" className="mt-6 inline-flex min-h-11 items-center rounded-full bg-lav px-6 font-medium text-lav-ink">
          Go to Settings
        </Link>
      </section>

      <section className="mt-10">
        <h2 className="font-display text-xl font-semibold tracking-[-0.02em] text-ink-fg">What is deleted</h2>
        <p className="mt-3 text-[15px] leading-relaxed text-ink-muted">
          Everything, straight away and permanently: your account and sign-in sessions, profile and onboarding answers,
          uploaded resume files and tailored versions, assessments and skill analysis, roadmap, saved jobs, application
          packages and recruiter messages. We keep nothing afterwards, so this cannot be undone.
        </p>
      </section>

      {SUPPORT_EMAIL && (
        <section className="mt-10">
          <h2 className="font-display text-xl font-semibold tracking-[-0.02em] text-ink-fg">Can&apos;t sign in?</h2>
          <p className="mt-3 text-[15px] leading-relaxed text-ink-muted">
            Email <a href={`mailto:${SUPPORT_EMAIL}`} className="text-lav underline underline-offset-4">{SUPPORT_EMAIL}</a>{' '}
            from the address on your account and we will delete it within 7 days.
          </p>
        </section>
      )}
    </div>
  );
}
