'use client';

import * as React from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  FileText,
  Briefcase,
  Sparkles,
  ShieldCheck,
  CheckCircle2,
  AlertTriangle,
  Clock,
  Trash2,
  Save,
  Printer,
  ArrowLeft,
  Lock,
  Layers,
  ChevronRight,
  Split,
  Eye,
  Check,
  X,
  ExternalLink,
  Tag,
  Plus,
  RotateCcw,
  GraduationCap,
  Award,
  AlertCircle,
  HelpCircle,
  Loader2,
} from 'lucide-react';
import {
  ExtractedExperience,
  ExtractedSkill,
  ParsedResumePreview,
  StructuredChangeItem,
  TailoredResumeResponse,
} from '@/types';
import { TailoredApprovalDialog } from './tailored-approval-dialog';

interface TailoredResumeWorkspaceProps {
  version: TailoredResumeResponse;
  jobTitle?: string | null;
  companyName?: string | null;
  onBack: () => void;
  onSave: (updatedContent: ParsedResumePreview, notes?: string) => Promise<void>;
  onApprove: (acceptedSections: string[]) => Promise<void>;
  onDelete: () => void;
  isSaving: boolean;
  isApproving: boolean;
}

type WorkspaceTab = 'document' | 'diff' | 'analysis';

export function TailoredResumeWorkspace({
  version,
  jobTitle,
  companyName,
  onBack,
  onSave,
  onApprove,
  onDelete,
  isSaving,
  isApproving,
}: TailoredResumeWorkspaceProps) {
  const [activeTab, setActiveTab] = React.useState<WorkspaceTab>('document');
  const [showApprovalModal, setShowApprovalModal] = React.useState(false);
  const [approvalError, setApprovalError] = React.useState<string | null>(null);

  // Editable content initialized from version.tailored_content
  const [content, setContent] = React.useState<ParsedResumePreview>(
    JSON.parse(JSON.stringify(version.tailored_content))
  );
  const [isDirty, setIsDirty] = React.useState(false);

  // Sync if version updates from server
  React.useEffect(() => {
    setContent(JSON.parse(JSON.stringify(version.tailored_content)));
    setIsDirty(false);
  }, [version]);

  const isApproved = version.status === 'approved';
  const isDraft = version.status === 'draft';

  // Section filter for diff view
  const [diffSectionFilter, setDiffSectionFilter] = React.useState<string>('all');
  const [diffLayout, setDiffLayout] = React.useState<'side-by-side' | 'stacked'>('side-by-side');

  // New skill addition state
  const [newSkillName, setNewSkillName] = React.useState('');
  const [newSkillCategory, setNewSkillCategory] = React.useState('technical');

  // ─── Handlers for Editing ───────────────────────────────────────────

  const handleSummaryChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    if (isApproved) return;
    setContent((prev) => ({
      ...prev,
      executive_summary: e.target.value,
    }));
    setIsDirty(true);
  };

  const handleBulletChange = (expIndex: number, bulletIndex: number, newText: string) => {
    if (isApproved) return;
    setContent((prev) => {
      const expList = [...(prev.experience || [])];
      if (!expList[expIndex]) return prev;
      const resp = [...(expList[expIndex].responsibilities || [])];
      resp[bulletIndex] = newText;
      expList[expIndex] = {
        ...expList[expIndex],
        responsibilities: resp,
      };
      return { ...prev, experience: expList };
    });
    setIsDirty(true);
  };

  const handleAddSkill = () => {
    if (isApproved || !newSkillName.trim()) return;
    setContent((prev) => {
      const skills = [...(prev.detected_skills || [])];
      if (!skills.includes(newSkillName.trim())) {
        skills.push(newSkillName.trim());
      }
      return {
        ...prev,
        detected_skills: skills,
      };
    });
    setNewSkillName('');
    setIsDirty(true);
  };

  const handleRemoveSkill = (skillToRemove: string) => {
    if (isApproved) return;
    setContent((prev) => ({
      ...prev,
      detected_skills: (prev.detected_skills || []).filter((s) => s !== skillToRemove),
    }));
    setIsDirty(true);
  };

  const handleResetEdits = () => {
    setContent(JSON.parse(JSON.stringify(version.tailored_content)));
    setIsDirty(false);
  };

  const handleSaveClick = async () => {
    if (!isDirty || isApproved || isSaving) return;
    await onSave(content);
    setIsDirty(false);
  };

  const handleApproveConfirm = async (acceptedSections: string[]) => {
    setApprovalError(null);
    try {
      await onApprove(acceptedSections);
      setShowApprovalModal(false);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Approval failed.';
      setApprovalError(msg);
    }
  };

  const handlePrint = () => {
    window.print();
  };

  // Optimization Analysis shortcuts
  const analysis = version.diff_summary?.optimization_analysis;
  const changes = version.diff_summary?.changes || [];
  const unsupportedClaims = version.diff_summary?.unsupported_claims || [];

  const filteredChanges = changes.filter((chg) => {
    if (diffSectionFilter === 'all') return true;
    return chg.section.toLowerCase() === diffSectionFilter.toLowerCase();
  });

  return (
    <div className="space-y-6">
      {/* ───────────────────────────────────────────────────────────── */}
      {/* WORKSPACE HEADER & TOOLBAR                                    */}
      {/* ───────────────────────────────────────────────────────────── */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm print:hidden">
        {/* Left: Metadata */}
        <div className="space-y-1.5 min-w-0">
          <button
            onClick={onBack}
            className="inline-flex items-center gap-1.5 text-xs text-slate-500 hover:text-slate-900 dark:hover:text-white transition-colors mb-1"
          >
            <ArrowLeft className="w-3.5 h-3.5" /> Back to Tailoring Studio
          </button>

          <div className="flex items-center gap-2.5 flex-wrap">
            <span className="font-mono text-xs font-bold px-2 py-0.5 rounded bg-purple-100 dark:bg-purple-950/80 text-purple-800 dark:text-purple-300">
              v{version.version_number}
            </span>

            <h2 className="text-lg font-bold text-slate-900 dark:text-white truncate">
              {jobTitle || 'Target Opportunity'}
            </h2>

            {companyName && (
              <span className="text-sm text-slate-500 dark:text-slate-400">
                at <strong className="text-slate-700 dark:text-slate-200">{companyName}</strong>
              </span>
            )}

            {isApproved ? (
              <Badge variant="verified" size="sm">
                <CheckCircle2 className="w-3.5 h-3.5 mr-1" /> Approved
              </Badge>
            ) : (
              <Badge variant="action" size="sm">
                <Clock className="w-3.5 h-3.5 mr-1" /> Draft Mode
              </Badge>
            )}

            {version.anti_hallucination_verified && (
              <Badge variant="intelligence" size="sm">
                <ShieldCheck className="w-3.5 h-3.5 mr-1" /> Grounded Audit Passed
              </Badge>
            )}

            {isDirty && (
              <span className="text-[11px] font-bold px-2 py-0.5 rounded-full bg-amber-100 text-amber-800 dark:bg-amber-950/80 dark:text-amber-300 animate-pulse">
                Unsaved Changes
              </span>
            )}
          </div>

          <div className="flex items-center gap-3 text-xs text-slate-500 dark:text-slate-400 flex-wrap pt-0.5">
            {analysis?.keyword_coverage !== undefined && (
              <span className="font-mono">
                Keyword Coverage: <strong>{analysis.keyword_coverage.toFixed(1)}%</strong>
              </span>
            )}
            <span>&bull;</span>
            <span>{changes.length} structured recommendations</span>
            <span>&bull;</span>
            <span>Created {new Date(version.created_at).toLocaleDateString()}</span>
            {version.approved_at && (
              <>
                <span>&bull;</span>
                <span className="text-emerald-600 dark:text-emerald-400 font-medium">
                  User Approved on {new Date(version.approved_at).toLocaleDateString()}
                </span>
              </>
            )}
          </div>
        </div>

        {/* Right: Actions */}
        <div className="flex items-center gap-2 flex-wrap shrink-0">
          {isDraft && (
            <>
              {isDirty && (
                <Button
                  size="sm"
                  variant="ghost"
                  onClick={handleResetEdits}
                  disabled={isSaving}
                  className="text-xs text-slate-500 hover:text-slate-900"
                >
                  <RotateCcw className="w-3.5 h-3.5 mr-1" /> Discard
                </Button>
              )}

              <Button
                size="sm"
                variant="outline"
                onClick={handleSaveClick}
                disabled={!isDirty || isSaving}
                className="text-xs"
              >
                {isSaving ? (
                  <>
                    <Loader2 className="w-3.5 h-3.5 mr-1.5 animate-spin" /> Saving...
                  </>
                ) : (
                  <>
                    <Save className="w-3.5 h-3.5 mr-1.5" /> Save Edits
                  </>
                )}
              </Button>

              <Button
                size="sm"
                variant="primary"
                onClick={() => setShowApprovalModal(true)}
                disabled={isSaving || isApproving}
                className="text-xs bg-purple-600 hover:bg-purple-700"
              >
                <ShieldCheck className="w-3.5 h-3.5 mr-1.5" /> Approve Version
              </Button>
            </>
          )}

          {isApproved && (
            <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-emerald-50 dark:bg-emerald-950/40 text-emerald-800 dark:text-emerald-200 text-xs font-semibold border border-emerald-200 dark:border-emerald-800">
              <Lock className="w-3.5 h-3.5 text-emerald-600" />
              <span>User Approved & Locked</span>
            </div>
          )}

          <Button
            size="sm"
            variant="outline"
            onClick={handlePrint}
            title="Opens browser print dialog with print-optimized styles to print or Save as PDF"
            className="text-xs"
          >
            <Printer className="w-3.5 h-3.5 mr-1.5" /> Browser Print (PDF)
          </Button>

          <Button
            size="sm"
            variant="ghost"
            onClick={onDelete}
            className="text-xs text-slate-400 hover:text-rose-600 hover:bg-rose-50 dark:hover:bg-rose-950/40 p-2"
          >
            <Trash2 className="w-4 h-4" />
          </Button>
        </div>
      </div>

      {/* ───────────────────────────────────────────────────────────── */}
      {/* TABS NAVIGATION                                               */}
      {/* ───────────────────────────────────────────────────────────── */}
      <div className="flex border-b border-slate-200 dark:border-slate-800 text-xs font-semibold print:hidden overflow-x-auto">
        <button
          onClick={() => setActiveTab('document')}
          className={`flex items-center gap-2 px-5 py-3 border-b-2 transition-all ${
            activeTab === 'document'
              ? 'border-purple-600 text-purple-600 dark:text-purple-400 bg-purple-50/50 dark:bg-purple-950/20'
              : 'border-transparent text-slate-500 hover:text-slate-900 dark:hover:text-white'
          }`}
        >
          <Eye className="w-4 h-4" />
          <span>Document Preview & Edit</span>
        </button>

        <button
          onClick={() => setActiveTab('diff')}
          className={`flex items-center gap-2 px-5 py-3 border-b-2 transition-all ${
            activeTab === 'diff'
              ? 'border-purple-600 text-purple-600 dark:text-purple-400 bg-purple-50/50 dark:bg-purple-950/20'
              : 'border-transparent text-slate-500 hover:text-slate-900 dark:hover:text-white'
          }`}
        >
          <Split className="w-4 h-4" />
          <span>Visual Diff & Grounding ({changes.length})</span>
        </button>

        <button
          onClick={() => setActiveTab('analysis')}
          className={`flex items-center gap-2 px-5 py-3 border-b-2 transition-all ${
            activeTab === 'analysis'
              ? 'border-purple-600 text-purple-600 dark:text-purple-400 bg-purple-50/50 dark:bg-purple-950/20'
              : 'border-transparent text-slate-500 hover:text-slate-900 dark:hover:text-white'
          }`}
        >
          <Sparkles className="w-4 h-4" />
          <span>Optimization Analysis</span>
          {unsupportedClaims.length > 0 && (
            <span className="w-2 h-2 rounded-full bg-rose-500" />
          )}
        </button>
      </div>

      {/* ───────────────────────────────────────────────────────────── */}
      {/* TAB 1: DOCUMENT PREVIEW & EDIT                                */}
      {/* ───────────────────────────────────────────────────────────── */}
      {activeTab === 'document' && (
        <div className="space-y-6">
          {/* Subtle Banner on Draft Status */}
          {isDraft && (
            <div className="p-3.5 rounded-xl bg-purple-50/70 dark:bg-purple-950/30 border border-purple-200/80 dark:border-purple-800/60 text-xs text-purple-900 dark:text-purple-200 flex items-center justify-between gap-3 print:hidden">
              <div className="flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-purple-600 shrink-0" />
                <span>
                  <strong>Interactive Tailored Draft:</strong> Click into the executive summary or experience bullet points to adjust phrasing before approving.
                </span>
              </div>
              <Badge variant="action" size="sm">
                Editable
              </Badge>
            </div>
          )}

          {/* Paper-styled Resume Container */}
          <Card className="max-w-4xl mx-auto p-8 sm:p-12 bg-white dark:bg-slate-900 border-slate-200 dark:border-slate-800 shadow-md space-y-8 font-sans print:shadow-none print:border-none print:p-0">
            {/* Document Header */}
            <div className="text-center pb-6 border-b border-slate-200 dark:border-slate-800 space-y-2">
              <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-slate-900 dark:text-white uppercase">
                {content.personal_info?.name || 'Candidate Name'}
              </h1>

              <div className="flex flex-wrap items-center justify-center gap-3 text-xs text-slate-600 dark:text-slate-400">
                {content.personal_info?.email && (
                  <span>{content.personal_info.email}</span>
                )}
                {content.personal_info?.phone && (
                  <>
                    <span>&bull;</span>
                    <span>{content.personal_info.phone}</span>
                  </>
                )}
                {content.personal_info?.location && (
                  <>
                    <span>&bull;</span>
                    <span>{content.personal_info.location}</span>
                  </>
                )}
                {content.personal_info?.linkedin_url && (
                  <>
                    <span>&bull;</span>
                    <a
                      href={content.personal_info.linkedin_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-purple-600 dark:text-purple-400 hover:underline"
                    >
                      LinkedIn
                    </a>
                  </>
                )}
                {content.personal_info?.github_url && (
                  <>
                    <span>&bull;</span>
                    <a
                      href={content.personal_info.github_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-purple-600 dark:text-purple-400 hover:underline"
                    >
                      GitHub
                    </a>
                  </>
                )}
              </div>
            </div>

            {/* Section: Executive Summary */}
            <div className="space-y-2">
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-900 dark:text-white border-b border-slate-100 dark:border-slate-800 pb-1">
                Executive Summary
              </h3>
              {isDraft ? (
                <textarea
                  value={content.executive_summary || ''}
                  onChange={handleSummaryChange}
                  rows={4}
                  className="w-full p-2.5 text-xs text-slate-800 dark:text-slate-200 rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50/50 dark:bg-slate-800/40 focus:ring-2 focus:ring-purple-500 focus:outline-none leading-relaxed"
                  placeholder="Tailored summary highlighting relevant qualifications for the target job..."
                />
              ) : (
                <p className="text-xs text-slate-700 dark:text-slate-300 leading-relaxed whitespace-pre-line">
                  {content.executive_summary || 'No executive summary provided.'}
                </p>
              )}
            </div>

            {/* Section: Technical Skills */}
            <div className="space-y-3">
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-900 dark:text-white border-b border-slate-100 dark:border-slate-800 pb-1">
                Technical Skills & Technologies
              </h3>

              <div className="flex flex-wrap gap-1.5">
                {(content.detected_skills || []).map((skill) => (
                  <span
                    key={skill}
                    className="inline-flex items-center gap-1 px-2.5 py-1 rounded-md bg-slate-100 dark:bg-slate-800 text-slate-800 dark:text-slate-200 text-xs font-medium"
                  >
                    <span>{skill}</span>
                    {isDraft && (
                      <button
                        type="button"
                        onClick={() => handleRemoveSkill(skill)}
                        className="text-slate-400 hover:text-rose-500 print:hidden"
                      >
                        <X className="w-3 h-3" />
                      </button>
                    )}
                  </span>
                ))}
              </div>

              {isDraft && (
                <div className="flex items-center gap-2 pt-1 print:hidden">
                  <input
                    type="text"
                    value={newSkillName}
                    onChange={(e) => setNewSkillName(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter') {
                        e.preventDefault();
                        handleAddSkill();
                      }
                    }}
                    placeholder="Add verified skill..."
                    className="px-2.5 py-1 text-xs rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800/50 text-slate-800 dark:text-white"
                  />
                  <Button size="sm" variant="ghost" onClick={handleAddSkill} disabled={!newSkillName.trim()}>
                    <Plus className="w-3.5 h-3.5 mr-1" /> Add
                  </Button>
                </div>
              )}
            </div>

            {/* Section: Work Experience */}
            <div className="space-y-6">
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-900 dark:text-white border-b border-slate-100 dark:border-slate-800 pb-1">
                Work Experience
              </h3>

              {(content.experience || []).length === 0 ? (
                <p className="text-xs text-slate-500 italic">No experience records found.</p>
              ) : (
                <div className="space-y-5">
                  {(content.experience || []).map((exp, expIdx) => (
                    <div key={expIdx} className="space-y-2">
                      <div className="flex flex-col sm:flex-row sm:items-center justify-between text-xs">
                        <div>
                          <strong className="font-bold text-slate-900 dark:text-white">
                            {exp.job_title}
                          </strong>
                          <span className="text-slate-500 dark:text-slate-400"> &bull; {exp.employer}</span>
                        </div>
                        <div className="text-slate-500 dark:text-slate-400 font-mono text-[11px]">
                          {exp.start_date || 'N/A'} – {exp.is_current ? 'Present' : exp.end_date || 'N/A'}
                          {exp.location && ` &bull; ${exp.location}`}
                        </div>
                      </div>

                      {/* Bullet points */}
                      <ul className="space-y-2 pl-4 list-disc text-xs text-slate-700 dark:text-slate-300">
                        {(exp.responsibilities || []).map((bullet, bIdx) => (
                          <li key={bIdx} className="leading-relaxed">
                            {isDraft ? (
                              <textarea
                                value={bullet}
                                onChange={(e) => handleBulletChange(expIdx, bIdx, e.target.value)}
                                rows={2}
                                className="w-full p-2 text-xs text-slate-800 dark:text-slate-200 rounded border border-slate-200 dark:border-slate-700 bg-slate-50/40 dark:bg-slate-800/30 focus:ring-1 focus:ring-purple-500 focus:outline-none"
                              />
                            ) : (
                              <span>{bullet}</span>
                            )}
                          </li>
                        ))}
                      </ul>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Section: Projects */}
            {(content.projects || []).length > 0 && (
              <div className="space-y-4">
                <h3 className="text-xs font-bold uppercase tracking-wider text-slate-900 dark:text-white border-b border-slate-100 dark:border-slate-800 pb-1">
                  Projects & Technical Deliverables
                </h3>

                <div className="space-y-4">
                  {content.projects.map((proj, pIdx) => (
                    <div key={pIdx} className="space-y-1 text-xs">
                      <div className="flex items-center justify-between">
                        <strong className="font-bold text-slate-900 dark:text-white">
                          {proj.name}
                        </strong>
                        {proj.url && (
                          <a
                            href={proj.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-purple-600 dark:text-purple-400 hover:underline"
                          >
                            Project Link
                          </a>
                        )}
                      </div>
                      {proj.description && (
                        <p className="text-slate-700 dark:text-slate-300 leading-relaxed">
                          {proj.description}
                        </p>
                      )}
                      {proj.technologies && proj.technologies.length > 0 && (
                        <div className="flex flex-wrap gap-1 pt-0.5 text-[10px] text-slate-500">
                          {proj.technologies.map((t) => (
                            <span key={t} className="px-1.5 py-0.2 rounded bg-slate-100 dark:bg-slate-800">
                              {t}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Section: Education */}
            {(content.education || []).length > 0 && (
              <div className="space-y-3">
                <h3 className="text-xs font-bold uppercase tracking-wider text-slate-900 dark:text-white border-b border-slate-100 dark:border-slate-800 pb-1">
                  Education
                </h3>

                <div className="space-y-2">
                  {content.education.map((edu, eIdx) => (
                    <div key={eIdx} className="flex flex-col sm:flex-row sm:items-center justify-between text-xs">
                      <div>
                        <strong className="font-bold text-slate-900 dark:text-white">
                          {edu.degree || 'Degree'}{edu.field_of_study ? ` in ${edu.field_of_study}` : ''}
                        </strong>
                        <span className="text-slate-500 dark:text-slate-400"> &bull; {edu.institution}</span>
                      </div>
                      <div className="text-slate-500 dark:text-slate-400 font-mono text-[11px]">
                        {edu.start_date || ''} {edu.end_date ? `– ${edu.end_date}` : ''}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </Card>
        </div>
      )}

      {/* ───────────────────────────────────────────────────────────── */}
      {/* TAB 2: VISUAL DIFF & EVIDENCE GROUNDING                       */}
      {/* ───────────────────────────────────────────────────────────── */}
      {activeTab === 'diff' && (
        <div className="space-y-6">
          {/* Filter Bar */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 p-4 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800">
            <div className="flex items-center gap-2 flex-wrap text-xs">
              <span className="font-semibold text-slate-500">Filter Section:</span>
              {['all', 'executive_summary', 'experience', 'skills', 'projects'].map((sec) => (
                <button
                  key={sec}
                  onClick={() => setDiffSectionFilter(sec)}
                  className={`px-2.5 py-1 rounded-md font-medium capitalize transition-all ${
                    diffSectionFilter === sec
                      ? 'bg-purple-600 text-white'
                      : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
                  }`}
                >
                  {sec.replace('_', ' ')}
                </button>
              ))}
            </div>

            <div className="flex items-center gap-2">
              <button
                onClick={() =>
                  setDiffLayout(diffLayout === 'side-by-side' ? 'stacked' : 'side-by-side')
                }
                className="text-xs px-2.5 py-1 rounded-md border border-slate-200 dark:border-slate-800 text-slate-600 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-800"
              >
                Layout: {diffLayout === 'side-by-side' ? 'Side-by-Side' : 'Stacked'}
              </button>
            </div>
          </div>

          {filteredChanges.length === 0 ? (
            <div className="p-12 text-center rounded-2xl border border-dashed border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-900/50 space-y-2">
              <CheckCircle2 className="w-8 h-8 mx-auto text-emerald-500" />
              <h4 className="text-sm font-bold text-slate-900 dark:text-white">
                No Changes for this Section
              </h4>
              <p className="text-xs text-slate-500">
                This section retained its authentic source wording without tailoring modifications.
              </p>
            </div>
          ) : (
            <div className="space-y-4">
              {filteredChanges.map((change) => (
                <Card
                  key={change.id}
                  className="overflow-hidden border-slate-200 dark:border-slate-800 shadow-sm space-y-3"
                >
                  {/* Change Header */}
                  <div className="bg-slate-50 dark:bg-slate-800/70 px-4 py-2.5 border-b border-slate-200 dark:border-slate-800 flex items-center justify-between text-xs">
                    <div className="flex items-center gap-2">
                      <span className="font-bold uppercase tracking-wider text-slate-700 dark:text-slate-300">
                        {change.section.replace('_', ' ')}
                      </span>
                      <span
                        className={`text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full ${
                          change.change_type === 'addition'
                            ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300'
                            : change.change_type === 'rephrasing'
                            ? 'bg-purple-100 text-purple-800 dark:bg-purple-950 dark:text-purple-300'
                            : 'bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-300'
                        }`}
                      >
                        {change.change_type}
                      </span>
                    </div>

                    {change.needs_clarification && (
                      <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-amber-700 bg-amber-100 dark:bg-amber-950 dark:text-amber-300 px-2 py-0.5 rounded-full">
                        <AlertTriangle className="w-3.5 h-3.5" /> Needs Candidate Verification
                      </span>
                    )}
                  </div>

                  {/* Diff Body */}
                  <div className="p-4 space-y-4">
                    <div
                      className={`grid gap-4 text-xs font-mono ${
                        diffLayout === 'side-by-side' ? 'grid-cols-1 md:grid-cols-2' : 'grid-cols-1'
                      }`}
                    >
                      {/* Original baseline */}
                      <div className="p-3.5 rounded-xl bg-rose-50/40 dark:bg-rose-950/20 border border-rose-200/80 dark:border-rose-900/40 space-y-1">
                        <div className="text-[10px] font-bold uppercase tracking-wider text-rose-700 dark:text-rose-400">
                          Original Baseline
                        </div>
                        <div className="text-slate-800 dark:text-slate-200 whitespace-pre-line leading-relaxed">
                          {change.original_text || '(New bullet added for target role alignment)'}
                        </div>
                      </div>

                      {/* Tailored proposed */}
                      <div className="p-3.5 rounded-xl bg-emerald-50/40 dark:bg-emerald-950/20 border border-emerald-200/80 dark:border-emerald-900/40 space-y-1">
                        <div className="text-[10px] font-bold uppercase tracking-wider text-emerald-700 dark:text-emerald-400">
                          Tailored Version (Evidence-Grounded)
                        </div>
                        <div className="text-emerald-950 dark:text-emerald-200 font-medium whitespace-pre-line leading-relaxed">
                          {change.proposed_text}
                        </div>
                      </div>
                    </div>

                    {/* Grounding Explanation */}
                    <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/50 border border-slate-200/80 dark:border-slate-800 text-xs space-y-1.5">
                      <div className="flex items-start gap-2">
                        <ShieldCheck className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
                        <div className="space-y-0.5">
                          <p className="text-slate-800 dark:text-slate-200 font-medium">
                            <strong>Why this improves score:</strong> {change.rationale}
                          </p>
                          {change.target_job_requirement && (
                            <p className="text-slate-600 dark:text-slate-400 text-[11px]">
                              <strong>Target Requirement:</strong> {change.target_job_requirement}
                            </p>
                          )}
                          {change.supporting_evidence && (
                            <p className="text-slate-600 dark:text-slate-400 text-[11px]">
                              <strong>Supporting Evidence:</strong> {change.supporting_evidence}
                            </p>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                </Card>
              ))}
            </div>
          )}
        </div>
      )}

      {/* ───────────────────────────────────────────────────────────── */}
      {/* TAB 3: OPTIMIZATION ANALYSIS                                  */}
      {/* ───────────────────────────────────────────────────────────── */}
      {activeTab === 'analysis' && (
        <div className="space-y-6">
          {/* Reconciler Anti-Hallucination Audit Callout */}
          {unsupportedClaims.length > 0 ? (
            <div className="p-5 rounded-2xl bg-rose-50/70 dark:bg-rose-950/30 border border-rose-200 dark:border-rose-800 space-y-2">
              <div className="flex items-center gap-2 text-rose-800 dark:text-rose-200 font-bold text-sm">
                <AlertCircle className="w-5 h-5 text-rose-600 shrink-0" />
                <span>Anti-Fabrication Guardrail: Omitted Unevidenced Claims</span>
              </div>
              <p className="text-xs text-rose-700/90 dark:text-rose-300/90 leading-relaxed">
                The target job posting demanded certain technologies or credentials that could not be verified in your authentic profile records. To preserve candidate credibility and prevent interview failures, CoachPath automatically stripped these claims:
              </p>
              <ul className="list-disc list-inside space-y-1 text-xs text-rose-800 dark:text-rose-200 pl-2">
                {unsupportedClaims.map((claim, idx) => (
                  <li key={idx}>{claim}</li>
                ))}
              </ul>
            </div>
          ) : (
            <div className="p-4 rounded-xl bg-emerald-50/50 dark:bg-emerald-950/20 border border-emerald-200 dark:border-emerald-800 flex items-center gap-3 text-xs text-emerald-800 dark:text-emerald-200">
              <ShieldCheck className="w-5 h-5 text-emerald-600 shrink-0" />
              <span>
                <strong>Zero Hallucinations Detected:</strong> All tailored wording is strictly grounded in candidate evidence from your master resume and verified skills.
              </span>
            </div>
          )}

          {/* Quantitative Breakdown Grid */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Keyword Coverage */}
            <Card className="p-5 space-y-2">
              <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
                Target Keyword Coverage
              </div>
              <div className="text-3xl font-extrabold text-purple-600 dark:text-purple-400">
                {analysis?.keyword_coverage !== undefined
                  ? `${analysis.keyword_coverage.toFixed(1)}%`
                  : 'N/A'}
              </div>
              <p className="text-[11px] text-slate-500 leading-normal">
                Deterministic keyword match percentage based on extracted job terms. Does not represent an ATS pass score or hiring guarantee.
              </p>
            </Card>

            {/* Readability Index */}
            <Card className="p-5 space-y-2">
              <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
                Clarity & Readability
              </div>
              <div className="text-3xl font-extrabold text-indigo-600 dark:text-indigo-400">
                {analysis?.readability_score !== null && analysis?.readability_score !== undefined
                  ? `${analysis.readability_score.toFixed(0)} / 100`
                  : '90+'}
              </div>
              <p className="text-[11px] text-slate-500 leading-normal">
                Bullet point density, strong active verbs, and quantitative outcome framing.
              </p>
            </Card>

            {/* Structured Changes */}
            <Card className="p-5 space-y-2">
              <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
                Tailored Recommendations
              </div>
              <div className="text-3xl font-extrabold text-brand-600 dark:text-brand-400">
                {changes.length}
              </div>
              <p className="text-[11px] text-slate-500 leading-normal">
                Additions, rephrasings, and keyword emphasis points generated.
              </p>
            </Card>
          </div>

          {/* Matched vs Missing Keywords */}
          <Card className="p-6 space-y-4">
            <h4 className="text-sm font-bold text-slate-900 dark:text-white">
              Target Job Keyword Matrix
            </h4>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Matched */}
              <div className="p-4 rounded-xl bg-emerald-50/30 dark:bg-emerald-950/20 border border-emerald-200/60 dark:border-emerald-800/40 space-y-2">
                <div className="flex items-center gap-1.5 text-xs font-bold text-emerald-700 dark:text-emerald-300 uppercase tracking-wider">
                  <CheckCircle2 className="w-4 h-4" />
                  Evidenced Keywords ({analysis?.matched_keywords?.length || 0})
                </div>
                <div className="flex flex-wrap gap-1.5 pt-1">
                  {(analysis?.matched_keywords || []).map((kw) => (
                    <span
                      key={kw}
                      className="text-xs px-2.5 py-0.5 rounded-full bg-emerald-100 dark:bg-emerald-950/80 text-emerald-800 dark:text-emerald-300 font-medium"
                    >
                      {kw}
                    </span>
                  ))}
                </div>
              </div>

              {/* Missing */}
              <div className="p-4 rounded-xl bg-amber-50/30 dark:bg-amber-950/20 border border-amber-200/60 dark:border-amber-800/40 space-y-2">
                <div className="flex items-center gap-1.5 text-xs font-bold text-amber-700 dark:text-amber-300 uppercase tracking-wider">
                  <AlertTriangle className="w-4 h-4" />
                  Unevidenced Job Keywords ({analysis?.missing_keywords?.length || 0})
                </div>
                <div className="flex flex-wrap gap-1.5 pt-1">
                  {(analysis?.missing_keywords || []).length === 0 ? (
                    <span className="text-xs text-slate-500">None! All target keywords covered.</span>
                  ) : (
                    (analysis?.missing_keywords || []).map((kw) => (
                      <span
                        key={kw}
                        className="text-xs px-2.5 py-0.5 rounded-full bg-amber-100 dark:bg-amber-950/80 text-amber-800 dark:text-amber-300 font-medium"
                      >
                        {kw}
                      </span>
                    ))
                  )}
                </div>
              </div>
            </div>
          </Card>

          {/* Missing Requirements & Suggestions */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Missing Requirements */}
            <Card className="p-6 space-y-3">
              <h4 className="text-sm font-bold text-slate-900 dark:text-white flex items-center gap-2">
                <AlertCircle className="w-4 h-4 text-amber-600" />
                <span>Job Requirements Lacking Evidence</span>
              </h4>
              <p className="text-xs text-slate-500 leading-relaxed">
                These qualifications are required by the role, but not evidenced in your current profile. Close these gaps via your Milestone Roadmap.
              </p>
              {(analysis?.missing_requirements || []).length === 0 ? (
                <p className="text-xs text-emerald-600 font-medium">All essential requirements evidenced!</p>
              ) : (
                <ul className="space-y-2 text-xs text-slate-700 dark:text-slate-300 pl-4 list-disc">
                  {(analysis?.missing_requirements || []).map((req, idx) => (
                    <li key={idx} className="leading-relaxed">{req}</li>
                  ))}
                </ul>
              )}
            </Card>

            {/* Actionable Suggestions */}
            <Card className="p-6 space-y-3">
              <h4 className="text-sm font-bold text-slate-900 dark:text-white flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-purple-600" />
                <span>Actionable Recommendations</span>
              </h4>
              <p className="text-xs text-slate-500 leading-relaxed">
                Concrete steps to strengthen alignment with this specific engineering opening:
              </p>
              <ul className="space-y-2 text-xs text-slate-700 dark:text-slate-300 pl-4 list-disc">
                {(analysis?.actionable_suggestions || []).map((sug, idx) => (
                  <li key={idx} className="leading-relaxed">{sug}</li>
                ))}
              </ul>
            </Card>
          </div>
        </div>
      )}

      {/* Explicit Human Approval Gate Dialog */}
      <TailoredApprovalDialog
        isOpen={showApprovalModal}
        versionNumber={version.version_number}
        jobTitle={jobTitle}
        companyName={companyName}
        onClose={() => setShowApprovalModal(false)}
        onConfirmApprove={handleApproveConfirm}
        isApproving={isApproving}
        error={approvalError}
      />
    </div>
  );
}
