/**
 * CoachPath Authentication API Client.
 * Centralized, reusable abstraction for communication with the FastAPI auth endpoints.
 * Interacts with /api/v1/auth adhering strictly to /docs/api-specification.md Group 1.
 */

import { apiClient } from './api-client';
import {
  AuthUser,
  LoginPayload,
  LoginResponse,
  LogoutResponse,
  RefreshTokenResponse,
  RegisterPayload,
  RegisterResponse,
} from '@/types';

export class AuthClient {
  /**
   * Registers a new candidate account.
   * Method: POST /api/v1/auth/register
   */
  public async register(payload: RegisterPayload): Promise<RegisterResponse> {
    return apiClient.post<RegisterResponse>('/auth/register', payload);
  }

  /**
   * Authenticates candidate credentials and establishes HttpOnly session cookies.
   * Method: POST /api/v1/auth/login
   */
  public async login(payload: LoginPayload): Promise<LoginResponse> {
    return apiClient.post<LoginResponse>('/auth/login', payload);
  }

  /**
   * Invalidates active session on the backend and clears auth cookies.
   * Method: POST /api/v1/auth/logout
   */
  public async logout(): Promise<LogoutResponse> {
    return apiClient.post<LogoutResponse>('/auth/logout', {});
  }

  /**
   * Retrieves the current authenticated user's sanitized identity and profile.
   * Method: GET /api/v1/auth/me
   */
  public async getCurrentUser(): Promise<AuthUser> {
    return apiClient.get<AuthUser>('/auth/me');
  }

  /**
   * Rotates refresh token and issues a new access token.
   * Method: POST /api/v1/auth/refresh
   */
  public async refreshToken(): Promise<RefreshTokenResponse> {
    return apiClient.post<RefreshTokenResponse>('/auth/refresh', {});
  }
}

export const authClient = new AuthClient();
