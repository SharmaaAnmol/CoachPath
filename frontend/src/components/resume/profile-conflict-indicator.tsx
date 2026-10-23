'use client';

import * as React from 'react';
import { Badge } from '@/components/ui/badge';
import { Check, Plus, AlertCircle, ShieldCheck } from 'lucide-react';

interface ProfileConflictIndicatorProps {
  status: 'existing' | 'new' | 'conflict';
  label?: string;
  className?: string;
}

export function ProfileConflictIndicator({
  status,
  label,
  className,
}: ProfileConflictIndicatorProps) {
  if (status === 'existing') {
    return (
      <Badge variant="secondary" size="sm" className={className}>
        <Check className="w-3 h-3 mr-1 text-slate-500" />
        {label || 'Already in Profile'}
      </Badge>
    );
  }

  if (status === 'conflict') {
    return (
      <Badge variant="action" size="sm" className={className}>
        <AlertCircle className="w-3 h-3 mr-1 text-amber-600" />
        {label || 'Modified / Conflicting Dates'}
      </Badge>
    );
  }

  return (
    <Badge variant="verified" size="sm" className={className}>
      <Plus className="w-3 h-3 mr-1 text-emerald-600" />
      {label || 'New Credential'}
    </Badge>
  );
}
