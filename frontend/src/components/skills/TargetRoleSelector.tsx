'use client';

import * as React from 'react';
import { TargetRoleDetail } from '@/types';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import {
  Briefcase,
  ChevronDown,
  Check,
  Compass,
  Star,
  Info,
} from 'lucide-react';

interface TargetRoleSelectorProps {
  roles: TargetRoleDetail[];
  selectedRoleId: string;
  onSelectRole: (roleId: string) => void;
  profileRoleId?: string | null;
  isLoading?: boolean;
  disabled?: boolean;
}

export function TargetRoleSelector({
  roles,
  selectedRoleId,
  onSelectRole,
  profileRoleId,
  isLoading = false,
  disabled = false,
}: TargetRoleSelectorProps) {
  const [isOpen, setIsOpen] = React.useState(false);
  const containerRef = React.useRef<HTMLDivElement>(null);

  const selectedRole = roles.find((r) => r.id === selectedRoleId) || roles[0];

  // Close dropdown on outside click
  React.useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  return (
    <Card className="p-4 sm:p-5 border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-sm">
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <span className="p-1.5 rounded-lg bg-indigo-50 dark:bg-indigo-950/50 text-indigo-600 dark:text-indigo-400">
              <Briefcase className="w-4 h-4" />
            </span>
            <h3 className="text-sm font-semibold text-slate-900 dark:text-white uppercase tracking-wider">
              Benchmark Target Role
            </h3>
            {profileRoleId === selectedRoleId && (
              <Badge variant="outline" className="text-[10px] bg-indigo-50 dark:bg-indigo-950/40 text-indigo-700 dark:text-indigo-300 border-indigo-200 dark:border-indigo-800 flex items-center gap-1">
                <Star className="w-2.5 h-2.5 fill-current" /> Profile Primary Target
              </Badge>
            )}
          </div>
          <p className="text-xs text-slate-500 dark:text-slate-400">
            {selectedRole
              ? selectedRole.description
              : 'Select a canonical role to compare your verified evidence against benchmark requirements.'}
          </p>
        </div>

        {/* Role Selector Trigger */}
        <div className="relative w-full lg:w-80 shrink-0" ref={containerRef}>
          <button
            type="button"
            disabled={disabled || isLoading || roles.length === 0}
            onClick={() => setIsOpen(!isOpen)}
            className={`w-full flex items-center justify-between px-3.5 py-2.5 rounded-xl border text-left text-sm font-medium transition-all ${
              isOpen
                ? 'border-indigo-500 ring-2 ring-indigo-500/10 bg-white dark:bg-slate-900'
                : 'border-slate-200 dark:border-slate-700 bg-slate-50/50 dark:bg-slate-800/50 hover:bg-white dark:hover:bg-slate-800'
            } ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
          >
            <div className="flex items-center gap-2 truncate">
              <Compass className="w-4 h-4 text-indigo-600 dark:text-indigo-400 shrink-0" />
              <span className="truncate text-slate-900 dark:text-white font-semibold">
                {selectedRole ? selectedRole.title : 'Select a Target Role...'}
              </span>
            </div>
            <ChevronDown className={`w-4 h-4 text-slate-400 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
          </button>

          {/* Dropdown Menu */}
          {isOpen && (
            <div className="absolute z-30 mt-1.5 w-full bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-700 shadow-xl overflow-hidden py-1.5 max-h-80 overflow-y-auto animate-in fade-in-50 zoom-in-95">
              <div className="px-3 py-1.5 text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
                Supported Canonical Roles ({roles.length})
              </div>
              {roles.map((role) => {
                const isSelected = role.id === selectedRoleId;
                const isProfileRole = role.id === profileRoleId;
                return (
                  <button
                    key={role.id}
                    type="button"
                    onClick={() => {
                      onSelectRole(role.id);
                      setIsOpen(false);
                    }}
                    className={`w-full flex items-start justify-between px-3.5 py-2.5 text-left text-xs transition-colors ${
                      isSelected
                        ? 'bg-indigo-50/80 dark:bg-indigo-950/40 text-indigo-950 dark:text-indigo-100 font-medium'
                        : 'text-slate-700 dark:text-slate-300 hover:bg-slate-100/70 dark:hover:bg-slate-800'
                    }`}
                  >
                    <div className="space-y-0.5 pr-2">
                      <div className="flex items-center gap-1.5">
                        <span className="font-semibold text-slate-900 dark:text-white">
                          {role.title}
                        </span>
                        {isProfileRole && (
                          <span className="px-1.5 py-0.2 text-[9px] font-bold rounded bg-indigo-100 dark:bg-indigo-900/60 text-indigo-700 dark:text-indigo-300">
                            Current
                          </span>
                        )}
                      </div>
                      <p className="text-[11px] text-slate-500 dark:text-slate-400 line-clamp-1">
                        {role.description}
                      </p>
                      <div className="text-[10px] text-slate-400 dark:text-slate-500 pt-0.5">
                        {role.requirements?.length || 0} required skills • Category: {role.category}
                      </div>
                    </div>
                    {isSelected && (
                      <Check className="w-4 h-4 text-indigo-600 dark:text-indigo-400 shrink-0 mt-0.5" />
                    )}
                  </button>
                );
              })}
            </div>
          )}
        </div>
      </div>
    </Card>
  );
}
