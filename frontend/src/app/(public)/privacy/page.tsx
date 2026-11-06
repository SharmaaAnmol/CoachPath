import Link from 'next/link';
import type { Metadata } from 'next';

export const metadata: Metadata = { title: 'Privacy policy · CoachPath' };

const SUPPORT_EMAIL = process.env.NEXT_PUBLIC_SUPPORT_EMAIL;
const UPDATED = '6 November 2026';

const SECTIONS: { title: string; body: React.ReactNode }[] = [
  {
    title: 'What we collect',
    body: (
      <ul>
        <li><strong>Account:</strong> your name, email address and a hashed password.</li>
        <li><strong>Career data you give us:</strong> onboarding answers, target roles, skills, assessment answers and scores, roadmap progress.</li>
        <li><strong>Resumes:</strong> the files you upload and the text we extract from them, plus the tailored versions you create.</li>
        <li><strong>Job search data:</strong> jobs you import or save, application packages and recruiter messages you write in CoachPath.</li>
        <li><strong>Technical data:</strong> sign-in sessions and basic request logs used to keep the service secure and working.</li>
      </ul>
    ),
  },
  {
    title: 'How we use it',
    body: (
      <p>
        Only to run CoachPath for you: to find your skill gaps, build your roadmap, match jobs, tailor resumes and draft
        messages. We do not sell your data, we do not show ads, and CoachPath never applies to jobs or messages anyone on
        your behalf. You review and send everything yourself.
      </p>
    ),
  },
  {
    title: 'Services that process your data',
    body: (
      <ul>
        <li><strong>Groq</strong> runs the AI features. We send only the text a feature needs, such as resume content for tailoring.</li>
        <li><strong>Vercel</strong> hosts the website and app.</li>
        <li><strong>Render</strong> hosts our server.</li>
        <li><strong>Neon</strong> stores our database.</li>
        <li><strong>Cloudflare R2</strong> stores uploaded resume files.</li>
      </ul>
    ),
  },
  {
    title: 'Security',
    body: (
      <p>
        Data is sent over HTTPS. Passwords are stored only as Argon2 hashes. Sessions use secure, HTTP-only cookies, and
        each account can only read its own data.
      </p>
    ),
  },
  {
    title: 'How long we keep it, and deleting it',
    body: (
      <p>
        We keep your data while your account exists. You can delete your account at any time in{' '}
        <strong>Settings → Delete account</strong>. That permanently removes your account, profile, resumes and files,
        assessments, roadmap, applications and messages straight away. See{' '}
        <Link href="/delete-account" className="text-lav underline underline-offset-4">how to delete your account</Link>.
      </p>
    ),
  },
  {
    title: 'Contact',
    body: (
      <p>
        Questions about your data:{' '}
        {SUPPORT_EMAIL ? (
          <a href={`mailto:${SUPPORT_EMAIL}`} className="text-lav underline underline-offset-4">{SUPPORT_EMAIL}</a>
        ) : (
          'use the contact address on our Google Play listing'
        )}
        .
      </p>
    ),
  },
];

export default function PrivacyPage() {
  return (
    <div className="mx-auto max-w-3xl px-4 py-16 sm:px-6">
      <h1 className="font-display text-4xl font-semibold tracking-[-0.03em] text-ink-fg">Privacy policy</h1>
      <p className="mt-3 text-sm text-ink-dim">Last updated {UPDATED}</p>
      <p className="mt-6 text-base leading-relaxed text-ink-muted">
        CoachPath is a career coaching app. This page explains what data it keeps about you, why, who else handles it,
        and how to delete it.
      </p>
      <div className="mt-10 space-y-10">
        {SECTIONS.map((s) => (
          <section key={s.title}>
            <h2 className="font-display text-xl font-semibold tracking-[-0.02em] text-ink-fg">{s.title}</h2>
            <div className="mt-3 text-[15px] leading-relaxed text-ink-muted [&_li]:mt-2 [&_strong]:text-ink-fg [&_ul]:list-disc [&_ul]:pl-5">
              {s.body}
            </div>
          </section>
        ))}
      </div>
    </div>
  );
}
