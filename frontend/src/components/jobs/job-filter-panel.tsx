'use client';

import * as React from 'react';
import { JobSearchQuery } from '@/types';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  Search,
  X,
  SlidersHorizontal,
  RotateCcw,
  Building2,
  MapPin,
  DollarSign,
  ChevronDown,
  Filter,
} from 'lucide-react';

export interface JobFilterPanelProps {
  query: JobSearchQuery;
  onQueryChange: (newQuery: Partial<JobSearchQuery>) => void;
  onResetFilters: () => void;
  totalResults: number;
  isLoading: boolean;
  className?: string;
}

const CANONICAL_ROLES = [
  { id: '', label: 'All Roles' },
  { id: 'backend-developer', label: 'Backend Developer' },
  { id: 'frontend-developer', label: 'Frontend Developer' },
  { id: 'fullstack-developer', label: 'Fullstack Developer' },
  { id: 'data-engineer', label: 'Data Engineer' },
  { id: 'mobile-engineer', label: 'Mobile Engineer' },
  { id: 'data-scientist', label: 'Data Scientist' },
  { id: 'machine-learning-engineer', label: 'ML Engineer' },
  { id: 'ai-engineer', label: 'AI Engineer' },
  { id: 'devops-cloud-engineer', label: 'DevOps & Cloud' },
  { id: 'software-engineer', label: 'Software Engineer' },
  { id: 'data-analyst', label: 'Data Analyst' },
];

const WORKPLACE_TYPES = [
  { id: '', label: 'All' },
  { id: 'remote', label: 'Remote' },
  { id: 'hybrid', label: 'Hybrid' },
  { id: 'onsite', label: 'Onsite' },
];

const EXPERIENCE_LEVELS = [
  { id: '', label: 'All Levels' },
  { id: 'entry_level', label: 'Entry-level' },
  { id: 'junior', label: 'Junior' },
  { id: 'mid', label: 'Mid-level' },
  { id: 'internship', label: 'Internship' },
];

const SALARY_THRESHOLDS = [
  { value: undefined, label: 'Any Salary' },
  { value: 80000, label: '$80k+ / yr' },
  { value: 100000, label: '$100k+ / yr' },
  { value: 120000, label: '$120k+ / yr' },
  { value: 140000, label: '$140k+ / yr' },
];

const POPULAR_SKILLS = [
  { id: 'python', label: 'Python' },
  { id: 'sql-databases', label: 'SQL' },
  { id: 'postgresql', label: 'PostgreSQL' },
  { id: 'react', label: 'React' },
  { id: 'typescript', label: 'TypeScript' },
  { id: 'fastapi', label: 'FastAPI' },
  { id: 'docker', label: 'Docker' },
  { id: 'aws', label: 'AWS' },
  { id: 'kubernetes', label: 'Kubernetes' },
  { id: 'machine-learning', label: 'Machine Learning' },
];

export function JobFilterPanel({
  query,
  onQueryChange,
  onResetFilters,
  totalResults,
  isLoading,
  className,
}: JobFilterPanelProps) {
  const [searchInput, setSearchInput] = React.useState(query.keyword || '');
  const [isAdvancedOpen, setIsAdvancedOpen] = React.useState(false);

  // Sync internal search input when query.keyword changes externally
  React.useEffect(() => {
    setSearchInput(query.keyword || '');
  }, [query.keyword]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onQueryChange({ keyword: searchInput.trim() || undefined, page: 1 });
  };

  const handleClearSearch = () => {
    setSearchInput('');
    onQueryChange({ keyword: undefined, page: 1 });
  };

  // Count active filters (excluding default page/page_size/sort)
  const activeFilterCount = [
    query.keyword,
    query.role_id,
    query.remote_type,
    query.employment_type,
    query.experience_level,
    query.skill_id,
    query.min_salary,
  ].filter(Boolean).length;

  return (
    <Card className="p-4 sm:p-5 space-y-4">
      {/* Search Input Bar */}
      <form onSubmit={handleSearchSubmit} className="flex items-center gap-2">
        <div className="relative flex-1">
          <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-3" />
          <input
            type="text"
            placeholder="Search jobs by title, company, or keyword (e.g. Stripe, Backend, Python)..."
            value={searchInput}
            onChange={(e) => setSearchInput(e.target.value)}
            className="w-full pl-10 pr-9 py-2 text-xs sm:text-sm rounded-xl border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900 text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-brand-500 shadow-sm"
          />
          {searchInput && (
            <button
              type="button"
              onClick={handleClearSearch}
              className="absolute right-3 top-2.5 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200"
              aria-label="Clear search text"
            >
              <X className="w-4 h-4" />
            </button>
          )}
        </div>

        <Button type="submit" size="sm" variant="primary" disabled={isLoading}>
          Search
        </Button>

        <Button
          type="button"
          size="sm"
          variant="outline"
          onClick={() => setIsAdvancedOpen(!isAdvancedOpen)}
          className="flex items-center gap-1.5 shrink-0"
        >
          <SlidersHorizontal className="w-3.5 h-3.5" />
          <span className="hidden sm:inline">Filters</span>
          {activeFilterCount > 0 && (
            <span className="rounded-full bg-brand-600 text-white text-[10px] w-4 h-4 flex items-center justify-center font-bold">
              {activeFilterCount}
            </span>
          )}
        </Button>
      </form>

      {/* Main Filter Pills: Workplace & Target Role */}
      <div className="flex flex-col lg:flex-row items-stretch lg:items-center justify-between gap-3 pt-1">
        {/* Workplace Type Selector */}
        <div className="flex items-center gap-1.5 overflow-x-auto text-xs pb-1 sm:pb-0">
          <span className="text-slate-400 font-semibold text-[11px] uppercase tracking-wider mr-1 shrink-0">
            Workplace:
          </span>
          {WORKPLACE_TYPES.map((t) => (
            <button
              key={t.id}
              type="button"
              onClick={() => onQueryChange({ remote_type: t.id || undefined, page: 1 })}
              className={`px-3 py-1.5 rounded-lg font-medium transition-all text-xs shrink-0 ${
                (query.remote_type || '') === t.id
                  ? 'bg-slate-900 text-white dark:bg-white dark:text-slate-900 font-semibold shadow-xs'
                  : 'bg-slate-100 text-slate-600 hover:bg-slate-200 dark:bg-slate-800 dark:text-slate-300 dark:hover:bg-slate-700'
              }`}
            >
              {t.label}
            </button>
          ))}
        </div>

        {/* Sort and Role Dropdowns */}
        <div className="flex flex-wrap items-center gap-2 text-xs">
          {/* Target Role Dropdown */}
          <select
            value={query.role_id || ''}
            onChange={(e) => onQueryChange({ role_id: e.target.value || undefined, page: 1 })}
            className="px-2.5 py-1.5 rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900 text-slate-800 dark:text-slate-200 font-medium focus:outline-none focus:ring-1 focus:ring-brand-500 text-xs"
          >
            {CANONICAL_ROLES.map((r) => (
              <option key={r.id} value={r.id}>
                {r.label}
              </option>
            ))}
          </select>

          {/* Sort By Dropdown */}
          <select
            value={query.sort_by || 'newest'}
            onChange={(e) =>
              onQueryChange({
                sort_by: e.target.value as 'newest' | 'salary_high' | 'title_asc' | 'oldest',
                page: 1,
              })
            }
            className="px-2.5 py-1.5 rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900 text-slate-800 dark:text-slate-200 font-medium focus:outline-none focus:ring-1 focus:ring-brand-500 text-xs"
          >
            <option value="newest">Newest Postings</option>
            <option value="salary_high">Highest Salary</option>
            <option value="title_asc">Title (A-Z)</option>
            <option value="oldest">Oldest First</option>
          </select>
        </div>
      </div>

      {/* Advanced Collapsible Filter Drawer */}
      {isAdvancedOpen && (
        <div className="pt-3 border-t border-slate-100 dark:border-slate-800 space-y-4 animate-in fade-in text-xs">
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            {/* Seniority Filter */}
            <div className="space-y-1.5">
              <label className="text-[11px] font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider block">
                Seniority Level
              </label>
              <select
                value={query.experience_level || ''}
                onChange={(e) =>
                  onQueryChange({ experience_level: e.target.value || undefined, page: 1 })
                }
                className="w-full px-2.5 py-1.5 rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900 text-slate-800 dark:text-slate-200 text-xs"
              >
                {EXPERIENCE_LEVELS.map((el) => (
                  <option key={el.id} value={el.id}>
                    {el.label}
                  </option>
                ))}
              </select>
            </div>

            {/* Minimum Salary Threshold */}
            <div className="space-y-1.5">
              <label className="text-[11px] font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider block">
                Minimum Annual Salary
              </label>
              <select
                value={query.min_salary || ''}
                onChange={(e) =>
                  onQueryChange({
                    min_salary: e.target.value ? Number(e.target.value) : undefined,
                    page: 1,
                  })
                }
                className="w-full px-2.5 py-1.5 rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900 text-slate-800 dark:text-slate-200 text-xs"
              >
                {SALARY_THRESHOLDS.map((st, i) => (
                  <option key={i} value={st.value || ''}>
                    {st.label}
                  </option>
                ))}
              </select>
            </div>

            {/* Canonical Skill Quick Selector */}
            <div className="space-y-1.5">
              <label className="text-[11px] font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider block">
                Canonical Skill Tag
              </label>
              <select
                value={query.skill_id || ''}
                onChange={(e) =>
                  onQueryChange({ skill_id: e.target.value || undefined, page: 1 })
                }
                className="w-full px-2.5 py-1.5 rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900 text-slate-800 dark:text-slate-200 text-xs"
              >
                <option value="">All Skills</option>
                {POPULAR_SKILLS.map((sk) => (
                  <option key={sk.id} value={sk.id}>
                    {sk.label}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Popular Skills Quick Chips */}
          <div className="space-y-1.5 pt-1">
            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">
              Quick Filter by In-Demand Skills:
            </span>
            <div className="flex flex-wrap gap-1.5">
              {POPULAR_SKILLS.map((s) => {
                const isSelected = query.skill_id === s.id;
                return (
                  <button
                    key={s.id}
                    type="button"
                    onClick={() =>
                      onQueryChange({
                        skill_id: isSelected ? undefined : s.id,
                        page: 1,
                      })
                    }
                    className={`px-2.5 py-1 rounded-md text-[11px] transition-all font-medium ${
                      isSelected
                        ? 'bg-brand-600 text-white font-semibold'
                        : 'bg-slate-100 text-slate-600 hover:bg-slate-200 dark:bg-slate-800 dark:text-slate-300'
                    }`}
                  >
                    {s.label}
                  </button>
                );
              })}
            </div>
          </div>
        </div>
      )}

      {/* Active Filter Chips & Reset Bar */}
      {activeFilterCount > 0 && (
        <div className="flex flex-wrap items-center justify-between gap-2 pt-2 border-t border-slate-100 dark:border-slate-800 text-xs">
          <div className="flex flex-wrap items-center gap-1.5">
            <span className="text-slate-400 font-semibold text-[11px]">Active:</span>

            {query.keyword && (
              <Badge variant="default" size="sm" className="gap-1 font-normal">
                Keyword: &quot;{query.keyword}&quot;
                <button
                  onClick={() => onQueryChange({ keyword: undefined, page: 1 })}
                  className="hover:text-slate-900"
                >
                  <X className="w-3 h-3" />
                </button>
              </Badge>
            )}

            {query.role_id && (
              <Badge variant="default" size="sm" className="gap-1 font-normal">
                Role: {CANONICAL_ROLES.find((r) => r.id === query.role_id)?.label || query.role_id}
                <button
                  onClick={() => onQueryChange({ role_id: undefined, page: 1 })}
                  className="hover:text-slate-900"
                >
                  <X className="w-3 h-3" />
                </button>
              </Badge>
            )}

            {query.remote_type && (
              <Badge variant="default" size="sm" className="gap-1 font-normal capitalize">
                {query.remote_type}
                <button
                  onClick={() => onQueryChange({ remote_type: undefined, page: 1 })}
                  className="hover:text-slate-900"
                >
                  <X className="w-3 h-3" />
                </button>
              </Badge>
            )}

            {query.experience_level && (
              <Badge variant="default" size="sm" className="gap-1 font-normal capitalize">
                {query.experience_level.replace('_', ' ')}
                <button
                  onClick={() => onQueryChange({ experience_level: undefined, page: 1 })}
                  className="hover:text-slate-900"
                >
                  <X className="w-3 h-3" />
                </button>
              </Badge>
            )}

            {query.skill_id && (
              <Badge variant="default" size="sm" className="gap-1 font-normal">
                Skill: {POPULAR_SKILLS.find((s) => s.id === query.skill_id)?.label || query.skill_id}
                <button
                  onClick={() => onQueryChange({ skill_id: undefined, page: 1 })}
                  className="hover:text-slate-900"
                >
                  <X className="w-3 h-3" />
                </button>
              </Badge>
            )}

            {query.min_salary && (
              <Badge variant="default" size="sm" className="gap-1 font-normal">
                Min: ${query.min_salary.toLocaleString()}
                <button
                  onClick={() => onQueryChange({ min_salary: undefined, page: 1 })}
                  className="hover:text-slate-900"
                >
                  <X className="w-3 h-3" />
                </button>
              </Badge>
            )}
          </div>

          <button
            type="button"
            onClick={onResetFilters}
            className="flex items-center gap-1 text-[11px] font-semibold text-rose-600 hover:text-rose-700 dark:text-rose-400 transition-colors"
          >
            <RotateCcw className="w-3 h-3" /> Reset All Filters
          </button>
        </div>
      )}
    </Card>
  );
}
