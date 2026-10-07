import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card } from '@/components/ui/card';
import { Sparkles, Shield, HeartHandshake, Code2, Users, ArrowRight } from 'lucide-react';

export default function AboutPage() {
  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-16 space-y-16">
      {/* Title */}
      <div className="text-center space-y-4 max-w-2xl mx-auto">
        <Badge variant="action" size="md">Our Mission & Principles</Badge>
        <h1 className="text-4xl font-extrabold text-slate-900 dark:text-white tracking-tight">
          Bringing Truth & Calm to Technical Careers
        </h1>
        <p className="text-base text-slate-600 dark:text-slate-300 leading-relaxed">
          We believe engineers deserve a system grounded in actual competence, verifiable evidence, and transparent feedback—not empty hype or fabricated AI resumes.
        </p>
      </div>

      {/* Story */}
      <div className="space-y-6 text-sm sm:text-base text-slate-700 dark:text-slate-300 leading-relaxed">
        <Card className="p-8 space-y-4 border-slate-200/80">
          <h2 className="text-xl font-bold text-slate-900 dark:text-white flex items-center gap-2">
            <HeartHandshake className="w-5 h-5 text-purple-600" />
            Why We Built CoachPath
          </h2>
          <p>
            The software job market underwent a drastic distortion over the past few years. Job boards became overcrowded with generic resumes, automated scrapers flooded recruiters with low-quality applications, and generative AI was weaponized to hallucinate technologies that candidates had never used.
          </p>
          <p>
            The result? Employers raised barriers higher, introducing grueling multi-stage screens, while capable software engineers—from motivated computer science students to early-career developers like our benchmark persona Aarav Mehta—found themselves lost in a cycle of silent rejections.
          </p>
          <p>
            CoachPath was founded to build a different path: one where candidates receive objective diagnostic truth regarding their skill gaps, a structured milestone roadmap to close those gaps through demonstrable deliverables, and the tools to present their truthful achievements with pride.
          </p>
        </Card>

        {/* Core Values Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-6">
          <div className="p-6 rounded-2xl bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 space-y-3">
            <div className="w-10 h-10 rounded-xl bg-purple-50 dark:bg-purple-950/50 text-purple-600 flex items-center justify-center font-bold">
              <Shield className="w-5 h-5" />
            </div>
            <h3 className="text-base font-bold text-slate-900 dark:text-white">Truth Over Hype</h3>
            <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed">
              We never fabricate bullet points. Every optimization is verified against real code tests or project repositories before you accept it.
            </p>
          </div>

          <div className="p-6 rounded-2xl bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 space-y-3">
            <div className="w-10 h-10 rounded-xl bg-emerald-50 dark:bg-emerald-950/50 text-emerald-600 flex items-center justify-center font-bold">
              <Code2 className="w-5 h-5" />
            </div>
            <h3 className="text-base font-bold text-slate-900 dark:text-white">Deterministic First</h3>
            <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed">
              We separate LLM reasoning from business-critical decisions. Scoring, grading, and roadmaps are anchored in deterministic logic.
            </p>
          </div>

          <div className="p-6 rounded-2xl bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 space-y-3">
            <div className="w-10 h-10 rounded-xl bg-amber-50 dark:bg-amber-950/50 text-amber-600 flex items-center justify-center font-bold">
              <Users className="w-5 h-5" />
            </div>
            <h3 className="text-base font-bold text-slate-900 dark:text-white">Human Agency</h3>
            <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed">
              You own your career. CoachPath never auto-applies or messages recruiters without your explicit review and copy action.
            </p>
          </div>
        </div>
      </div>

      {/* CTA */}
      <div className="text-center pt-6">
        <Link href="/dashboard">
          <Button size="lg" variant="primary" className="shadow-elevated px-8">
            Explore the Platform <ArrowRight className="w-4 h-4 ml-2" />
          </Button>
        </Link>
      </div>
    </div>
  );
}
