'use client';

import * as React from 'react';
import { useRouter } from 'next/navigation';
import { mockJobs } from '@/lib/mock/data';
import { JobListing } from '@/types';
import { JobCard } from '@/components/ui/job-card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card } from '@/components/ui/card';
import {
  Briefcase,
  Sparkles,
  Filter,
  Search,
  SlidersHorizontal,
  Building2,
  MapPin,
  DollarSign,
} from 'lucide-react';

export default function JobsPage() {
  const router = useRouter();
  const [selectedRemote, setSelectedRemote] = React.useState('All');
  const [minMatch, setMinMatch] = React.useState<number>(80);
  const [searchQuery, setSearchQuery] = React.useState('');

  const filteredJobs = mockJobs.filter((job) => {
    const matchesRemote = selectedRemote === 'All' || job.remoteType === selectedRemote;
    const matchesScore = job.matchScore >= minMatch;
    const matchesSearch =
      job.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      job.company.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesRemote && matchesScore && matchesSearch;
  });

  const handleApplyOrOptimize = (job: JobListing) => {
    router.push(`/resume?targetJob=${encodeURIComponent(job.title)}&company=${encodeURIComponent(job.company)}`);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-slate-900 dark:text-white">
            Semantic Job Discovery & Vector Matching
          </h2>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
            Jobs ranked via 1536-dimensional cosine distance between your verified skills and role job requirements.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Badge variant="intelligence" size="md">
            <Sparkles className="w-3.5 h-3.5 mr-1" /> pgvector Active
          </Badge>
        </div>
      </div>

      {/* Filter & Search Bar */}
      <Card className="p-4 space-y-4">
        <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-3">
          <div className="flex-1 relative">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
            <input
              type="text"
              placeholder="Search by job title or company (e.g. Stripe, Linear)..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-9 pr-4 py-2 text-xs rounded-lg border border-slate-300 bg-white text-slate-900 focus:outline-none focus:ring-2 focus:ring-brand-500"
            />
          </div>

          {/* Remote Filter */}
          <div className="flex items-center gap-1.5 overflow-x-auto text-xs">
            {['All', 'Remote', 'Hybrid'].map((type) => (
              <button
                key={type}
                onClick={() => setSelectedRemote(type)}
                className={`px-3 py-1.5 rounded-lg font-medium transition-all ${
                  selectedRemote === type
                    ? 'bg-slate-900 text-white dark:bg-white dark:text-slate-900 font-semibold'
                    : 'bg-slate-100 text-slate-600 hover:bg-slate-200 dark:bg-slate-800 dark:text-slate-300'
                }`}
              >
                {type}
              </button>
            ))}
          </div>
        </div>

        <div className="flex items-center justify-between pt-2 border-t border-slate-100 dark:border-slate-800 text-xs">
          <div className="flex items-center gap-2 text-slate-500">
            <span>Minimum Semantic Fit:</span>
            <div className="flex gap-1.5">
              {[70, 80, 90].map((score) => (
                <button
                  key={score}
                  onClick={() => setMinMatch(score)}
                  className={`px-2.5 py-0.5 rounded text-[11px] font-mono font-bold ${
                    minMatch === score
                      ? 'bg-brand-100 text-brand-700 dark:bg-brand-950 dark:text-brand-300'
                      : 'text-slate-400 hover:text-slate-700'
                  }`}
                >
                  {score}%+
                </button>
              ))}
            </div>
          </div>

          <span className="text-slate-400">
            Showing <strong>{filteredJobs.length}</strong> matching positions
          </span>
        </div>
      </Card>

      {/* Jobs List */}
      <div className="space-y-4">
        {filteredJobs.map((job) => (
          <JobCard
            key={job.id}
            job={job}
            onApplyOrOptimize={handleApplyOrOptimize}
          />
        ))}

        {filteredJobs.length === 0 && (
          <Card className="p-8 text-center text-slate-500 space-y-2">
            <p className="font-semibold">No job postings found matching your current filter criteria.</p>
            <p className="text-xs text-slate-400">Try lowering your minimum match score or clearing search terms.</p>
          </Card>
        )}
      </div>
    </div>
  );
}
