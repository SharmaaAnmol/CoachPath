'use client';

import * as React from 'react';
import { useSearchParams } from 'next/navigation';
import { JobOpportunity, JobSearchQuery, MarketIntelligenceData } from '@/types';
import { jobClient } from '@/lib/job-client';
import { JobCard } from '@/components/jobs/job-card';
import { JobDetailModal } from '@/components/jobs/job-detail-modal';
import { JobFilterPanel } from '@/components/jobs/job-filter-panel';
import { MarketIntelligenceCard } from '@/components/jobs/market-intelligence-card';
import { ManualJobImportModal } from '@/components/jobs/manual-job-import-modal';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card } from '@/components/ui/card';
import { EmptyState } from '@/components/ui/empty-state';
import {
  Briefcase,
  Sparkles,
  BarChart3,
  PlusCircle,
  AlertTriangle,
  RotateCcw,
  ChevronLeft,
  ChevronRight,
  Database,
  Search,
} from 'lucide-react';

export default function JobsPage() {
  const searchParams = useSearchParams();

  // Search and Filter State
  const [query, setQuery] = React.useState<JobSearchQuery>({
    page: 1,
    page_size: 20,
    sort_by: 'newest',
  });

  // Results State
  const [jobs, setJobs] = React.useState<JobOpportunity[]>([]);
  const [totalCount, setTotalCount] = React.useState(0);
  const [totalPages, setTotalPages] = React.useState(1);
  const [isLoading, setIsLoading] = React.useState(true);
  const [errorMessage, setErrorMessage] = React.useState<string | null>(null);
  const [isDatasetEmpty, setIsDatasetEmpty] = React.useState(false);

  // Selected Job (for modal)
  const [selectedJob, setSelectedJob] = React.useState<JobOpportunity | null>(null);

  // Market Intelligence State
  const [showMarketIntelligence, setShowMarketIntelligence] = React.useState(false);
  const [marketData, setMarketData] = React.useState<MarketIntelligenceData | null>(null);
  const [isMarketLoading, setIsMarketLoading] = React.useState(false);
  const [marketRoleId, setMarketRoleId] = React.useState<string>('');

  // Import Modal State
  const [showImportModal, setShowImportModal] = React.useState(false);

  // Request cancellation / Stale response protection
  const activeRequestId = React.useRef(0);

  // 1. Fetch Jobs Function with stale response guard
  const fetchJobs = React.useCallback(async (searchQuery: JobSearchQuery) => {
    const requestId = ++activeRequestId.current;
    setIsLoading(true);
    setErrorMessage(null);

    try {
      const response = await jobClient.searchJobs(searchQuery);

      // Only update state if this is the most recent request
      if (requestId === activeRequestId.current) {
        setJobs(response.items || []);
        setTotalCount(response.total || 0);
        setTotalPages(response.total_pages || 1);

        // Check if database is completely empty (no filters applied, 0 total)
        const hasFilters = Boolean(
          searchQuery.keyword ||
            searchQuery.role_id ||
            searchQuery.remote_type ||
            searchQuery.employment_type ||
            searchQuery.experience_level ||
            searchQuery.skill_id ||
            searchQuery.min_salary
        );
        if (!hasFilters && response.total === 0) {
          setIsDatasetEmpty(true);
        } else {
          setIsDatasetEmpty(false);
        }
      }
    } catch (err: any) {
      if (requestId === activeRequestId.current) {
        setErrorMessage(
          err?.message ||
            'Unable to load job opportunities from CoachPath. Please verify backend connection.'
        );
      }
    } finally {
      if (requestId === activeRequestId.current) {
        setIsLoading(false);
      }
    }
  }, []);

  // 2. Fetch Market Intelligence
  const fetchMarketIntelligence = React.useCallback(async (roleId?: string) => {
    try {
      setIsMarketLoading(true);
      const data = await jobClient.getMarketIntelligence(roleId || undefined);
      setMarketData(data);
    } catch (err: any) {
      console.warn('Failed to load market intelligence:', err);
    } finally {
      setIsMarketLoading(false);
    }
  }, []);

  // 3. Initial Load and Query Changes
  React.useEffect(() => {
    fetchJobs(query);
  }, [query, fetchJobs]);

  // 4. Handle initial deep-linked job selection (?selected=UUID)
  React.useEffect(() => {
    const selectedId = searchParams.get('selected');
    if (selectedId) {
      jobClient
        .getJobById(selectedId)
        .then((job) => setSelectedJob(job))
        .catch(() => {
          // If not found, ignore
        });
    }
  }, [searchParams]);

  // 5. Load Market Intelligence on toggle
  React.useEffect(() => {
    if (showMarketIntelligence && !marketData) {
      fetchMarketIntelligence(marketRoleId);
    }
  }, [showMarketIntelligence, marketData, marketRoleId, fetchMarketIntelligence]);

  // Handlers
  const handleQueryChange = (updates: Partial<JobSearchQuery>) => {
    setQuery((prev) => ({
      ...prev,
      ...updates,
    }));
  };

  const handleResetFilters = () => {
    setQuery({
      page: 1,
      page_size: 20,
      sort_by: 'newest',
    });
  };

  const handlePageChange = (newPage: number) => {
    if (newPage >= 1 && newPage <= totalPages) {
      handleQueryChange({ page: newPage });
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  };

  const handleImportSuccess = (newJob: JobOpportunity) => {
    // Refresh current query and select the newly imported job
    fetchJobs(query);
    setSelectedJob(newJob);
  };

  const handleMarketRoleChange = (roleId: string) => {
    setMarketRoleId(roleId);
    fetchMarketIntelligence(roleId);
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto pb-12">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-xl sm:text-2xl font-bold text-slate-900 dark:text-white">
              Job Discovery & Market Intelligence
            </h1>
            <Badge variant="verified" size="md">
              Verified Catalog
            </Badge>
          </div>
          <p className="text-xs sm:text-sm text-slate-500 dark:text-slate-400 mt-1">
            Search verified tech opportunities grounded in canonical skills, role requirements, and live labor market aggregates.
          </p>
        </div>

        {/* Action CTAs */}
        <div className="flex items-center gap-2.5">
          <Button
            size="sm"
            variant={showMarketIntelligence ? 'primary' : 'outline'}
            onClick={() => setShowMarketIntelligence(!showMarketIntelligence)}
            className="flex items-center gap-1.5"
          >
            <BarChart3 className="w-3.5 h-3.5" />
            <span className="text-xs">Market Insights</span>
          </Button>

          <Button
            size="sm"
            variant="outline"
            onClick={() => setShowImportModal(true)}
            className="flex items-center gap-1.5"
          >
            <PlusCircle className="w-3.5 h-3.5 text-brand-600" />
            <span className="text-xs">Import Job</span>
          </Button>
        </div>
      </div>

      {/* Market Intelligence Section (Toggleable) */}
      {showMarketIntelligence && (
        <MarketIntelligenceCard
          data={marketData}
          isLoading={isMarketLoading}
          selectedRoleId={marketRoleId}
          onRoleChange={handleMarketRoleChange}
          onClose={() => setShowMarketIntelligence(false)}
        />
      )}

      {/* Search & Filter Controls */}
      <JobFilterPanel
        query={query}
        onQueryChange={handleQueryChange}
        onResetFilters={handleResetFilters}
        totalResults={totalCount}
        isLoading={isLoading}
      />

      {/* Results Header Counter */}
      <div className="flex items-center justify-between text-xs text-slate-500 dark:text-slate-400 px-1">
        <span>
          Showing <strong>{jobs.length}</strong> of <strong>{totalCount}</strong> verified opportunities
        </span>
        {query.sort_by && (
          <span className="capitalize">
            Sorted by: <strong>{query.sort_by.replace('_', ' ')}</strong>
          </span>
        )}
      </div>

      {/* Job Postings Results List */}
      <div className="space-y-4">
        {isLoading ? (
          // Skeleton Loaders
          <div className="space-y-4">
            {[1, 2, 3, 4].map((i) => (
              <Card key={i} className="p-5 space-y-3 animate-pulse">
                <div className="flex justify-between">
                  <div className="h-5 bg-slate-200 dark:bg-slate-700 rounded-md w-1/3" />
                  <div className="h-5 bg-slate-200 dark:bg-slate-700 rounded-md w-24" />
                </div>
                <div className="h-4 bg-slate-100 dark:bg-slate-800 rounded-md w-1/2" />
                <div className="h-10 bg-slate-100 dark:bg-slate-800 rounded-md w-full" />
                <div className="flex gap-2">
                  <div className="h-6 bg-slate-200 dark:bg-slate-700 rounded-md w-16" />
                  <div className="h-6 bg-slate-200 dark:bg-slate-700 rounded-md w-16" />
                  <div className="h-6 bg-slate-200 dark:bg-slate-700 rounded-md w-16" />
                </div>
              </Card>
            ))}
          </div>
        ) : errorMessage ? (
          // Error State
          <EmptyState
            icon={<AlertTriangle className="w-6 h-6 text-rose-500" />}
            title="Unable to Retrieve Job Listings"
            description={errorMessage}
            actionLabel="Retry Request"
            onAction={() => fetchJobs(query)}
          />
        ) : isDatasetEmpty ? (
          // Case A: The Dataset is Empty
          <EmptyState
            icon={<Database className="w-6 h-6 text-slate-400" />}
            title="Job Catalog is Currently Empty"
            description="No job postings have been ingested into the system yet. You can paste and import a job posting directly to start analyzing role requirements."
            actionLabel="Import a Job Manually"
            onAction={() => setShowImportModal(true)}
          />
        ) : jobs.length === 0 ? (
          // Case B: Search Returned No Matches
          <EmptyState
            icon={<Search className="w-6 h-6 text-slate-400" />}
            title="No Matching Positions Found"
            description="None of the verified jobs in the catalog match your current filter parameters. Try clearing search keywords, adjusting seniority tiers, or resetting all filters."
            actionLabel="Reset All Filters"
            onAction={handleResetFilters}
          />
        ) : (
          // Render Job Cards
          <>
            <div className="space-y-3.5">
              {jobs.map((job) => (
                <JobCard
                  key={job.id}
                  job={job}
                  onSelect={(j) => setSelectedJob(j)}
                />
              ))}
            </div>

            {/* Pagination Controls */}
            {totalPages > 1 && (
              <div className="flex items-center justify-between pt-6 border-t border-slate-200/80 dark:border-slate-800 text-xs">
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => handlePageChange((query.page || 1) - 1)}
                  disabled={(query.page || 1) <= 1 || isLoading}
                  className="flex items-center gap-1"
                >
                  <ChevronLeft className="w-4 h-4" /> Previous
                </Button>

                <div className="flex items-center gap-1 text-slate-600 dark:text-slate-300">
                  <span>
                    Page <strong>{query.page || 1}</strong> of <strong>{totalPages}</strong>
                  </span>
                </div>

                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => handlePageChange((query.page || 1) + 1)}
                  disabled={(query.page || 1) >= totalPages || isLoading}
                  className="flex items-center gap-1"
                >
                  Next <ChevronRight className="w-4 h-4" />
                </Button>
              </div>
            )}
          </>
        )}
      </div>

      {/* Job Detail Modal */}
      <JobDetailModal
        job={selectedJob}
        isOpen={selectedJob !== null}
        onClose={() => setSelectedJob(null)}
      />

      {/* Manual Job Import Modal */}
      <ManualJobImportModal
        isOpen={showImportModal}
        onClose={() => setShowImportModal(false)}
        onSuccess={handleImportSuccess}
      />
    </div>
  );
}
