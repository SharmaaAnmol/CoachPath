import { notFound } from 'next/navigation';
import { AppShell } from '@/components/layout/app-shell';
import Dashboard from '@/app/(app)/dashboard/page';
import Jobs from '@/app/(app)/jobs/page';
import Resume from '@/app/(app)/resume/page';
import Roadmap from '@/app/(app)/roadmap/page';
import Skills from '@/app/(app)/skills/page';
import Assessments from '@/app/(app)/assessments/page';
import Onboarding from '@/app/(app)/onboarding/page';
import CareerProfile from '@/app/(app)/career-profile/page';
import Applications from '@/app/(app)/applications/page';
import Recruiters from '@/app/(app)/recruiters/page';
import Interviews from '@/app/(app)/interviews/page';
import CareerReadiness from '@/app/(app)/career-readiness/page';
import Settings from '@/app/(app)/settings/page';

const pages: Record<string, React.ComponentType> = {
  dashboard: Dashboard, jobs: Jobs, resume: Resume, roadmap: Roadmap, skills: Skills,
  assessments: Assessments, onboarding: Onboarding, 'career-profile': CareerProfile,
  applications: Applications, recruiters: Recruiters, interviews: Interviews,
  'career-readiness': CareerReadiness, settings: Settings,
};

/** Dev-only: real app pages inside the real shell without sign-in, so data cards show their empty states. */
export default function Preview({ params }: { params: { page: string } }) {
  const Page = pages[params.page];
  if (process.env.NODE_ENV === 'production' || !Page) notFound();
  return (
    <AppShell>
      <Page />
    </AppShell>
  );
}
