import { notFound } from 'next/navigation';
import { AppShell } from '@/components/layout/app-shell';
import Dashboard from '@/app/(app)/dashboard/page';
import Jobs from '@/app/(app)/jobs/page';
import Roadmap from '@/app/(app)/roadmap/page';

const pages: Record<string, React.ComponentType> = { dashboard: Dashboard, jobs: Jobs, roadmap: Roadmap };

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
