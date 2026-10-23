'use client';

import * as React from 'react';
import { Modal } from '@/components/ui/modal';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { skillGapClient } from '@/lib/skill-gap-client';
import { SkillEvidenceDetailResponse, SkillEvidenceItem } from '@/types';
import {
  ShieldCheck,
  AlertCircle,
  FileCheck,
  FolderGit2,
  User,
  ClipboardCheck,
  Clock,
  Sparkles,
  ExternalLink,
  CheckCircle2,
} from 'lucide-react';
import Link from 'next/link';

interface SkillEvidenceModalProps {
  skillId: string | null;
  skillName: string;
  isOpen: boolean;
  onClose: () => void;
}

export function SkillEvidenceModal({
  skillId,
  skillName,
  isOpen,
  onClose,
}: SkillEvidenceModalProps) {
  const [evidenceData, setEvidenceData] = React.useState<SkillEvidenceDetailResponse | null>(null);
  const [isLoading, setIsLoading] = React.useState(false);
  const [errorMessage, setErrorMessage] = React.useState<string | null>(null);

  React.useEffect(() => {
    if (!isOpen || !skillId) {
      setEvidenceData(null);
      return;
    }

    let isMounted = true;
    const fetchEvidence = async () => {
      try {
        setIsLoading(true);
        setErrorMessage(null);
        const data = await skillGapClient.getSkillEvidence(skillId);
        if (isMounted) {
          setEvidenceData(data);
        }
      } catch (err: any) {
        if (isMounted) {
          setErrorMessage(err?.message || 'Failed to retrieve evidence items.');
        }
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    };

    fetchEvidence();
    return () => {
      isMounted = false;
    };
  }, [isOpen, skillId]);

  const getSourceIcon = (source: string) => {
    switch (source) {
      case 'assessment':
        return <ClipboardCheck className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />;
      case 'project':
        return <FolderGit2 className="w-4 h-4 text-indigo-600 dark:text-indigo-400" />;
      case 'resume':
        return <FileCheck className="w-4 h-4 text-sky-600 dark:text-sky-400" />;
      default:
        return <User className="w-4 h-4 text-slate-500" />;
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={`Evidence Graph: ${skillName}`}
      description="Transparent provenance and verification trail supporting this competency."
      maxWidth="xl"
    >
      <div className="space-y-4 py-2">
        {isLoading && (
          <div className="py-8 flex flex-col items-center justify-center space-y-3">
            <div className="w-8 h-8 rounded-full border-2 border-indigo-600 border-t-transparent animate-spin" />
            <p className="text-xs text-slate-500">Retrieving calibrated evidence graph...</p>
          </div>
        )}

        {errorMessage && (
          <div className="p-3.5 rounded-xl bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-800 text-xs text-rose-700 dark:text-rose-300 flex items-start gap-2">
            <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
            <p>{errorMessage}</p>
          </div>
        )}

        {!isLoading && !errorMessage && evidenceData && (
          <div className="space-y-4">
            {/* Status Summary Banner */}
            <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 flex items-center justify-between">
              <div className="space-y-0.5">
                <div className="flex items-center gap-2">
                  <span className="text-xs font-bold text-slate-900 dark:text-white">
                    Level {evidenceData.current_level}
                  </span>
                  <span className="text-xs text-slate-400">•</span>
                  <span className="text-xs capitalize text-slate-600 dark:text-slate-300 font-medium">
                    {evidenceData.current_tier}
                  </span>
                </div>
                <div className="text-[11px] text-slate-400">
                  Category: <span className="capitalize">{evidenceData.category}</span>
                </div>
              </div>

              {evidenceData.is_verified ? (
                <Badge variant="outline" className="bg-emerald-50 text-emerald-700 border-emerald-300 dark:bg-emerald-950 dark:text-emerald-300 flex items-center gap-1 text-xs">
                  <ShieldCheck className="w-3.5 h-3.5" /> Verified Competency
                </Badge>
              ) : (
                <Badge variant="outline" className="bg-amber-50 text-amber-700 border-amber-300 dark:bg-amber-950 dark:text-amber-300 flex items-center gap-1 text-xs">
                  <AlertCircle className="w-3.5 h-3.5" /> Unverified Claim
                </Badge>
              )}
            </div>

            {/* Evidence List */}
            <div className="space-y-2.5">
              <h4 className="text-xs font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider">
                Supporting Evidence Artifacts ({evidenceData.evidence_items.length})
              </h4>

              {evidenceData.evidence_items.length === 0 ? (
                <div className="p-6 rounded-xl border border-dashed border-slate-200 dark:border-slate-800 text-center space-y-2">
                  <p className="text-xs text-slate-500 dark:text-slate-400">
                    No verified assessments, profile skills, or projects have been linked to {skillName} yet.
                  </p>
                  <Link href="/assessments">
                    <Button size="sm" variant="outline" className="text-xs mt-2">
                      <ClipboardCheck className="w-3.5 h-3.5 mr-1" /> Take Diagnostic Assessment
                    </Button>
                  </Link>
                </div>
              ) : (
                <div className="space-y-2 max-h-72 overflow-y-auto pr-1">
                  {evidenceData.evidence_items.map((item, idx) => (
                    <div
                      key={idx}
                      className="p-3 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 space-y-1.5 shadow-sm"
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          {getSourceIcon(item.source)}
                          <span className="font-semibold text-xs text-slate-900 dark:text-white">
                            {item.title}
                          </span>
                        </div>
                        <span className="text-[10px] text-slate-400 uppercase tracking-wider font-semibold">
                          {item.source}
                        </span>
                      </div>

                      <p className="text-xs text-slate-600 dark:text-slate-400 leading-relaxed">
                        {item.description}
                      </p>

                      <div className="flex items-center justify-between pt-1 border-t border-slate-100 dark:border-slate-800/80 text-[11px]">
                        <span className="text-slate-500">
                          Confidence: <strong className="text-slate-700 dark:text-slate-300">{(item.confidence_score * 100).toFixed(0)}%</strong>
                        </span>
                        <div className="flex items-center gap-2">
                          {item.score !== undefined && item.score !== null && (
                            <span className="font-bold text-indigo-600 dark:text-indigo-400">
                              Score: {item.score.toFixed(0)}%
                            </span>
                          )}
                          {item.is_verified ? (
                            <span className="text-emerald-600 dark:text-emerald-400 font-semibold flex items-center gap-0.5 text-[10px]">
                              <CheckCircle2 className="w-3 h-3" /> Verified
                            </span>
                          ) : (
                            <span className="text-amber-600 dark:text-amber-400 font-medium text-[10px]">
                              Unverified
                            </span>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            <div className="pt-2 flex justify-end">
              <Button size="sm" variant="outline" onClick={onClose}>
                Close
              </Button>
            </div>
          </div>
        )}
      </div>
    </Modal>
  );
}
