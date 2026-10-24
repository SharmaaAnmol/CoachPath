'use client';

import * as React from 'react';
import { useSearchParams } from 'next/navigation';
import Link from 'next/link';
import {
  JobOpportunity,
  JobSearchQuery,
  MarketIntelligenceData,
  JobRecommendationItem,
  JobRecommendationQuery,
  JobMatchResponse,
} from '@/types';
import { jobClient } from '@/lib/job-client';
import { jobMatchingClient } from '@/lib/job-matching-client';
import { JobCard } from '@/components/jobs/job-card';
import { JobMatchCard } from '@/components/jobs/job-match-card';
import { JobMatchDrawer } from '@/components/jobs/job-match-drawer';
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
  RefreshCw,
  SlidersHorizontal,
  Award,
  Layers,
  ArrowRight,
} from 'lucide-react';

type PageTab = 'recommendations' | 'all';

export default function JobsPage() {
  const searchParams = useSearchParams();

  // Active Main Tab
  const [activeTab, setActiveTab] = React.useState<PageTab>('recommendations');

  // ─────────────────────────────────────────────
  // Tab 1: Recommendations State (Phase 9B)
  // ─────────────────────────────────────────────
  const [recomQuery, setRecomQuery] = React.useState<JobRecommendationQuery>({
    page: 1,
    page_size: 15,
    min_score: undefined,
    remote_type: undefined,
    role_id: undefined,
    include_provisional: true,
  });
  const [recommendations, setRecommendations] = React.useState<JobRecommendationItem[]>([]);
  const [recomTotal, setRecomTotal] = React.useState(0);
  const [recomTotalPages, setRecomTotalPages] = React.useState(1);
  const [isRecomLoading, setIsRecomLoading] = React.useState(true);
  const [recomError, setRecomError] = React.useState<string | null>(null);
  const [isBatchRefreshing, setIsBatchRefreshing] = React.useState(false);
  const [batchRefreshNotice, setBatchRefreshNotice] = React.useState<string | null>(null);

  // ─────────────────────────────────────────────
  // Tab 2: All Jobs Search & Filter State (Phase 8)
  // ─────────────────────────────────────────────
  const [searchQuery, setSearchQuery] = React.useState<JobSearchQuery>({
    page: 1,
    page_size: 20,
    sort_by: 'newest',
  });
  const [jobs, setJobs] = React.useState<JobOpportunity[]>([]);
  const [totalCount, setTotalCount] = React.useState(0);
  const [totalPages, setTotalPages] = React.useState(1);
  const [isLoading, setIsLoading] = React.useState(true);
  const [errorMessage, setErrorMessage] = React.useState<string | null>(null);
  const [isDatasetEmpty, setIsDatasetEmpty] = React.useState(false);

  // ─────────────────────────────────────────────
  // Modals & Drawers
  // ─────────────────────────────────────────────
  // Job Detail Modal
  const [selectedJob, setSelectedJob] = React.useState<JobOpportunity | null>(null);

  // Match Explainability Drawer
  const [selectedMatchJob, setSelectedMatchJob] = React.useState<JobOpportunity | null>(null);
  const [selectedMatch, setSelectedMatch] = React.useState<JobMatchResponse | null>(null);
  const [showMatchDrawer, setShowMatchDrawer] = React.useState(false);

  // Market Intelligence State
  const [showMarketIntelligence, setShowMarketIntelligence] = React.useState(false);
  const [marketData, setMarketData] = React.useState<MarketIntelligenceData | null>(null);
  const [isMarketLoading, setIsMarketLoading] = React.useState(false);
  const [marketRoleId, setMarketRoleId] = React.useState<string>('');

  // Import Modal State
  const [showImportModal, setShowImportModal] = React.useState(false);

  // Request cancellation / Stale response protection
  const activeJobsReqId = React.useRef(0);
  const activeRecomReqId = React.useRef(0);

  // ─────────────────────────────────────────────
  // 1. Fetch Recommendations
  // ─────────────────────────────────────────────
  const fetchRecommendations = React.useCallback(async (query: JobRecommendationQuery) => {
    const reqId = ++activeRecomReqId.current;
    setIsRecomLoading(true);
    setRecomError(null);

    try {
      const resp = await jobMatchingClient.getRecommendations(query);
      if (reqId === activeRecomReqId.current) {
        setRecommendations(resp.items || []);
        setRecomTotal(resp.total || 0);
        setRecomTotalPages(resp.total_pages || 1);
      }
    } catch (err: any) {
      if (reqId === activeRecomReqId.current) {
        setRecomError(
          err?.message ||
            'Unable to load personalized recommendations. Please ensure your profile is initialized.'
        );
      }
    } finally {
      if (reqId === activeRecomReqId.current) {
        setIsRecomLoading(false);
      }
    }
  }, []);

  // ─────────────────────────────────────────────
  // 2. Fetch All Jobs (Catalog Explore)
  // ─────────────────────────────────────────────
  const fetchJobs = React.useCallback(async (q: JobSearchQuery) => {
    const reqId = ++activeJobsReqId.current;
    setIsLoading(true);
    setErrorMessage(null);

    try {
      const resp = await jobClient.searchJobs(q);
      if (reqId === activeJobsReqId.current) {
        setJobs(resp.items || []);
        setTotalCount(resp.total || 0);
        setTotalPages(resp.total_pages || 1);

        const hasFilters = Boolean(
          q.keyword ||
            q.role_id ||
            q.remote_type ||
            q.employment_type ||
            q.experience_level ||
            q.skill_id ||
            q.min_salary
        );
        setIsDatasetEmpty(!hasFilters && resp.total === 0);
      }
    } catch (err: any) {
      if (reqId === activeJobsReqId.current) {
        setErrorMessage(
          err?.message ||
            'Unable to load job opportunities from CoachPath. Please verify backend connection.'
        );
      }
    } finally {
      if (reqId === activeJobsReqId.current) {
        setIsLoading(false);
      }
    }
  }, []);

  // ─────────────────────────────────────────────
  // 3. Fetch Market Intelligence
  // ─────────────────────────────────────────────
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

  // Load recommendations on recomQuery changes
  React.useEffect(() => {
    if (activeTab === 'recommendations') {
      fetchRecommendations(recomQuery);
    }
  }, [activeTab, recomQuery, fetchRecommendations]);

  // Load all jobs on searchQuery changes
  React.useEffect(() => {
    if (activeTab === 'all') {
      fetchJobs(searchQuery);
    }
  }, [activeTab, searchQuery, fetchJobs]);

  // Deep-linked job selection (?selected=UUID)
  React.useEffect(() => {
    const selectedId = searchParams.get('selected');
    if (selectedId) {
      jobClient
        .getJobById(selectedId)
        .then((job) => setSelectedJob(job))
        .catch(() => {});
    }
  }, [searchParams]);

  // Load Market Intelligence on toggle
  React.useEffect(() => {
    if (showMarketIntelligence && !marketData) {
      fetchMarketIntelligence(marketRoleId);
    }
  }, [showMarketIntelligence, marketData, marketRoleId, fetchMarketIntelligence]);

  // ─────────────────────────────────────────────
  // Handlers for Recommendations Tab
  // ─────────────────────────────────────────────
  const handleBatchRefresh = async () => {
    setIsBatchRefreshing(true);
    setBatchRefreshNotice(null);
    try {
      const result = await jobMatchingClient.refreshRecommendations();
      setBatchRefreshNotice(result.message);
      await fetchRecommendations(recomQuery);
      setTimeout(() => setBatchRefreshNotice(null), 5000);
    } catch (err: any) {
      setRecomError(err?.message || 'Failed to refresh recommendations.');
    } finally {
      setIsBatchRefreshing(false);
    }
  };

  const handleOpenBreakdown = (job: JobOpportunity, match: JobMatchResponse) => {
    setSelectedMatchJob(job);
    setSelectedMatch(match);
    setShowMatchDrawer(true);
  };

  const handleRecalculateSuccess = (updatedMatch: JobMatchResponse) => {
    // Update match in local state list
    setRecommendations((prev) =>
      prev.map((item) =>
        item.job.id === updatedMatch.job_id ? { ...item, match: updatedMatch } : item
      )
    );
    setSelectedMatch(updatedMatch);
  };

  const handleRecomPageChange = (newPage: number) => {
    if (newPage >= 1 && newPage <= recomTotalPages) {
      setRecomQuery((prev) => ({ ...prev, page: newPage }));
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  };

  const handleResetRecomFilters = () => {
    setRecomQuery({
      page: 1,
      page_size: 15,
      min_score: undefined,
      remote_type: undefined,
      role_id: undefined,
      include_provisional: true,
    });
  };

  // ─────────────────────────────────────────────
  // Handlers for All Jobs Tab
  // ─────────────────────────────────────────────
  const handleSearchQueryChange = (updates: Partial<JobSearchQuery>) => {
    setSearchQuery((prev) => ({ ...prev, ...updates }));
  };

  const handleResetSearchFilters = () => {
    setSearchQuery({
      page: 1,
      page_size: 20,
      sort_by: 'newest',
    });
  };

  const handleAllJobsPageChange = (newPage: number) => {
    if (newPage >= 1 && newPage <= totalPages) {
      handleSearchQueryChange({ page: newPage });
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  };

  const handleImportSuccess = (newJob: JobOpportunity) => {
    if (activeTab === 'all') {
      fetchJobs(searchQuery);
    } else {
      fetchRecommendations(recomQuery);
    }
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
              Job Intelligence & Matching Engine
            </h1>
            <Badge variant="verified" size="md">
              Phase 9B Verified
            </Badge>
          </div>
          <p className="text-xs sm:text-sm text-slate-500 dark:text-slate-400 mt-1">
            Personalized role recommendations ranked by deterministic skill evidence alignment, labor market requirements, and candidate preferences.
          </p>
        </div>

        {/* Global Action CTAs */}
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

      {/* Main Tab Navigation */}
      <div className="flex items-center justify-between border-b border-slate-200 dark:border-slate-800 pb-px">
        <div className="flex items-center gap-2">
          <button
            onClick={() => setActiveTab('recommendations')}
            className={`px-4 py-2.5 text-xs sm:text-sm font-bold border-b-2 transition-all flex items-center gap-2 ${
              activeTab === 'recommendations'
                ? 'border-brand-600 text-brand-600 dark:text-brand-400'
                : 'border-transparent text-slate-500 hover:text-slate-800 dark:hover:text-slate-300'
            }`}
          >
            <Sparkles className="w-4 h-4 text-brand-500" />
            <span>Recommended For You</span>
            {recomTotal > 0 && (
              <span className="text-[11px] bg-brand-50 text-brand-700 dark:bg-brand-950 dark:text-brand-300 px-2 py-0.5 rounded-full font-bold">
                {recomTotal}
              </span>
            )}
          </button>

          <button
            onClick={() => setActiveTab('all')}
            className={`px-4 py-2.5 text-xs sm:text-sm font-bold border-b-2 transition-all flex items-center gap-2 ${
              activeTab === 'all'
                ? 'border-brand-600 text-brand-600 dark:text-brand-400'
                : 'border-transparent text-slate-500 hover:text-slate-800 dark:hover:text-slate-300'
            }`}
          >
            <Database className="w-4 h-4 text-slate-400" />
            <span>All Opportunities</span>
            {totalCount > 0 && (
              <span className="text-[11px] bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300 px-2 py-0.5 rounded-full font-medium">
                {totalCount}
              </span>
            )}
          </button>
        </div>

        {/* Tab Specific Quick CTA */}
        {activeTab === 'recommendations' && (
          <Button
            size="sm"
            variant="outline"
            onClick={handleBatchRefresh}
            disabled={isBatchRefreshing || isRecomLoading}
            className="flex items-center gap-1.5 text-xs"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isBatchRefreshing ? 'animate-spin' : ''}`} />
            <span>{isBatchRefreshing ? 'Recalculating...' : 'Refresh Matches'}</span>
          </Button>
        )}
      </div>

      {/* Batch Refresh Notice */}
      {batchRefreshNotice && (
        <div className="bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-200 dark:border-emerald-900/60 rounded-xl p-3 text-xs text-emerald-800 dark:text-emerald-200 flex items-center justify-between">
          <span>{batchRefreshNotice}</span>
          <button
            onClick={() => setBatchRefreshNotice(null)}
            className="text-emerald-600 hover:text-emerald-900 dark:hover:text-emerald-100 font-bold"
          >
            ✕
          </button>
        </div>
      )}

      {/* ─────────────────────────────────────────────
          TAB 1: RECOMMENDED FOR YOU CONTENT
          ───────────────────────────────────────────── */}
      {activeTab === 'recommendations' && (
        <div className="space-y-5">
          {/* Recommendation Filter Bar */}
          <Card className="p-4 space-y-3 bg-slate-50/60 dark:bg-slate-900/40 border-slate-200/80">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-3 text-xs">
              {/* Score Filter */}
              <div className="flex flex-wrap items-center gap-2">
                <span className="font-bold text-slate-700 dark:text-slate-300 flex items-center gap-1">
                  <SlidersHorizontal className="w-3.5 h-3.5 text-slate-400" />
                  Fit Threshold:
                </span>
                {[
                  { label: 'All Fits', val: undefined },
                  { label: 'Moderate (≥50%)', val: 50 },
                  { label: 'Strong (≥70%)', val: 70 },
                  { label: 'Exceptional (≥80%)', val: 80 },
                ].map((tier) => (
                  <button
                    key={tier.label}
                    onClick={() =>
                      setRecomQuery((prev) => ({
                        ...prev,
                        min_score: tier.val,
                        page: 1,
                      }))
                    }
                    className={`px-2.5 py-1 rounded-full font-medium transition-colors ${
                      recomQuery.min_score === tier.val
                        ? 'bg-brand-600 text-white dark:bg-brand-500'
                        : 'bg-white dark:bg-slate-800 text-slate-600 dark:text-slate-300 border border-slate-200 dark:border-slate-700 hover:bg-slate-100 dark:hover:bg-slate-750'
                    }`}
                  >
                    {tier.label}
                  </button>
                ))}
              </div>

              {/* Work Mode Filter */}
              <div className="flex flex-wrap items-center gap-2">
                <span className="font-bold text-slate-700 dark:text-slate-300">Workplace:</span>
                {[
                  { label: 'Any', val: undefined },
                  { label: 'Remote', val: 'remote' as const },
                  { label: 'Hybrid', val: 'hybrid' as const },
                  { label: 'Onsite', val: 'onsite' as const },
                ].map((mode) => (
                  <button
                    key={mode.label}
                    onClick={() =>
                      setRecomQuery((prev) => ({
                        ...prev,
                        remote_type: mode.val,
                        page: 1,
                      }))
                    }
                    className={`px-2.5 py-1 rounded-full font-medium transition-colors ${
                      recomQuery.remote_type === mode.val
                        ? 'bg-slate-900 text-white dark:bg-white dark:text-slate-900'
                        : 'bg-white dark:bg-slate-800 text-slate-600 dark:text-slate-300 border border-slate-200 dark:border-slate-700 hover:bg-slate-100 dark:hover:bg-slate-750'
                    }`}
                  >
                    {mode.label}
                  </button>
                ))}
              </div>

              {/* Provisional Toggle & Reset */}
              <div className="flex items-center gap-3">
                <label className="flex items-center gap-1.5 cursor-pointer text-slate-600 dark:text-slate-400 select-none">
                  <input
                    type="checkbox"
                    checked={recomQuery.include_provisional}
                    onChange={(e) =>
                      setRecomQuery((prev) => ({
                        ...prev,
                        include_provisional: e.target.checked,
                        page: 1,
                      }))
                    }
                    className="rounded text-brand-600 focus:ring-brand-500 w-3.5 h-3.5 border-slate-300 dark:border-slate-700"
                  />
                  <span>Include Provisional (&lt;40% data)</span>
                </label>

                {(recomQuery.min_score !== undefined ||
                  recomQuery.remote_type !== undefined ||
                  !recomQuery.include_provisional) && (
                  <button
                    onClick={handleResetRecomFilters}
                    className="text-brand-600 dark:text-brand-400 hover:underline flex items-center gap-1"
                  >
                    <RotateCcw className="w-3 h-3" />
                    Reset
                  </button>
                )}
              </div>
            </div>
          </Card>

          {/* Results Summary Counter */}
          <div className="flex items-center justify-between text-xs text-slate-500 dark:text-slate-400 px-1">
            <span>
              Showing <strong>{recommendations.length}</strong> of <strong>{recomTotal}</strong> personalized recommendations
            </span>
            <span>
              Ranked by: <strong>Deterministic Match Fit</strong> (v1.0)
            </span>
          </div>

          {/* Recommendations Content States */}
          {isRecomLoading ? (
            <div className="space-y-4">
              {[1, 2, 3].map((n) => (
                <div key={n} className="p-6 rounded-2xl border border-slate-200 dark:border-slate-800 animate-pulse space-y-3 bg-white dark:bg-slate-900">
                  <div className="h-5 bg-slate-200 dark:bg-slate-700 rounded w-1/3" />
                  <div className="h-4 bg-slate-100 dark:bg-slate-800 rounded w-1/4" />
                  <div className="h-12 bg-slate-100 dark:bg-slate-800 rounded w-full" />
                </div>
              ))}
            </div>
          ) : recomError ? (
            <Card className="p-8 text-center space-y-4 max-w-xl mx-auto">
              <AlertTriangle className="w-10 h-10 text-amber-500 mx-auto" />
              <div className="space-y-1">
                <h3 className="text-base font-bold text-slate-900 dark:text-white">
                  Match Scoring Unavailable
                </h3>
                <p className="text-xs text-slate-500">{recomError}</p>
              </div>
              <div className="flex items-center justify-center gap-3 pt-2">
                <Link href="/assessments">
                  <Button size="sm" variant="primary">
                    Take Skill Assessments
                  </Button>
                </Link>
                <Button size="sm" variant="outline" onClick={() => fetchRecommendations(recomQuery)}>
                  Retry
                </Button>
              </div>
            </Card>
          ) : recommendations.length === 0 ? (
            <EmptyState
              icon={<Sparkles className="w-8 h-8 text-brand-500" />}
              title={
                recomQuery.min_score !== undefined || recomQuery.remote_type !== undefined
                  ? 'No Matches Meet Selected Filters'
                  : 'No Recommendations Available Yet'
              }
              description={
                recomQuery.min_score !== undefined || recomQuery.remote_type !== undefined
                  ? 'Try relaxing your minimum match score filter or workplace requirements to discover more opportunities.'
                  : 'Complete diagnostic assessments or explore the full catalog to seed recommendations.'
              }
              actionLabel={
                recomQuery.min_score !== undefined || recomQuery.remote_type !== undefined
                  ? 'Reset Filter Criteria'
                  : 'Explore All Opportunities'
              }
              onAction={
                recomQuery.min_score !== undefined || recomQuery.remote_type !== undefined
                  ? handleResetRecomFilters
                  : () => setActiveTab('all')
              }
            />
          ) : (
            <div className="space-y-4">
              {recommendations.map((item) => (
                <JobMatchCard
                  key={item.job.id}
                  job={item.job}
                  match={item.match}
                  onSelectBreakdown={handleOpenBreakdown}
                  onSelectJob={(j) => setSelectedJob(j)}
                />
              ))}

              {/* Recommendations Pagination */}
              {recomTotalPages > 1 && (
                <div className="flex items-center justify-between pt-6 border-t border-slate-200 dark:border-slate-800">
                  <Button
                    variant="outline"
                    size="sm"
                    disabled={(recomQuery.page ?? 1) <= 1}
                    onClick={() => handleRecomPageChange((recomQuery.page ?? 1) - 1)}
                    className="flex items-center gap-1.5"
                  >
                    <ChevronLeft className="w-4 h-4" />
                    <span>Previous</span>
                  </Button>

                  <span className="text-xs text-slate-500">
                    Page <strong>{recomQuery.page ?? 1}</strong> of <strong>{recomTotalPages}</strong>
                  </span>

                  <Button
                    variant="outline"
                    size="sm"
                    disabled={(recomQuery.page ?? 1) >= recomTotalPages}
                    onClick={() => handleRecomPageChange((recomQuery.page ?? 1) + 1)}
                    className="flex items-center gap-1.5"
                  >
                    <span>Next</span>
                    <ChevronRight className="w-4 h-4" />
                  </Button>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* ─────────────────────────────────────────────
          TAB 2: ALL OPPORTUNITIES CONTENT (Catalog Explore)
          ───────────────────────────────────────────── */}
      {activeTab === 'all' && (
        <div className="space-y-5">
          {/* Search & Filter Controls */}
          <JobFilterPanel
            query={searchQuery}
            onQueryChange={handleSearchQueryChange}
            onResetFilters={handleResetSearchFilters}
            totalResults={totalCount}
            isLoading={isLoading}
          />

          {/* Results Header Counter */}
          <div className="flex items-center justify-between text-xs text-slate-500 dark:text-slate-400 px-1">
            <span>
              Showing <strong>{jobs.length}</strong> of <strong>{totalCount}</strong> verified opportunities
            </span>
            {searchQuery.sort_by && (
              <span className="capitalize">
                Sorted by: <strong>{searchQuery.sort_by.replace('_', ' ')}</strong>
              </span>
            )}
          </div>

          {/* Loading Skeleton */}
          {isLoading ? (
            <div className="space-y-3">
              {[1, 2, 3, 4].map((i) => (
                <div
                  key={i}
                  className="p-5 rounded-2xl border border-slate-200/80 dark:border-slate-800 bg-white dark:bg-slate-900 animate-pulse space-y-3"
                >
                  <div className="h-5 bg-slate-200 dark:bg-slate-700 rounded-md w-1/3" />
                  <div className="h-4 bg-slate-100 dark:bg-slate-800 rounded-md w-1/4" />
                  <div className="h-10 bg-slate-100 dark:bg-slate-800 rounded-md w-full" />
                </div>
              ))}
            </div>
          ) : errorMessage ? (
            <Card className="p-8 text-center space-y-4 max-w-xl mx-auto">
              <div className="w-12 h-12 rounded-full bg-rose-100 dark:bg-rose-950/60 text-rose-600 dark:text-rose-400 flex items-center justify-center mx-auto">
                <AlertTriangle className="w-6 h-6" />
              </div>
              <div className="space-y-1">
                <h3 className="text-base font-bold text-slate-900 dark:text-white">
                  Error Loading Catalog
                </h3>
                <p className="text-xs text-slate-500 dark:text-slate-400">{errorMessage}</p>
              </div>
              <Button size="sm" variant="outline" onClick={() => fetchJobs(searchQuery)}>
                Retry
              </Button>
            </Card>
          ) : isDatasetEmpty ? (
            <EmptyState
              icon={<Database className="w-8 h-8 text-slate-400" />}
              title="Job Catalog is Currently Empty"
              description="No job listings have been ingested into CoachPath yet. You can import an official job description directly to analyze skill requirements and track market matches."
              actionLabel="Import Your First Job"
              onAction={() => setShowImportModal(true)}
            />
          ) : jobs.length === 0 ? (
            <EmptyState
              icon={<Search className="w-8 h-8 text-slate-400" />}
              title="No Jobs Match Your Filters"
              description="Try adjusting your keywords, role selection, work modality, or clearing salary filters to discover more open positions."
              actionLabel="Reset Search Filters"
              onAction={handleResetSearchFilters}
            />
          ) : (
            <div className="space-y-3.5">
              {jobs.map((job) => (
                <JobCard
                  key={job.id}
                  job={job}
                  onSelect={(selected) => setSelectedJob(selected)}
                />
              ))}

              {/* Catalog Pagination Controls */}
              {totalPages > 1 && (
                <div className="flex items-center justify-between pt-6 border-t border-slate-200 dark:border-slate-800">
                  <Button
                    variant="outline"
                    size="sm"
                    disabled={(searchQuery.page ?? 1) <= 1}
                    onClick={() => handleAllJobsPageChange((searchQuery.page ?? 1) - 1)}
                    className="flex items-center gap-1.5"
                  >
                    <ChevronLeft className="w-4 h-4" />
                    <span>Previous</span>
                  </Button>

                  <span className="text-xs text-slate-500">
                    Page <strong>{searchQuery.page ?? 1}</strong> of <strong>{totalPages}</strong>
                  </span>

                  <Button
                    variant="outline"
                    size="sm"
                    disabled={(searchQuery.page ?? 1) >= totalPages}
                    onClick={() => handleAllJobsPageChange((searchQuery.page ?? 1) + 1)}
                    className="flex items-center gap-1.5"
                  >
                    <span>Next</span>
                    <ChevronRight className="w-4 h-4" />
                  </Button>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* ─────────────────────────────────────────────
          MODALS & DRAWERS
          ───────────────────────────────────────────── */}
      {/* 1. Job Detail Modal */}
      <JobDetailModal
        job={selectedJob}
        isOpen={Boolean(selectedJob)}
        onClose={() => setSelectedJob(null)}
        onOpenMatchDrawer={(j, m) => {
          setSelectedMatchJob(j);
          setSelectedMatch(m || null);
          setShowMatchDrawer(true);
        }}
      />

      {/* 2. Match Explainability Drawer */}
      <JobMatchDrawer
        job={selectedMatchJob}
        match={selectedMatch}
        isOpen={showMatchDrawer}
        onClose={() => {
          setShowMatchDrawer(false);
          setSelectedMatchJob(null);
          setSelectedMatch(null);
        }}
        onRecalculateSuccess={handleRecalculateSuccess}
        onViewFullJob={(j) => {
          setShowMatchDrawer(false);
          setSelectedJob(j);
        }}
      />

      {/* 3. Manual Job Import Modal */}
      <ManualJobImportModal
        isOpen={showImportModal}
        onClose={() => setShowImportModal(false)}
        onSuccess={handleImportSuccess}
      />
    </div>
  );
}
