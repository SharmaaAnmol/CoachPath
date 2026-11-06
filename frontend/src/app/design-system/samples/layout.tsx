import { notFound } from 'next/navigation';
import { SampleShell } from './sample-shell';

export const metadata = { title: 'CoachPath Look D samples' };

/** Dev-only previews of real app screens in Look D, with mock data. Hidden in production. */
export default function SamplesLayout({ children }: { children: React.ReactNode }) {
  if (process.env.NODE_ENV === 'production') notFound();
  return <SampleShell>{children}</SampleShell>;
}
