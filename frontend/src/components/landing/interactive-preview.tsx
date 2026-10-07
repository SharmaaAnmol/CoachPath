'use client';

import * as React from 'react';
import { cn } from '@/lib/utils';
import {
  Gauge,
  Cpu,
  Compass,
  FileText,
  CheckCircle2,
  AlertCircle,
  Clock,
  Sparkles,
  ShieldCheck,
  Building2,
  DollarSign,
  ArrowRight,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import Link from 'next/link';

export function InteractivePlatformPreview() {
  const [activeTab, setActiveTab] = React.useState<'readiness' | 'skills' | 'roadmap' | 'diff'>('readiness');

  return (
    <div className="w-full rounded-2xl border border-slate-700/80 bg-slate-900/95 shadow-2xl backdrop-blur-xl overflow-hidden text-left text-slate-100">
      {/* Window Title Bar */}
      <div className="flex items-center justify-between px-4 py-3 bg-slate-950/70 border-b border-slate-800 text-xs">
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-rose-500/80" />
          <div className="w-3 h-3 rounded-full bg-amber-500/80" />
          <div className="w-3 h-3 rounded-full bg-emerald-500/80" />
          <span className="ml-2 font-mono text-[11px] text-slate-400">
            CoachPath Intelligence Engine &bull; Candidate: Aarav Mehta (Target: Full-Stack Engineer)
          </span>
        </div>
        <div className="hidden sm:flex items-center gap-2 text-[11px] text-emerald-400 font-mono">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
          Evidence Grounded &bull; Active
        </div>
      </div>

      {/* Interactive Tabs Header */}
      <div className="flex border-b border-slate-800 bg-slate-900/50 overflow-x-auto">
        <button
          onClick={() => setActiveTab('readiness')}
          className={cn(
            'flex items-center gap-2 px-5 py-3 text-xs font-semibold transition-all border-b-2',
            activeTab === 'readiness'
              ? 'border-brand-500 text-white bg-slate-800/60'
              : 'border-transparent text-slate-400 hover:text-slate-200 hover:bg-slate-800/30'
          )}
        >
          <Gauge className="w-4 h-4 text-purple-400" />
          <span>Readiness Score (78%)</span>
        </button>

        <button
          onClick={() => setActiveTab('skills')}
          className={cn(
            'flex items-center gap-2 px-5 py-3 text-xs font-semibold transition-all border-b-2',
            activeTab === 'skills'
              ? 'border-brand-500 text-white bg-slate-800/60'
              : 'border-transparent text-slate-400 hover:text-slate-200 hover:bg-slate-800/30'
          )}
        >
          <Cpu className="w-4 h-4 text-emerald-400" />
          <span>Skill Gap Engine</span>
        </button>

        <button
          onClick={() => setActiveTab('roadmap')}
          className={cn(
            'flex items-center gap-2 px-5 py-3 text-xs font-semibold transition-all border-b-2',
            activeTab === 'roadmap'
              ? 'border-brand-500 text-white bg-slate-800/60'
              : 'border-transparent text-slate-400 hover:text-slate-200 hover:bg-slate-800/30'
          )}
        >
          <Compass className="w-4 h-4 text-amber-400" />
          <span>Dynamic Roadmap</span>
        </button>

        <button
          onClick={() => setActiveTab('diff')}
          className={cn(
            'flex items-center gap-2 px-5 py-3 text-xs font-semibold transition-all border-b-2',
            activeTab === 'diff'
              ? 'border-brand-500 text-white bg-slate-800/60'
              : 'border-transparent text-slate-400 hover:text-slate-200 hover:bg-slate-800/30'
          )}
        >
          <FileText className="w-4 h-4 text-brand-400" />
          <span>Anti-Hallucination Diff</span>
        </button>
      </div>

      {/* Tab Panels Content */}
      <div className="p-6 min-h-[340px]">
        {/* Tab 1: Readiness Score */}
        {activeTab === 'readiness' && (
          <div className="space-y-6 animate-in fade-in duration-200">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-4 rounded-xl bg-slate-800/50 border border-slate-700/60">
              <div className="flex items-center gap-4">
                <div className="h-16 w-16 rounded-2xl bg-gradient-to-tr from-purple-600 to-indigo-600 flex flex-col items-center justify-center font-bold shadow-lg">
                  <span className="text-2xl leading-none">78%</span>
                  <span className="text-[9px] uppercase tracking-wider text-purple-200 font-mono mt-0.5">Index</span>
                </div>
                <div>
                  <h4 className="text-base font-bold text-white flex items-center gap-2">
                    Market Competency Calibrated
                    <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                      Tier 1 Qualified
                    </span>
                  </h4>
                  <p className="text-xs text-slate-400 mt-1 max-w-lg">
                    Weighted across validated diagnostic code tests, GitHub project artifacts, semantic role requirements, and interview STAR fluency.
                  </p>
                </div>
              </div>
              <Link href="/career-readiness">
                <Button size="sm" variant="intelligence">
                  Inspect All 4 Pillars <ArrowRight className="w-3.5 h-3.5 ml-1" />
                </Button>
              </Link>
            </div>

            {/* 4 Constituent Pillars Grid */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-xs">
              <div className="p-3.5 rounded-xl bg-slate-800/40 border border-slate-700/50">
                <div className="text-[11px] text-slate-400">Skill Verification (35%)</div>
                <div className="text-lg font-bold text-emerald-400 mt-1">82%</div>
                <div className="text-[10px] text-slate-400 mt-1">TypeScript & PostgreSQL verified</div>
              </div>
              <div className="p-3.5 rounded-xl bg-slate-800/40 border border-slate-700/50">
                <div className="text-[11px] text-slate-400">Project Evidence (25%)</div>
                <div className="text-lg font-bold text-indigo-400 mt-1">75%</div>
                <div className="text-[10px] text-slate-400 mt-1">2 verified GitHub repos</div>
              </div>
              <div className="p-3.5 rounded-xl bg-slate-800/40 border border-slate-700/50">
                <div className="text-[11px] text-slate-400">Market Relevance (25%)</div>
                <div className="text-lg font-bold text-purple-400 mt-1">85%</div>
                <div className="text-[10px] text-slate-400 mt-1">Stripe, Linear 90%+ match</div>
              </div>
              <div className="p-3.5 rounded-xl bg-slate-800/40 border border-slate-700/50">
                <div className="text-[11px] text-slate-400">Interview Fluency (15%)</div>
                <div className="text-lg font-bold text-amber-400 mt-1">70%</div>
                <div className="text-[10px] text-slate-400 mt-1">Idempotency STAR ready</div>
              </div>
            </div>
          </div>
        )}

        {/* Tab 2: Skill Gaps */}
        {activeTab === 'skills' && (
          <div className="space-y-4 animate-in fade-in duration-200">
            <p className="text-xs text-slate-400">
              Deterministic skill taxonomy compares self-reported claims against diagnostic code assessments and target job market demands.
            </p>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {/* Verified Strengths */}
              <div className="space-y-2 p-3.5 rounded-xl bg-slate-800/40 border border-emerald-500/20">
                <div className="flex items-center gap-1.5 text-xs font-bold text-emerald-400 uppercase tracking-wider">
                  <CheckCircle2 className="w-3.5 h-3.5" /> Verified Strengths
                </div>
                <div className="space-y-1.5 pt-1">
                  <div className="flex justify-between items-center text-xs p-2 rounded-lg bg-slate-800/70">
                    <span className="font-semibold text-white">TypeScript</span>
                    <span className="font-mono text-emerald-400 font-bold">92%</span>
                  </div>
                  <div className="flex justify-between items-center text-xs p-2 rounded-lg bg-slate-800/70">
                    <span className="font-semibold text-white">React 18 / Next.js</span>
                    <span className="font-mono text-emerald-400 font-bold">88%</span>
                  </div>
                  <div className="flex justify-between items-center text-xs p-2 rounded-lg bg-slate-800/70">
                    <span className="font-semibold text-white">PostgreSQL & SQL Tuning</span>
                    <span className="font-mono text-emerald-400 font-bold">84%</span>
                  </div>
                </div>
              </div>

              {/* Developing */}
              <div className="space-y-2 p-3.5 rounded-xl bg-slate-800/40 border border-amber-500/20">
                <div className="flex items-center gap-1.5 text-xs font-bold text-amber-400 uppercase tracking-wider">
                  <Clock className="w-3.5 h-3.5" /> Developing Skills
                </div>
                <div className="space-y-1.5 pt-1">
                  <div className="flex justify-between items-center text-xs p-2 rounded-lg bg-slate-800/70">
                    <span className="font-semibold text-white">Redis Caching</span>
                    <span className="font-mono text-amber-400 font-bold">65%</span>
                  </div>
                  <div className="flex justify-between items-center text-xs p-2 rounded-lg bg-slate-800/70">
                    <span className="font-semibold text-white">Distributed Architecture</span>
                    <span className="font-mono text-amber-400 font-bold">60%</span>
                  </div>
                  <div className="flex justify-between items-center text-xs p-2 rounded-lg bg-slate-800/70">
                    <span className="font-semibold text-white">GraphQL APIs</span>
                    <span className="font-mono text-amber-400 font-bold">58%</span>
                  </div>
                </div>
              </div>

              {/* Identified Gaps */}
              <div className="space-y-2 p-3.5 rounded-xl bg-slate-800/40 border border-rose-500/20">
                <div className="flex items-center gap-1.5 text-xs font-bold text-rose-400 uppercase tracking-wider">
                  <AlertCircle className="w-3.5 h-3.5" /> Identified Market Gaps
                </div>
                <div className="space-y-1.5 pt-1">
                  <div className="flex justify-between items-center text-xs p-2 rounded-lg bg-slate-800/70">
                    <span className="font-semibold text-white">Kubernetes Orchestration</span>
                    <span className="font-mono text-rose-400 font-bold">Gap</span>
                  </div>
                  <div className="flex justify-between items-center text-xs p-2 rounded-lg bg-slate-800/70">
                    <span className="font-semibold text-white">Distributed Tracing (OTel)</span>
                    <span className="font-mono text-rose-400 font-bold">Gap</span>
                  </div>
                  <div className="flex justify-between items-center text-xs p-2 rounded-lg bg-slate-800/70">
                    <span className="font-semibold text-white">Apache Kafka Streams</span>
                    <span className="font-mono text-rose-400 font-bold">Gap</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Tab 3: Dynamic Roadmap */}
        {activeTab === 'roadmap' && (
          <div className="space-y-4 animate-in fade-in duration-200">
            <div className="flex items-center justify-between text-xs">
              <span className="font-semibold text-purple-400 uppercase tracking-wider text-[11px]">
                Phase 1: High-Performance Caching & Data Consistency (75% Complete)
              </span>
              <span className="text-slate-400">Weeks 1 – 3</span>
            </div>

            <div className="space-y-2.5">
              <div className="p-3 rounded-xl bg-slate-800/50 border border-emerald-500/30 flex items-start gap-3">
                <CheckCircle2 className="w-4 h-4 text-emerald-400 mt-0.5 shrink-0" />
                <div className="flex-1 text-xs">
                  <div className="font-semibold text-white">Master Cache-Aside and Write-Through Strategies</div>
                  <p className="text-slate-400 mt-0.5 text-[11px]">
                    Implemented distributed locking with Redlock and evaluated race conditions.
                  </p>
                </div>
                <Badge variant="verified" size="sm">Completed</Badge>
              </div>

              <div className="p-3 rounded-xl bg-slate-800/50 border border-emerald-500/30 flex items-start gap-3">
                <CheckCircle2 className="w-4 h-4 text-emerald-400 mt-0.5 shrink-0" />
                <div className="flex-1 text-xs">
                  <div className="font-semibold text-white">Build Distributed Rate Limiter with Sliding Window</div>
                  <p className="text-slate-400 mt-0.5 text-[11px]">
                    Created Express middleware enforcing sliding log rate limit using Redis Sorted Sets.
                  </p>
                </div>
                <Badge variant="verified" size="sm">Completed</Badge>
              </div>

              <div className="p-3 rounded-xl bg-slate-800/80 border border-amber-500/40 flex items-start gap-3">
                <Clock className="w-4 h-4 text-amber-400 mt-0.5 shrink-0 animate-pulse" />
                <div className="flex-1 text-xs">
                  <div className="font-semibold text-white">Take Redis Architecture Diagnostic Assessment</div>
                  <p className="text-slate-400 mt-0.5 text-[11px]">
                    Verify conceptual mastery across LRU eviction and pub/sub message loss semantics.
                  </p>
                </div>
                <Badge variant="action" size="sm">In Progress</Badge>
              </div>
            </div>
          </div>
        )}

        {/* Tab 4: Anti-Hallucination Diff */}
        {activeTab === 'diff' && (
          <div className="space-y-4 animate-in fade-in duration-200">
            <div className="flex items-center justify-between text-xs pb-1 border-b border-slate-800">
              <div className="flex items-center gap-2">
                <ShieldCheck className="w-4 h-4 text-emerald-400" />
                <span className="font-bold text-white">Two-Pass Grounded Resume Optimization</span>
              </div>
              <span className="font-mono text-purple-400 text-[11px]">+12% Match Score Boost</span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs font-mono">
              <div className="p-3 rounded-xl bg-rose-950/20 border border-rose-900/50">
                <div className="text-[10px] text-rose-400 font-bold uppercase mb-1">Original Bullet</div>
                <div className="text-slate-300 leading-relaxed">
                  &ldquo;Worked on backend services and database queries for webhooks, fixing slow queries when traffic spiked.&rdquo;
                </div>
              </div>

              <div className="p-3 rounded-xl bg-emerald-950/20 border border-emerald-900/50">
                <div className="text-[10px] text-emerald-400 font-bold uppercase mb-1">Tailored Bullet (Evidence-Backed)</div>
                <div className="text-emerald-200 font-medium leading-relaxed">
                  &ldquo;Architected asynchronous webhook ingestion engine handling 250,000+ daily events, tuning PostgreSQL B-tree indices to eliminate query bottlenecks and sustain 99.98% uptime.&rdquo;
                </div>
              </div>
            </div>

            <div className="p-3 rounded-xl bg-slate-800/60 border border-slate-700/50 text-xs flex items-center justify-between">
              <div className="flex items-center gap-2 text-slate-300">
                <Sparkles className="w-3.5 h-3.5 text-purple-400 shrink-0" />
                <span>
                  <strong>Evidence Grounding:</strong> Verified by Project QueryLens & Assessment PostgreSQL Indexing (84%).
                </span>
              </div>
              <Badge variant="verified" size="sm">Human Approved</Badge>
            </div>
          </div>
        )}
      </div>

      {/* Footer bar */}
      <div className="p-4 bg-slate-950/80 border-t border-slate-800 flex flex-col sm:flex-row items-center justify-between gap-3 text-xs">
        <span className="text-slate-400">
          Ready to experience your own personalized career graph?
        </span>
        <div className="flex items-center gap-3">
          <Link href="/dashboard">
            <Button size="sm" variant="intelligence">
              Explore Live Sandbox
            </Button>
          </Link>
          <Link href="/signup">
            <Button size="sm" variant="primary">
              Build Your Profile
            </Button>
          </Link>
        </div>
      </div>
    </div>
  );
}
