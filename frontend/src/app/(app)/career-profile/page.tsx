'use client';

import * as React from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs } from '@/components/ui/tabs';
import { Modal } from '@/components/ui/modal';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { ProgressBar } from '@/components/ui/progress-bar';
import { Alert } from '@/components/ui/alert';
import { EmptyState } from '@/components/ui/empty-state';
import { Skeleton } from '@/components/ui/skeleton';
import { profileClient } from '@/lib/profile-client';
import { ApiClientError } from '@/lib/api-client';
import {
  MasterCareerProfile,
  ProfileCertificationEntry,
  ProfileEducationEntry,
  ProfileExperienceEntry,
  ProfileProjectEntry,
  RoleItem,
  UserProfileUpdatePayload,
  CareerGoalsUpdatePayload,
} from '@/types';
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
  Edit3,
  Trash2,
  Loader2,
  Sparkles,
  MapPin,
  Mail,
  Phone,
  Globe,
  Linkedin,
  Calendar,
  AlertCircle,
} from 'lucide-react';

export default function CareerProfilePage() {
  const [activeTab, setActiveTab] = React.useState('overview');
  const [profile, setProfile] = React.useState<MasterCareerProfile | null>(null);
  const [supportedRoles, setSupportedRoles] = React.useState<RoleItem[]>([]);
  const [isLoading, setIsLoading] = React.useState(true);
  const [actionLoading, setActionLoading] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);
  const [notification, setNotification] = React.useState<{
    type: 'success' | 'error';
    message: string;
  } | null>(null);

  // Modals state
  const [isResumeModalOpen, setIsResumeModalOpen] = React.useState(false);
  const [isPersonalModalOpen, setIsPersonalModalOpen] = React.useState(false);
  const [isGoalsModalOpen, setIsGoalsModalOpen] = React.useState(false);

  // CRUD Item Modals
  const [experienceModal, setExperienceModal] = React.useState<{
    isOpen: boolean;
    mode: 'add' | 'edit';
    item?: ProfileExperienceEntry;
  }>({ isOpen: false, mode: 'add' });

  const [projectModal, setProjectModal] = React.useState<{
    isOpen: boolean;
    mode: 'add' | 'edit';
    item?: ProfileProjectEntry;
  }>({ isOpen: false, mode: 'add' });

  const [educationModal, setEducationModal] = React.useState<{
    isOpen: boolean;
    mode: 'add' | 'edit';
    item?: ProfileEducationEntry;
  }>({ isOpen: false, mode: 'add' });

  const [certModal, setCertModal] = React.useState<{
    isOpen: boolean;
    mode: 'add' | 'edit';
    item?: ProfileCertificationEntry;
  }>({ isOpen: false, mode: 'add' });

  const [deleteModal, setDeleteModal] = React.useState<{
    isOpen: boolean;
    type: 'experience' | 'project' | 'education' | 'cert';
    id: string;
    title: string;
  }>({ isOpen: false, type: 'experience', id: '', title: '' });

  // Form states
  const [personalForm, setPersonalForm] = React.useState<UserProfileUpdatePayload>({});
  const [goalsForm, setGoalsForm] = React.useState<CareerGoalsUpdatePayload>({
    primary_role_id: 'backend-developer',
    secondary_role_id: '',
    career_stage: 'student',
    work_preference: 'hybrid',
    target_locations: ['Remote'],
    years_of_experience: 0,
  });

  // Entry forms
  const [expForm, setExpForm] = React.useState({
    company_name: '',
    role_title: '',
    location: '',
    start_date: '',
    end_date: '',
    is_current: false,
    bulletsText: '',
  });

  const [projForm, setProjForm] = React.useState({
    title: '',
    description: '',
    technologiesText: '',
    github_url: '',
    live_url: '',
    bulletsText: '',
  });

  const [eduForm, setEduForm] = React.useState({
    institution_name: '',
    degree: '',
    field_of_study: '',
    start_date: '',
    end_date: '',
    is_current: false,
    gpa: '',
  });

  const [certForm, setCertForm] = React.useState({
    name: '',
    issuing_organization: '',
    issue_date: '',
    expiration_date: '',
    credential_id: '',
    credential_url: '',
  });

  // Fetch initial profile & roles
  const loadProfile = React.useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);
      const [masterData, rolesData] = await Promise.all([
        profileClient.getMasterProfile(),
        profileClient.getSupportedRoles().catch(() => []),
      ]);
      setProfile(masterData);
      setSupportedRoles(rolesData);
    } catch (err: unknown) {
      if (err instanceof ApiClientError) {
        setError(err.message);
      } else {
        setError('Failed to load career profile. Please verify your connection.');
      }
    } finally {
      setIsLoading(false);
    }
  }, []);

  React.useEffect(() => {
    loadProfile();
  }, [loadProfile]);

  // Show transient notifications
  const showNotification = (type: 'success' | 'error', message: string) => {
    setNotification({ type, message });
    setTimeout(() => {
      setNotification((curr) => (curr?.message === message ? null : curr));
    }, 4500);
  };

  // Helper initials
  const initials = React.useMemo(() => {
    if (!profile?.full_name) return 'CP';
    const parts = profile.full_name.trim().split(/\s+/);
    if (parts.length >= 2) return `${parts[0][0]}${parts[1][0]}`.toUpperCase();
    return profile.full_name.slice(0, 2).toUpperCase();
  }, [profile?.full_name]);

  // ---------------------------------------------------------------------------
  // Action Handlers
  // ---------------------------------------------------------------------------

  // Personal Info update
  const openPersonalModal = () => {
    if (!profile) return;
    setPersonalForm({
      full_name: profile.full_name,
      headline: profile.headline || '',
      location: profile.location || '',
      phone_number: profile.phone_number || '',
      linkedin_url: profile.linkedin_url || '',
      github_url: profile.github_url || '',
      portfolio_url: profile.portfolio_url || '',
      bio: profile.bio || '',
    });
    setIsPersonalModalOpen(true);
  };

  const handleSavePersonal = async (e: React.FormEvent) => {
    e.preventDefault();
    setActionLoading(true);
    try {
      const updated = await profileClient.updatePersonalProfile(personalForm);
      setProfile(updated);
      setIsPersonalModalOpen(false);
      showNotification('success', 'Personal details successfully updated.');
    } catch (err: unknown) {
      const msg = err instanceof ApiClientError ? err.message : 'Error updating profile';
      showNotification('error', msg);
    } finally {
      setActionLoading(false);
    }
  };

  // Career Goals update
  const openGoalsModal = () => {
    if (!profile) return;
    setGoalsForm({
      primary_role_id: profile.primary_role?.id || 'backend-developer',
      secondary_role_id: profile.secondary_role?.id || '',
      career_stage: profile.career_stage || 'student',
      work_preference: profile.work_preference || 'hybrid',
      target_locations: profile.target_locations || ['Remote'],
      years_of_experience: profile.years_of_experience || 0,
    });
    setIsGoalsModalOpen(true);
  };

  const handleSaveGoals = async (e: React.FormEvent) => {
    e.preventDefault();
    setActionLoading(true);
    try {
      await profileClient.updateCareerGoals({
        ...goalsForm,
        secondary_role_id: goalsForm.secondary_role_id || null,
      });
      // Refresh master profile to synchronize completeness
      const refreshed = await profileClient.getMasterProfile();
      setProfile(refreshed);
      setIsGoalsModalOpen(false);
      showNotification('success', 'Career goals and preferences calibrated.');
    } catch (err: unknown) {
      const msg = err instanceof ApiClientError ? err.message : 'Error saving career goals';
      showNotification('error', msg);
    } finally {
      setActionLoading(false);
    }
  };

  // Experience handlers
  const openAddExperience = () => {
    setExpForm({
      company_name: '',
      role_title: '',
      location: '',
      start_date: '',
      end_date: '',
      is_current: false,
      bulletsText: '',
    });
    setExperienceModal({ isOpen: true, mode: 'add' });
  };

  const openEditExperience = (item: ProfileExperienceEntry) => {
    setExpForm({
      company_name: item.company_name,
      role_title: item.role_title,
      location: item.location || '',
      start_date: item.start_date,
      end_date: item.end_date || '',
      is_current: item.is_current,
      bulletsText: (item.bullet_points || []).join('\n'),
    });
    setExperienceModal({ isOpen: true, mode: 'edit', item });
  };

  const handleSaveExperience = async (e: React.FormEvent) => {
    e.preventDefault();
    setActionLoading(true);
    const bullets = expForm.bulletsText
      .split('\n')
      .map((b) => b.trim())
      .filter(Boolean);

    try {
      if (experienceModal.mode === 'add') {
        await profileClient.createExperience({
          company_name: expForm.company_name,
          role_title: expForm.role_title,
          location: expForm.location || null,
          start_date: expForm.start_date,
          end_date: expForm.is_current ? null : expForm.end_date || null,
          is_current: expForm.is_current,
          bullet_points: bullets,
        });
      } else if (experienceModal.item) {
        await profileClient.updateExperience(experienceModal.item.id, {
          company_name: expForm.company_name,
          role_title: expForm.role_title,
          location: expForm.location || null,
          start_date: expForm.start_date,
          end_date: expForm.is_current ? null : expForm.end_date || null,
          is_current: expForm.is_current,
          bullet_points: bullets,
        });
      }
      const refreshed = await profileClient.getMasterProfile();
      setProfile(refreshed);
      setExperienceModal({ isOpen: false, mode: 'add' });
      showNotification(
        'success',
        experienceModal.mode === 'add'
          ? 'Work position added successfully.'
          : 'Work position updated.'
      );
    } catch (err: unknown) {
      const msg = err instanceof ApiClientError ? err.message : 'Failed to save experience';
      showNotification('error', msg);
    } finally {
      setActionLoading(false);
    }
  };

  // Projects handlers
  const openAddProject = () => {
    setProjForm({
      title: '',
      description: '',
      technologiesText: '',
      github_url: '',
      live_url: '',
      bulletsText: '',
    });
    setProjectModal({ isOpen: true, mode: 'add' });
  };

  const openEditProject = (item: ProfileProjectEntry) => {
    setProjForm({
      title: item.title,
      description: item.description,
      technologiesText: (item.technologies || []).join(', '),
      github_url: item.github_url || '',
      live_url: item.live_url || '',
      bulletsText: (item.bullet_points || []).join('\n'),
    });
    setProjectModal({ isOpen: true, mode: 'edit', item });
  };

  const handleSaveProject = async (e: React.FormEvent) => {
    e.preventDefault();
    setActionLoading(true);
    const tech = projForm.technologiesText
      .split(',')
      .map((t) => t.trim())
      .filter(Boolean);
    const bullets = projForm.bulletsText
      .split('\n')
      .map((b) => b.trim())
      .filter(Boolean);

    try {
      if (projectModal.mode === 'add') {
        await profileClient.createProject({
          title: projForm.title,
          description: projForm.description,
          technologies: tech,
          github_url: projForm.github_url || null,
          live_url: projForm.live_url || null,
          bullet_points: bullets,
        });
      } else if (projectModal.item) {
        await profileClient.updateProject(projectModal.item.id, {
          title: projForm.title,
          description: projForm.description,
          technologies: tech,
          github_url: projForm.github_url || null,
          live_url: projForm.live_url || null,
          bullet_points: bullets,
        });
      }
      const refreshed = await profileClient.getMasterProfile();
      setProfile(refreshed);
      setProjectModal({ isOpen: false, mode: 'add' });
      showNotification(
        'success',
        projectModal.mode === 'add'
          ? 'Project repository added.'
          : 'Project details updated.'
      );
    } catch (err: unknown) {
      const msg = err instanceof ApiClientError ? err.message : 'Failed to save project';
      showNotification('error', msg);
    } finally {
      setActionLoading(false);
    }
  };

  // Education handlers
  const openAddEducation = () => {
    setEduForm({
      institution_name: '',
      degree: '',
      field_of_study: '',
      start_date: '',
      end_date: '',
      is_current: false,
      gpa: '',
    });
    setEducationModal({ isOpen: true, mode: 'add' });
  };

  const openEditEducation = (item: ProfileEducationEntry) => {
    setEduForm({
      institution_name: item.institution_name,
      degree: item.degree,
      field_of_study: item.field_of_study,
      start_date: item.start_date,
      end_date: item.end_date || '',
      is_current: item.is_current,
      gpa: item.gpa !== null && item.gpa !== undefined ? String(item.gpa) : '',
    });
    setEducationModal({ isOpen: true, mode: 'edit', item });
  };

  const handleSaveEducation = async (e: React.FormEvent) => {
    e.preventDefault();
    setActionLoading(true);
    const parsedGpa = eduForm.gpa ? parseFloat(eduForm.gpa) : null;

    try {
      if (educationModal.mode === 'add') {
        await profileClient.createEducation({
          institution_name: eduForm.institution_name,
          degree: eduForm.degree,
          field_of_study: eduForm.field_of_study,
          start_date: eduForm.start_date,
          end_date: eduForm.is_current ? null : eduForm.end_date || null,
          is_current: eduForm.is_current,
          gpa: parsedGpa,
        });
      } else if (educationModal.item) {
        await profileClient.updateEducation(educationModal.item.id, {
          institution_name: eduForm.institution_name,
          degree: eduForm.degree,
          field_of_study: eduForm.field_of_study,
          start_date: eduForm.start_date,
          end_date: eduForm.is_current ? null : eduForm.end_date || null,
          is_current: eduForm.is_current,
          gpa: parsedGpa,
        });
      }
      const refreshed = await profileClient.getMasterProfile();
      setProfile(refreshed);
      setEducationModal({ isOpen: false, mode: 'add' });
      showNotification(
        'success',
        educationModal.mode === 'add'
          ? 'Academic credential added.'
          : 'Academic credential updated.'
      );
    } catch (err: unknown) {
      const msg = err instanceof ApiClientError ? err.message : 'Failed to save education';
      showNotification('error', msg);
    } finally {
      setActionLoading(false);
    }
  };

  // Certification handlers
  const openAddCert = () => {
    setCertForm({
      name: '',
      issuing_organization: '',
      issue_date: '',
      expiration_date: '',
      credential_id: '',
      credential_url: '',
    });
    setCertModal({ isOpen: true, mode: 'add' });
  };

  const openEditCert = (item: ProfileCertificationEntry) => {
    setCertForm({
      name: item.name,
      issuing_organization: item.issuing_organization,
      issue_date: item.issue_date,
      expiration_date: item.expiration_date || '',
      credential_id: item.credential_id || '',
      credential_url: item.credential_url || '',
    });
    setCertModal({ isOpen: true, mode: 'edit', item });
  };

  const handleSaveCert = async (e: React.FormEvent) => {
    e.preventDefault();
    setActionLoading(true);
    try {
      if (certModal.mode === 'add') {
        await profileClient.createCertification({
          name: certForm.name,
          issuing_organization: certForm.issuing_organization,
          issue_date: certForm.issue_date,
          expiration_date: certForm.expiration_date || null,
          credential_id: certForm.credential_id || null,
          credential_url: certForm.credential_url || null,
        });
      } else if (certModal.item) {
        await profileClient.updateCertification(certModal.item.id, {
          name: certForm.name,
          issuing_organization: certForm.issuing_organization,
          issue_date: certForm.issue_date,
          expiration_date: certForm.expiration_date || null,
          credential_id: certForm.credential_id || null,
          credential_url: certForm.credential_url || null,
        });
      }
      const refreshed = await profileClient.getMasterProfile();
      setProfile(refreshed);
      setCertModal({ isOpen: false, mode: 'add' });
      showNotification(
        'success',
        certModal.mode === 'add'
          ? 'Certification credential added.'
          : 'Certification credential updated.'
      );
    } catch (err: unknown) {
      const msg = err instanceof ApiClientError ? err.message : 'Failed to save certification';
      showNotification('error', msg);
    } finally {
      setActionLoading(false);
    }
  };

  // Deletion handler
  const confirmDelete = async () => {
    setActionLoading(true);
    try {
      if (deleteModal.type === 'experience') {
        await profileClient.deleteExperience(deleteModal.id);
      } else if (deleteModal.type === 'project') {
        await profileClient.deleteProject(deleteModal.id);
      } else if (deleteModal.type === 'education') {
        await profileClient.deleteEducation(deleteModal.id);
      } else if (deleteModal.type === 'cert') {
        await profileClient.deleteCertification(deleteModal.id);
      }
      const refreshed = await profileClient.getMasterProfile();
      setProfile(refreshed);
      setDeleteModal({ isOpen: false, type: 'experience', id: '', title: '' });
      showNotification('success', 'Entry deleted successfully.');
    } catch (err: unknown) {
      const msg = err instanceof ApiClientError ? err.message : 'Failed to delete record';
      showNotification('error', msg);
    } finally {
      setActionLoading(false);
    }
  };

  // Export profile JSON
  const handleExportGraph = () => {
    if (!profile) return;
    const blob = new Blob([JSON.stringify(profile, null, 2)], {
      type: 'application/json',
    });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `CoachPath_Profile_${profile.full_name.replace(/\s+/g, '_')}.json`;
    link.click();
    URL.revokeObjectURL(url);
    showNotification('success', 'Profile graph JSON exported.');
  };

  // Tabs configuration
  const tabs = [
    {
      id: 'overview',
      label: 'Overview & Goals',
      icon: <User className="w-4 h-4" />,
    },
    {
      id: 'experience',
      label: 'Work Experience',
      icon: <Briefcase className="w-4 h-4" />,
      badge: profile?.experience.length || 0,
    },
    {
      id: 'projects',
      label: 'Verified Projects',
      icon: <FolderGit2 className="w-4 h-4" />,
      badge: profile?.projects.length || 0,
    },
    {
      id: 'education',
      label: 'Education & Certs',
      icon: <GraduationCap className="w-4 h-4" />,
      badge: (profile?.education.length || 0) + (profile?.certifications.length || 0),
    },
  ];

  // Loading state
  if (isLoading) {
    return (
      <div className="space-y-6">
        <Card className="p-6 md:p-8 space-y-4">
          <div className="flex items-center gap-4">
            <Skeleton className="h-20 w-20 rounded-2xl" />
            <div className="space-y-2 flex-1">
              <Skeleton className="h-7 w-48" />
              <Skeleton className="h-4 w-72" />
              <Skeleton className="h-4 w-36" />
            </div>
          </div>
        </Card>
        <Skeleton className="h-12 w-full rounded-xl" />
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 space-y-6">
            <Skeleton className="h-44 w-full rounded-xl" />
            <Skeleton className="h-44 w-full rounded-xl" />
          </div>
          <Skeleton className="h-64 w-full rounded-xl" />
        </div>
      </div>
    );
  }

  // Error state
  if (error || !profile) {
    return (
      <div className="space-y-6">
        <Alert variant="destructive" title="Unable to load Career Profile">
          <p>{error || 'An unexpected error occurred while fetching your profile.'}</p>
          <div className="mt-4">
            <Button size="sm" variant="primary" onClick={loadProfile}>
              Retry Connection
            </Button>
          </div>
        </Alert>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Toast Notification */}
      {notification && (
        <div className="fixed bottom-6 right-6 z-50 animate-in fade-in slide-in-from-bottom-4">
          <Alert
            variant={notification.type === 'success' ? 'success' : 'destructive'}
            title={notification.type === 'success' ? 'Success' : 'Error'}
          >
            {notification.message}
          </Alert>
        </div>
      )}

      {/* Profile Header Banner */}
      <Card className="p-6 md:p-8">
        <div className="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-6">
          <div className="flex items-start sm:items-center gap-5">
            <div className="h-20 w-20 rounded-2xl bg-gradient-to-tr from-brand-600 to-purple-600 text-white flex items-center justify-center font-extrabold text-2xl shadow-lg shrink-0">
              {initials}
            </div>
            <div className="space-y-1">
              <div className="flex flex-wrap items-center gap-2">
                <h2 className="text-2xl font-bold text-slate-900 dark:text-white">
                  {profile.full_name}
                </h2>
                <Badge variant="verified" size="sm">
                  <ShieldCheck className="w-3.5 h-3.5 mr-1" /> Profile Active
                </Badge>
                <Badge variant="default" size="sm">
                  {profile.completeness_score.toFixed(0)}% Complete
                </Badge>
              </div>
              <p className="text-sm font-medium text-slate-600 dark:text-slate-300">
                {profile.headline || 'Career Profile Candidate'}
                {profile.location ? ` • ${profile.location}` : ''}
              </p>
              <div className="flex flex-wrap items-center gap-2 pt-1 text-xs text-slate-500 dark:text-slate-400">
                <span>Target Role:</span>
                <span className="font-bold text-purple-700 dark:text-purple-300 bg-purple-50 dark:bg-purple-950/40 px-2 py-0.5 rounded border border-purple-200 dark:border-purple-800">
                  {profile.primary_role?.title || 'Backend Developer'}
                </span>
                <span>• {profile.years_of_experience} YOE</span>
                <span>• Stage: {profile.career_stage.replace('_', ' ')}</span>
                <span>• Pref: {profile.work_preference}</span>
              </div>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-2 self-stretch lg:self-auto">
            <Button
              variant="outline"
              size="sm"
              onClick={openPersonalModal}
            >
              <Edit3 className="w-3.5 h-3.5 mr-1.5" /> Edit Details
            </Button>
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
              onClick={handleExportGraph}
            >
              <Download className="w-3.5 h-3.5 mr-1.5" /> Export Graph
            </Button>
          </div>
        </div>

        {/* Completeness Engine Progress Bar */}
        <div className="mt-6 pt-5 border-t border-slate-100 dark:border-slate-800 space-y-2">
          <div className="flex items-center justify-between text-xs">
            <span className="font-semibold text-slate-700 dark:text-slate-300 flex items-center gap-1.5">
              <Sparkles className="w-3.5 h-3.5 text-purple-600" />
              Deterministic Profile Completeness Engine
            </span>
            <span className="font-bold text-purple-700 dark:text-purple-300 font-mono">
              {profile.completeness_score.toFixed(0)}%
            </span>
          </div>
          <ProgressBar
            value={profile.completeness_score}
            variant="intelligence"
            size="md"
          />
          <div className="flex flex-wrap items-center gap-2 text-[11px] text-slate-500 dark:text-slate-400 pt-1">
            <span className={profile.headline && profile.location ? 'text-emerald-600 font-semibold' : ''}>
              ✓ Details (20%)
            </span>
            <span>•</span>
            <span className={profile.primary_role ? 'text-emerald-600 font-semibold' : ''}>
              ✓ Goals (20%)
            </span>
            <span>•</span>
            <span className={profile.education.length > 0 ? 'text-emerald-600 font-semibold' : ''}>
              {profile.education.length > 0 ? '✓' : '○'} Education (20%)
            </span>
            <span>•</span>
            <span className={profile.experience.length > 0 ? 'text-emerald-600 font-semibold' : ''}>
              {profile.experience.length > 0 ? '✓' : '○'} Experience (20%)
            </span>
            <span>•</span>
            <span className={profile.projects.length > 0 ? 'text-emerald-600 font-semibold' : ''}>
              {profile.projects.length > 0 ? '✓' : '○'} Projects (15%)
            </span>
            <span>•</span>
            <span className={profile.certifications.length > 0 ? 'text-emerald-600 font-semibold' : ''}>
              {profile.certifications.length > 0 ? '✓' : '○'} Certs (5%)
            </span>
          </div>
        </div>
      </Card>

      {/* Tabs Navigation */}
      <Tabs tabs={tabs} activeTab={activeTab} onChange={setActiveTab} />

      {/* =================================================================== */}
      {/* Tab 1: Overview & Goals                                             */}
      {/* =================================================================== */}
      {activeTab === 'overview' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 space-y-6">
            {/* Bio & Summary */}
            <Card className="p-6 space-y-3">
              <div className="flex items-center justify-between">
                <h3 className="text-base font-bold text-slate-900 dark:text-white">
                  Executive Bio & Professional Narrative
                </h3>
                <Button variant="ghost" size="sm" onClick={openPersonalModal}>
                  <Edit3 className="w-3.5 h-3.5 mr-1" /> Edit
                </Button>
              </div>
              <p className="text-sm text-slate-600 dark:text-slate-300 leading-relaxed whitespace-pre-line">
                {profile.bio ||
                  'No professional biography added yet. Click "Edit" to summarize your technical background, career trajectory, and engineering philosophy.'}
              </p>
            </Card>

            {/* Target Roles & Exploration */}
            <Card className="p-6 space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-base font-bold text-slate-900 dark:text-white">
                    Benchmark Target Roles & Trajectory
                  </h3>
                  <p className="text-xs text-slate-500">
                    Primary and secondary benchmark paths calibrated against our skill taxonomy.
                  </p>
                </div>
                <Button variant="outline" size="sm" onClick={openGoalsModal}>
                  <Edit3 className="w-3.5 h-3.5 mr-1" /> Calibrate Goals
                </Button>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-1">
                <div className="p-4 rounded-xl bg-purple-50/50 dark:bg-purple-950/20 border border-purple-200/60 dark:border-purple-800/60 space-y-1.5">
                  <span className="text-[11px] font-semibold uppercase tracking-wider text-purple-700 dark:text-purple-300">
                    Primary Target Benchmark
                  </span>
                  <p className="text-sm font-bold text-slate-900 dark:text-white">
                    {profile.primary_role?.title || 'Backend Developer'}
                  </p>
                  <p className="text-xs text-slate-600 dark:text-slate-400">
                    {profile.primary_role?.description ||
                      'Server-side application architecture and database systems.'}
                  </p>
                </div>

                <div className="p-4 rounded-xl bg-slate-50 dark:bg-slate-800/40 border border-slate-200/80 dark:border-slate-800 space-y-1.5">
                  <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-500">
                    Secondary Target Trajectory
                  </span>
                  <p className="text-sm font-bold text-slate-900 dark:text-white">
                    {profile.secondary_role?.title || 'None Specified'}
                  </p>
                  <p className="text-xs text-slate-600 dark:text-slate-400">
                    {profile.secondary_role?.description ||
                      'Select a secondary benchmark role to compare skill alignments across disciplines.'}
                  </p>
                </div>
              </div>

              <div className="pt-2 text-xs space-y-1 text-slate-600 dark:text-slate-400">
                <div className="flex gap-2">
                  <span className="font-semibold text-slate-700 dark:text-slate-300">Target Locations:</span>
                  <span>{profile.target_locations.join(', ') || 'Remote'}</span>
                </div>
                <div className="flex gap-2">
                  <span className="font-semibold text-slate-700 dark:text-slate-300">Work Preference:</span>
                  <span className="capitalize">{profile.work_preference}</span>
                </div>
              </div>
            </Card>

            {/* Social & Contact Links */}
            <Card className="p-6 space-y-4">
              <h3 className="text-base font-bold text-slate-900 dark:text-white">
                Contact & Professional Profiles
              </h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
                <div className="flex items-center gap-2.5 p-3 rounded-lg bg-slate-50 dark:bg-slate-800/50">
                  <Mail className="w-4 h-4 text-slate-400" />
                  <div className="truncate">
                    <span className="text-slate-400 block text-[10px]">Email</span>
                    <span className="font-medium text-slate-800 dark:text-slate-200 truncate">{profile.email}</span>
                  </div>
                </div>

                <div className="flex items-center gap-2.5 p-3 rounded-lg bg-slate-50 dark:bg-slate-800/50">
                  <Phone className="w-4 h-4 text-slate-400" />
                  <div className="truncate">
                    <span className="text-slate-400 block text-[10px]">Phone</span>
                    <span className="font-medium text-slate-800 dark:text-slate-200">{profile.phone_number || 'Not provided'}</span>
                  </div>
                </div>

                <div className="flex items-center gap-2.5 p-3 rounded-lg bg-slate-50 dark:bg-slate-800/50">
                  <Linkedin className="w-4 h-4 text-brand-600" />
                  <div className="truncate">
                    <span className="text-slate-400 block text-[10px]">LinkedIn</span>
                    {profile.linkedin_url ? (
                      <a href={profile.linkedin_url} target="_blank" rel="noopener noreferrer" className="font-medium text-brand-600 hover:underline truncate block">
                        {profile.linkedin_url.replace(/^https?:\/\//, '')}
                      </a>
                    ) : (
                      <span className="text-slate-400">Not provided</span>
                    )}
                  </div>
                </div>

                <div className="flex items-center gap-2.5 p-3 rounded-lg bg-slate-50 dark:bg-slate-800/50">
                  <Github className="w-4 h-4 text-slate-800 dark:text-slate-200" />
                  <div className="truncate">
                    <span className="text-slate-400 block text-[10px]">GitHub</span>
                    {profile.github_url ? (
                      <a href={profile.github_url} target="_blank" rel="noopener noreferrer" className="font-medium text-brand-600 hover:underline truncate block">
                        {profile.github_url.replace(/^https?:\/\//, '')}
                      </a>
                    ) : (
                      <span className="text-slate-400">Not provided</span>
                    )}
                  </div>
                </div>

                {profile.portfolio_url && (
                  <div className="sm:col-span-2 flex items-center gap-2.5 p-3 rounded-lg bg-slate-50 dark:bg-slate-800/50">
                    <Globe className="w-4 h-4 text-emerald-600" />
                    <div className="truncate">
                      <span className="text-slate-400 block text-[10px]">Portfolio Website</span>
                      <a href={profile.portfolio_url} target="_blank" rel="noopener noreferrer" className="font-medium text-brand-600 hover:underline truncate block">
                        {profile.portfolio_url}
                      </a>
                    </div>
                  </div>
                )}
              </div>
            </Card>
          </div>

          {/* Right Column: Evidence Summary & Metadata */}
          <div className="space-y-6">
            <Card className="p-6 space-y-4">
              <h3 className="text-base font-bold text-slate-900 dark:text-white">
                Career Evidence Graph
              </h3>
              <div className="space-y-3 text-xs text-slate-600 dark:text-slate-300">
                <div className="flex justify-between py-1.5 border-b border-slate-100 dark:border-slate-800">
                  <span className="text-slate-400">Work Positions:</span>
                  <span className="font-bold text-slate-800 dark:text-slate-200">
                    {profile.experience.length} Entries
                  </span>
                </div>
                <div className="flex justify-between py-1.5 border-b border-slate-100 dark:border-slate-800">
                  <span className="text-slate-400">Technical Projects:</span>
                  <span className="font-bold text-slate-800 dark:text-slate-200">
                    {profile.projects.length} Repositories
                  </span>
                </div>
                <div className="flex justify-between py-1.5 border-b border-slate-100 dark:border-slate-800">
                  <span className="text-slate-400">Academic Degrees:</span>
                  <span className="font-bold text-slate-800 dark:text-slate-200">
                    {profile.education.length} Credentials
                  </span>
                </div>
                <div className="flex justify-between py-1.5 border-b border-slate-100 dark:border-slate-800">
                  <span className="text-slate-400">Certifications:</span>
                  <span className="font-bold text-slate-800 dark:text-slate-200">
                    {profile.certifications.length} Certified
                  </span>
                </div>
                <div className="flex justify-between py-1.5 border-b border-slate-100 dark:border-slate-800">
                  <span className="text-slate-400">Verified Skills:</span>
                  <span className="font-bold text-emerald-600">
                    {profile.verified_skills_count} Verified
                  </span>
                </div>
                <div className="flex justify-between py-1 text-[11px] text-slate-400">
                  <span>Profile Storage:</span>
                  <span className="font-mono text-slate-500">PostgreSQL Isolated</span>
                </div>
              </div>
            </Card>

            <Card className="p-6 space-y-3 bg-purple-50/30 dark:bg-purple-950/20 border-purple-200/60 dark:border-purple-900/40">
              <div className="flex items-center gap-2 text-purple-700 dark:text-purple-300 font-bold text-sm">
                <ShieldCheck className="w-4 h-4" />
                <span>Deterministic Ground Truth</span>
              </div>
              <p className="text-xs text-slate-600 dark:text-slate-400 leading-relaxed">
                CoachPath guarantees zero hallucinations: resume bullets and job match algorithms
                strictly derive their claims from the verified credentials and project evidence
                recorded here.
              </p>
            </Card>
          </div>
        </div>
      )}

      {/* =================================================================== */}
      {/* Tab 2: Work Experience                                             */}
      {/* =================================================================== */}
      {activeTab === 'experience' && (
        <div className="space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div>
              <h3 className="text-base font-bold text-slate-900 dark:text-white">
                Professional Experience ({profile.experience.length})
              </h3>
              <p className="text-xs text-slate-500">
                Verified work history and company contributions.
              </p>
            </div>
            <Button size="sm" variant="outline" onClick={openAddExperience}>
              <Plus className="w-3.5 h-3.5 mr-1" /> Add Position
            </Button>
          </div>

          {profile.experience.length === 0 ? (
            <Card className="p-8">
              <EmptyState
                icon={<Briefcase className="w-10 h-10 text-slate-400" />}
                title="No work experience entries yet"
                description="Add your internships, software engineering roles, or co-op experiences to power semantic matching."
                actionLabel="Add Your First Position"
                onAction={openAddExperience}
              />
            </Card>
          ) : (
            <div className="space-y-4">
              {profile.experience.map((exp) => (
                <Card key={exp.id} className="p-6 space-y-3">
                  <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-2">
                    <div>
                      <h4 className="text-base font-bold text-slate-900 dark:text-white">
                        {exp.role_title}
                      </h4>
                      <p className="text-xs font-semibold text-purple-700 dark:text-purple-300">
                        {exp.company_name}
                        {exp.location ? ` • ${exp.location}` : ''}
                      </p>
                    </div>
                    <div className="flex items-center gap-2 self-start sm:self-auto">
                      <span className="text-xs font-mono text-slate-500 bg-slate-100 dark:bg-slate-800 px-2.5 py-1 rounded-md">
                        {exp.start_date} – {exp.is_current ? 'Present' : exp.end_date || 'N/A'}
                      </span>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => openEditExperience(exp)}
                        aria-label="Edit position"
                      >
                        <Edit3 className="w-3.5 h-3.5" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() =>
                          setDeleteModal({
                            isOpen: true,
                            type: 'experience',
                            id: exp.id,
                            title: `${exp.role_title} at ${exp.company_name}`,
                          })
                        }
                        className="text-rose-600 hover:text-rose-700 hover:bg-rose-50 dark:hover:bg-rose-950/30"
                        aria-label="Delete position"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </Button>
                    </div>
                  </div>

                  {exp.bullet_points && exp.bullet_points.length > 0 && (
                    <ul className="list-disc list-inside space-y-1.5 text-xs text-slate-600 dark:text-slate-300 leading-relaxed pt-1">
                      {exp.bullet_points.map((bullet, idx) => (
                        <li key={idx}>{bullet}</li>
                      ))}
                    </ul>
                  )}
                </Card>
              ))}
            </div>
          )}
        </div>
      )}

      {/* =================================================================== */}
      {/* Tab 3: Verified Projects                                           */}
      {/* =================================================================== */}
      {activeTab === 'projects' && (
        <div className="space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div>
              <h3 className="text-base font-bold text-slate-900 dark:text-white">
                Technical Projects & Evidence Artifacts ({profile.projects.length})
              </h3>
              <p className="text-xs text-slate-500">
                Software repositories, system architecture capstones, and open-source contributions.
              </p>
            </div>
            <Button size="sm" variant="outline" onClick={openAddProject}>
              <Plus className="w-3.5 h-3.5 mr-1" /> Add Repository
            </Button>
          </div>

          {profile.projects.length === 0 ? (
            <Card className="p-8">
              <EmptyState
                icon={<FolderGit2 className="w-10 h-10 text-slate-400" />}
                title="No projects added yet"
                description="Technical projects serve as verifiable proof for resume bullets and diagnostic confidence scores."
                actionLabel="Add Your First Project"
                onAction={openAddProject}
              />
            </Card>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {profile.projects.map((proj) => (
                <Card key={proj.id} className="p-6 flex flex-col justify-between space-y-4">
                  <div className="space-y-2">
                    <div className="flex items-start justify-between gap-2">
                      <h4 className="text-base font-bold text-slate-900 dark:text-white">
                        {proj.title}
                      </h4>
                      <div className="flex items-center gap-1">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => openEditProject(proj)}
                          aria-label="Edit project"
                        >
                          <Edit3 className="w-3.5 h-3.5" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() =>
                            setDeleteModal({
                              isOpen: true,
                              type: 'project',
                              id: proj.id,
                              title: proj.title,
                            })
                          }
                          className="text-rose-600 hover:text-rose-700 hover:bg-rose-50 dark:hover:bg-rose-950/30"
                          aria-label="Delete project"
                        >
                          <Trash2 className="w-3.5 h-3.5" />
                        </Button>
                      </div>
                    </div>

                    <p className="text-xs text-slate-600 dark:text-slate-300 leading-relaxed">
                      {proj.description}
                    </p>

                    {proj.technologies && proj.technologies.length > 0 && (
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
                    )}

                    {proj.bullet_points && proj.bullet_points.length > 0 && (
                      <ul className="list-disc list-inside space-y-1 text-xs text-slate-500 pt-2">
                        {proj.bullet_points.map((bp, i) => (
                          <li key={i}>{bp}</li>
                        ))}
                      </ul>
                    )}
                  </div>

                  <div className="flex items-center gap-4 pt-3 border-t border-slate-100 dark:border-slate-800 text-xs">
                    {proj.github_url && (
                      <a
                        href={proj.github_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center gap-1 font-semibold text-slate-700 dark:text-slate-300 hover:text-brand-600"
                      >
                        <Github className="w-3.5 h-3.5" /> Source Code
                      </a>
                    )}
                    {proj.live_url && (
                      <a
                        href={proj.live_url}
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
          )}
        </div>
      )}

      {/* =================================================================== */}
      {/* Tab 4: Education & Certifications                                  */}
      {/* =================================================================== */}
      {activeTab === 'education' && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Education Column */}
          <Card className="p-6 space-y-4">
            <div className="flex items-center justify-between pb-2 border-b border-slate-100 dark:border-slate-800">
              <div className="flex items-center gap-2 font-bold text-slate-900 dark:text-white">
                <GraduationCap className="w-5 h-5 text-purple-600" />
                <h3>Academic Education ({profile.education.length})</h3>
              </div>
              <Button size="sm" variant="outline" onClick={openAddEducation}>
                <Plus className="w-3.5 h-3.5 mr-1" /> Add
              </Button>
            </div>

            {profile.education.length === 0 ? (
              <EmptyState
                icon={<GraduationCap className="w-8 h-8 text-slate-400" />}
                title="No education credentials"
                description="Add your university, degree, and GPA information."
                actionLabel="Add Credential"
                onAction={openAddEducation}
              />
            ) : (
              <div className="space-y-4">
                {profile.education.map((edu) => (
                  <div
                    key={edu.id}
                    className="p-3.5 rounded-xl bg-slate-50 dark:bg-slate-800/40 border border-slate-200/80 dark:border-slate-800 space-y-1.5 text-xs"
                  >
                    <div className="flex items-start justify-between">
                      <div className="text-sm font-bold text-slate-900 dark:text-white">
                        {edu.institution_name}
                      </div>
                      <div className="flex items-center gap-1">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => openEditEducation(edu)}
                          aria-label="Edit education"
                        >
                          <Edit3 className="w-3.5 h-3.5" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() =>
                            setDeleteModal({
                              isOpen: true,
                              type: 'education',
                              id: edu.id,
                              title: `${edu.degree} at ${edu.institution_name}`,
                            })
                          }
                          className="text-rose-600 hover:text-rose-700 hover:bg-rose-50 dark:hover:bg-rose-950/30"
                          aria-label="Delete education"
                        >
                          <Trash2 className="w-3.5 h-3.5" />
                        </Button>
                      </div>
                    </div>
                    <div className="text-purple-700 dark:text-purple-300 font-medium">
                      {edu.degree} &bull; {edu.field_of_study}
                    </div>
                    <div className="text-slate-400 flex items-center justify-between">
                      <span>
                        {edu.start_date} – {edu.is_current ? 'Present' : edu.end_date || 'N/A'}
                      </span>
                      {edu.gpa !== null && edu.gpa !== undefined && (
                        <span className="font-mono font-semibold text-slate-600 dark:text-slate-300">
                          GPA: {edu.gpa.toFixed(2)}
                        </span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </Card>

          {/* Certifications Column */}
          <Card className="p-6 space-y-4">
            <div className="flex items-center justify-between pb-2 border-b border-slate-100 dark:border-slate-800">
              <div className="flex items-center gap-2 font-bold text-slate-900 dark:text-white">
                <Award className="w-5 h-5 text-amber-600" />
                <h3>Verified Certifications ({profile.certifications.length})</h3>
              </div>
              <Button size="sm" variant="outline" onClick={openAddCert}>
                <Plus className="w-3.5 h-3.5 mr-1" /> Add
              </Button>
            </div>

            {profile.certifications.length === 0 ? (
              <EmptyState
                icon={<Award className="w-8 h-8 text-slate-400" />}
                title="No certifications added"
                description="Add cloud credentials or industry certificates (AWS, GCP, CKA)."
                actionLabel="Add Certification"
                onAction={openAddCert}
              />
            ) : (
              <div className="space-y-4">
                {profile.certifications.map((cert) => (
                  <div
                    key={cert.id}
                    className="p-3.5 rounded-xl bg-slate-50 dark:bg-slate-800/40 border border-slate-200/80 dark:border-slate-800 space-y-1.5 text-xs"
                  >
                    <div className="flex items-start justify-between">
                      <div className="text-sm font-bold text-slate-900 dark:text-white">
                        {cert.name}
                      </div>
                      <div className="flex items-center gap-1">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => openEditCert(cert)}
                          aria-label="Edit cert"
                        >
                          <Edit3 className="w-3.5 h-3.5" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() =>
                            setDeleteModal({
                              isOpen: true,
                              type: 'cert',
                              id: cert.id,
                              title: cert.name,
                            })
                          }
                          className="text-rose-600 hover:text-rose-700 hover:bg-rose-50 dark:hover:bg-rose-950/30"
                          aria-label="Delete cert"
                        >
                          <Trash2 className="w-3.5 h-3.5" />
                        </Button>
                      </div>
                    </div>
                    <div className="text-amber-700 dark:text-amber-400 font-medium">
                      {cert.issuing_organization} &bull; Issued {cert.issue_date}
                    </div>
                    <div className="text-slate-400 flex flex-wrap items-center justify-between gap-2">
                      {cert.credential_id && (
                        <span className="font-mono">ID: {cert.credential_id}</span>
                      )}
                      {cert.credential_url && (
                        <a
                          href={cert.credential_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-brand-600 hover:underline flex items-center gap-1"
                        >
                          <ExternalLink className="w-3 h-3" /> Verify
                        </a>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </Card>
        </div>
      )}

      {/* =================================================================== */}
      {/* MODALS                                                              */}
      {/* =================================================================== */}

      {/* 1. Personal Details Modal */}
      <Modal
        isOpen={isPersonalModalOpen}
        onClose={() => setIsPersonalModalOpen(false)}
        title="Edit Personal Information"
        description="Update your contact details, professional headline, and links."
      >
        <form onSubmit={handleSavePersonal} className="space-y-4">
          <Input
            label="Full Name"
            value={personalForm.full_name || ''}
            onChange={(e) => setPersonalForm({ ...personalForm, full_name: e.target.value })}
            required
          />
          <Input
            label="Headline"
            placeholder="e.g. CS Senior | Aspiring Backend Developer"
            value={personalForm.headline || ''}
            onChange={(e) => setPersonalForm({ ...personalForm, headline: e.target.value })}
          />
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <Input
              label="Location"
              placeholder="e.g. San Francisco, CA"
              value={personalForm.location || ''}
              onChange={(e) => setPersonalForm({ ...personalForm, location: e.target.value })}
            />
            <Input
              label="Phone Number"
              placeholder="e.g. +1 (555) 123-4567"
              value={personalForm.phone_number || ''}
              onChange={(e) => setPersonalForm({ ...personalForm, phone_number: e.target.value })}
            />
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <Input
              label="LinkedIn URL"
              placeholder="https://linkedin.com/in/username"
              value={personalForm.linkedin_url || ''}
              onChange={(e) => setPersonalForm({ ...personalForm, linkedin_url: e.target.value })}
            />
            <Input
              label="GitHub URL"
              placeholder="https://github.com/username"
              value={personalForm.github_url || ''}
              onChange={(e) => setPersonalForm({ ...personalForm, github_url: e.target.value })}
            />
          </div>
          <Input
            label="Portfolio Website"
            placeholder="https://yourportfolio.dev"
            value={personalForm.portfolio_url || ''}
            onChange={(e) => setPersonalForm({ ...personalForm, portfolio_url: e.target.value })}
          />
          <Textarea
            label="Professional Bio"
            placeholder="Brief narrative of your software experience and career passions..."
            value={personalForm.bio || ''}
            onChange={(e) => setPersonalForm({ ...personalForm, bio: e.target.value })}
            rows={4}
          />
          <div className="pt-2 flex justify-end gap-2">
            <Button
              type="button"
              variant="outline"
              size="sm"
              onClick={() => setIsPersonalModalOpen(false)}
            >
              Cancel
            </Button>
            <Button type="submit" variant="primary" size="sm" disabled={actionLoading}>
              {actionLoading ? <Loader2 className="w-4 h-4 animate-spin mr-1" /> : null}
              Save Changes
            </Button>
          </div>
        </form>
      </Modal>

      {/* 2. Career Goals Modal */}
      <Modal
        isOpen={isGoalsModalOpen}
        onClose={() => setIsGoalsModalOpen(false)}
        title="Calibrate Career Goals & Target Benchmark"
        description="Choose your target benchmark role and workplace preferences to tailor your learning roadmap."
      >
        <form onSubmit={handleSaveGoals} className="space-y-4">
          <div className="space-y-1.5">
            <label className="block text-xs font-semibold uppercase tracking-wider text-slate-700 dark:text-slate-300">
              Primary Target Role
            </label>
            <select
              className="flex h-10 w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 focus:border-brand-500 focus:outline-none dark:border-slate-700 dark:bg-slate-900 dark:text-slate-100"
              value={goalsForm.primary_role_id}
              onChange={(e) => setGoalsForm({ ...goalsForm, primary_role_id: e.target.value })}
              required
            >
              {supportedRoles.map((role) => (
                <option key={role.id} value={role.id}>
                  {role.title}
                </option>
              ))}
            </select>
          </div>

          <div className="space-y-1.5">
            <label className="block text-xs font-semibold uppercase tracking-wider text-slate-700 dark:text-slate-300">
              Secondary Target Role (Optional)
            </label>
            <select
              className="flex h-10 w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 focus:border-brand-500 focus:outline-none dark:border-slate-700 dark:bg-slate-900 dark:text-slate-100"
              value={goalsForm.secondary_role_id || ''}
              onChange={(e) => setGoalsForm({ ...goalsForm, secondary_role_id: e.target.value })}
            >
              <option value="">None (Focus exclusively on primary)</option>
              {supportedRoles
                .filter((r) => r.id !== goalsForm.primary_role_id)
                .map((role) => (
                  <option key={role.id} value={role.id}>
                    {role.title}
                  </option>
                ))}
            </select>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div className="space-y-1.5">
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-700 dark:text-slate-300">
                Career Stage
              </label>
              <select
                className="flex h-10 w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 focus:border-brand-500 focus:outline-none dark:border-slate-700 dark:bg-slate-900 dark:text-slate-100"
                value={goalsForm.career_stage}
                onChange={(e) => setGoalsForm({ ...goalsForm, career_stage: e.target.value })}
              >
                <option value="student">Student</option>
                <option value="recent_graduate">Recent Graduate</option>
                <option value="early_career">Early Career (&lt;3 YOE)</option>
              </select>
            </div>

            <div className="space-y-1.5">
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-700 dark:text-slate-300">
                Work Preference
              </label>
              <select
                className="flex h-10 w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 focus:border-brand-500 focus:outline-none dark:border-slate-700 dark:bg-slate-900 dark:text-slate-100"
                value={goalsForm.work_preference}
                onChange={(e) => setGoalsForm({ ...goalsForm, work_preference: e.target.value })}
              >
                <option value="remote">Remote</option>
                <option value="hybrid">Hybrid</option>
                <option value="onsite">On-site</option>
                <option value="flexible">Flexible</option>
              </select>
            </div>
          </div>

          <Input
            label="Years of Experience"
            type="number"
            step="0.5"
            min="0"
            max="50"
            value={goalsForm.years_of_experience}
            onChange={(e) =>
              setGoalsForm({
                ...goalsForm,
                years_of_experience: parseFloat(e.target.value) || 0,
              })
            }
          />

          <Input
            label="Target Locations (Comma separated)"
            placeholder="e.g. San Francisco, CA, Remote, New York, NY"
            value={goalsForm.target_locations.join(', ')}
            onChange={(e) =>
              setGoalsForm({
                ...goalsForm,
                target_locations: e.target.value
                  .split(',')
                  .map((l) => l.trim())
                  .filter(Boolean),
              })
            }
          />

          <div className="pt-2 flex justify-end gap-2">
            <Button
              type="button"
              variant="outline"
              size="sm"
              onClick={() => setIsGoalsModalOpen(false)}
            >
              Cancel
            </Button>
            <Button type="submit" variant="primary" size="sm" disabled={actionLoading}>
              {actionLoading ? <Loader2 className="w-4 h-4 animate-spin mr-1" /> : null}
              Save Goals
            </Button>
          </div>
        </form>
      </Modal>

      {/* 3. Work Experience Modal */}
      <Modal
        isOpen={experienceModal.isOpen}
        onClose={() => setExperienceModal({ isOpen: false, mode: 'add' })}
        title={experienceModal.mode === 'add' ? 'Add Work Position' : 'Edit Work Position'}
        description="Detail your employment record, internships, and key software deliverables."
      >
        <form onSubmit={handleSaveExperience} className="space-y-4">
          <Input
            label="Company Name"
            placeholder="e.g. Acme Cloud Corp"
            value={expForm.company_name}
            onChange={(e) => setExpForm({ ...expForm, company_name: e.target.value })}
            required
          />
          <Input
            label="Role Title"
            placeholder="e.g. Software Engineering Intern"
            value={expForm.role_title}
            onChange={(e) => setExpForm({ ...expForm, role_title: e.target.value })}
            required
          />
          <Input
            label="Location"
            placeholder="e.g. San Francisco, CA (or Remote)"
            value={expForm.location}
            onChange={(e) => setExpForm({ ...expForm, location: e.target.value })}
          />
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <Input
              label="Start Date"
              type="date"
              value={expForm.start_date}
              onChange={(e) => setExpForm({ ...expForm, start_date: e.target.value })}
              required
            />
            {!expForm.is_current && (
              <Input
                label="End Date"
                type="date"
                value={expForm.end_date}
                onChange={(e) => setExpForm({ ...expForm, end_date: e.target.value })}
              />
            )}
          </div>
          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              id="exp_is_current"
              checked={expForm.is_current}
              onChange={(e) => setExpForm({ ...expForm, is_current: e.target.checked })}
              className="rounded border-slate-300 text-brand-600 focus:ring-brand-500"
            />
            <label htmlFor="exp_is_current" className="text-xs font-medium text-slate-700 dark:text-slate-300">
              I currently work here
            </label>
          </div>
          <Textarea
            label="Key Impact & Responsibilities (1 bullet per line)"
            placeholder="Architected RESTful microservices reducing p99 latency by 20%&#10;Integrated PostgreSQL database connection pooling"
            value={expForm.bulletsText}
            onChange={(e) => setExpForm({ ...expForm, bulletsText: e.target.value })}
            rows={4}
          />
          <div className="pt-2 flex justify-end gap-2">
            <Button
              type="button"
              variant="outline"
              size="sm"
              onClick={() => setExperienceModal({ isOpen: false, mode: 'add' })}
            >
              Cancel
            </Button>
            <Button type="submit" variant="primary" size="sm" disabled={actionLoading}>
              {actionLoading ? <Loader2 className="w-4 h-4 animate-spin mr-1" /> : null}
              {experienceModal.mode === 'add' ? 'Add Position' : 'Save Position'}
            </Button>
          </div>
        </form>
      </Modal>

      {/* 4. Projects Modal */}
      <Modal
        isOpen={projectModal.isOpen}
        onClose={() => setProjectModal({ isOpen: false, mode: 'add' })}
        title={projectModal.mode === 'add' ? 'Add Technical Project' : 'Edit Technical Project'}
        description="Add repository artifacts and software projects that serve as verifiable proof."
      >
        <form onSubmit={handleSaveProject} className="space-y-4">
          <Input
            label="Project Title"
            placeholder="e.g. Distributed In-Memory Cache"
            value={projForm.title}
            onChange={(e) => setProjForm({ ...projForm, title: e.target.value })}
            required
          />
          <Textarea
            label="Description"
            placeholder="High-performance LRU cache implementation built in Go with concurrent read/write locks..."
            value={projForm.description}
            onChange={(e) => setProjForm({ ...projForm, description: e.target.value })}
            rows={3}
            required
          />
          <Input
            label="Technologies (Comma separated)"
            placeholder="e.g. Go, Redis, Docker, gRPC"
            value={projForm.technologiesText}
            onChange={(e) => setProjForm({ ...projForm, technologiesText: e.target.value })}
          />
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <Input
              label="GitHub Repository URL"
              placeholder="https://github.com/user/project"
              value={projForm.github_url}
              onChange={(e) => setProjForm({ ...projForm, github_url: e.target.value })}
            />
            <Input
              label="Live Demo URL"
              placeholder="https://myproject.demo.app"
              value={projForm.live_url}
              onChange={(e) => setProjForm({ ...projForm, live_url: e.target.value })}
            />
          </div>
          <Textarea
            label="Key Technical Accomplishments (1 bullet per line)"
            placeholder="Engineered custom shard hashing algorithm for partition tolerance&#10;Benchmarked 45,000 requests/sec under synthetic load"
            value={projForm.bulletsText}
            onChange={(e) => setProjForm({ ...projForm, bulletsText: e.target.value })}
            rows={3}
          />
          <div className="pt-2 flex justify-end gap-2">
            <Button
              type="button"
              variant="outline"
              size="sm"
              onClick={() => setProjectModal({ isOpen: false, mode: 'add' })}
            >
              Cancel
            </Button>
            <Button type="submit" variant="primary" size="sm" disabled={actionLoading}>
              {actionLoading ? <Loader2 className="w-4 h-4 animate-spin mr-1" /> : null}
              {projectModal.mode === 'add' ? 'Add Project' : 'Save Project'}
            </Button>
          </div>
        </form>
      </Modal>

      {/* 5. Education Modal */}
      <Modal
        isOpen={educationModal.isOpen}
        onClose={() => setEducationModal({ isOpen: false, mode: 'add' })}
        title={educationModal.mode === 'add' ? 'Add Academic Credential' : 'Edit Academic Credential'}
        description="Add university degrees, colleges, or bootcamps."
      >
        <form onSubmit={handleSaveEducation} className="space-y-4">
          <Input
            label="Institution Name"
            placeholder="e.g. San Jose State University"
            value={eduForm.institution_name}
            onChange={(e) => setEduForm({ ...eduForm, institution_name: e.target.value })}
            required
          />
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <Input
              label="Degree"
              placeholder="e.g. B.S., M.S., Minor"
              value={eduForm.degree}
              onChange={(e) => setEduForm({ ...eduForm, degree: e.target.value })}
              required
            />
            <Input
              label="Field of Study"
              placeholder="e.g. Computer Science"
              value={eduForm.field_of_study}
              onChange={(e) => setEduForm({ ...eduForm, field_of_study: e.target.value })}
              required
            />
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <Input
              label="Start Date"
              type="date"
              value={eduForm.start_date}
              onChange={(e) => setEduForm({ ...eduForm, start_date: e.target.value })}
              required
            />
            {!eduForm.is_current && (
              <Input
                label="End Date"
                type="date"
                value={eduForm.end_date}
                onChange={(e) => setEduForm({ ...eduForm, end_date: e.target.value })}
              />
            )}
          </div>
          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              id="edu_is_current"
              checked={eduForm.is_current}
              onChange={(e) => setEduForm({ ...eduForm, is_current: e.target.checked })}
              className="rounded border-slate-300 text-brand-600 focus:ring-brand-500"
            />
            <label htmlFor="edu_is_current" className="text-xs font-medium text-slate-700 dark:text-slate-300">
              Currently enrolled
            </label>
          </div>
          <Input
            label="GPA (Optional, 0.0 – 4.0)"
            type="number"
            step="0.01"
            min="0"
            max="4.0"
            placeholder="e.g. 3.85"
            value={eduForm.gpa}
            onChange={(e) => setEduForm({ ...eduForm, gpa: e.target.value })}
          />
          <div className="pt-2 flex justify-end gap-2">
            <Button
              type="button"
              variant="outline"
              size="sm"
              onClick={() => setEducationModal({ isOpen: false, mode: 'add' })}
            >
              Cancel
            </Button>
            <Button type="submit" variant="primary" size="sm" disabled={actionLoading}>
              {actionLoading ? <Loader2 className="w-4 h-4 animate-spin mr-1" /> : null}
              {educationModal.mode === 'add' ? 'Add Credential' : 'Save Credential'}
            </Button>
          </div>
        </form>
      </Modal>

      {/* 6. Certification Modal */}
      <Modal
        isOpen={certModal.isOpen}
        onClose={() => setCertModal({ isOpen: false, mode: 'add' })}
        title={certModal.mode === 'add' ? 'Add Certification' : 'Edit Certification'}
        description="Add verified professional credentials and certificates."
      >
        <form onSubmit={handleSaveCert} className="space-y-4">
          <Input
            label="Certification Name"
            placeholder="e.g. AWS Certified Solutions Architect – Associate"
            value={certForm.name}
            onChange={(e) => setCertForm({ ...certForm, name: e.target.value })}
            required
          />
          <Input
            label="Issuing Organization"
            placeholder="e.g. Amazon Web Services, Linux Foundation"
            value={certForm.issuing_organization}
            onChange={(e) => setCertForm({ ...certForm, issuing_organization: e.target.value })}
            required
          />
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <Input
              label="Issue Date"
              type="date"
              value={certForm.issue_date}
              onChange={(e) => setCertForm({ ...certForm, issue_date: e.target.value })}
              required
            />
            <Input
              label="Expiration Date (Optional)"
              type="date"
              value={certForm.expiration_date}
              onChange={(e) => setCertForm({ ...certForm, expiration_date: e.target.value })}
            />
          </div>
          <Input
            label="Credential ID (Optional)"
            placeholder="e.g. AWS-SAA-998822"
            value={certForm.credential_id}
            onChange={(e) => setCertForm({ ...certForm, credential_id: e.target.value })}
          />
          <Input
            label="Credential Verification URL (Optional)"
            placeholder="https://aws.amazon.com/verify/..."
            value={certForm.credential_url}
            onChange={(e) => setCertForm({ ...certForm, credential_url: e.target.value })}
          />
          <div className="pt-2 flex justify-end gap-2">
            <Button
              type="button"
              variant="outline"
              size="sm"
              onClick={() => setCertModal({ isOpen: false, mode: 'add' })}
            >
              Cancel
            </Button>
            <Button type="submit" variant="primary" size="sm" disabled={actionLoading}>
              {actionLoading ? <Loader2 className="w-4 h-4 animate-spin mr-1" /> : null}
              {certModal.mode === 'add' ? 'Add Certification' : 'Save Certification'}
            </Button>
          </div>
        </form>
      </Modal>

      {/* 7. Delete Confirmation Modal */}
      <Modal
        isOpen={deleteModal.isOpen}
        onClose={() => setDeleteModal({ isOpen: false, type: 'experience', id: '', title: '' })}
        title="Confirm Deletion"
        description="Are you sure you want to remove this record from your career profile? This will update your completeness score."
      >
        <div className="space-y-4">
          <p className="text-sm font-semibold text-slate-800 dark:text-slate-200">
            Deleting: <span className="text-rose-600">{deleteModal.title}</span>
          </p>
          <div className="flex justify-end gap-2 pt-2">
            <Button
              type="button"
              variant="outline"
              size="sm"
              onClick={() =>
                setDeleteModal({ isOpen: false, type: 'experience', id: '', title: '' })
              }
            >
              Cancel
            </Button>
            <Button
              type="button"
              variant="destructive"
              size="sm"
              disabled={actionLoading}
              onClick={confirmDelete}
            >
              {actionLoading ? <Loader2 className="w-4 h-4 animate-spin mr-1" /> : null}
              Confirm Delete
            </Button>
          </div>
        </div>
      </Modal>

      {/* 8. Re-parse Resume Modal Placeholder (Phase 5 Gateway) */}
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
            PDF, DOCX, or Markdown up to 10MB. Scheduled for full AI ingestion pipeline in Phase 5.
          </p>
          <Button size="sm" variant="outline" onClick={() => setIsResumeModalOpen(false)}>
            Close
          </Button>
        </div>
      </Modal>
    </div>
  );
}
