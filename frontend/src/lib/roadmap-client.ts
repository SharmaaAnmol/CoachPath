/**
 * CoachPath Personalized Learning Roadmap API Client.
 * Communicates with Phase 7A backend endpoints (/api/v1/roadmap).
 */

import { apiClient } from './api-client';
import {
  RoadmapAdaptationData,
  RoadmapData,
  RoadmapGenerateRequestPayload,
  RoadmapProgressData,
  RoadmapTaskItem,
  UpdateRoadmapTaskPayload,
} from '@/types';

export class RoadmapClient {
  /**
   * Retrieves the active personalized learning roadmap for the authenticated user.
   * Method: GET /api/v1/roadmap
   */
  public async getActiveRoadmap(roleId?: string): Promise<RoadmapData> {
    const query = roleId ? `?role_id=${encodeURIComponent(roleId)}` : '';
    return apiClient.get<RoadmapData>(`/roadmap${query}`);
  }

  /**
   * Retrieves a specific roadmap by ID.
   * Method: GET /api/v1/roadmap/{id}
   */
  public async getRoadmapById(roadmapId: string): Promise<RoadmapData> {
    return apiClient.get<RoadmapData>(`/roadmap/${roadmapId}`);
  }

  /**
   * Generates or regenerates a personalized learning roadmap.
   * Method: POST /api/v1/roadmap/generate
   */
  public async generateRoadmap(payload?: RoadmapGenerateRequestPayload): Promise<RoadmapData> {
    return apiClient.post<RoadmapData>('/roadmap/generate', payload || {});
  }

  /**
   * Retrieves real-time calculated progress metrics and next recommended tasks.
   * Method: GET /api/v1/roadmap/{id}/progress
   */
  public async getRoadmapProgress(roadmapId: string): Promise<RoadmapProgressData> {
    return apiClient.get<RoadmapProgressData>(`/roadmap/${roadmapId}/progress`);
  }

  /**
   * Updates task status or deliverable proof submission link.
   * Method: PATCH /api/v1/roadmap/tasks/{id}
   */
  public async updateTaskStatus(taskId: string, payload: UpdateRoadmapTaskPayload): Promise<RoadmapTaskItem> {
    return apiClient.patch<RoadmapTaskItem>(`/roadmap/tasks/${taskId}`, payload);
  }

  /**
   * Dynamically adapts the roadmap based on newly passed diagnostic skill assessments.
   * Method: POST /api/v1/roadmap/{id}/adapt
   */
  public async adaptRoadmap(roadmapId: string): Promise<RoadmapAdaptationData> {
    return apiClient.post<RoadmapAdaptationData>(`/roadmap/${roadmapId}/adapt`, {});
  }
}

export const roadmapClient = new RoadmapClient();
