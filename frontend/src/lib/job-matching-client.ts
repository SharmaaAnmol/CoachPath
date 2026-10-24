/**
 * CoachPath Intelligent Job Matching API Client.
 * Communicates with Phase 9A backend matching endpoints (/api/v1/jobs/recommendations, /api/v1/jobs/{id}/match, etc.).
 */

import { apiClient } from './api-client';
import {
  JobMatchBatchRefreshResponse,
  JobMatchExplanationDrawerResponse,
  JobMatchResponse,
  JobRecommendationQuery,
  JobRecommendationResponse,
} from '@/types';

export class JobMatchingClient {
  /**
   * Retrieve personalized job recommendations ranked descending by match score.
   * Method: GET /api/v1/jobs/recommendations
   */
  public async getRecommendations(
    query: JobRecommendationQuery = {}
  ): Promise<JobRecommendationResponse> {
    const params: Record<string, string | number | boolean | undefined> = {};

    if (query.min_score !== undefined) params.min_score = query.min_score;
    if (query.role_id) params.role_id = query.role_id;
    if (query.remote_type) params.remote_type = query.remote_type;
    if (query.include_provisional !== undefined) {
      params.include_provisional = query.include_provisional;
    }
    if (query.page !== undefined) params.page = query.page;
    if (query.page_size !== undefined) params.page_size = query.page_size;

    return apiClient.get<JobRecommendationResponse>('/jobs/recommendations', { params });
  }

  /**
   * Retrieve or compute multi-factor match details for a specific job posting.
   * Method: GET /api/v1/jobs/{job_id}/match
   */
  public async getJobMatch(jobId: string): Promise<JobMatchResponse> {
    return apiClient.get<JobMatchResponse>(`/jobs/${encodeURIComponent(jobId)}/match`);
  }

  /**
   * Retrieve explainability drawer payload (conforming to API Spec Section 8.2).
   * Method: GET /api/v1/jobs/{job_id}/match-explanation
   */
  public async getJobMatchExplanation(
    jobId: string
  ): Promise<JobMatchExplanationDrawerResponse> {
    return apiClient.get<JobMatchExplanationDrawerResponse>(
      `/jobs/${encodeURIComponent(jobId)}/match-explanation`
    );
  }

  /**
   * Force recalculation of match score and factors for a specific job.
   * Method: POST /api/v1/jobs/{job_id}/match/recalculate
   */
  public async recalculateJobMatch(
    jobId: string,
    force: boolean = true
  ): Promise<JobMatchResponse> {
    return apiClient.post<JobMatchResponse>(
      `/jobs/${encodeURIComponent(jobId)}/match/recalculate`,
      { force }
    );
  }

  /**
   * Batch refresh / recalculate all recommendations across active listings.
   * Method: POST /api/v1/jobs/matches/refresh
   */
  public async refreshRecommendations(): Promise<JobMatchBatchRefreshResponse> {
    return apiClient.post<JobMatchBatchRefreshResponse>('/jobs/matches/refresh', {});
  }

  /**
   * List all previously computed matches for current user ordered by score descending.
   * Method: GET /api/v1/jobs/matches
   */
  public async listMatches(): Promise<JobMatchResponse[]> {
    return apiClient.get<JobMatchResponse[]>('/jobs/matches');
  }
}

export const jobMatchingClient = new JobMatchingClient();
