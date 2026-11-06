'use client';

import * as React from 'react';
import Link from 'next/link';
import { RoadmapData } from '@/types';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  RotateCcw,
  Sparkles,
  ClipboardCheck,
  Cpu,
  RefreshCw,
  ExternalLink,
  Award,
  Layers,
} from 'lucide-react';

interface RoadmapHeaderProps {
  roadmap: RoadmapData;
  onOpenRegenerateModal: () => void;
  onAdaptRoadmap: () => Promise<void>;
  isAdapting: boolean;
}

export function RoadmapHeader({
  roadmap,
  onOpenRegenerateModal,
  onAdaptRoadmap,
  isAdapting,
}: RoadmapHeaderProps) {
  return (
    <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 pb-1 border-b border-slate-200/80 dark:border-white/10">
      <div className="space-y-1.5">
        <div className="flex flex-wrap items-center gap-2">
          <Badge variant="verified" size="sm">
            {roadmap.target_role_title}
          </Badge>

          <span className="font-mono text-xs px-2 py-0.5 rounded bg-slate-100 dark:bg-white/[0.07] text-slate-600 dark:text-ink-fg/80 font-semibold border border-slate-200 dark:border-white/15">
            v{roadmap.version}
          </span>

          <Badge variant="outline" size="sm" className="capitalize text-[10px]">
            {roadmap.status}
          </Badge>
        </div>

        <h1 className="font-display text-3xl font-semibold tracking-[-0.035em] text-slate-900 dark:text-ink-fg [text-wrap:balance] md:text-4xl">
          {roadmap.title}
        </h1>

        {roadmap.description && (
          <p className="text-xs text-slate-600 dark:text-ink-fg/80 max-w-3xl leading-relaxed">
            {roadmap.description}
          </p>
        )}
      </div>

      {/* Action Buttons */}
      <div className="flex flex-wrap items-center gap-2 shrink-0">
        <Button
          size="sm"
          variant="outline"
          className="text-xs h-8"
          onClick={onAdaptRoadmap}
          disabled={isAdapting}
          title="Scans for newly passed diagnostic skill assessments and auto-completes corresponding milestones"
        >
          <Sparkles className={`w-3.5 h-3.5 mr-1.5 text-brand-600 ${isAdapting ? 'animate-spin' : ''}`} />
          {isAdapting ? 'Adapting...' : 'Adapt to Evidence'}
        </Button>

        <Button
          size="sm"
          variant="outline"
          className="text-xs h-8"
          onClick={onOpenRegenerateModal}
        >
          <RotateCcw className="w-3.5 h-3.5 mr-1.5" /> Regenerate
        </Button>

        <Link href="/skills">
          <Button size="sm" variant="ghost" className="text-xs h-8">
            <Cpu className="w-3.5 h-3.5 mr-1.5 text-purple-600 dark:text-lav" /> Skill Gaps
          </Button>
        </Link>

        <Link href="/assessments">
          <Button size="sm" variant="ghost" className="text-xs h-8">
            <ClipboardCheck className="w-3.5 h-3.5 mr-1.5 text-emerald-600 dark:text-lime" /> Diagnostic Tests
          </Button>
        </Link>
      </div>
    </div>
  );
}
