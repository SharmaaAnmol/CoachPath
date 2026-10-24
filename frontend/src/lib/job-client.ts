/**
 * CoachPath Job Discovery and Market Intelligence API Client.
 * Communicates with Phase 8A backend endpoints (/api/v1/jobs).
 */

import { apiClient } from './api-client';
import {
  JobOpportunity,
  JobSearchQuery,
  JobSearchResponse,
  ManualJobImportPayload,
  MarketIntelligenceData,
} from '@/types';

export class JobClient {
  /**
   * Search and filter curated job opportunities.
   * Method: GET /api/v1/jobs
   */
  public async searchJobs(query: JobSearchQuery = {}): Promise<JobSearchResponse> {
    const params: Record<string, string | number | boolean | undefined> = {};

    if (query.role_id) params.role_id = query.role_id;
    if (query.remote_type) params.remote_type = query.remote_type;
    if (query.employment_type) params.employment_type = query.employment_type;
    if (query.experience_level) params.experience_level = query.experience_level;
    if (query.skill_id) params.skill_id = query.skill_id;
    if (query.keyword) params.keyword = query.keyword;
    if (query.freshness_status) params.freshness_status = query.freshness_status;
    if (query.min_salary !== undefined) params.min_salary = query.min_salary;
    if (query.sort_by) params.sort_by = query.sort_by;
    if (query.page !== undefined) params.page = query.page;
    if (query.page_size !== undefined) params.page_size = query.page_size;

    return apiClient.get<JobSearchResponse>('/jobs', { params });
  }

  /**
   * Retrieve complete details for a specific job posting.
   * Method: GET /api/v1/jobs/{job_id}
   */
  public async getJobById(jobId: string): Promise<JobOpportunity> {
    return apiClient.get<JobOpportunity>(`/jobs/${encodeURIComponent(jobId)}`);
  }

  /**
   * Retrieve aggregated market intelligence indicators.
   * Method: GET /api/v1/jobs/market-intelligence
   */
  public async getMarketIntelligence(roleId?: string): Promise<MarketIntelligenceData> {
    const params = roleId ? { role_id: roleId } : undefined;
    return apiClient.get<MarketIntelligenceData>('/jobs/market-intelligence', { params });
  }

  /**
   * Manually import and process a job posting for the user's catalog.
   * Method: POST /api/v1/jobs/import
   */
  public async importJob(payload: ManualJobImportPayload): Promise<JobOpportunity> {
    return apiClient.post<JobOpportunity>('/jobs/import', payload);
  }
}

export const jobClient = new JobClient();
