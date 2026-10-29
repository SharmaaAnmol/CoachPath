/**
 * CoachPath Resume Ingestion and Parsing API Client.
 * Connects frontend UI components to Phase 5A and Phase 5B resume endpoints.
 * Interacts with /api/v1/resume strictly adhering to backend Pydantic contracts.
 */

import { apiClient } from './api-client';
import {
  ParsedResumeResponse,
  ResumeConfirmationPayload,
  ResumeConfirmationResponse,
  ResumeDetailResponse,
  ResumeListResponse,
  ResumeTailorRequest,
  ResumeUploadResponse,
  RetryParsingResponse,
  TailoredResumeAnalysisResponse,
  TailoredResumeApprovalRequest,
  TailoredResumeDiffResponse,
  TailoredResumeListResponse,
  TailoredResumeResponse,
  TailoredResumeUpdateRequest,
} from '@/types';

export class ResumeClient {
  /**
   * Uploads a candidate resume document (PDF or DOCX, max 10MB) via multipart/form-data.
   * Method: POST /api/v1/resume/upload
   */
  public async uploadResume(file: File): Promise<ResumeUploadResponse> {
    const formData = new FormData();
    formData.append('file', file);
    return apiClient.postMultipart<ResumeUploadResponse>('/resume/upload', formData);
  }

  /**
   * Lists all uploaded resume documents for the authenticated user.
   * Method: GET /api/v1/resume
   */
  public async listResumes(): Promise<ResumeListResponse> {
    return apiClient.get<ResumeListResponse>('/resume');
  }

  /**
   * Retrieves processing status, error category, and metadata for a specific resume.
   * Method: GET /api/v1/resume/{id}
   */
  public async getResume(resumeId: string): Promise<ResumeDetailResponse> {
    return apiClient.get<ResumeDetailResponse>(`/resume/${resumeId}`);
  }

  /**
   * Retrieves the structured parsed draft with normalized canonical skills.
   * Method: GET /api/v1/resume/{id}/parsed
   */
  public async getParsedResume(resumeId: string): Promise<ParsedResumeResponse> {
    return apiClient.get<ParsedResumeResponse>(`/resume/${resumeId}/parsed`);
  }

  /**
   * Re-attempts text extraction and AI parsing for an existing uploaded resume.
   * Useful when AI provider was temporarily unavailable.
   * Method: POST /api/v1/resume/{id}/retry
   */
  public async retryParsing(resumeId: string): Promise<RetryParsingResponse> {
    return apiClient.post<RetryParsingResponse>(`/resume/${resumeId}/retry`, {});
  }

  /**
   * Triggers a secure streaming download of the original uploaded document.
   * Method: GET /api/v1/resume/{id}/download
   */
  public async downloadResume(resumeId: string, defaultFilename?: string): Promise<void> {
    const { blob, filename } = await apiClient.downloadBlob(`/resume/${resumeId}/download`);
    const downloadUrl = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = downloadUrl;
    link.download = filename || defaultFilename || `resume-${resumeId}.pdf`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(downloadUrl);
  }

  /**
   * Permanently deletes a resume record, draft, and physical file from server storage.
   * Method: DELETE /api/v1/resume/{id}
   */
  public async deleteResume(resumeId: string): Promise<void> {
    return apiClient.delete<void>(`/resume/${resumeId}`);
  }

  /**
   * Explicit Human Approval Gate:
   * Merges user-reviewed & corrected resume entities into canonical CareerProfile in PostgreSQL.
   * Method: POST /api/v1/resume/{id}/confirm
   */
  public async confirmResume(
    resumeId: string,
    payload: ResumeConfirmationPayload
  ): Promise<ResumeConfirmationResponse> {
    return apiClient.post<ResumeConfirmationResponse>(`/resume/${resumeId}/confirm`, payload);
  }

  // ─── Phase 10A/10B: Resume Tailoring & Optimization Endpoints ───────

  /**
   * Generates an evidence-grounded tailored resume draft aligned with the target job posting.
   * Method: POST /api/v1/resume/{resume_id}/tailor
   */
  public async tailorResume(
    resumeId: string,
    request: ResumeTailorRequest
  ): Promise<TailoredResumeResponse> {
    return apiClient.post<TailoredResumeResponse>(`/resume/${resumeId}/tailor`, request);
  }

  /**
   * Returns all tailored resume versions belonging to the authenticated candidate.
   * Method: GET /api/v1/resume/versions
   */
  public async listTailoredVersions(params?: {
    resume_id?: string;
    job_id?: string;
    status?: string;
    page?: number;
    page_size?: number;
  }): Promise<TailoredResumeListResponse> {
    return apiClient.get<TailoredResumeListResponse>('/resume/versions', { params });
  }

  /**
   * Retrieves a specific tailored resume draft or approved version by UUID.
   * Method: GET /api/v1/resume/versions/{version_id}
   */
  public async getTailoredVersion(versionId: string): Promise<TailoredResumeResponse> {
    return apiClient.get<TailoredResumeResponse>(`/resume/versions/${versionId}`);
  }

  /**
   * Updates user-modified content or notes on a tailored version (draft status only).
   * Method: PUT /api/v1/resume/versions/{version_id}
   */
  public async updateTailoredVersion(
    versionId: string,
    request: TailoredResumeUpdateRequest
  ): Promise<TailoredResumeResponse> {
    return apiClient.put<TailoredResumeResponse>(`/resume/versions/${versionId}`, request);
  }

  /**
   * Explicit human approval gate: certifies the tailored draft as candidate-approved.
   * Method: POST /api/v1/resume/versions/{version_id}/approve
   */
  public async approveTailoredVersion(
    versionId: string,
    request: TailoredResumeApprovalRequest
  ): Promise<TailoredResumeResponse> {
    return apiClient.post<TailoredResumeResponse>(`/resume/versions/${versionId}/approve`, request);
  }

  /**
   * Retrieves structured before-and-after change list for visual review.
   * Method: GET /api/v1/resume/versions/{version_id}/diff
   */
  public async getTailoredDiff(versionId: string): Promise<TailoredResumeDiffResponse> {
    return apiClient.get<TailoredResumeDiffResponse>(`/resume/versions/${versionId}/diff`);
  }

  /**
   * Retrieves quantitative optimization analysis, keyword coverage, and evidence gaps.
   * Method: GET /api/v1/resume/versions/{version_id}/analysis
   */
  public async getTailoredAnalysis(versionId: string): Promise<TailoredResumeAnalysisResponse> {
    return apiClient.get<TailoredResumeAnalysisResponse>(`/resume/versions/${versionId}/analysis`);
  }

  /**
   * Permanently deletes a tailored resume version under strict ownership check.
   * Method: DELETE /api/v1/resume/versions/{version_id}
   */
  public async deleteTailoredVersion(versionId: string): Promise<void> {
    return apiClient.delete<void>(`/resume/versions/${versionId}`);
  }
}

export const resumeClient = new ResumeClient();
