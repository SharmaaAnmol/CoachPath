import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card } from '@/components/ui/card';
import {
  Sparkles,
  ShieldCheck,
  Cpu,
  Compass,
  Briefcase,
  FileText,
  Kanban,
  Users,
  MessageSquareCode,
  Gauge,
  Lock,
  ArrowRight,
  CheckCircle2,
} from 'lucide-react';

export default function FeaturesPage() {
  const features = [
    {
      title: 'Central Career Profile Graph',
      desc: 'One authoritative profile tracking education, verified experience, code repos, and skills. Eliminates duplicate data entry across platforms.',
      icon: Cpu,
      color: 'text-purple-600 bg-purple-50 dark:bg-purple-950/40',
      bullets: ['Normalized relational schema', 'Evidence-linked records', 'Instant PDF/JSON export'],
    },
    {
      title: 'Diagnostic Skill Assessments',
      desc: 'Deterministic evaluations that calibrate self-reported confidence into verified badges through code optimization and architecture questions.',
      icon: ShieldCheck,
      color: 'text-emerald-600 bg-emerald-50 dark:bg-emerald-950/40',
      bullets: ['15-minute diagnostic tests', 'Anti-cheat randomize logic', 'Transparent grading criteria'],
    },
    {
      title: 'Skill Gap & Market Intelligence',
      desc: 'Live clustering categorizes your competencies into Verified Strengths, Developing, and Gaps according to target role seniority.',
      icon: Cpu,
      color: 'text-indigo-600 bg-indigo-50 dark:bg-indigo-950/40',
      bullets: ['Tri-state categorization', 'Market demand ratios', 'Target role requirement trees'],
    },
    {
      title: 'Dynamic Milestone Roadmap',
      desc: 'Phased, task-oriented curriculum designed to close gaps with real GitHub deliverables and curated engineering documentation.',
      icon: Compass,
      color: 'text-amber-600 bg-amber-50 dark:bg-amber-950/40',
      bullets: ['3-phase milestone sprints', 'Verifiable project tasks', 'Estimated hour budgets'],
    },
    {
      title: 'Semantic Vector Job Search',
      desc: 'High-dimensional embeddings evaluate deep semantic fit beyond brittle keyword queries, surfacing relevant software roles.',
      icon: Briefcase,
      color: 'text-blue-600 bg-blue-50 dark:bg-blue-950/40',
      bullets: ['pgvector cosine similarity', 'Real-time compensation stats', 'Remote & hybrid filtering'],
    },
    {
      title: 'Explainable Multi-Factor Matching',
      desc: 'Understand exactly why a job scored 94% or 78% with individual factor scores across skills, experience, domain, and seniority.',
      icon: Sparkles,
      color: 'text-purple-600 bg-purple-50 dark:bg-purple-950/40',
      bullets: ['Transparent score factors', 'Matched vs missing skills', 'Actionable qualification tips'],
    },
    {
      title: 'Truthful Resume Optimizer',
      desc: 'Two-pass anti-hallucination engine suggests targeted wording backed strictly by verified candidate experience. No ChatGPT fabrications.',
      icon: FileText,
      color: 'text-emerald-600 bg-emerald-50 dark:bg-emerald-950/40',
      bullets: ['Side-by-side diff review', 'Zero hallucination audit', 'Targeted ATS keyword mapping'],
    },
    {
      title: 'Application Pipeline Kanban',
      desc: 'Visual board tracking applications across Saved, Applied, Interviewing, and Offered stages with deadlines and follow-up reminders.',
      icon: Kanban,
      color: 'text-amber-600 bg-amber-50 dark:bg-amber-950/40',
      bullets: ['Kanban drag-and-drop states', 'Recruiter contact logging', 'Historic application notes'],
    },
    {
      title: 'Recruiter Discovery Gate',
      desc: 'Find the right technical hiring managers for your target positions and generate personalized outreach drafts with human-copy gates.',
      icon: Users,
      color: 'text-indigo-600 bg-indigo-50 dark:bg-indigo-950/40',
      bullets: ['Company talent leads', 'Value-first draft messages', 'Strict manual copy safeguard'],
    },
    {
      title: 'STAR Interview Question Bank',
      desc: 'Role-specific question bank offering tailored Situation, Task, Action, and Result talking points for upcoming technical rounds.',
      icon: MessageSquareCode,
      color: 'text-rose-600 bg-rose-50 dark:bg-rose-950/40',
      bullets: ['Staff-level architecture drills', 'Behavioral STAR templates', 'Personal talking point notes'],
    },
    {
      title: 'Composite Career Readiness Score',
      desc: 'Objective 0-100% index calculating readiness across Skill Verification, Practical Projects, Market Relevance, and Interview Fluency.',
      icon: Gauge,
      color: 'text-purple-600 bg-purple-50 dark:bg-purple-950/40',
      bullets: ['4 objective pillars', 'Market readiness index', 'Targeted deficiency alerts'],
    },
    {
      title: 'Privacy & Data Erasure Controls',
      desc: 'Your career profile and resumes are never used for public LLM training or sold to third-party data brokers. One-click data deletion.',
      icon: Lock,
      color: 'text-slate-600 bg-slate-100 dark:bg-slate-800',
      bullets: ['GDPR & CCPA compliance', 'One-click full account wipe', 'JSON portability export'],
    },
  ];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 space-y-16">
      <div className="text-center space-y-4 max-w-3xl mx-auto">
        <Badge variant="intelligence" size="md">Core Capabilities</Badge>
        <h1 className="text-4xl font-extrabold text-slate-900 dark:text-white tracking-tight">
          Everything You Need to Become Truly Job-Ready
        </h1>
        <p className="text-base text-slate-600 dark:text-slate-300 leading-relaxed">
          Explore the 12 unified intelligence pillars built to eliminate guesswork and advance your software engineering career.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {features.map((f) => {
          const Icon = f.icon;
          return (
            <Card key={f.title} className="p-6 flex flex-col justify-between hover:border-slate-300 transition-all hover:shadow-card">
              <div className="space-y-4">
                <div className={`w-12 h-12 rounded-2xl flex items-center justify-center ${f.color}`}>
                  <Icon className="w-6 h-6" />
                </div>
                <div>
                  <h3 className="text-lg font-bold text-slate-900 dark:text-white">{f.title}</h3>
                  <p className="text-xs text-slate-500 dark:text-slate-400 mt-1.5 leading-relaxed">
                    {f.desc}
                  </p>
                </div>
                <div className="space-y-1.5 pt-2 border-t border-slate-100 dark:border-slate-800">
                  {f.bullets.map((b) => (
                    <div key={b} className="flex items-center gap-2 text-xs text-slate-700 dark:text-slate-300">
                      <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
                      <span>{b}</span>
                    </div>
                  ))}
                </div>
              </div>
            </Card>
          );
        })}
      </div>

      <div className="text-center pt-8">
        <Link href="/dashboard">
          <Button size="lg" variant="intelligence" className="shadow-elevated px-8">
            Experience All Features Live <ArrowRight className="w-4 h-4 ml-2" />
          </Button>
        </Link>
      </div>
    </div>
  );
}
