'use client';

import * as React from 'react';
import { mockProfile } from '@/lib/mock/data';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs } from '@/components/ui/tabs';
import { Modal } from '@/components/ui/modal';
import {
  User,
  Briefcase,
  FolderGit2,
  GraduationCap,
  Award,
  ExternalLink,
  Github,
  Plus,
  Upload,
  Download,
  ShieldCheck,
  CheckCircle2,
} from 'lucide-react';

export default function CareerProfilePage() {
  const [activeTab, setActiveTab] = React.useState('overview');
  const [isResumeModalOpen, setIsResumeModalOpen] = React.useState(false);

  const tabs = [
    { id: 'overview', label: 'Overview & Goals', icon: <User className="w-4 h-4" /> },
    { id: 'experience', label: 'Work Experience', icon: <Briefcase className="w-4 h-4" />, badge: mockProfile.experience.length },
    { id: 'projects', label: 'Verified Projects', icon: <FolderGit2 className="w-4 h-4" />, badge: mockProfile.projects.length },
    { id: 'education', label: 'Education & Certs', icon: <GraduationCap className="w-4 h-4" />, badge: '2' },
  ];

  return (
    <div className="space-y-6">
      {/* Profile Header Banner */}
      <Card className="p-6 md:p-8">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-6">
          <div className="flex items-center gap-5">
            <div className="h-20 w-20 rounded-2xl bg-gradient-to-tr from-brand-600 to-purple-600 text-white flex items-center justify-center font-extrabold text-2xl shadow-lg shrink-0">
              AM
            </div>
            <div className="space-y-1">
              <div className="flex flex-wrap items-center gap-2">
                <h2 className="text-2xl font-bold text-slate-900 dark:text-white">
                  {mockProfile.name}
                </h2>
                <Badge variant="verified" size="sm">
                  <ShieldCheck className="w-3.5 h-3.5 mr-1" /> Profile Verified
                </Badge>
              </div>
              <p className="text-sm font-medium text-slate-600 dark:text-slate-300">
                {mockProfile.title} &bull; {mockProfile.location}
              </p>
              <div className="flex items-center gap-2 pt-1">
                <span className="text-xs text-slate-400">Target Role:</span>
                <span className="text-xs font-bold text-purple-700 dark:text-purple-300 bg-purple-50 dark:bg-purple-950/40 px-2 py-0.5 rounded border border-purple-200 dark:border-purple-800">
                  {mockProfile.targetRole}
                </span>
                <span className="text-xs text-slate-400">&bull; {mockProfile.yearsExperience} YOE</span>
              </div>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-2 self-stretch sm:self-auto">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setIsResumeModalOpen(true)}
            >
              <Upload className="w-3.5 h-3.5 mr-1.5" /> Re-parse Resume
            </Button>
            <Button
              variant="secondary"
              size="sm"
              onClick={() => alert('Exporting normalized career profile JSON...')}
            >
              <Download className="w-3.5 h-3.5 mr-1.5" /> Export Graph
            </Button>
          </div>
        </div>
      </Card>

      {/* Tabs Switcher */}
      <Tabs tabs={tabs} activeTab={activeTab} onChange={setActiveTab} />

      {/* Tab 1: Overview & Goals */}
      {activeTab === 'overview' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 space-y-6">
            <Card className="p-6 space-y-3">
              <h3 className="text-base font-bold text-slate-900 dark:text-white">
                Executive Bio & Career Focus
              </h3>
              <p className="text-sm text-slate-600 dark:text-slate-300 leading-relaxed">
                {mockProfile.bio}
              </p>
            </Card>

            <Card className="p-6 space-y-4">
              <h3 className="text-base font-bold text-slate-900 dark:text-white">
                Secondary Target Roles & Exploration
              </h3>
              <p className="text-xs text-slate-500">
                Alternative technical trajectories evaluated by our vector matching engine.
              </p>
              <div className="flex flex-wrap gap-2">
                {mockProfile.secondaryRoles.map((role) => (
                  <Badge key={role} variant="default" size="md">
                    {role}
                  </Badge>
                ))}
              </div>
            </Card>
          </div>

          <div className="space-y-6">
            <Card className="p-6 space-y-3">
              <h3 className="text-base font-bold text-slate-900 dark:text-white">
                Verification Metadata
              </h3>
              <div className="space-y-2 text-xs text-slate-600 dark:text-slate-300">
                <div className="flex justify-between py-1 border-b border-slate-100 dark:border-slate-800">
                  <span className="text-slate-400">Total Skills Claimed:</span>
                  <span className="font-bold">12 Skills</span>
                </div>
                <div className="flex justify-between py-1 border-b border-slate-100 dark:border-slate-800">
                  <span className="text-slate-400">Verified via Tests:</span>
                  <span className="font-bold text-emerald-600">6 Verified</span>
                </div>
                <div className="flex justify-between py-1 border-b border-slate-100 dark:border-slate-800">
                  <span className="text-slate-400">Identified Gaps:</span>
                  <span className="font-bold text-rose-600">3 Gaps</span>
                </div>
                <div className="flex justify-between py-1">
                  <span className="text-slate-400">Last Calibrated:</span>
                  <span className="font-mono">Oct 5, 2026</span>
                </div>
              </div>
            </Card>
          </div>
        </div>
      )}

      {/* Tab 2: Work Experience */}
      {activeTab === 'experience' && (
        <div className="space-y-4">
          <div className="flex justify-between items-center">
            <h3 className="text-base font-bold text-slate-900 dark:text-white">
              Work History
            </h3>
            <Button size="sm" variant="outline">
              <Plus className="w-3.5 h-3.5 mr-1" /> Add Position
            </Button>
          </div>

          <div className="space-y-4">
            {mockProfile.experience.map((exp) => (
              <Card key={exp.id} className="p-6 space-y-3">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                  <div>
                    <h4 className="text-base font-bold text-slate-900 dark:text-white">
                      {exp.role}
                    </h4>
                    <p className="text-xs font-semibold text-purple-700 dark:text-purple-300">
                      {exp.company} &bull; {exp.location}
                    </p>
                  </div>
                  <span className="text-xs font-mono text-slate-400 bg-slate-100 dark:bg-slate-800 px-2.5 py-1 rounded-md self-start sm:self-auto">
                    {exp.startDate} – {exp.current ? 'Present' : exp.endDate}
                  </span>
                </div>

                <ul className="list-disc list-inside space-y-1.5 text-xs text-slate-600 dark:text-slate-300 leading-relaxed pt-1">
                  {exp.description.map((bullet, idx) => (
                    <li key={idx}>{bullet}</li>
                  ))}
                </ul>

                <div className="flex flex-wrap items-center gap-1.5 pt-3 border-t border-slate-100 dark:border-slate-800">
                  <span className="text-[11px] font-semibold text-slate-400 mr-1">Skills Applied:</span>
                  {exp.skillsUsed.map((sk) => (
                    <Badge key={sk} variant="default" size="sm">
                      {sk}
                    </Badge>
                  ))}
                </div>
              </Card>
            ))}
          </div>
        </div>
      )}

      {/* Tab 3: Verified Projects */}
      {activeTab === 'projects' && (
        <div className="space-y-4">
          <div className="flex justify-between items-center">
            <div>
              <h3 className="text-base font-bold text-slate-900 dark:text-white">
                Portfolio Projects with Verified Evidence
              </h3>
              <p className="text-xs text-slate-500">
                These repositories serve as verifiable proof for resume bullets and skill confidence scores.
              </p>
            </div>
            <Button size="sm" variant="outline">
              <Plus className="w-3.5 h-3.5 mr-1" /> Add Repository
            </Button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {mockProfile.projects.map((proj) => (
              <Card key={proj.id} className="p-6 flex flex-col justify-between space-y-4">
                <div className="space-y-2">
                  <div className="flex items-start justify-between gap-2">
                    <h4 className="text-base font-bold text-slate-900 dark:text-white">
                      {proj.title}
                    </h4>
                    {proj.verifiedEvidence && (
                      <Badge variant="verified" size="sm">
                        <CheckCircle2 className="w-3 h-3 mr-1" /> Verified Proof
                      </Badge>
                    )}
                  </div>
                  <p className="text-xs text-slate-600 dark:text-slate-300 leading-relaxed">
                    {proj.description}
                  </p>
                  <div className="flex flex-wrap gap-1.5 pt-1">
                    {proj.technologies.map((t) => (
                      <span
                        key={t}
                        className="rounded px-2 py-0.5 text-[11px] font-mono bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300"
                      >
                        {t}
                      </span>
                    ))}
                  </div>
                </div>

                <div className="flex items-center gap-3 pt-3 border-t border-slate-100 dark:border-slate-800 text-xs">
                  {proj.githubUrl && (
                    <a
                      href={proj.githubUrl}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center gap-1 font-semibold text-slate-700 dark:text-slate-300 hover:text-brand-600"
                    >
                      <Github className="w-3.5 h-3.5" /> Source Code
                    </a>
                  )}
                  {proj.liveUrl && (
                    <a
                      href={proj.liveUrl}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center gap-1 font-semibold text-brand-600 hover:underline"
                    >
                      <ExternalLink className="w-3.5 h-3.5" /> Live Demo
                    </a>
                  )}
                </div>
              </Card>
            ))}
          </div>
        </div>
      )}

      {/* Tab 4: Education & Certifications */}
      {activeTab === 'education' && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Card className="p-6 space-y-4">
            <div className="flex items-center gap-2 font-bold text-slate-900 dark:text-white">
              <GraduationCap className="w-5 h-5 text-purple-600" />
              <h3>Academic Education</h3>
            </div>
            {mockProfile.education.map((edu) => (
              <div key={edu.id} className="space-y-1 text-xs">
                <div className="text-sm font-bold text-slate-900 dark:text-white">
                  {edu.institution}
                </div>
                <div className="text-purple-700 dark:text-purple-300 font-medium">
                  {edu.degree} &bull; {edu.fieldOfStudy}
                </div>
                <div className="text-slate-400">
                  {edu.startDate} – {edu.endDate} &bull; {edu.grade}
                </div>
              </div>
            ))}
          </Card>

          <Card className="p-6 space-y-4">
            <div className="flex items-center gap-2 font-bold text-slate-900 dark:text-white">
              <Award className="w-5 h-5 text-amber-600" />
              <h3>Verified Certifications</h3>
            </div>
            {mockProfile.certifications.map((cert) => (
              <div key={cert.id} className="space-y-1 text-xs">
                <div className="text-sm font-bold text-slate-900 dark:text-white">
                  {cert.name}
                </div>
                <div className="text-amber-700 dark:text-amber-400 font-medium">
                  {cert.issuingOrganization} &bull; Issued {cert.issueDate}
                </div>
                <div className="font-mono text-slate-400">
                  ID: {cert.credentialId}
                </div>
              </div>
            ))}
          </Card>
        </div>
      )}

      {/* Re-parse Resume Modal */}
      <Modal
        isOpen={isResumeModalOpen}
        onClose={() => setIsResumeModalOpen(false)}
        title="Upload Resume for AI Ingestion"
        description="Upload an updated PDF or Markdown resume. Our parser will extract entities without overwriting verified assessment grades."
      >
        <div className="p-8 border-2 border-dashed border-slate-300 dark:border-slate-700 rounded-xl text-center space-y-3">
          <Upload className="w-10 h-10 text-slate-400 mx-auto" />
          <div className="text-sm font-medium text-slate-700 dark:text-slate-300">
            Drag and drop your updated PDF resume here, or click to browse
          </div>
          <p className="text-xs text-slate-400">
            PDF, DOCX, or Markdown up to 10MB. Sensitive PII is sanitized before AI processing.
          </p>
          <Button size="sm" variant="outline">
            Select File
          </Button>
        </div>
      </Modal>
    </div>
  );
}
