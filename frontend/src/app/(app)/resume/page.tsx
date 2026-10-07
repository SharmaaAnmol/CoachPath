'use client';

import * as React from 'react';
import { mockResumeVersion } from '@/lib/mock/data';
import { ResumeDiffChange } from '@/types';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs } from '@/components/ui/tabs';
import { DiffViewer } from '@/components/ui/diff-viewer';
import {
  FileText,
  ShieldCheck,
  Sparkles,
  Download,
  Copy,
  Plus,
  CheckCircle2,
  FileCode,
} from 'lucide-react';

export default function ResumePage() {
  const [activeTab, setActiveTab] = React.useState('diff');
  const [changes, setChanges] = React.useState<ResumeDiffChange[]>(mockResumeVersion.changes);

  const tabs = [
    { id: 'diff', label: 'Anti-Hallucination Diff Review', icon: <Sparkles className="w-4 h-4" />, badge: `${changes.length} Changes` },
    { id: 'preview', label: 'Full Document Preview', icon: <FileText className="w-4 h-4" /> },
  ];

  const handleAcceptChange = (id: string) => {
    setChanges((prev) =>
      prev.map((c) => (c.id === id ? { ...c, status: 'accepted' } : c))
    );
  };

  const handleRejectChange = (id: string) => {
    setChanges((prev) =>
      prev.map((c) => (c.id === id ? { ...c, status: 'rejected' } : c))
    );
  };

  const acceptedCount = changes.filter((c) => c.status === 'accepted').length;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-2xl font-bold text-slate-900 dark:text-white">
              Truthful Resume Optimization & Diff Review
            </h2>
            <Badge variant="verified" size="sm">
              <ShieldCheck className="w-3.5 h-3.5 mr-1" /> Two-Pass Grounded
            </Badge>
          </div>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
            Active Version: <strong className="text-purple-600">{mockResumeVersion.versionName}</strong> &bull; Target: {mockResumeVersion.targetCompany}
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Button
            size="sm"
            variant="outline"
            onClick={() => {
              navigator.clipboard?.writeText(mockResumeVersion.fullMarkdown);
              alert('Resume Markdown copied to clipboard!');
            }}
          >
            <Copy className="w-3.5 h-3.5 mr-1.5" /> Copy Markdown
          </Button>
          <Button
            size="sm"
            variant="primary"
            onClick={() => alert('Compiling tailored resume to PDF...')}
          >
            <Download className="w-3.5 h-3.5 mr-1.5" /> Export PDF
          </Button>
        </div>
      </div>

      {/* Two-Pass Auditor Verification Banner */}
      <Card className="p-4 sm:p-5 bg-gradient-to-r from-purple-900 via-slate-900 to-indigo-950 text-white border-slate-800 space-y-3">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-xl bg-purple-500/20 border border-purple-400/30 flex items-center justify-center text-purple-300">
              <ShieldCheck className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-bold text-sm">Two-Pass Grounding Auditor Active</span>
                <span className="text-[10px] font-mono bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 px-2 py-0.5 rounded-full font-bold">
                  Zero Hallucinations
                </span>
              </div>
              <p className="text-xs text-slate-300 mt-0.5">
                Every suggested bullet is cross-referenced against your verified GitHub repositories and passed test scores.
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2 font-mono text-xs bg-slate-800/80 px-3 py-1.5 rounded-lg border border-slate-700">
            <span className="text-purple-300 font-bold">+{mockResumeVersion.matchScoreBoost}% Match Boost</span>
            <span className="text-slate-400">({acceptedCount} of {changes.length} Accepted)</span>
          </div>
        </div>
      </Card>

      {/* Tabs */}
      <Tabs tabs={tabs} activeTab={activeTab} onChange={setActiveTab} />

      {/* Tab 1: Diff Review */}
      {activeTab === 'diff' && (
        <div className="space-y-4">
          <div className="flex justify-between items-center text-xs text-slate-500">
            <span>Review and approve AI proposed phrasing. Only accepted changes will be baked into the export.</span>
            <span className="font-semibold">{acceptedCount} / {changes.length} Approved</span>
          </div>

          <div className="space-y-4">
            {changes.map((change) => (
              <DiffViewer
                key={change.id}
                change={change}
                onAccept={handleAcceptChange}
                onReject={handleRejectChange}
              />
            ))}
          </div>
        </div>
      )}

      {/* Tab 2: Full Document Preview */}
      {activeTab === 'preview' && (
        <Card className="p-8 font-mono text-xs leading-relaxed bg-white dark:bg-slate-900 border-slate-200 dark:border-slate-800 overflow-x-auto whitespace-pre-line shadow-card">
          {mockResumeVersion.fullMarkdown}
        </Card>
      )}
    </div>
  );
}
