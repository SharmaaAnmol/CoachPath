import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card } from '@/components/ui/card';
import {
  ArrowRight,
  Target,
  Terminal,
  Cpu,
  Compass,
  Briefcase,
  Layers,
  FileText,
  Kanban,
  Users,
  Gauge,
  CheckCircle2,
} from 'lucide-react';

export default function HowItWorksPage() {
  const steps = [
    {
      num: '01',
      title: 'Career Profile Ingestion & Graph Initialization',
      icon: Target,
      tag: 'Step 1: Ingestion',
      description:
        'Upload your baseline PDF or Markdown resume, or complete our structured career questionnaire. CoachPath extracts your education, past positions, project links, and self-reported skills into a normalized PostgreSQL profile schema.',
      outputs: ['Normalized Career Profile', 'Parsed Work Experiences', 'Initial Skill Claims'],
    },
    {
      num: '02',
      title: 'Diagnostic Skill Testing & Grounding',
      icon: Terminal,
      tag: 'Step 2: Verification',
      description:
        'Self-reported skills often fail technical interview scrutiny. CoachPath tests your proficiency through targeted 15-minute diagnostic assessments covering syntax, code optimization, SQL indices, and system architecture.',
      outputs: ['Calibrated Confidence Scores (0-100)', 'Verified Skill Badges', 'Diagnostic Test Reports'],
    },
    {
      num: '03',
      title: 'Transparent Skill Gap Matrix',
      icon: Cpu,
      tag: 'Step 3: Gap Analysis',
      description:
        'The skill gap engine classifies your competencies into three distinct buckets: Verified Strengths, Developing Skills, and Identified Gaps. Gaps are directly mapped against live job market demands for your target role.',
      outputs: ['Tri-State Skill Categorization', 'Market Relevance Ratios', 'Priority Deficit Ranking'],
    },
    {
      num: '04',
      title: 'Dynamic Milestone Roadmap Generation',
      icon: Compass,
      tag: 'Step 4: Action Plan',
      description:
        'Rather than vague advice, CoachPath generates an actionable 3-phase milestone plan. Each task includes verified educational resources, estimated hours, and verifiable deliverables (e.g. GitHub pull requests, benchmark test suites).',
      outputs: ['Phased Weekly Sprints', 'Vetted Documentation Links', 'Verifiable Project Artifacts'],
    },
    {
      num: '05',
      title: 'Semantic Job Ingestion & pgvector Search',
      icon: Briefcase,
      tag: 'Step 5: Discovery',
      description:
        'CoachPath continuously ingests software engineering roles from leading technology employers. Descriptions are converted into 1536-dimensional vector embeddings, allowing high-fidelity cosine similarity matching against your profile graph.',
      outputs: ['Normalized Job Postings', 'Salary Transparency Ranges', 'Vector Distance Indexing'],
    },
    {
      num: '06',
      title: 'Explainable Multi-Factor Job Fit Scoring',
      icon: Layers,
      tag: 'Step 6: Match Transparency',
      description:
        'No mysterious percentages. Every job match score (e.g. 94%) is broken down into its four constituent factors: Skill Match (40%), Experience Alignment (25%), Domain Relevance (20%), and Role Seniority (15%).',
      outputs: ['Composite Match Index', 'Matched vs Missing Skills Breakdown', 'Salary Expectations Check'],
    },
    {
      num: '07',
      title: 'Truthful Resume Optimization & Diff Review',
      icon: FileText,
      tag: 'Step 7: ATS Tailoring',
      description:
        'Our two-pass anti-hallucination auditor rewrites resume bullets to align with target job keywords, strictly restricting claims to your verified project repositories and passed diagnostic assessments. You accept or reject each diff.',
      outputs: ['Side-by-Side Diff Comparison', 'Anti-Hallucination Audit Log', 'Tailored PDF & Markdown Export'],
    },
    {
      num: '08',
      title: 'Application Pipeline & Kanban Tracker',
      icon: Kanban,
      tag: 'Step 8: Execution',
      description:
        'Manage your active job hunt through a structured Kanban board: Saved, Applied, Interviewing, and Offered. Maintain historical logs, deadlines, recruiter contacts, and personal interview notes in one cohesive workspace.',
      outputs: ['Visual Pipeline Status', 'Next Action Reminders', 'Historical Transition Logs'],
    },
    {
      num: '09',
      title: 'Recruiter Discovery & Copy-Confirmation Gate',
      icon: Users,
      tag: 'Step 9: Outreach',
      description:
        'Discover relevant hiring managers and technical sourcers for matched roles. CoachPath drafts concise, value-focused outreach emails. Under our strict ethical guidelines, drafts require manual copy-to-clipboard by the candidate.',
      outputs: ['Target Recruiter Profiles', 'High-Context Message Drafts', 'Human Approval Safeguard'],
    },
    {
      num: '10',
      title: 'Interview Preparation & Career Readiness Index',
      icon: Gauge,
      tag: 'Step 10: Conversion',
      description:
        'Prepare for upcoming rounds with role-specific STAR question banks and talking points. CoachPath computes an ongoing composite Readiness Index (0-100%) so you walk into technical screens with calm confidence.',
      outputs: ['STAR Story Architect', 'System Design Talking Points', '4-Pillar Readiness Calibration'],
    },
  ];

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-16 space-y-16">
      <div className="text-center space-y-4 max-w-3xl mx-auto">
        <Badge variant="intelligence" size="md">Architecture & Methodology</Badge>
        <h1 className="text-4xl font-extrabold text-slate-900 dark:text-white tracking-tight">
          How CoachPath Powers Your Career Journey
        </h1>
        <p className="text-base text-slate-600 dark:text-slate-300 leading-relaxed">
          The step-by-step engineering feedback loop that takes you from self-reported uncertainty to verified market readiness.
        </p>
      </div>

      <div className="space-y-8">
        {steps.map((step) => {
          const Icon = step.icon;
          return (
            <Card key={step.num} className="p-6 md:p-8 hover:border-slate-300 transition-all">
              <div className="flex flex-col md:flex-row md:items-start gap-6">
                <div className="flex md:flex-col items-center gap-3 shrink-0">
                  <div className="h-12 w-12 rounded-2xl bg-purple-50 dark:bg-purple-950/50 border border-purple-200 dark:border-purple-800 flex items-center justify-center text-purple-600 dark:text-purple-400 font-bold">
                    <Icon className="w-6 h-6" />
                  </div>
                  <span className="font-mono text-xs font-bold text-slate-400">
                    {step.num}
                  </span>
                </div>

                <div className="space-y-4 flex-1">
                  <div>
                    <span className="text-[11px] font-bold uppercase tracking-wider text-purple-600 dark:text-purple-400">
                      {step.tag}
                    </span>
                    <h3 className="text-xl font-bold text-slate-900 dark:text-white mt-0.5">
                      {step.title}
                    </h3>
                  </div>

                  <p className="text-sm text-slate-600 dark:text-slate-300 leading-relaxed">
                    {step.description}
                  </p>

                  <div className="pt-2 flex flex-wrap items-center gap-2">
                    <span className="text-[11px] font-semibold text-slate-400 mr-1">Generated Deliverables:</span>
                    {step.outputs.map((out) => (
                      <span
                        key={out}
                        className="inline-flex items-center gap-1 rounded-md px-2.5 py-1 text-xs font-medium bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 border border-slate-200/80 dark:border-slate-700"
                      >
                        <CheckCircle2 className="w-3 h-3 text-emerald-600" />
                        {out}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            </Card>
          );
        })}
      </div>

      <div className="p-8 rounded-2xl bg-gradient-to-r from-brand-600 to-purple-600 text-white text-center space-y-4 shadow-elevated">
        <h3 className="text-2xl font-bold">Experience the connected intelligence loop</h3>
        <p className="text-sm text-purple-100 max-w-lg mx-auto">
          Explore the full interactive system with pre-loaded candidate data, or build your own profile in minutes.
        </p>
        <div className="flex justify-center gap-3 pt-2">
          <Link href="/dashboard">
            <Button size="md" variant="secondary">
              Launch Live Sandbox
            </Button>
          </Link>
          <Link href="/signup">
            <Button size="md" variant="outline" className="bg-white/10 text-white border-white/30 hover:bg-white/20">
              Create Free Account <ArrowRight className="w-4 h-4 ml-1" />
            </Button>
          </Link>
        </div>
      </div>
    </div>
  );
}
