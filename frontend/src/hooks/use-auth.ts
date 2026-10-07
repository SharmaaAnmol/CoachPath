'use client';

/**
 * useAuth Hook.
 * Accesses CoachPath authentication state and actions.
 */

import { useContext } from 'react';
import { AuthContext, AuthContextValue } from '@/providers/auth-provider';

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
