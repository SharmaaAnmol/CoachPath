import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card } from '@/components/ui/card';
import { Lock, ShieldCheck, FileCheck, CheckCircle2, ArrowRight } from 'lucide-react';

export default function PrivacyPage() {
  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-16 space-y-12">
      <div className="text-center space-y-4 max-w-2xl mx-auto">
        <Badge variant="verified" size="md">Security & Trust</Badge>
        <h1 className="text-4xl font-extrabold text-slate-900 dark:text-white tracking-tight">
          Privacy Policy & Responsible AI Commitments
        </h1>
        <p className="text-base text-slate-600 dark:text-slate-300 leading-relaxed">
          How CoachPath safeguards your personal career data, enforces ethical AI boundaries, and ensures you retain full ownership of your records.
        </p>
      </div>

      <div className="space-y-8 text-sm text-slate-700 dark:text-slate-300 leading-relaxed">
        {/* Section 1 */}
        <Card className="p-6 md:p-8 space-y-4">
          <div className="flex items-center gap-2 text-base font-bold text-slate-900 dark:text-white">
            <ShieldCheck className="w-5 h-5 text-emerald-600" />
            <h3>1. Grounded Anti-Fabrication & Evidence Safeguards</h3>
          </div>
          <p>
            CoachPath utilizes a specialized two-pass audit pipeline for resume tailoring. Our system is designed to prevent fabricating credentials, fake project statistics, or technology claims that lack grounded evidence in your profile records or diagnostic test logs. If an LLM suggests a phrase unsupported by evidence, our server-side validator flags unverified skills before presentation, reinforcing human-in-the-loop candidate review.
          </p>
        </Card>

        {/* Section 2 */}
        <Card className="p-6 md:p-8 space-y-4">
          <div className="flex items-center gap-2 text-base font-bold text-slate-900 dark:text-white">
            <Lock className="w-5 h-5 text-purple-600" />
            <h3>2. Strict Data Ownership & Evidence-Bounded AI</h3>
          </div>
          <p>
            Your career profile, resumes, project links, and assessment scores are strictly your intellectual property. CoachPath does not sell candidate data to third-party data brokers, nor do we permit public AI providers to train public models on your private documents. All AI interactions utilize prompt minimization and evidence bounding, sending only the context necessary to evaluate skills or tailor documents.
          </p>
        </Card>

        {/* Section 3 */}
        <Card className="p-6 md:p-8 space-y-4">
          <div className="flex items-center gap-2 text-base font-bold text-slate-900 dark:text-white">
            <FileCheck className="w-5 h-5 text-blue-600" />
            <h3>3. Mandatory Human Approval Gate</h3>
          </div>
          <p>
            CoachPath does not deploy autonomous agents that auto-apply to jobs or email recruiters without human knowledge. All generated recruiter messages, application submissions, and resume diffs require explicit candidate review, approval, and action.
          </p>
        </Card>

        {/* Section 4 */}
        <Card className="p-6 md:p-8 space-y-4">
          <div className="flex items-center gap-2 text-base font-bold text-slate-900 dark:text-white">
            <CheckCircle2 className="w-5 h-5 text-amber-600" />
            <h3>4. Data Portability & Account Erasure</h3>
          </div>
          <p>
            CoachPath is designed around principles of data minimization and user ownership aligned with our Phase 16 compliance roadmap:
          </p>
          <ul className="list-disc list-inside space-y-2 pl-2 text-slate-600 dark:text-slate-400">
            <li><strong>Career Data Portability:</strong> Self-service JSON export tools are currently in development for Phase 16. In the interim, candidates can request a manual export of their profile and assessment history by contacting support.</li>
            <li><strong>Account Erasure:</strong> Candidates retain the right to delete their data. While self-service automated deletion workflows are scheduled for Phase 16, candidates can request permanent account and resume file erasure via admin support, which removes records from Neon Cloud PostgreSQL and file storage.</li>
          </ul>
        </Card>
      </div>

      <div className="text-center pt-4">
        <Link href="/settings">
          <Button variant="outline" size="md">
            Manage Privacy Settings in App
          </Button>
        </Link>
      </div>
    </div>
  );
}
