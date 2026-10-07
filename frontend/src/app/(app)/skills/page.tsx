'use client';

import * as React from 'react';
import Link from 'next/link';
import { mockSkills } from '@/lib/mock/data';
import { SkillItem, SkillStatus } from '@/types';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { SkillBadge } from '@/components/ui/skill-badge';
import { Tabs } from '@/components/ui/tabs';
import {
  Cpu,
  CheckCircle2,
  Clock,
  AlertCircle,
  Plus,
  ArrowRight,
  ClipboardCheck,
  Compass,
  Filter,
} from 'lucide-react';

export default function SkillsPage() {
  const [statusFilter, setStatusFilter] = React.useState<string>('all');
  const [selectedCategory, setSelectedCategory] = React.useState<string>('All');

  const categories = ['All', 'Languages', 'Frameworks', 'Databases', 'Cloud & DevOps', 'Architecture'];

  const verifiedSkills = mockSkills.filter((s) => s.status === 'verified');
  const developingSkills = mockSkills.filter((s) => s.status === 'developing');
  const missingSkills = mockSkills.filter((s) => s.status === 'missing');

  const filteredSkills = mockSkills.filter((s) => {
    const matchesStatus = statusFilter === 'all' || s.status === statusFilter;
    const matchesCategory = selectedCategory === 'All' || s.category === selectedCategory;
    return matchesStatus && matchesCategory;
  });

  const filterTabs = [
    { id: 'all', label: 'All Tracked Skills', badge: mockSkills.length },
    { id: 'verified', label: 'Verified Strengths', badge: verifiedSkills.length },
    { id: 'developing', label: 'Developing', badge: developingSkills.length },
    { id: 'missing', label: 'Identified Gaps', badge: missingSkills.length },
  ];

  return (
    <div className="space-y-6">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-slate-900 dark:text-white">
            Skill Taxonomy & Competency Engine
          </h2>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
            Grounded verification compares your profile against role standards for <strong className="text-purple-600">Full-Stack Engineer</strong>.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Link href="/assessments">
            <Button size="sm" variant="intelligence">
              <ClipboardCheck className="w-3.5 h-3.5 mr-1.5" /> Take Assessment
            </Button>
          </Link>
          <Button size="sm" variant="outline">
            <Plus className="w-3.5 h-3.5 mr-1" /> Add Skill Claim
          </Button>
        </div>
      </div>

      {/* Tri-State Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Verified Card */}
        <Card className="p-5 border-emerald-200 bg-emerald-50/20 dark:bg-emerald-950/20 space-y-2">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-emerald-700 dark:text-emerald-300 font-bold text-sm">
              <CheckCircle2 className="w-4 h-4" />
              <span>Verified Strengths</span>
            </div>
            <span className="text-xl font-extrabold text-emerald-700 dark:text-emerald-300">
              {verifiedSkills.length}
            </span>
          </div>
          <p className="text-xs text-slate-600 dark:text-slate-400">
            Validated by diagnostic coding assessments and GitHub project evidence.
          </p>
        </Card>

        {/* Developing Card */}
        <Card className="p-5 border-amber-200 bg-amber-50/20 dark:bg-amber-950/20 space-y-2">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-amber-700 dark:text-amber-300 font-bold text-sm">
              <Clock className="w-4 h-4" />
              <span>Developing Skills</span>
            </div>
            <span className="text-xl font-extrabold text-amber-700 dark:text-amber-300">
              {developingSkills.length}
            </span>
          </div>
          <p className="text-xs text-slate-600 dark:text-slate-400">
            Familiar concepts in progress. Ready for diagnostic calibration.
          </p>
        </Card>

        {/* Missing Gaps Card */}
        <Card className="p-5 border-rose-200 bg-rose-50/20 dark:bg-rose-950/20 space-y-2">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-rose-700 dark:text-rose-300 font-bold text-sm">
              <AlertCircle className="w-4 h-4" />
              <span>Target Market Gaps</span>
            </div>
            <span className="text-xl font-extrabold text-rose-700 dark:text-rose-300">
              {missingSkills.length}
            </span>
          </div>
          <p className="text-xs text-slate-600 dark:text-slate-400">
            Required by top employer listings (e.g. Stripe, Datadog) not yet demonstrated.
          </p>
        </Card>
      </div>

      {/* Filter Tabs & Category Filter */}
      <div className="space-y-4">
        <Tabs tabs={filterTabs} activeTab={statusFilter} onChange={setStatusFilter} />

        <div className="flex flex-wrap items-center gap-2 pt-1">
          <span className="text-xs text-slate-400 flex items-center gap-1 mr-1">
            <Filter className="w-3.5 h-3.5" /> Category:
          </span>
          {categories.map((cat) => (
            <button
              key={cat}
              onClick={() => setSelectedCategory(cat)}
              className={`px-3 py-1 rounded-lg text-xs font-medium transition-all ${
                selectedCategory === cat
                  ? 'bg-slate-900 text-white dark:bg-white dark:text-slate-900'
                  : 'bg-slate-100 text-slate-600 hover:bg-slate-200 dark:bg-slate-800 dark:text-slate-300'
              }`}
            >
              {cat}
            </button>
          ))}
        </div>
      </div>

      {/* Skills Table / Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filteredSkills.map((skill) => (
          <Card key={skill.id} className="p-4 flex flex-col justify-between space-y-3 hover:border-slate-300 transition-all">
            <div className="space-y-2">
              <div className="flex items-start justify-between gap-2">
                <div>
                  <h4 className="text-sm font-bold text-slate-900 dark:text-white">
                    {skill.name}
                  </h4>
                  <span className="text-[11px] text-slate-400 font-medium">
                    {skill.category}
                  </span>
                </div>
                <Badge
                  variant={
                    skill.status === 'verified'
                      ? 'verified'
                      : skill.status === 'developing'
                      ? 'action'
                      : 'gap'
                  }
                  size="sm"
                >
                  {skill.status === 'verified'
                    ? 'Verified'
                    : skill.status === 'developing'
                    ? 'Developing'
                    : 'Missing Gap'}
                </Badge>
              </div>

              <div className="space-y-1 pt-1">
                <div className="flex justify-between text-xs">
                  <span className="text-slate-500">Calibrated Confidence</span>
                  <span className="font-mono font-bold text-slate-800 dark:text-slate-200">
                    {skill.confidenceScore}%
                  </span>
                </div>
                <div className="w-full h-1.5 rounded-full bg-slate-100 dark:bg-slate-800 overflow-hidden">
                  <div
                    className={`h-full rounded-full ${
                      skill.status === 'verified'
                        ? 'bg-emerald-500'
                        : skill.status === 'developing'
                        ? 'bg-amber-500'
                        : 'bg-rose-500'
                    }`}
                    style={{ width: `${skill.confidenceScore}%` }}
                  />
                </div>
              </div>

              <div className="text-[11px] text-slate-500 pt-1 flex items-center justify-between">
                <span>Evidence: <strong className="text-slate-700 dark:text-slate-300">{skill.evidenceSource}</strong></span>
                {skill.lastEvaluated && (
                  <span className="text-slate-400">{skill.lastEvaluated}</span>
                )}
              </div>
            </div>

            <div className="pt-3 border-t border-slate-100 dark:border-slate-800 flex items-center justify-end gap-2">
              {skill.status === 'missing' && (
                <Link href="/roadmap">
                  <Button size="sm" variant="outline" className="text-xs">
                    <Compass className="w-3.5 h-3.5 mr-1" /> Add to Roadmap
                  </Button>
                </Link>
              )}
              {skill.status === 'developing' && (
                <Link href="/assessments">
                  <Button size="sm" variant="intelligence" className="text-xs">
                    Validate Now
                  </Button>
                </Link>
              )}
              {skill.status === 'verified' && (
                <span className="text-[11px] font-semibold text-emerald-600 flex items-center gap-1">
                  <CheckCircle2 className="w-3.5 h-3.5" /> High Confidence
                </span>
              )}
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
}
