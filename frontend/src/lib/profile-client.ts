/**
 * CoachPath Profile and Evidence Graph API Client.
 * Communicates with /api/v1/profile to provide persistent career profile management.
 */

import { apiClient } from './api-client';
import {
  CareerGoalsData,
  CareerGoalsUpdatePayload,
  MasterCareerProfile,
  ProfileCertificationEntry,
  ProfileCertificationPayload,
  ProfileEducationEntry,
  ProfileEducationPayload,
  ProfileExperienceEntry,
  ProfileExperiencePayload,
  ProfileProjectEntry,
  ProfileProjectPayload,
  RoleItem,
  UserProfileUpdatePayload,
} from '@/types';

export class ProfileClient {
  /**
   * Retrieves the authenticated candidate's consolidated career profile and evidence graph.
   */
  public async getMasterProfile(): Promise<MasterCareerProfile> {
    return apiClient.get<MasterCareerProfile>('/profile');
  }

  /**
   * Updates candidate personal demographic, headline, contact, and portfolio links.
   */
  public async updatePersonalProfile(
    payload: UserProfileUpdatePayload
  ): Promise<MasterCareerProfile> {
    return apiClient.put<MasterCareerProfile>('/profile', payload);
  }

  /**
   * Retrieves active career targets and workplace preferences.
   */
  public async getCareerGoals(): Promise<CareerGoalsData> {
    return apiClient.get<CareerGoalsData>('/profile/career-goals');
  }

  /**
   * Updates primary/secondary benchmark target roles, stage, and workplace preferences.
   */
  public async updateCareerGoals(
    payload: CareerGoalsUpdatePayload
  ): Promise<CareerGoalsData> {
    return apiClient.put<CareerGoalsData>('/profile/career-goals', payload);
  }

  /**
   * Retrieves supported benchmark roles from the canonical taxonomy.
   */
  public async getSupportedRoles(): Promise<RoleItem[]> {
    return apiClient.get<RoleItem[]>('/profile/roles');
  }

  // ---------------------------------------------------------------------------
  // Education CRUD
  // ---------------------------------------------------------------------------

  public async listEducation(): Promise<ProfileEducationEntry[]> {
    return apiClient.get<ProfileEducationEntry[]>('/profile/education');
  }

  public async createEducation(
    payload: ProfileEducationPayload
  ): Promise<ProfileEducationEntry> {
    return apiClient.post<ProfileEducationEntry>('/profile/education', payload);
  }

  public async updateEducation(
    id: string,
    payload: Partial<ProfileEducationPayload>
  ): Promise<ProfileEducationEntry> {
    return apiClient.put<ProfileEducationEntry>(`/profile/education/${id}`, payload);
  }

  public async deleteEducation(id: string): Promise<void> {
    await apiClient.delete<void>(`/profile/education/${id}`);
  }

  // ---------------------------------------------------------------------------
  // Experience CRUD
  // ---------------------------------------------------------------------------

  public async listExperience(): Promise<ProfileExperienceEntry[]> {
    return apiClient.get<ProfileExperienceEntry[]>('/profile/experience');
  }

  public async createExperience(
    payload: ProfileExperiencePayload
  ): Promise<ProfileExperienceEntry> {
    return apiClient.post<ProfileExperienceEntry>('/profile/experience', payload);
  }

  public async updateExperience(
    id: string,
    payload: Partial<ProfileExperiencePayload>
  ): Promise<ProfileExperienceEntry> {
    return apiClient.put<ProfileExperienceEntry>(`/profile/experience/${id}`, payload);
  }

  public async deleteExperience(id: string): Promise<void> {
    await apiClient.delete<void>(`/profile/experience/${id}`);
  }

  // ---------------------------------------------------------------------------
  // Projects CRUD
  // ---------------------------------------------------------------------------

  public async listProjects(): Promise<ProfileProjectEntry[]> {
    return apiClient.get<ProfileProjectEntry[]>('/profile/projects');
  }

  public async createProject(
    payload: ProfileProjectPayload
  ): Promise<ProfileProjectEntry> {
    return apiClient.post<ProfileProjectEntry>('/profile/projects', payload);
  }

  public async updateProject(
    id: string,
    payload: Partial<ProfileProjectPayload>
  ): Promise<ProfileProjectEntry> {
    return apiClient.put<ProfileProjectEntry>(`/profile/projects/${id}`, payload);
  }

  public async deleteProject(id: string): Promise<void> {
    await apiClient.delete<void>(`/profile/projects/${id}`);
  }

  // ---------------------------------------------------------------------------
  // Certifications CRUD
  // ---------------------------------------------------------------------------

  public async listCertifications(): Promise<ProfileCertificationEntry[]> {
    return apiClient.get<ProfileCertificationEntry[]>('/profile/certifications');
  }

  public async createCertification(
    payload: ProfileCertificationPayload
  ): Promise<ProfileCertificationEntry> {
    return apiClient.post<ProfileCertificationEntry>('/profile/certifications', payload);
  }

  public async updateCertification(
    id: string,
    payload: Partial<ProfileCertificationPayload>
  ): Promise<ProfileCertificationEntry> {
    return apiClient.put<ProfileCertificationEntry>(`/profile/certifications/${id}`, payload);
  }

  public async deleteCertification(id: string): Promise<void> {
    await apiClient.delete<void>(`/profile/certifications/${id}`);
  }
}

export const profileClient = new ProfileClient();
