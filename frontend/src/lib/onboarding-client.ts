/**
 * CoachPath AI Onboarding API Client.
 * Connects frontend UI components to Phase 4A conversational discovery endpoints.
 * Interacts with /api/v1/onboarding strictly adhering to backend Pydantic contracts.
 */

import { apiClient } from './api-client';
import {
  ConfirmSummaryPayload,
  ConversationTurn,
  OnboardingProgressData,
  OnboardingSessionData,
  OnboardingSummaryResponse,
  StartOnboardingResponse,
  SubmitResponseResult,
} from '@/types';

export class OnboardingClient {
  /**
   * Initiates a new onboarding discovery interview or resumes an ongoing session.
   * Method: POST /api/v1/onboarding/start
   */
  public async startOnboarding(): Promise<StartOnboardingResponse> {
    return apiClient.post<StartOnboardingResponse>('/onboarding/start', {});
  }

  /**
   * Retrieves active onboarding session state, turn counts, and current question.
   * Method: GET /api/v1/onboarding/session
   */
  public async getSession(): Promise<OnboardingSessionData> {
    return apiClient.get<OnboardingSessionData>('/onboarding/session');
  }

  /**
   * Reports the proportion of the 15 discovery categories covered versus remaining.
   * Method: GET /api/v1/onboarding/progress
   */
  public async getProgress(): Promise<OnboardingProgressData> {
    return apiClient.get<OnboardingProgressData>('/onboarding/progress');
  }

  /**
   * Submits candidate answer to the current question. The backend AI extracts facts
   * and returns the next interview question or triggers summary readiness.
   * Method: POST /api/v1/onboarding/respond
   */
  public async respond(responseText: string): Promise<SubmitResponseResult> {
    return apiClient.post<SubmitResponseResult>('/onboarding/respond', {
      response_text: responseText,
    });
  }

  /**
   * Retrieves the complete chronological question-and-answer exchange for the session.
   * Method: GET /api/v1/onboarding/history
   */
  public async getHistory(): Promise<ConversationTurn[]> {
    return apiClient.get<ConversationTurn[]>('/onboarding/history');
  }

  /**
   * Retrieves the AI-synthesized career profile summary awaiting candidate confirmation.
   * Only accessible when session is in 'awaiting_confirmation' or 'completed'.
   * Method: GET /api/v1/onboarding/summary
   */
  public async getSummary(): Promise<OnboardingSummaryResponse> {
    return apiClient.get<OnboardingSummaryResponse>('/onboarding/summary');
  }

  /**
   * Confirms the career summary (with optional candidate edits), updates the CareerProfile,
   * and marks the session complete in PostgreSQL.
   * Method: POST /api/v1/onboarding/confirm
   */
  public async confirmSummary(
    payload: ConfirmSummaryPayload
  ): Promise<OnboardingSessionData> {
    return apiClient.post<OnboardingSessionData>('/onboarding/confirm', payload);
  }
}

export const onboardingClient = new OnboardingClient();
