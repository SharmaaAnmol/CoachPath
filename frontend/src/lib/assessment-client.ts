/**
 * CoachPath Diagnostic Skill Assessments API Client.
 * Connects frontend UI to the server-side deterministic assessment engine.
 */

import { apiClient } from './api-client';
import {
  AssessmentCategoryItem,
  AssessmentResultResponse,
  AttemptHistoryItem,
  AttemptSession,
} from '@/types';

export class AssessmentClient {
  /**
   * Lists all 9 assessment categories with user attempt status and best scores.
   * Method: GET /api/v1/assessments
   */
  public async listAssessments(): Promise<AssessmentCategoryItem[]> {
    return apiClient.get<AssessmentCategoryItem[]>('/assessments');
  }

  /**
   * Retrieves syllabus details and question breakdown for a category.
   * Method: GET /api/v1/assessments/{category_id}
   */
  public async getAssessmentDetail(categoryId: string): Promise<any> {
    return apiClient.get<any>(`/assessments/${categoryId}`);
  }

  /**
   * Starts a new 20-question diagnostic attempt or resumes an in-progress attempt.
   * Method: POST /api/v1/assessments/{category_id}/start
   */
  public async startOrResumeAttempt(categoryId: string): Promise<AttemptSession> {
    return apiClient.post<AttemptSession>(`/assessments/${categoryId}/start`, {});
  }

  /**
   * Retrieves an in-progress attempt session with questions and recorded answers.
   * Method: GET /api/v1/assessments/attempts/{attempt_id}
   */
  public async getActiveAttempt(attemptId: string): Promise<AttemptSession> {
    return apiClient.get<AttemptSession>(`/assessments/attempts/${attemptId}`);
  }

  /**
   * Records or updates a chosen answer option for a specific question.
   * Method: POST /api/v1/assessments/attempts/{attempt_id}/answer
   */
  public async submitAnswer(
    attemptId: string,
    questionId: string,
    selectedOptionIndex: number,
    responseTimeSeconds: number = 0,
  ): Promise<{ attempt_id: string; question_id: string; selected_option_index: number; answered_count: number; total_questions: number }> {
    return apiClient.post(`/assessments/attempts/${attemptId}/answer`, {
      question_id: questionId,
      selected_option_index: selectedOptionIndex,
      response_time_seconds: responseTimeSeconds,
    });
  }

  /**
   * Finalizes the attempt, runs server-side grading, and returns complete scored results.
   * Method: POST /api/v1/assessments/attempts/{attempt_id}/complete
   */
  public async completeAttempt(attemptId: string): Promise<AssessmentResultResponse> {
    return apiClient.post<AssessmentResultResponse>(`/assessments/attempts/${attemptId}/complete`, {});
  }

  /**
   * Retrieves the finalized result and review with explanations for a completed attempt.
   * Method: GET /api/v1/assessments/attempts/{attempt_id}/result
   */
  public async getAttemptResult(attemptId: string): Promise<AssessmentResultResponse> {
    return apiClient.get<AssessmentResultResponse>(`/assessments/attempts/${attemptId}/result`);
  }

  /**
   * Retrieves historical attempts taken by the candidate.
   * Method: GET /api/v1/assessments/history
   */
  public async getHistory(): Promise<AttemptHistoryItem[]> {
    return apiClient.get<AttemptHistoryItem[]>('/assessments/history');
  }
}

export const assessmentClient = new AssessmentClient();
