/**
 * Application packages and recruiter outreach (Phase 11A backend).
 * Nothing here sends anything: the user copies or opens links and then confirms by hand.
 */
import { apiClient } from './api-client';

export type PackageStatus = 'draft' | 'approved' | 'handoff_initiated' | 'submitted';
export type OutreachStatus = 'draft' | 'awaiting_approval' | 'approved' | 'handoff_initiated' | 'sent' | 'cancelled';

export interface ApplicationQuestionAnswer {
  id?: string | null;
  question: string;
  answer: string;
  supporting_evidence?: string | null;
  evidence_citations?: string[];
  needs_clarification?: boolean;
  requires_clarification?: boolean;
  clarification_prompt?: string | null;
}

export interface ApplicationPackage {
  id: string;
  job_id: string;
  job_title?: string | null;
  company_name?: string | null;
  tailored_resume_version_id: string;
  status: PackageStatus;
  cover_note: string;
  application_questions: ApplicationQuestionAnswer[];
  evidence_references: string[];
  user_notes?: string | null;
  approved_at?: string | null;
  handoff_initiated_at?: string | null;
  application_url?: string | null;
  user_confirmed_submission: boolean;
  submitted_at?: string | null;
  created_at: string;
  updated_at: string;
}

export interface PackageHandoff {
  package_id: string;
  status: PackageStatus;
  application_url?: string | null;
  instructions: string;
}

export interface OutreachDraft {
  id: string;
  job_id: string;
  job_title?: string | null;
  company_name?: string | null;
  application_package_id?: string | null;
  recruiter_name?: string | null;
  recruiter_role_type?: string | null;
  recruiter_profile_url?: string | null;
  recruiter_contact_info?: string | null;
  candidate_notes?: string | null;
  subject_line: string;
  message_body: string;
  word_count: number;
  suggested_role_types: string[];
  status: OutreachStatus;
  approved_at?: string | null;
  sent_at?: string | null;
  user_confirmed_sent: boolean;
  created_at: string;
  updated_at: string;
}

export interface OutreachHandoff {
  status: OutreachStatus;
  handoff_type?: string | null;
  mailto_uri?: string | null;
  mailto_url?: string | null;
  recruiter_profile_url?: string | null;
  profile_url?: string | null;
  clipboard_text?: string | null;
  copy_text?: string | null;
  subject_line?: string | null;
  handoff_instructions?: string | null;
  instructions?: string | null;
}

export interface OutreachCreate {
  job_id?: string;
  application_package_id?: string;
  outreach_channel?: 'recruiter_inmail' | 'email' | 'linkedin_message' | string;
  recruiter_name?: string;
  recruiter_role_type?: string;
  recruiter_profile_url?: string;
  recruiter_contact_info?: string;
  candidate_notes?: string;
}

export const applicationClient = {
  listPackages: () => apiClient.get<{ packages: ApplicationPackage[]; total: number }>('/applications/packages'),
  preparePackage: (body: { job_id: string; tailored_resume_version_id?: string; user_notes?: string }) =>
    apiClient.post<ApplicationPackage>('/applications/prepare', body),
  updatePackage: (id: string, body: { cover_note?: string; application_questions?: ApplicationQuestionAnswer[]; user_notes?: string }) =>
    apiClient.put<ApplicationPackage>(`/applications/packages/${id}`, body),
  approvePackage: (id: string) =>
    apiClient.post<ApplicationPackage>(`/applications/packages/${id}/approve`, { user_confirmation: true }),
  handoffPackage: (id: string) => apiClient.post<PackageHandoff>(`/applications/packages/${id}/handoff`, {}),
  confirmSubmission: (id: string) =>
    apiClient.post<ApplicationPackage>(`/applications/packages/${id}/confirm-submission`, { user_confirmation: true }),
};

export const outreachClient = {
  list: () => apiClient.get<{ drafts: OutreachDraft[]; total: number }>('/recruiters/outreach'),
  create: (body: OutreachCreate) => apiClient.post<OutreachDraft>('/recruiters/outreach', body),
  update: (id: string, body: Partial<Pick<OutreachDraft, 'subject_line' | 'message_body' | 'recruiter_name' | 'recruiter_role_type' | 'recruiter_profile_url' | 'recruiter_contact_info' | 'candidate_notes'>>) =>
    apiClient.put<OutreachDraft>(`/recruiters/outreach/${id}`, body),
  approve: (id: string) => apiClient.post<OutreachDraft>(`/recruiters/outreach/${id}/approve`, { user_confirmation: true }),
  handoff: (id: string) => apiClient.post<OutreachHandoff>(`/recruiters/outreach/${id}/handoff`, {}),
  confirmSent: (id: string) => apiClient.post<OutreachDraft>(`/recruiters/outreach/${id}/confirm-sent`, { user_confirmation: true }),
  cancel: (id: string) => apiClient.post<OutreachDraft>(`/recruiters/outreach/${id}/cancel`, {}),
  remove: (id: string) => apiClient.delete<void>(`/recruiters/outreach/${id}`),
};
