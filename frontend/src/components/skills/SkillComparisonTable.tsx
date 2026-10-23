'use client';

import * as React from 'react';
import {
  SkillCompetencyDetailItem,
  SkillCompetencyStatus,
} from '@/types';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Tabs } from '@/components/ui/tabs';
import {
  Search,
  Filter,
  CheckCircle2,
  Clock,
  AlertCircle,
  FileQuestion,
  HelpCircle,
  ClipboardCheck,
  ShieldCheck,
  Eye,
  ArrowRight,
  Info,
} from 'lucide-react';
import Link from 'next/link';

interface SkillComparisonTableProps {
  skills: Record<string, SkillCompetencyDetailItem>;
  onInspectEvidence: (skillId: string, skillName: string) => void;
}

export function SkillComparisonTable({
  skills,
  onInspectEvidence,
}: SkillComparisonTableProps) {
  const [activeTab, setActiveTab] = React.useState<string>('all');
  const [selectedCategory, setSelectedCategory] = React.useState<string>('All');
  const [searchQuery, setSearchQuery] = React.useState<string>('');

  const skillList = Object.values(skills);

  // Categorize counts
  const strengths = skillList.filter((s) => s.status === 'STRENGTH');
  const developing = skillList.filter((s) => s.status === 'DEVELOPING');
  const gaps = skillList.filter((s) => s.status === 'GAP');
  const unassessed = skillList.filter((s) => s.status === 'NOT_ASSESSED');
  const missing = skillList.filter((s) => s.status === 'NOT_IN_PROFILE');

  // Categories list
  const uniqueCategories = ['All', ...Array.from(new Set(skillList.map((s) => s.category)))];

  // Filtering logic
  const filteredSkills = skillList.filter((skill) => {
    // 1. Tab filter
    if (activeTab === 'strengths' && skill.status !== 'STRENGTH') return false;
    if (activeTab === 'developing' && skill.status !== 'DEVELOPING') return false;
    if (activeTab === 'gaps' && skill.status !== 'GAP') return false;
    if (activeTab === 'unassessed' && skill.status !== 'NOT_ASSESSED') return false;
    if (activeTab === 'missing' && skill.status !== 'NOT_IN_PROFILE') return false;

    // 2. Category filter
    if (selectedCategory !== 'All' && skill.category.toLowerCase() !== selectedCategory.toLowerCase()) {
      return false;
    }

    // 3. Search query
    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase();
      const nameMatches = skill.skill_name.toLowerCase().includes(q);
      const catMatches = skill.category.toLowerCase().includes(q);
      const ratMatches = skill.rationale?.toLowerCase().includes(q);
      return nameMatches || catMatches || ratMatches;
    }

    return true;
  });

  const filterTabs = [
    { id: 'all', label: 'All Requirements', badge: skillList.length },
    { id: 'strengths', label: 'Strengths', badge: strengths.length },
    { id: 'developing', label: 'Developing', badge: developing.length },
    { id: 'gaps', label: 'Confirmed Gaps', badge: gaps.length },
    { id: 'unassessed', label: 'Needs Assessment', badge: unassessed.length },
    { id: 'missing', label: 'Missing in Profile', badge: missing.length },
  ];

  const getStatusBadge = (status: SkillCompetencyStatus) => {
    switch (status) {
      case 'STRENGTH':
        return (
          <Badge className="bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300 border-emerald-300 text-[10px] font-bold flex items-center gap-1">
            <CheckCircle2 className="w-3 h-3" /> STRENGTH
          </Badge>
        );
      case 'DEVELOPING':
        return (
          <Badge className="bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-300 border-amber-300 text-[10px] font-bold flex items-center gap-1">
            <Clock className="w-3 h-3" /> DEVELOPING
          </Badge>
        );
      case 'GAP':
        return (
          <Badge className="bg-rose-100 text-rose-800 dark:bg-rose-950 dark:text-rose-300 border-rose-300 text-[10px] font-bold flex items-center gap-1">
            <AlertCircle className="w-3 h-3" /> CONFIRMED GAP
          </Badge>
        );
      case 'NOT_ASSESSED':
        return (
          <Badge className="bg-purple-100 text-purple-800 dark:bg-purple-950 dark:text-purple-300 border-purple-300 text-[10px] font-bold flex items-center gap-1">
            <FileQuestion className="w-3 h-3" /> NEEDS ASSESSMENT
          </Badge>
        );
      case 'NOT_IN_PROFILE':
        return (
          <Badge className="bg-slate-200 text-slate-700 dark:bg-slate-800 dark:text-slate-300 border-slate-300 text-[10px] font-bold flex items-center gap-1">
            <HelpCircle className="w-3 h-3" /> NOT IN PROFILE
          </Badge>
        );
    }
  };

  const getImportanceBadge = (importance: string) => {
    switch (importance) {
      case 'mandatory':
        return (
          <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider bg-rose-50 text-rose-700 border border-rose-200 dark:bg-rose-950/40 dark:text-rose-300 dark:border-rose-900">
            Mandatory
          </span>
        );
      case 'preferred':
        return (
          <span className="px-2 py-0.5 rounded text-[10px] font-semibold uppercase tracking-wider bg-sky-50 text-sky-700 border border-sky-200 dark:bg-sky-950/40 dark:text-sky-300 dark:border-sky-900">
            Preferred
          </span>
        );
      default:
        return (
          <span className="px-2 py-0.5 rounded text-[10px] font-medium uppercase tracking-wider bg-slate-100 text-slate-600 border border-slate-200 dark:bg-slate-800 dark:text-slate-400 dark:border-slate-700">
            Bonus
          </span>
        );
    }
  };

  const getLevelLabel = (lvl: number) => {
    switch (lvl) {
      case 1:
        return 'Foundational';
      case 2:
        return 'Developing';
      case 3:
        return 'Proficient';
      case 4:
        return 'Advanced';
      default:
        return 'Not Assessed';
    }
  };

  return (
    <div className="space-y-4">
      {/* Tabs */}
      <Tabs tabs={filterTabs} activeTab={activeTab} onChange={setActiveTab} />

      {/* Filter and Search Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pt-1">
        {/* Search */}
        <div className="relative w-full sm:w-72">
          <Search className="w-3.5 h-3.5 absolute left-3 top-3 text-slate-400" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search role skills or rationale..."
            className="w-full pl-9 pr-3 py-1.5 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 text-xs text-slate-900 dark:text-white placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500"
          />
        </div>

        {/* Categories */}
        <div className="flex flex-wrap items-center gap-1.5">
          <span className="text-xs text-slate-400 flex items-center gap-1 mr-1">
            <Filter className="w-3.5 h-3.5" /> Category:
          </span>
          {uniqueCategories.map((cat) => (
            <button
              key={cat}
              onClick={() => setSelectedCategory(cat)}
              className={`px-2.5 py-1 rounded-lg text-xs font-medium capitalize transition-all ${
                selectedCategory.toLowerCase() === cat.toLowerCase()
                  ? 'bg-slate-900 text-white dark:bg-white dark:text-slate-900'
                  : 'bg-slate-100 text-slate-600 hover:bg-slate-200 dark:bg-slate-800 dark:text-slate-300'
              }`}
            >
              {cat}
            </button>
          ))}
        </div>
      </div>

      {/* Results Count & Grid */}
      {filteredSkills.length === 0 ? (
        <Card className="p-8 text-center space-y-2 border-dashed border-slate-200 dark:border-slate-800">
          <p className="text-xs text-slate-500 dark:text-slate-400">
            No role skills match your selected filters.
          </p>
          <Button
            size="sm"
            variant="outline"
            className="text-xs"
            onClick={() => {
              setActiveTab('all');
              setSelectedCategory('All');
              setSearchQuery('');
            }}
          >
            Reset Filters
          </Button>
        </Card>
      ) : (
        <div className="grid grid-cols-1 gap-3">
          {filteredSkills.map((skill) => {
            const hasAssessmentEvidence = skill.evidence_items.some((e) => e.source === 'assessment');
            const hasAssessmentRecommendation = skill.status === 'NOT_ASSESSED' || skill.status === 'NOT_IN_PROFILE' || skill.status === 'GAP';

            return (
              <Card
                key={skill.skill_id}
                className="p-4 sm:p-5 border-slate-200 dark:border-slate-800 hover:border-slate-300 dark:hover:border-slate-700 transition-all space-y-3 bg-white dark:bg-slate-900 shadow-sm"
              >
                <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-3">
                  {/* Left: Skill Identity & Category */}
                  <div className="space-y-1">
                    <div className="flex flex-wrap items-center gap-2">
                      <h4 className="text-sm font-bold text-slate-900 dark:text-white">
                        {skill.skill_name}
                      </h4>
                      <Badge variant="outline" className="text-[10px] capitalize">
                        {skill.category}
                      </Badge>
                      {getImportanceBadge(skill.importance)}
                      {getStatusBadge(skill.status)}
                    </div>
                    {skill.rationale && (
                      <p className="text-xs text-slate-500 dark:text-slate-400 line-clamp-2">
                        {skill.rationale}
                      </p>
                    )}
                  </div>

                  {/* Actions */}
                  <div className="flex items-center gap-2 shrink-0 self-end lg:self-center">
                    <Button
                      size="sm"
                      variant="outline"
                      className="text-xs h-8"
                      onClick={() => onInspectEvidence(skill.skill_id, skill.skill_name)}
                    >
                      <Eye className="w-3.5 h-3.5 mr-1" />
                      Evidence ({skill.evidence_count})
                    </Button>

                    <Link href={`/assessments`}>
                      <Button size="sm" variant={hasAssessmentRecommendation ? 'intelligence' : 'secondary'} className="text-xs h-8">
                        <ClipboardCheck className="w-3.5 h-3.5 mr-1" />
                        Assess
                      </Button>
                    </Link>
                  </div>
                </div>

                {/* Level Comparison Visualizer */}
                <div className="pt-2 border-t border-slate-100 dark:border-slate-800/80 grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
                  {/* Required Level */}
                  <div className="space-y-1.5">
                    <div className="flex items-center justify-between text-[11px]">
                      <span className="text-slate-500">Benchmark Requirement:</span>
                      <span className="font-bold text-slate-800 dark:text-slate-200">
                        Level {skill.required_level} ({getLevelLabel(skill.required_level)})
                      </span>
                    </div>
                    {/* Segmented Level Bar (1-4) */}
                    <div className="grid grid-cols-4 gap-1.5 h-2">
                      {[1, 2, 3, 4].map((step) => (
                        <div
                          key={step}
                          className={`rounded-sm transition-all ${
                            step <= skill.required_level
                              ? 'bg-slate-700 dark:bg-slate-300'
                              : 'bg-slate-100 dark:bg-slate-800'
                          }`}
                        />
                      ))}
                    </div>
                  </div>

                  {/* Current Supported Level */}
                  <div className="space-y-1.5">
                    <div className="flex items-center justify-between text-[11px]">
                      <span className="text-slate-500">Supported Evidence Level:</span>
                      <span className={`font-bold ${
                        skill.current_level >= skill.required_level
                          ? 'text-emerald-600 dark:text-emerald-400'
                          : skill.current_level > 0
                          ? 'text-amber-600 dark:text-amber-400'
                          : 'text-slate-400'
                      }`}>
                        {skill.current_level > 0
                          ? `Level ${skill.current_level} (${getLevelLabel(skill.current_level)})`
                          : 'Level 0 (Unobserved)'}
                      </span>
                    </div>
                    {/* Segmented Level Bar (0-4) */}
                    <div className="grid grid-cols-4 gap-1.5 h-2">
                      {[1, 2, 3, 4].map((step) => {
                        const isMet = step <= skill.current_level;
                        const isStrength = isMet && skill.current_level >= skill.required_level;
                        const isDeveloping = isMet && skill.current_level < skill.required_level;
                        return (
                          <div
                            key={step}
                            className={`rounded-sm transition-all ${
                              isStrength
                                ? 'bg-emerald-500'
                                : isDeveloping
                                ? 'bg-amber-500'
                                : 'bg-slate-100 dark:bg-slate-800'
                            }`}
                          />
                        );
                      })}
                    </div>
                  </div>
                </div>

                {/* Remedial Recommendation Text */}
                {skill.recommended_action && (
                  <div className="p-2.5 rounded-lg bg-slate-50 dark:bg-slate-800/40 text-[11px] text-slate-600 dark:text-slate-400 flex items-center justify-between">
                    <span className="flex items-center gap-1.5">
                      <span className="font-semibold text-slate-900 dark:text-slate-200">Recommended Action:</span>
                      {skill.recommended_action}
                    </span>
                    <span className="text-slate-400 shrink-0 font-mono text-[10px]">
                      Weight: {skill.weight.toFixed(2)}x
                    </span>
                  </div>
                )}
              </Card>
            );
          })}
        </div>
      )}
    </div>
  );
}
