'use client';

import * as React from 'react';
import { mockRecruiters } from '@/lib/mock/data';
import { RecruiterContact } from '@/types';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Alert } from '@/components/ui/alert';
import { DemoPreviewBanner } from '@/components/ui/demo-preview-banner';
import {
  Users,
  Copy,
  Check,
  ShieldCheck,
  Building2,
  ExternalLink,
  Mail,
  Linkedin,
} from 'lucide-react';

export default function RecruitersPage() {
  const [recruiters, setRecruiters] = React.useState<RecruiterContact[]>(mockRecruiters);
  const [copiedId, setCopiedId] = React.useState<string | null>(null);

  const handleCopy = (recruiter: RecruiterContact) => {
    const textToCopy = `Subject: ${recruiter.outreachDraftSubject}\n\n${recruiter.outreachDraftBody}`;
    navigator.clipboard?.writeText(textToCopy);
    setCopiedId(recruiter.id);
    setRecruiters((prev) =>
      prev.map((r) => (r.id === recruiter.id ? { ...r, copiedToClipboard: true } : r))
    );
    setTimeout(() => setCopiedId(null), 2500);
  };

  return (
    <div className="space-y-6">
      {/* Demo Preview Banner */}
      <DemoPreviewBanner
        plannedPhase="Phase 13"
        featureName="Recruiter discovery & outreach"
      />

      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="font-display text-3xl font-semibold tracking-[-0.035em] text-slate-900 dark:text-ink-fg [text-wrap:balance] md:text-4xl">
              Recruiter Discovery & Contextual Outreach
            </h1>
            <Badge variant="action" size="sm">
              <ShieldCheck className="w-3.5 h-3.5 mr-1" /> Human Gate Enforced
            </Badge>
          </div>
          <p className="text-xs text-slate-500 dark:text-ink-muted mt-1">
            Verified hiring leads mapped to your high-affinity match targets with high-signal personalized drafts.
          </p>
        </div>
      </div>

      {/* Human Approval Warning Banner */}
      <Alert
        variant="intelligence"
        title="Responsible Outreach Policy: Zero Automated Bot Spam"
      >
        <p className="text-xs leading-relaxed mt-1">
          To preserve candidate reputation, CoachPath will never send automated unsolicited emails on your behalf.
          Every message draft below must be personally reviewed, approved, and copied by you before sending.
        </p>
      </Alert>

      {/* Recruiters List */}
      <div className="space-y-6">
        {recruiters.map((recruiter) => {
          const isCopied = copiedId === recruiter.id || recruiter.copiedToClipboard;
          return (
            <Card key={recruiter.id} className="p-6 space-y-4 hover:border-slate-300 transition-all">
              <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4 pb-4 border-b border-slate-100 dark:border-white/10">
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <h3 className="text-lg font-bold dark:font-display dark:font-semibold dark:tracking-[-0.02em] text-slate-900 dark:text-white">
                      {recruiter.name}
                    </h3>
                    <Badge variant="default" size="sm">
                      {recruiter.company}
                    </Badge>
                  </div>
                  <p className="text-xs text-slate-600 dark:text-ink-fg/80">
                    {recruiter.role}
                  </p>
                  <p className="text-xs text-purple-700 dark:text-lav-light pt-0.5">
                    <strong>Why relevant:</strong> {recruiter.relevanceReason}
                  </p>
                </div>

                <div className="flex items-center gap-2 text-xs">
                  {recruiter.verifiedEmail && (
                    <span className="flex items-center gap-1 font-mono text-slate-500 bg-slate-100 dark:bg-white/[0.07] px-2.5 py-1 rounded-md">
                      <Mail className="w-3.5 h-3.5 text-slate-400" />
                      {recruiter.verifiedEmail}
                    </span>
                  )}
                  <a
                    href={recruiter.linkedInUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="p-2 rounded-lg bg-blue-50 text-blue-600 hover:bg-blue-100 dark:bg-lav/10 dark:text-lav dark:hover:bg-lav/10"
                    title="View LinkedIn Profile"
                  >
                    <Linkedin className="w-4 h-4" />
                  </a>
                </div>
              </div>

              {/* Message Draft Box */}
              <div className="space-y-2">
                <div className="flex items-center justify-between text-xs">
                  <span className="font-semibold text-slate-500 uppercase tracking-wider text-[11px]">
                    Personalized Outreach Draft (Grounded in Your Experience)
                  </span>
                  <span className="text-[11px] text-slate-400 font-mono">
                    Subject: {recruiter.outreachDraftSubject}
                  </span>
                </div>

                <div className="p-4 rounded-xl bg-slate-50 dark:bg-white/[0.07] border border-slate-200/90 dark:border-white/15 font-mono text-xs text-slate-800 dark:text-ink-fg whitespace-pre-line leading-relaxed">
                  {recruiter.outreachDraftBody}
                </div>
              </div>

              {/* Copy Gate Action */}
              <div className="flex items-center justify-between pt-2">
                <span className="text-xs text-slate-400">
                  {recruiter.copiedToClipboard
                    ? 'Copied to clipboard previously'
                    : 'Awaiting candidate review & copy action'}
                </span>

                <Button
                  size="sm"
                  variant={isCopied ? 'secondary' : 'primary'}
                  onClick={() => handleCopy(recruiter)}
                >
                  {isCopied ? (
                    <>
                      <Check className="w-3.5 h-3.5 mr-1 text-emerald-600 dark:text-lime" />
                      Copied to Clipboard
                    </>
                  ) : (
                    <>
                      <Copy className="w-3.5 h-3.5 mr-1" />
                      Copy Outreach Message
                    </>
                  )}
                </Button>
              </div>
            </Card>
          );
        })}
      </div>
    </div>
  );
}
