'use client';

import * as React from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Tabs } from '@/components/ui/tabs';
import { Alert } from '@/components/ui/alert';
import {
  User,
  GraduationCap,
  Briefcase,
  Code2,
  FolderGit2,
  Award,
  FileText,
  Plus,
  Trash2,
  CheckCircle2,
  X,
  AlertCircle,
  ExternalLink,
  Edit2,
  Check,
  ShieldCheck,
  RotateCcw,
} from 'lucide-react';
import {
  ConfirmCertificationItem,
  ConfirmEducationItem,
  ConfirmExperienceItem,
  ConfirmPersonalInfo,
  ConfirmProjectItem,
  MasterCareerProfile,
  ParsedResumeResponse,
  ResumeConfirmationPayload,
} from '@/types';
import { ProfileConflictIndicator } from './profile-conflict-indicator';
import { ResumeApprovalSummary } from './resume-approval-summary';

interface ParsedResumeReviewProps {
  parsedData: ParsedResumeResponse;
  existingProfile: MasterCareerProfile | null;
  onConfirm: (payload: ResumeConfirmationPayload) => Promise<void>;
  onBack: () => void;
  isConfirming: boolean;
}

export function ParsedResumeReview({
  parsedData,
  existingProfile,
  onConfirm,
  onBack,
  isConfirming,
}: ParsedResumeReviewProps) {
  const preview = parsedData.extracted_preview;

  // ─── Local State for Editable / Selectable Draft Items ─────────────

  // Personal Info
  const [includePersonalInfo, setIncludePersonalInfo] = React.useState(true);
  const [personalInfo, setPersonalInfo] = React.useState<ConfirmPersonalInfo>({
    headline: preview?.personal_info?.name
      ? `${preview.personal_info.name} - Software Engineer`
      : existingProfile?.headline || '',
    location: preview?.personal_info?.location || existingProfile?.location || '',
    phone_number: preview?.personal_info?.phone || existingProfile?.phone_number || '',
    linkedin_url: preview?.personal_info?.linkedin_url || existingProfile?.linkedin_url || '',
    github_url: preview?.personal_info?.github_url || existingProfile?.github_url || '',
    portfolio_url: preview?.personal_info?.portfolio_url || existingProfile?.portfolio_url || '',
    bio: preview?.executive_summary || existingProfile?.bio || '',
  });

  // Education list with selected flag
  const [educationList, setEducationList] = React.useState<
    (ConfirmEducationItem & { id: string; selected: boolean })[]
  >(() => {
    return (preview?.education || []).map((edu, idx) => ({
      id: `edu_${idx}_${Date.now()}`,
      institution_name: edu.institution,
      degree: edu.degree || 'Degree',
      field_of_study: edu.field_of_study || 'General',
      start_date: edu.start_date || '2020-01-01',
      end_date: edu.end_date || null,
      is_current: !edu.end_date,
      gpa: edu.grade_or_gpa ? parseFloat(edu.grade_or_gpa) || null : null,
      selected: true,
    }));
  });

  // Experience list with selected flag
  const [experienceList, setExperienceList] = React.useState<
    (ConfirmExperienceItem & { id: string; selected: boolean })[]
  >(() => {
    return (preview?.experience || []).map((exp, idx) => ({
      id: `exp_${idx}_${Date.now()}`,
      company_name: exp.employer,
      role_title: exp.job_title,
      location: exp.location || null,
      start_date: exp.start_date || '2021-01-01',
      end_date: exp.end_date || null,
      is_current: exp.is_current || false,
      bullet_points: exp.responsibilities.concat(exp.achievements),
      selected: true,
    }));
  });

  // Projects list with selected flag
  const [projectsList, setProjectsList] = React.useState<
    (ConfirmProjectItem & { id: string; selected: boolean })[]
  >(() => {
    return (preview?.projects || []).map((proj, idx) => ({
      id: `proj_${idx}_${Date.now()}`,
      title: proj.name,
      description: proj.description || proj.highlights.join(' ') || 'Project description',
      technologies: proj.technologies || [],
      github_url: proj.url?.includes('github.com') ? proj.url : null,
      live_url: !proj.url?.includes('github.com') ? proj.url : null,
      bullet_points: proj.highlights || [],
      selected: true,
    }));
  });

  // Certifications list with selected flag
  const [certificationsList, setCertificationsList] = React.useState<
    (ConfirmCertificationItem & { id: string; selected: boolean })[]
  >(() => {
    return (preview?.certifications || []).map((cert, idx) => ({
      id: `cert_${idx}_${Date.now()}`,
      name: cert.name,
      issuing_organization: cert.issuing_organization || 'Certifying Body',
      issue_date: cert.issue_date || '2023-01-01',
      expiration_date: cert.expiration_date || null,
      credential_id: cert.credential_id || null,
      credential_url: null,
      selected: true,
    }));
  });

  // Skills with selected map (skill_id or raw name -> boolean)
  const [selectedSkills, setSelectedSkills] = React.useState<Record<string, boolean>>(() => {
    const map: Record<string, boolean> = {};
    (preview?.normalized_skills || []).forEach((s) => {
      map[s.skill_id] = true;
    });
    (preview?.raw_unmatched_skills || []).forEach((s) => {
      map[s] = true;
    });
    return map;
  });

  const [activeTab, setActiveTab] = React.useState('education');

  // ─── Existing Profile Comparison Helpers ──────────────────────────

  const checkEducationInProfile = (inst: string, deg: string): 'existing' | 'new' => {
    if (!existingProfile?.education) return 'new';
    const match = existingProfile.education.some(
      (e) =>
        e.institution_name.toLowerCase().includes(inst.toLowerCase()) ||
        inst.toLowerCase().includes(e.institution_name.toLowerCase())
    );
    return match ? 'existing' : 'new';
  };

  const checkExperienceInProfile = (company: string, role: string): 'existing' | 'new' => {
    if (!existingProfile?.experience) return 'new';
    const match = existingProfile.experience.some(
      (e) =>
        e.company_name.toLowerCase().includes(company.toLowerCase()) ||
        company.toLowerCase().includes(e.company_name.toLowerCase())
    );
    return match ? 'existing' : 'new';
  };

  const checkProjectInProfile = (title: string): 'existing' | 'new' => {
    if (!existingProfile?.projects) return 'new';
    const match = existingProfile.projects.some(
      (p) =>
        p.title.toLowerCase().includes(title.toLowerCase()) ||
        title.toLowerCase().includes(p.title.toLowerCase())
    );
    return match ? 'existing' : 'new';
  };

  const checkCertInProfile = (name: string): 'existing' | 'new' => {
    if (!existingProfile?.certifications) return 'new';
    const match = existingProfile.certifications.some((c) =>
      c.name.toLowerCase().includes(name.toLowerCase())
    );
    return match ? 'existing' : 'new';
  };

  // ─── Approval Submission Handler ──────────────────────────────────

  const handleConfirmSubmit = async () => {
    const selectedEducation = educationList
      .filter((e) => e.selected)
      .map(({ id, selected, ...rest }) => rest);

    const selectedExperience = experienceList
      .filter((e) => e.selected)
      .map(({ id, selected, ...rest }) => rest);

    const selectedProjects = projectsList
      .filter((p) => p.selected)
      .map(({ id, selected, ...rest }) => rest);

    const selectedCertifications = certificationsList
      .filter((c) => c.selected)
      .map(({ id, selected, ...rest }) => rest);

    const confirmedSkillsList = Object.entries(selectedSkills)
      .filter(([_, isSelected]) => isSelected)
      .map(([skillId]) => skillId);

    const payload: ResumeConfirmationPayload = {
      personal_info: includePersonalInfo ? personalInfo : null,
      education: selectedEducation,
      experience: selectedExperience,
      projects: selectedProjects,
      certifications: selectedCertifications,
      confirmed_skills: confirmedSkillsList,
      make_primary: true,
    };

    await onConfirm(payload);
  };

  const selectedEduCount = educationList.filter((e) => e.selected).length;
  const selectedExpCount = experienceList.filter((e) => e.selected).length;
  const selectedProjCount = projectsList.filter((p) => p.selected).length;
  const selectedCertCount = certificationsList.filter((c) => c.selected).length;
  const selectedSkillsCount = Object.values(selectedSkills).filter(Boolean).length;

  const tabs = [
    {
      id: 'education',
      label: 'Education',
      icon: <GraduationCap className="w-4 h-4" />,
      badge: `${selectedEduCount}/${educationList.length}`,
    },
    {
      id: 'experience',
      label: 'Experience',
      icon: <Briefcase className="w-4 h-4" />,
      badge: `${selectedExpCount}/${experienceList.length}`,
    },
    {
      id: 'skills',
      label: 'Skills',
      icon: <Code2 className="w-4 h-4" />,
      badge: `${selectedSkillsCount}`,
    },
    {
      id: 'projects',
      label: 'Projects',
      icon: <FolderGit2 className="w-4 h-4" />,
      badge: `${selectedProjCount}/${projectsList.length}`,
    },
    {
      id: 'certifications',
      label: 'Certifications',
      icon: <Award className="w-4 h-4" />,
      badge: `${selectedCertCount}/${certificationsList.length}`,
    },
    {
      id: 'personal',
      label: 'Personal Details',
      icon: <User className="w-4 h-4" />,
    },
    {
      id: 'summary',
      label: 'Executive Summary',
      icon: <FileText className="w-4 h-4" />,
    },
  ];

  return (
    <div className="space-y-6">
      {/* Top Banner & Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-xl font-bold text-slate-900 dark:text-white">
              Resume Review & Verification Workbench
            </h2>
            <Badge variant="intelligence" size="sm">
              <ShieldCheck className="w-3.5 h-3.5 mr-1" /> Draft Mode
            </Badge>
          </div>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
            Source: <strong className="text-slate-700 dark:text-slate-300">{parsedData.file_name}</strong> &bull; Inspect and edit extracted details before confirming profile merge.
          </p>
        </div>

        <Button variant="outline" size="sm" onClick={onBack}>
          Back to Resumes
        </Button>
      </div>

      {/* Sticky Approval Summary Banner */}
      <ResumeApprovalSummary
        educationCount={selectedEduCount}
        experienceCount={selectedExpCount}
        projectsCount={selectedProjCount}
        certificationsCount={selectedCertCount}
        skillsCount={selectedSkillsCount}
        hasPersonalInfo={includePersonalInfo}
        onConfirm={handleConfirmSubmit}
        onDiscard={onBack}
        isConfirming={isConfirming}
      />

      {/* Navigation Tabs */}
      <Tabs tabs={tabs} activeTab={activeTab} onChange={setActiveTab} />

      {/* ───────────────────────────────────────────────────────────── */}
      {/* TAB 1: EDUCATION REVIEW                                       */}
      {/* ───────────────────────────────────────────────────────────── */}
      {activeTab === 'education' && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <p className="text-xs text-slate-500 dark:text-slate-400">
              Select and review academic degrees to commit to your profile.
            </p>
            <Button
              variant="outline"
              size="sm"
              onClick={() => {
                setEducationList((prev) => [
                  ...prev,
                  {
                    id: `edu_new_${Date.now()}`,
                    institution_name: 'University Name',
                    degree: 'Degree / Major',
                    field_of_study: 'Field of Study',
                    start_date: '2020-01-01',
                    end_date: null,
                    is_current: false,
                    gpa: null,
                    selected: true,
                  },
                ]);
              }}
            >
              <Plus className="w-3.5 h-3.5 mr-1" /> Add Education
            </Button>
          </div>

          {educationList.length === 0 ? (
            <Card className="p-8 text-center text-xs text-slate-500">
              No education entries were detected in this resume document. Click &ldquo;Add Education&rdquo; above to include one.
            </Card>
          ) : (
            educationList.map((edu, index) => {
              const compStatus = checkEducationInProfile(edu.institution_name, edu.degree);
              return (
                <Card
                  key={edu.id}
                  className={`p-5 transition-all space-y-4 border ${
                    edu.selected
                      ? 'border-brand-200 dark:border-brand-900 bg-white dark:bg-slate-900'
                      : 'border-slate-200 dark:border-slate-800 opacity-60 bg-slate-50/50 dark:bg-slate-950/20'
                  }`}
                >
                  <div className="flex items-center justify-between gap-3">
                    <div className="flex items-center gap-3">
                      <input
                        type="checkbox"
                        checked={edu.selected}
                        onChange={(e) => {
                          const checked = e.target.checked;
                          setEducationList((prev) =>
                            prev.map((item) =>
                              item.id === edu.id ? { ...item, selected: checked } : item
                            )
                          );
                        }}
                        className="w-4 h-4 rounded text-brand-600 focus:ring-brand-500 border-slate-300 dark:border-slate-700"
                        id={`edu_check_${edu.id}`}
                      />
                      <label
                        htmlFor={`edu_check_${edu.id}`}
                        className="text-sm font-semibold text-slate-900 dark:text-white cursor-pointer"
                      >
                        {edu.selected ? 'Include in Profile Merge' : 'Excluded from Merge'}
                      </label>
                    </div>

                    <div className="flex items-center gap-2">
                      <ProfileConflictIndicator status={compStatus} />
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() =>
                          setEducationList((prev) => prev.filter((item) => item.id !== edu.id))
                        }
                        className="text-slate-400 hover:text-rose-600 h-8 w-8 p-0"
                      >
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    </div>
                  </div>

                  {/* Form fields */}
                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 pt-2">
                    <div>
                      <label className="text-xs font-medium text-slate-600 dark:text-slate-400">
                        Institution Name
                      </label>
                      <Input
                        value={edu.institution_name}
                        onChange={(e) => {
                          const val = e.target.value;
                          setEducationList((prev) =>
                            prev.map((item) =>
                              item.id === edu.id ? { ...item, institution_name: val } : item
                            )
                          );
                        }}
                        className="mt-1"
                      />
                    </div>

                    <div>
                      <label className="text-xs font-medium text-slate-600 dark:text-slate-400">
                        Degree
                      </label>
                      <Input
                        value={edu.degree}
                        onChange={(e) => {
                          const val = e.target.value;
                          setEducationList((prev) =>
                            prev.map((item) =>
                              item.id === edu.id ? { ...item, degree: val } : item
                            )
                          );
                        }}
                        className="mt-1"
                      />
                    </div>

                    <div>
                      <label className="text-xs font-medium text-slate-600 dark:text-slate-400">
                        Field of Study
                      </label>
                      <Input
                        value={edu.field_of_study}
                        onChange={(e) => {
                          const val = e.target.value;
                          setEducationList((prev) =>
                            prev.map((item) =>
                              item.id === edu.id ? { ...item, field_of_study: val } : item
                            )
                          );
                        }}
                        className="mt-1"
                      />
                    </div>

                    <div>
                      <label className="text-xs font-medium text-slate-600 dark:text-slate-400">
                        Start Date
                      </label>
                      <Input
                        value={edu.start_date}
                        onChange={(e) => {
                          const val = e.target.value;
                          setEducationList((prev) =>
                            prev.map((item) =>
                              item.id === edu.id ? { ...item, start_date: val } : item
                            )
                          );
                        }}
                        className="mt-1"
                      />
                    </div>

                    <div>
                      <label className="text-xs font-medium text-slate-600 dark:text-slate-400">
                        End Date / Graduation
                      </label>
                      <Input
                        value={edu.end_date || ''}
                        placeholder={edu.is_current ? 'Present' : 'e.g. 2024-05'}
                        onChange={(e) => {
                          const val = e.target.value;
                          setEducationList((prev) =>
                            prev.map((item) =>
                              item.id === edu.id
                                ? { ...item, end_date: val || null, is_current: !val }
                                : item
                            )
                          );
                        }}
                        className="mt-1"
                      />
                    </div>

                    <div>
                      <label className="text-xs font-medium text-slate-600 dark:text-slate-400">
                        GPA (Optional)
                      </label>
                      <Input
                        type="number"
                        step="0.01"
                        max="4.0"
                        value={edu.gpa !== null ? String(edu.gpa) : ''}
                        onChange={(e) => {
                          const val = e.target.value ? parseFloat(e.target.value) : null;
                          setEducationList((prev) =>
                            prev.map((item) =>
                              item.id === edu.id ? { ...item, gpa: val } : item
                            )
                          );
                        }}
                        className="mt-1"
                      />
                    </div>
                  </div>
                </Card>
              );
            })
          )}
        </div>
      )}

      {/* ───────────────────────────────────────────────────────────── */}
      {/* TAB 2: EXPERIENCE REVIEW                                      */}
      {/* ───────────────────────────────────────────────────────────── */}
      {activeTab === 'experience' && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <p className="text-xs text-slate-500 dark:text-slate-400">
              Select and review professional work experiences. Edit bullet points as needed.
            </p>
            <Button
              variant="outline"
              size="sm"
              onClick={() => {
                setExperienceList((prev) => [
                  ...prev,
                  {
                    id: `exp_new_${Date.now()}`,
                    company_name: 'Company Name',
                    role_title: 'Job Title',
                    location: 'City, State / Remote',
                    start_date: '2022-01-01',
                    end_date: null,
                    is_current: true,
                    bullet_points: ['Key responsibility or achievement.'],
                    selected: true,
                  },
                ]);
              }}
            >
              <Plus className="w-3.5 h-3.5 mr-1" /> Add Experience
            </Button>
          </div>

          {experienceList.length === 0 ? (
            <Card className="p-8 text-center text-xs text-slate-500">
              No work experience entries were detected in this resume document.
            </Card>
          ) : (
            experienceList.map((exp) => {
              const compStatus = checkExperienceInProfile(exp.company_name, exp.role_title);
              return (
                <Card
                  key={exp.id}
                  className={`p-5 transition-all space-y-4 border ${
                    exp.selected
                      ? 'border-brand-200 dark:border-brand-900 bg-white dark:bg-slate-900'
                      : 'border-slate-200 dark:border-slate-800 opacity-60 bg-slate-50/50 dark:bg-slate-950/20'
                  }`}
                >
                  <div className="flex items-center justify-between gap-3">
                    <div className="flex items-center gap-3">
                      <input
                        type="checkbox"
                        checked={exp.selected}
                        onChange={(e) => {
                          const checked = e.target.checked;
                          setExperienceList((prev) =>
                            prev.map((item) =>
                              item.id === exp.id ? { ...item, selected: checked } : item
                            )
                          );
                        }}
                        className="w-4 h-4 rounded text-brand-600 focus:ring-brand-500 border-slate-300 dark:border-slate-700"
                        id={`exp_check_${exp.id}`}
                      />
                      <label
                        htmlFor={`exp_check_${exp.id}`}
                        className="text-sm font-semibold text-slate-900 dark:text-white cursor-pointer"
                      >
                        {exp.selected ? 'Include in Profile Merge' : 'Excluded from Merge'}
                      </label>
                    </div>

                    <div className="flex items-center gap-2">
                      <ProfileConflictIndicator status={compStatus} />
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() =>
                          setExperienceList((prev) => prev.filter((item) => item.id !== exp.id))
                        }
                        className="text-slate-400 hover:text-rose-600 h-8 w-8 p-0"
                      >
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 pt-2">
                    <div>
                      <label className="text-xs font-medium text-slate-600 dark:text-slate-400">
                        Company Name
                      </label>
                      <Input
                        value={exp.company_name}
                        onChange={(e) => {
                          const val = e.target.value;
                          setExperienceList((prev) =>
                            prev.map((item) =>
                              item.id === exp.id ? { ...item, company_name: val } : item
                            )
                          );
                        }}
                        className="mt-1"
                      />
                    </div>

                    <div>
                      <label className="text-xs font-medium text-slate-600 dark:text-slate-400">
                        Job Title
                      </label>
                      <Input
                        value={exp.role_title}
                        onChange={(e) => {
                          const val = e.target.value;
                          setExperienceList((prev) =>
                            prev.map((item) =>
                              item.id === exp.id ? { ...item, role_title: val } : item
                            )
                          );
                        }}
                        className="mt-1"
                      />
                    </div>

                    <div>
                      <label className="text-xs font-medium text-slate-600 dark:text-slate-400">
                        Start Date
                      </label>
                      <Input
                        value={exp.start_date}
                        onChange={(e) => {
                          const val = e.target.value;
                          setExperienceList((prev) =>
                            prev.map((item) =>
                              item.id === exp.id ? { ...item, start_date: val } : item
                            )
                          );
                        }}
                        className="mt-1"
                      />
                    </div>

                    <div>
                      <label className="text-xs font-medium text-slate-600 dark:text-slate-400">
                        End Date
                      </label>
                      <Input
                        value={exp.end_date || ''}
                        placeholder={exp.is_current ? 'Current / Present' : 'e.g. 2024-02'}
                        onChange={(e) => {
                          const val = e.target.value;
                          setExperienceList((prev) =>
                            prev.map((item) =>
                              item.id === exp.id
                                ? { ...item, end_date: val || null, is_current: !val }
                                : item
                            )
                          );
                        }}
                        className="mt-1"
                      />
                    </div>
                  </div>

                  {/* Bullet points */}
                  <div className="space-y-2 pt-2">
                    <label className="text-xs font-medium text-slate-600 dark:text-slate-400">
                      Responsibilities & Quantified Achievements
                    </label>
                    {exp.bullet_points.map((bullet, bIdx) => (
                      <div key={bIdx} className="flex items-start gap-2">
                        <span className="text-slate-400 mt-2 text-xs">&bull;</span>
                        <Textarea
                          rows={2}
                          value={bullet}
                          onChange={(e) => {
                            const val = e.target.value;
                            setExperienceList((prev) =>
                              prev.map((item) => {
                                if (item.id !== exp.id) return item;
                                const newBullets = [...item.bullet_points];
                                newBullets[bIdx] = val;
                                return { ...item, bullet_points: newBullets };
                              })
                            );
                          }}
                          className="text-xs"
                        />
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => {
                            setExperienceList((prev) =>
                              prev.map((item) => {
                                if (item.id !== exp.id) return item;
                                return {
                                  ...item,
                                  bullet_points: item.bullet_points.filter((_, i) => i !== bIdx),
                                };
                              })
                            );
                          }}
                          className="h-8 w-8 p-0 text-slate-400 hover:text-rose-500"
                        >
                          <X className="w-3.5 h-3.5" />
                        </Button>
                      </div>
                    ))}
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => {
                        setExperienceList((prev) =>
                          prev.map((item) => {
                            if (item.id !== exp.id) return item;
                            return {
                              ...item,
                              bullet_points: [...item.bullet_points, 'New achievement or responsibility'],
                            };
                          })
                        );
                      }}
                      className="text-xs text-brand-600 dark:text-brand-400"
                    >
                      <Plus className="w-3 h-3 mr-1" /> Add Bullet Point
                    </Button>
                  </div>
                </Card>
              );
            })
          )}
        </div>
      )}

      {/* ───────────────────────────────────────────────────────────── */}
      {/* TAB 3: SKILLS SELECTION                                       */}
      {/* ───────────────────────────────────────────────────────────── */}
      {activeTab === 'skills' && (
        <div className="space-y-6">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div>
              <p className="text-xs text-slate-500 dark:text-slate-400">
                Skills normalized against the CoachPath taxonomy. Checked skills will be linked to your profile as unverified claims.
              </p>
            </div>
            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => {
                  const updated: Record<string, boolean> = {};
                  (preview?.normalized_skills || []).forEach((s) => (updated[s.skill_id] = true));
                  (preview?.raw_unmatched_skills || []).forEach((s) => (updated[s] = true));
                  setSelectedSkills(updated);
                }}
              >
                Select All
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setSelectedSkills({})}
              >
                Deselect All
              </Button>
            </div>
          </div>

          {/* Canonical Matched Skills */}
          <div className="space-y-3">
            <div className="flex items-center gap-2">
              <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-700 dark:text-slate-300">
                Taxonomy Matched Skills ({preview?.normalized_skills.length || 0})
              </h4>
              <Badge variant="verified" size="sm">
                Canonical Link Ready
              </Badge>
            </div>

            {preview?.normalized_skills && preview.normalized_skills.length > 0 ? (
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                {preview.normalized_skills.map((skill) => {
                  const isChecked = !!selectedSkills[skill.skill_id];
                  return (
                    <Card
                      key={skill.skill_id}
                      onClick={() =>
                        setSelectedSkills((prev) => ({
                          ...prev,
                          [skill.skill_id]: !isChecked,
                        }))
                      }
                      className={`p-3 cursor-pointer border flex items-center justify-between gap-3 transition-all ${
                        isChecked
                          ? 'border-brand-500 bg-brand-50/40 dark:bg-brand-950/20'
                          : 'border-slate-200 dark:border-slate-800 opacity-60'
                      }`}
                    >
                      <div className="flex items-center gap-2.5 min-w-0">
                        <input
                          type="checkbox"
                          checked={isChecked}
                          onChange={() => {}} // handled by card onClick
                          className="w-4 h-4 rounded text-brand-600 focus:ring-brand-500 border-slate-300"
                        />
                        <div className="min-w-0">
                          <p className="text-sm font-semibold text-slate-900 dark:text-white truncate">
                            {skill.name}
                          </p>
                          <p className="text-[11px] text-slate-500 capitalize">
                            {skill.category} &bull; Stated in source: &ldquo;{skill.raw_matched}&rdquo;
                          </p>
                        </div>
                      </div>
                    </Card>
                  );
                })}
              </div>
            ) : (
              <p className="text-xs text-slate-400 italic">No canonical skills identified.</p>
            )}
          </div>

          {/* Unmapped Raw Skills */}
          {preview?.raw_unmatched_skills && preview.raw_unmatched_skills.length > 0 && (
            <div className="space-y-3 pt-3">
              <div className="flex items-center gap-2">
                <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-700 dark:text-slate-300">
                  Additional Unmapped Terms ({preview.raw_unmatched_skills.length})
                </h4>
                <Badge variant="secondary" size="sm">
                  Unmapped
                </Badge>
              </div>

              <div className="flex flex-wrap gap-2">
                {preview.raw_unmatched_skills.map((rawTerm) => {
                  const isChecked = !!selectedSkills[rawTerm];
                  return (
                    <button
                      type="button"
                      key={rawTerm}
                      onClick={() =>
                        setSelectedSkills((prev) => ({
                          ...prev,
                          [rawTerm]: !isChecked,
                        }))
                      }
                      className={`px-3 py-1.5 rounded-full text-xs font-medium border flex items-center gap-1.5 transition-all ${
                        isChecked
                          ? 'bg-slate-900 text-white dark:bg-white dark:text-slate-900 border-transparent'
                          : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 border-slate-200 dark:border-slate-700'
                      }`}
                    >
                      {isChecked ? <Check className="w-3 h-3" /> : <Plus className="w-3 h-3" />}
                      {rawTerm}
                    </button>
                  );
                })}
              </div>
            </div>
          )}
        </div>
      )}

      {/* ───────────────────────────────────────────────────────────── */}
      {/* TAB 4: PROJECTS REVIEW                                        */}
      {/* ───────────────────────────────────────────────────────────── */}
      {activeTab === 'projects' && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <p className="text-xs text-slate-500 dark:text-slate-400">
              Technical software repositories and portfolio artifacts extracted from your resume.
            </p>
            <Button
              variant="outline"
              size="sm"
              onClick={() => {
                setProjectsList((prev) => [
                  ...prev,
                  {
                    id: `proj_new_${Date.now()}`,
                    title: 'New Technical Project',
                    description: 'Technical overview and architectural design.',
                    technologies: ['Python', 'FastAPI'],
                    github_url: null,
                    live_url: null,
                    bullet_points: ['Key feature or technical contribution.'],
                    selected: true,
                  },
                ]);
              }}
            >
              <Plus className="w-3.5 h-3.5 mr-1" /> Add Project
            </Button>
          </div>

          {projectsList.length === 0 ? (
            <Card className="p-8 text-center text-xs text-slate-500">
              No technical project entries were detected in this resume document.
            </Card>
          ) : (
            projectsList.map((proj) => {
              const compStatus = checkProjectInProfile(proj.title);
              return (
                <Card
                  key={proj.id}
                  className={`p-5 transition-all space-y-4 border ${
                    proj.selected
                      ? 'border-brand-200 dark:border-brand-900 bg-white dark:bg-slate-900'
                      : 'border-slate-200 dark:border-slate-800 opacity-60 bg-slate-50/50 dark:bg-slate-950/20'
                  }`}
                >
                  <div className="flex items-center justify-between gap-3">
                    <div className="flex items-center gap-3">
                      <input
                        type="checkbox"
                        checked={proj.selected}
                        onChange={(e) => {
                          const checked = e.target.checked;
                          setProjectsList((prev) =>
                            prev.map((item) =>
                              item.id === proj.id ? { ...item, selected: checked } : item
                            )
                          );
                        }}
                        className="w-4 h-4 rounded text-brand-600 focus:ring-brand-500 border-slate-300"
                        id={`proj_check_${proj.id}`}
                      />
                      <label
                        htmlFor={`proj_check_${proj.id}`}
                        className="text-sm font-semibold text-slate-900 dark:text-white cursor-pointer"
                      >
                        {proj.selected ? 'Include in Profile Merge' : 'Excluded from Merge'}
                      </label>
                    </div>

                    <div className="flex items-center gap-2">
                      <ProfileConflictIndicator status={compStatus} />
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() =>
                          setProjectsList((prev) => prev.filter((item) => item.id !== proj.id))
                        }
                        className="text-slate-400 hover:text-rose-600 h-8 w-8 p-0"
                      >
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-2">
                    <div>
                      <label className="text-xs font-medium text-slate-600 dark:text-slate-400">
                        Project Title
                      </label>
                      <Input
                        value={proj.title}
                        onChange={(e) => {
                          const val = e.target.value;
                          setProjectsList((prev) =>
                            prev.map((item) =>
                              item.id === proj.id ? { ...item, title: val } : item
                            )
                          );
                        }}
                        className="mt-1"
                      />
                    </div>

                    <div>
                      <label className="text-xs font-medium text-slate-600 dark:text-slate-400">
                        GitHub URL (Optional)
                      </label>
                      <Input
                        value={proj.github_url || ''}
                        placeholder="https://github.com/..."
                        onChange={(e) => {
                          const val = e.target.value;
                          setProjectsList((prev) =>
                            prev.map((item) =>
                              item.id === proj.id ? { ...item, github_url: val || null } : item
                            )
                          );
                        }}
                        className="mt-1"
                      />
                    </div>

                    <div>
                      <label className="text-xs font-medium text-slate-600 dark:text-slate-400">
                        Live Demo URL (Optional)
                      </label>
                      <Input
                        value={proj.live_url || ''}
                        placeholder="https://..."
                        onChange={(e) => {
                          const val = e.target.value;
                          setProjectsList((prev) =>
                            prev.map((item) =>
                              item.id === proj.id ? { ...item, live_url: val || null } : item
                            )
                          );
                        }}
                        className="mt-1"
                      />
                    </div>
                  </div>

                  <div>
                    <label className="text-xs font-medium text-slate-600 dark:text-slate-400">
                      Project Description
                    </label>
                    <Textarea
                      rows={2}
                      value={proj.description}
                      onChange={(e) => {
                        const val = e.target.value;
                        setProjectsList((prev) =>
                          prev.map((item) =>
                            item.id === proj.id ? { ...item, description: val } : item
                          )
                        );
                      }}
                      className="mt-1 text-xs"
                    />
                  </div>

                  <div>
                    <label className="text-xs font-medium text-slate-600 dark:text-slate-400">
                      Technologies (comma separated)
                    </label>
                    <Input
                      value={proj.technologies.join(', ')}
                      onChange={(e) => {
                        const arr = e.target.value
                          .split(',')
                          .map((t) => t.trim())
                          .filter(Boolean);
                        setProjectsList((prev) =>
                          prev.map((item) =>
                            item.id === proj.id ? { ...item, technologies: arr } : item
                          )
                        );
                      }}
                      className="mt-1 text-xs"
                    />
                  </div>
                </Card>
              );
            })
          )}
        </div>
      )}

      {/* ───────────────────────────────────────────────────────────── */}
      {/* TAB 5: CERTIFICATIONS REVIEW                                 */}
      {/* ───────────────────────────────────────────────────────────── */}
      {activeTab === 'certifications' && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <p className="text-xs text-slate-500 dark:text-slate-400">
              Professional licenses, cloud certifications, and credentials.
            </p>
            <Button
              variant="outline"
              size="sm"
              onClick={() => {
                setCertificationsList((prev) => [
                  ...prev,
                  {
                    id: `cert_new_${Date.now()}`,
                    name: 'Certification Title',
                    issuing_organization: 'Issuing Body',
                    issue_date: '2023-01-01',
                    expiration_date: null,
                    credential_id: null,
                    credential_url: null,
                    selected: true,
                  },
                ]);
              }}
            >
              <Plus className="w-3.5 h-3.5 mr-1" /> Add Certification
            </Button>
          </div>

          {certificationsList.length === 0 ? (
            <Card className="p-8 text-center text-xs text-slate-500">
              No certifications were identified in this document.
            </Card>
          ) : (
            certificationsList.map((cert) => {
              const compStatus = checkCertInProfile(cert.name);
              return (
                <Card
                  key={cert.id}
                  className={`p-5 transition-all space-y-4 border ${
                    cert.selected
                      ? 'border-brand-200 dark:border-brand-900 bg-white dark:bg-slate-900'
                      : 'border-slate-200 dark:border-slate-800 opacity-60 bg-slate-50/50 dark:bg-slate-950/20'
                  }`}
                >
                  <div className="flex items-center justify-between gap-3">
                    <div className="flex items-center gap-3">
                      <input
                        type="checkbox"
                        checked={cert.selected}
                        onChange={(e) => {
                          const checked = e.target.checked;
                          setCertificationsList((prev) =>
                            prev.map((item) =>
                              item.id === cert.id ? { ...item, selected: checked } : item
                            )
                          );
                        }}
                        className="w-4 h-4 rounded text-brand-600 focus:ring-brand-500 border-slate-300"
                        id={`cert_check_${cert.id}`}
                      />
                      <label
                        htmlFor={`cert_check_${cert.id}`}
                        className="text-sm font-semibold text-slate-900 dark:text-white cursor-pointer"
                      >
                        {cert.selected ? 'Include in Profile Merge' : 'Excluded from Merge'}
                      </label>
                    </div>

                    <div className="flex items-center gap-2">
                      <ProfileConflictIndicator status={compStatus} />
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() =>
                          setCertificationsList((prev) =>
                            prev.filter((item) => item.id !== cert.id)
                          )
                        }
                        className="text-slate-400 hover:text-rose-600 h-8 w-8 p-0"
                      >
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 pt-2">
                    <div>
                      <label className="text-xs font-medium text-slate-600 dark:text-slate-400">
                        Certification Name
                      </label>
                      <Input
                        value={cert.name}
                        onChange={(e) => {
                          const val = e.target.value;
                          setCertificationsList((prev) =>
                            prev.map((item) =>
                              item.id === cert.id ? { ...item, name: val } : item
                            )
                          );
                        }}
                        className="mt-1"
                      />
                    </div>

                    <div>
                      <label className="text-xs font-medium text-slate-600 dark:text-slate-400">
                        Issuing Organization
                      </label>
                      <Input
                        value={cert.issuing_organization}
                        onChange={(e) => {
                          const val = e.target.value;
                          setCertificationsList((prev) =>
                            prev.map((item) =>
                              item.id === cert.id
                                ? { ...item, issuing_organization: val }
                                : item
                            )
                          );
                        }}
                        className="mt-1"
                      />
                    </div>

                    <div>
                      <label className="text-xs font-medium text-slate-600 dark:text-slate-400">
                        Issue Date
                      </label>
                      <Input
                        value={cert.issue_date}
                        onChange={(e) => {
                          const val = e.target.value;
                          setCertificationsList((prev) =>
                            prev.map((item) =>
                              item.id === cert.id ? { ...item, issue_date: val } : item
                            )
                          );
                        }}
                        className="mt-1"
                      />
                    </div>

                    <div>
                      <label className="text-xs font-medium text-slate-600 dark:text-slate-400">
                        Credential ID (Optional)
                      </label>
                      <Input
                        value={cert.credential_id || ''}
                        onChange={(e) => {
                          const val = e.target.value;
                          setCertificationsList((prev) =>
                            prev.map((item) =>
                              item.id === cert.id
                                ? { ...item, credential_id: val || null }
                                : item
                            )
                          );
                        }}
                        className="mt-1"
                      />
                    </div>
                  </div>
                </Card>
              );
            })
          )}
        </div>
      )}

      {/* ───────────────────────────────────────────────────────────── */}
      {/* TAB 6: PERSONAL DETAILS REVIEW                                */}
      {/* ───────────────────────────────────────────────────────────── */}
      {activeTab === 'personal' && (
        <Card className="p-6 space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <input
                type="checkbox"
                checked={includePersonalInfo}
                onChange={(e) => setIncludePersonalInfo(e.target.checked)}
                className="w-4 h-4 rounded text-brand-600 focus:ring-brand-500 border-slate-300"
                id="check_personal"
              />
              <label
                htmlFor="check_personal"
                className="text-sm font-semibold text-slate-900 dark:text-white cursor-pointer"
              >
                Apply Contact Details & Professional Links to Profile
              </label>
            </div>
          </div>

          <div
            className={`grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 pt-2 ${
              !includePersonalInfo ? 'opacity-50 pointer-events-none' : ''
            }`}
          >
            <div>
              <label className="text-xs font-medium text-slate-600 dark:text-slate-400">
                Headline
              </label>
              <Input
                value={personalInfo.headline || ''}
                onChange={(e) =>
                  setPersonalInfo((prev) => ({ ...prev, headline: e.target.value || null }))
                }
                className="mt-1"
              />
            </div>

            <div>
              <label className="text-xs font-medium text-slate-600 dark:text-slate-400">
                Location
              </label>
              <Input
                value={personalInfo.location || ''}
                onChange={(e) =>
                  setPersonalInfo((prev) => ({ ...prev, location: e.target.value || null }))
                }
                className="mt-1"
              />
            </div>

            <div>
              <label className="text-xs font-medium text-slate-600 dark:text-slate-400">
                Phone Number
              </label>
              <Input
                value={personalInfo.phone_number || ''}
                onChange={(e) =>
                  setPersonalInfo((prev) => ({ ...prev, phone_number: e.target.value || null }))
                }
                className="mt-1"
              />
            </div>

            <div>
              <label className="text-xs font-medium text-slate-600 dark:text-slate-400">
                LinkedIn Profile URL
              </label>
              <Input
                value={personalInfo.linkedin_url || ''}
                onChange={(e) =>
                  setPersonalInfo((prev) => ({ ...prev, linkedin_url: e.target.value || null }))
                }
                className="mt-1"
              />
            </div>

            <div>
              <label className="text-xs font-medium text-slate-600 dark:text-slate-400">
                GitHub Profile URL
              </label>
              <Input
                value={personalInfo.github_url || ''}
                onChange={(e) =>
                  setPersonalInfo((prev) => ({ ...prev, github_url: e.target.value || null }))
                }
                className="mt-1"
              />
            </div>

            <div>
              <label className="text-xs font-medium text-slate-600 dark:text-slate-400">
                Portfolio URL
              </label>
              <Input
                value={personalInfo.portfolio_url || ''}
                onChange={(e) =>
                  setPersonalInfo((prev) => ({ ...prev, portfolio_url: e.target.value || null }))
                }
                className="mt-1"
              />
            </div>
          </div>
        </Card>
      )}

      {/* ───────────────────────────────────────────────────────────── */}
      {/* TAB 7: EXECUTIVE SUMMARY / RAW EXTRACT                       */}
      {/* ───────────────────────────────────────────────────────────── */}
      {activeTab === 'summary' && (
        <Card className="p-6 space-y-3">
          <h4 className="text-sm font-semibold text-slate-900 dark:text-white">
            Resume Summary & Objective Statement
          </h4>
          <p className="text-xs text-slate-500 dark:text-slate-400">
            Extracted directly from candidate document header:
          </p>
          <div className="p-4 bg-slate-50 dark:bg-slate-800/60 rounded-xl border border-slate-200 dark:border-slate-700 text-xs leading-relaxed text-slate-700 dark:text-slate-300 whitespace-pre-wrap font-mono">
            {preview?.executive_summary ||
              'No standalone executive summary was explicitly detected in this document.'}
          </div>
        </Card>
      )}
    </div>
  );
}
