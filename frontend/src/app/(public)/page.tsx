import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card } from '@/components/ui/card';
import { InteractivePlatformPreview } from '@/components/landing/interactive-preview';
import {
  Sparkles,
  ShieldCheck,
  CheckCircle2,
  AlertCircle,
  ArrowRight,
  Cpu,
  Compass,
  Briefcase,
  FileText,
  Users,
  MessageSquareCode,
  Lock,
  Target,
  GraduationCap,
  Layers,
  Terminal,
} from 'lucide-react';

export default function LandingPage() {
  const steps = [
    { num: '01', title: 'Central Profile', desc: 'Centralizes education, experience, verified code repositories, and career goals.', icon: Target },
    { num: '02', title: 'Diagnostic Tests', desc: 'Evaluates real proficiency through deterministic coding and architectural questions.', icon: Terminal },
    { num: '03', title: 'Skill Gap Matrix', desc: 'Transparently separates verified strengths from developing skills and missing market gaps.', icon: Cpu },
    { num: '04', title: 'Dynamic Roadmap', desc: 'Generates step-by-step milestones with vetted resources and verifiable deliverables.', icon: Compass },
    { num: '05', title: 'Job Vector Search', desc: 'Ingests real opportunities and ranks them using semantic embeddings across 7 engineering roles.', icon: Briefcase },
    { num: '06', title: 'Explainable Match', desc: 'Breaks down job fit by skills, experience, domain, and role similarity without black boxes.', icon: Layers },
    { num: '07', title: 'Truthful Resume Diff', desc: 'Two-pass AI optimizer tailors resumes using only verified evidence—strictly zero hallucinations.', icon: FileText },
    { num: '08', title: 'Pipeline Kanban', desc: 'Tracks applications from saved to offer stage with automatic next-step reminders.', icon: CheckCircle2 },
    { num: '09', title: 'Recruiter Gate', desc: 'Generates high-context outreach drafts requiring manual human review and copy confirmation.', icon: Users },
    { num: '10', title: 'Readiness Index', desc: 'Calibrates a composite 0-100% readiness score across 4 objective pillars.', icon: Sparkles },
  ];

  const personas = [
    {
      title: 'University Student',
      subtitle: 'Searching for career direction & hands-on proof',
      icon: GraduationCap,
      color: 'border-brand-500/30 bg-brand-50/50 dark:bg-brand-950/20',
      points: [
        'Overcome uncertainty about which engineering paths match personal strengths.',
        'Convert academic coursework into verified portfolio project deliverables.',
        'Target structured summer internships with calibrated skill confidence.',
      ],
    },
    {
      title: 'Recent Graduate',
      subtitle: 'Breaking out of the entry-level bottleneck',
      icon: Terminal,
      color: 'border-emerald-500/30 bg-emerald-50/50 dark:bg-emerald-950/20',
      points: [
        'Close practical engineering gaps (PostgreSQL tuning, Docker, Redis) missed in university.',
        'Bypass automated ATS keyword filters with truthful, tailored resumes.',
        'Track active applications systematically across top tech hubs.',
      ],
    },
    {
      title: 'Early-Career Professional',
      subtitle: '1–3 YOE aiming for Mid / Senior compensation',
      icon: Cpu,
      color: 'border-purple-500/30 bg-purple-50/50 dark:bg-purple-950/20',
      points: [
        'Map out missing distributed systems patterns required for senior engineering bands.',
        'Optimize resumes for specific tier-1 tech firms (Stripe, Linear, Vercel).',
        'Master system design trade-offs and behavioral STAR question delivery.',
      ],
    },
  ];

  return (
    <div className="space-y-24 pb-20">
      {/* Hero Section */}
      <section className="relative pt-12 sm:pt-20 pb-12 overflow-hidden">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center space-y-8">
          {/* Trust Banner */}
          <div className="inline-flex items-center gap-2 rounded-full px-4 py-1.5 text-xs font-semibold bg-purple-50 dark:bg-purple-950/50 border border-purple-200 dark:border-purple-800 text-purple-700 dark:text-purple-300 shadow-subtle">
            <ShieldCheck className="w-4 h-4 text-purple-600" />
            <span>Two-Pass Anti-Hallucination AI &bull; Human-in-the-Loop &bull; Calibrated Skills</span>
          </div>

          {/* Headline */}
          <div className="max-w-4xl mx-auto space-y-4">
            <h1 className="text-4xl sm:text-6xl font-extrabold tracking-tight text-slate-900 dark:text-white leading-[1.1]">
              From Career Uncertainty to{' '}
              <span className="bg-gradient-to-r from-brand-600 via-purple-600 to-indigo-600 bg-clip-text text-transparent">
                Verified Job Readiness
              </span>
            </h1>
            <p className="text-lg sm:text-xl text-slate-600 dark:text-slate-300 leading-relaxed max-w-2xl mx-auto">
              Stop guessing what tech companies want. CoachPath links diagnostic skill testing, personalized roadmaps, truthful resume diffing, and explainable job matching into one connected career graph.
            </p>
          </div>

          {/* Action CTAs */}
          <div className="flex flex-wrap items-center justify-center gap-4 pt-2">
            <Link href="/signup">
              <Button size="lg" variant="primary" className="shadow-elevated px-8">
                Build Your Career Profile <ArrowRight className="w-4 h-4 ml-2" />
              </Button>
            </Link>
            <Link href="/dashboard">
              <Button size="lg" variant="intelligence" className="shadow-elevated px-6">
                Explore Live Candidate Sandbox
              </Button>
            </Link>
            <Link href="/how-it-works">
              <Button size="lg" variant="outline">
                See How It Works
              </Button>
            </Link>
          </div>

          {/* Live Interactive Preview */}
          <div className="pt-10 max-w-5xl mx-auto">
            <InteractivePlatformPreview />
          </div>
        </div>
      </section>

      {/* The Problem vs The CoachPath Solution */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-3xl mx-auto mb-12 space-y-3">
          <Badge variant="action" size="md">The Paradigm Shift</Badge>
          <h2 className="text-3xl font-bold text-slate-900 dark:text-white">
            Why Generic AI & Fragmented Job Boards Fail Engineers
          </h2>
          <p className="text-sm text-slate-500 dark:text-slate-400">
            Applying blindly with hallucinated ChatGPT bullet points destroys candidate credibility. CoachPath replaces guesswork with deterministic evidence.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {/* Fragmented Way */}
          <Card className="p-8 border-rose-200/80 bg-rose-50/20 dark:bg-rose-950/10 space-y-5">
            <div className="flex items-center gap-3 text-rose-600 font-bold text-lg">
              <AlertCircle className="w-6 h-6" />
              <span>The Fragmented, Guesswork Approach</span>
            </div>
            <ul className="space-y-3 text-sm text-slate-600 dark:text-slate-300">
              <li className="flex items-start gap-2.5">
                <span className="text-rose-500 font-bold shrink-0">&times;</span>
                <span>Uncertainty regarding which skills are genuinely required for target engineering bands.</span>
              </li>
              <li className="flex items-start gap-2.5">
                <span className="text-rose-500 font-bold shrink-0">&times;</span>
                <span>Submitting generic resumes across 200 job portals with zero insight into match probability.</span>
              </li>
              <li className="flex items-start gap-2.5">
                <span className="text-rose-500 font-bold shrink-0">&times;</span>
                <span>Using ungrounded LLM prompts that fabricate unverified skills, causing immediate interview failure.</span>
              </li>
              <li className="flex items-start gap-2.5">
                <span className="text-rose-500 font-bold shrink-0">&times;</span>
                <span>Scattered notes across spreadsheets, LinkedIn messages, and unorganized interview notes.</span>
              </li>
            </ul>
          </Card>

          {/* CoachPath Connected Solution */}
          <Card className="p-8 border-emerald-200/80 bg-emerald-50/20 dark:bg-emerald-950/10 space-y-5">
            <div className="flex items-center gap-3 text-emerald-600 font-bold text-lg">
              <CheckCircle2 className="w-6 h-6" />
              <span>The CoachPath Connected Intelligence Layer</span>
            </div>
            <ul className="space-y-3 text-sm text-slate-700 dark:text-slate-200">
              <li className="flex items-start gap-2.5">
                <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
                <span><strong>Calibrated Evidence:</strong> Skill confidence backed by code tests and repository audits.</span>
              </li>
              <li className="flex items-start gap-2.5">
                <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
                <span><strong>Milestone Roadmaps:</strong> Clear tasks with verifiable project deliverables.</span>
              </li>
              <li className="flex items-start gap-2.5">
                <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
                <span><strong>Two-Pass Anti-Hallucination:</strong> Resume changes only cite verified candidate achievements.</span>
              </li>
              <li className="flex items-start gap-2.5">
                <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
                <span><strong>Complete Lifecycle:</strong> From diagnostic assessment to recruiter outreach and STAR prep.</span>
              </li>
            </ul>
          </Card>
        </div>
      </section>

      {/* The 10-Step Connected Journey */}
      <section className="bg-slate-100/70 dark:bg-slate-900/60 py-16 border-y border-slate-200/80 dark:border-slate-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-12">
          <div className="text-center max-w-3xl mx-auto space-y-3">
            <Badge variant="intelligence" size="md">Deterministic Feedback Loop</Badge>
            <h2 className="text-3xl font-bold text-slate-900 dark:text-white">
              The 10-Step Connected Career Journey
            </h2>
            <p className="text-sm text-slate-500 dark:text-slate-400">
              Every action feeds back into your central career profile, dynamically recalculating readiness and surfacing higher-probability job matches.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
            {steps.map((st) => {
              const Icon = st.icon;
              return (
                <div
                  key={st.num}
                  className="p-5 rounded-2xl bg-white dark:bg-slate-800/90 border border-slate-200/90 dark:border-slate-700 shadow-sm flex flex-col justify-between hover:border-brand-500 transition-all hover:shadow-card"
                >
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="font-mono text-xs font-bold text-purple-600 dark:text-purple-400">
                        {st.num}
                      </span>
                      <div className="p-2 rounded-lg bg-slate-50 dark:bg-slate-700/60 text-slate-600 dark:text-slate-300">
                        <Icon className="w-4 h-4" />
                      </div>
                    </div>
                    <h3 className="font-bold text-sm text-slate-900 dark:text-white">
                      {st.title}
                    </h3>
                    <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed">
                      {st.desc}
                    </p>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* Target Personas Section */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-12">
        <div className="text-center max-w-3xl mx-auto space-y-3">
          <Badge variant="action" size="md">Designed For Your Stage</Badge>
          <h2 className="text-3xl font-bold text-slate-900 dark:text-white">
            Built for Students, Graduates, and Early-Career Engineers
          </h2>
          <p className="text-sm text-slate-500 dark:text-slate-400">
            Tailored guidance adapts to whether you are building your first repository or preparing for staff-level systems design rounds.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {personas.map((p) => {
            const Icon = p.icon;
            return (
              <Card key={p.title} className={`p-6 border ${p.color} space-y-5 flex flex-col justify-between`}>
                <div className="space-y-3">
                  <div className="w-10 h-10 rounded-xl bg-white dark:bg-slate-800 shadow-sm flex items-center justify-center text-slate-800 dark:text-white">
                    <Icon className="w-5 h-5" />
                  </div>
                  <div>
                    <h3 className="text-lg font-bold text-slate-900 dark:text-white">{p.title}</h3>
                    <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">{p.subtitle}</p>
                  </div>
                  <ul className="space-y-2.5 pt-2 text-xs text-slate-600 dark:text-slate-300">
                    {p.points.map((pt, idx) => (
                      <li key={idx} className="flex items-start gap-2">
                        <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 shrink-0 mt-0.5" />
                        <span>{pt}</span>
                      </li>
                    ))}
                  </ul>
                </div>
                <div className="pt-4 border-t border-slate-200/60 dark:border-slate-800/60">
                  <Link href="/signup">
                    <Button size="sm" variant="outline" className="w-full">
                      Start as {p.title.split(' ')[0]}
                    </Button>
                  </Link>
                </div>
              </Card>
            );
          })}
        </div>
      </section>

      {/* Trust & Responsible AI Principles */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="rounded-3xl bg-slate-900 text-white p-8 sm:p-12 border border-slate-800 space-y-8">
          <div className="max-w-2xl space-y-3">
            <div className="flex items-center gap-2 text-emerald-400 font-mono text-xs uppercase tracking-wider">
              <Lock className="w-4 h-4" /> Responsible AI Architecture
            </div>
            <h2 className="text-3xl font-extrabold tracking-tight">
              AI Must Empower You, Not Compromise Your Integrity
            </h2>
            <p className="text-sm text-slate-400 leading-relaxed">
              CoachPath enforces deterministic verification before any generative model is called. We protect you from hallucinations, spam filters, and data leakage.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-4 text-xs">
            <div className="p-4 rounded-xl bg-slate-800/60 border border-slate-700/60 space-y-2">
              <h4 className="font-bold text-emerald-400 text-sm">Two-Pass Grounding Audit</h4>
              <p className="text-slate-300 leading-relaxed">
                Every generated resume bullet is inspected against your verified project and assessment database. Claims lacking evidence are rejected automatically.
              </p>
            </div>
            <div className="p-4 rounded-xl bg-slate-800/60 border border-slate-700/60 space-y-2">
              <h4 className="font-bold text-purple-400 text-sm">Human Approval Gateway</h4>
              <p className="text-slate-300 leading-relaxed">
                CoachPath will never auto-submit applications or send messages to recruiters. You review, approve, and copy outreach drafts with full personal agency.
              </p>
            </div>
            <div className="p-4 rounded-xl bg-slate-800/60 border border-slate-700/60 space-y-2">
              <h4 className="font-bold text-amber-400 text-sm">Right to Erasure & Export</h4>
              <p className="text-slate-300 leading-relaxed">
                Your career data belongs to you. Export your complete data graph in JSON format anytime or purge your account and resumes with a single click.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Final Call to Action */}
      <section className="max-w-5xl mx-auto px-4 text-center space-y-6">
        <h2 className="text-3xl sm:text-4xl font-extrabold text-slate-900 dark:text-white">
          Ready to bridge your skill gap and become job-ready?
        </h2>
        <p className="text-base text-slate-600 dark:text-slate-300 max-w-xl mx-auto">
          Join thousands of software engineers navigating their career journey with verifiable evidence and calm confidence.
        </p>
        <div className="flex flex-wrap items-center justify-center gap-4 pt-2">
          <Link href="/signup">
            <Button size="lg" variant="primary" className="px-8 shadow-elevated">
              Create Your Free Account <ArrowRight className="w-4 h-4 ml-2" />
            </Button>
          </Link>
          <Link href="/dashboard">
            <Button size="lg" variant="outline">
              Test Interactive Sandbox
            </Button>
          </Link>
        </div>
      </section>
    </div>
  );
}
