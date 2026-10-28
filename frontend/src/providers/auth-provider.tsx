'use client';

/**
 * CoachPath Authentication Context and Provider.
 * Maintains reliable auth state (loading, authenticated, unauthenticated, error).
 * Avoids credential exposure in localStorage, relying strictly on HttpOnly session cookies.
 */

import * as React from 'react';
import { useRouter } from 'next/navigation';
import { authClient } from '@/lib/auth-client';
import { ApiClientError } from '@/lib/api-client';
import {
  AuthUser,
  LoginPayload,
  RegisterPayload,
  RegisterResponse,
} from '@/types';

export type AuthStatus = 'loading' | 'authenticated' | 'unauthenticated';

export interface AuthContextValue {
  status: AuthStatus;
  user: AuthUser | null;
  error: string | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (credentials: LoginPayload) => Promise<AuthUser>;
  register: (payload: RegisterPayload) => Promise<RegisterResponse>;
  logout: () => Promise<void>;
  refreshUser: () => Promise<void>;
  clearError: () => void;
}

export const AuthContext = React.createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const [status, setStatus] = React.useState<AuthStatus>('loading');
  const [user, setUser] = React.useState<AuthUser | null>(null);
  const [error, setError] = React.useState<string | null>(null);
  const [isLoading, setIsLoading] = React.useState<boolean>(true);

  // Initialize and verify authentication session on application mount
  React.useEffect(() => {
    let isMounted = true;

    async function checkSession() {
      try {
        const currentUser = await authClient.getCurrentUser();
        if (isMounted) {
          setUser(currentUser);
          setStatus('authenticated');
          setError(null);
        }
      } catch (err: unknown) {
        if (isMounted) {
          setUser(null);
          setStatus('unauthenticated');
        }
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    }

    checkSession();

    return () => {
      isMounted = false;
    };
  }, []);

  const login = React.useCallback(async (credentials: LoginPayload): Promise<AuthUser> => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await authClient.login(credentials);
      setUser(response.user);
      setStatus('authenticated');
      setError(null);
      return response.user;
    } catch (err: unknown) {
      setUser(null);
      setStatus('unauthenticated');

      let errorMessage = 'Invalid email or password.';
      if (err instanceof ApiClientError) {
        if (err.status === 401) {
          errorMessage = 'Invalid email or password. Please verify your credentials.';
        } else if (err.status === 429) {
          errorMessage = 'Too many failed login attempts. Account temporarily locked for 15 minutes.';
        } else if (err.status === 403) {
          errorMessage = 'Account has been suspended. Please contact support.';
        } else if (err.code === 'NETWORK_ERROR' || err.status === 0) {
          errorMessage = 'Unable to reach CoachPath server. Please verify your connection.';
        } else {
          errorMessage = err.message || 'An unexpected error occurred during login.';
        }
      }
      setError(errorMessage);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const register = React.useCallback(
    async (payload: RegisterPayload): Promise<RegisterResponse> => {
      setIsLoading(true);
      setError(null);
      try {
        const response = await authClient.register(payload);
        return response;
      } catch (err: unknown) {
        let errorMessage = 'Registration could not be completed.';
        if (err instanceof ApiClientError) {
          if (err.status === 409) {
            errorMessage = 'An account with this email already exists. Please sign in instead.';
          } else if (err.status === 422) {
            errorMessage =
              err.details && err.details.length > 0
                ? err.details.map((d) => d.issue).join(' ')
                : err.message || 'Validation error: please check required fields.';
          } else if (err.code === 'NETWORK_ERROR' || err.status === 0) {
            errorMessage = 'Unable to reach CoachPath server. Please verify your connection.';
          } else {
            errorMessage = err.message || 'Registration failed.';
          }
        }
        setError(errorMessage);
        throw err;
      } finally {
        setIsLoading(false);
      }
    },
    []
  );

  const logout = React.useCallback(async (): Promise<void> => {
    setIsLoading(true);
    try {
      await authClient.logout();
    } catch (err) {
      // Gracefully continue clearing local state even if backend is unreachable
      console.warn('Logout API error:', err);
    } finally {
      setUser(null);
      setStatus('unauthenticated');
      setError(null);
      setIsLoading(false);
      window.location.href = '/login';
    }
  }, []);

  const refreshUser = React.useCallback(async (): Promise<void> => {
    try {
      const refreshed = await authClient.getCurrentUser();
      setUser(refreshed);
      setStatus('authenticated');
    } catch {
      setUser(null);
      setStatus('unauthenticated');
    }
  }, []);

  const clearError = React.useCallback(() => {
    setError(null);
  }, []);

  const value: AuthContextValue = React.useMemo(
    () => ({
      status,
      user,
      error,
      isLoading,
      isAuthenticated: status === 'authenticated' && user !== null,
      login,
      register,
      logout,
      refreshUser,
      clearError,
    }),
    [status, user, error, isLoading, login, register, logout, refreshUser, clearError]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
