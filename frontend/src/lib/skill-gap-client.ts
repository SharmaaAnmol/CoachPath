/**
 * CoachPath Skill Gap Analysis API Client.
 * Communicates with Phase 6A backend endpoints (/api/v1/roles, /api/v1/skills/gap-analysis).
 */

import { apiClient } from './api-client';
import {
  CanonicalSkillItem,
  RoleRequirementItem,
  SkillEvidenceDetailResponse,
  SkillGapAnalysisData,
  SkillGapHistoryResponse,
  TargetRoleDetail,
  TargetRolesListResponse,
} from '@/types';

export class SkillGapClient {
  /**
   * Lists all supported canonical target roles with their requirement summaries.
   * Method: GET /api/v1/roles
   */
  public async listRoles(): Promise<TargetRolesListResponse> {
    return apiClient.get<TargetRolesListResponse>('/roles');
  }

  /**
   * Retrieves full details and requirement benchmarks for a specific target role.
   * Method: GET /api/v1/roles/{role_id}
   */
  public async getRole(roleId: string): Promise<TargetRoleDetail> {
    return apiClient.get<TargetRoleDetail>(`/roles/${roleId}`);
  }

  /**
   * Retrieves curated requirements for a specific target role.
   * Method: GET /api/v1/roles/{role_id}/requirements
   */
  public async getRoleRequirements(roleId: string): Promise<RoleRequirementItem[]> {
    return apiClient.get<RoleRequirementItem[]>(`/roles/${roleId}/requirements`);
  }

  /**
   * Retrieves the master canonical skills taxonomy.
   * Method: GET /api/v1/skills
   */
  public async listCanonicalSkills(): Promise<CanonicalSkillItem[]> {
    return apiClient.get<CanonicalSkillItem[]>('/skills');
  }

  /**
   * Retrieves the latest active (is_current=True) skill gap analysis for the authenticated candidate.
   * Method: GET /api/v1/skills/gap-analysis
   */
  public async getLatestAnalysis(): Promise<SkillGapAnalysisData> {
    return apiClient.get<SkillGapAnalysisData>('/skills/gap-analysis');
  }

  /**
   * Calculates and commits a new deterministic skill gap analysis snapshot.
   * Method: POST /api/v1/skills/gap-analysis
   */
  public async calculateAnalysis(roleId?: string): Promise<SkillGapAnalysisData> {
    return apiClient.post<SkillGapAnalysisData>('/skills/gap-analysis', {
      role_id: roleId || null,
    });
  }

  /**
   * Forces recalculation of the skill gap analysis incorporating fresh assessment results or profile changes.
   * Method: POST /api/v1/skills/gap-analysis/recalculate
   */
  public async recalculateAnalysis(roleId?: string): Promise<SkillGapAnalysisData> {
    return apiClient.post<SkillGapAnalysisData>('/skills/gap-analysis/recalculate', {
      role_id: roleId || null,
    });
  }

  /**
   * Retrieves the timeline history of all previous gap analysis snapshots.
   * Method: GET /api/v1/skills/gap-analysis/history
   */
  public async getAnalysisHistory(): Promise<SkillGapHistoryResponse> {
    return apiClient.get<SkillGapHistoryResponse>('/skills/gap-analysis/history');
  }

  /**
   * Retrieves granular multi-source evidence supporting a specific canonical skill.
   * Method: GET /api/v1/skills/gap-analysis/{skill_id}/evidence
   */
  public async getSkillEvidence(skillId: string): Promise<SkillEvidenceDetailResponse> {
    return apiClient.get<SkillEvidenceDetailResponse>(`/skills/gap-analysis/${skillId}/evidence`);
  }
}

export const skillGapClient = new SkillGapClient();
