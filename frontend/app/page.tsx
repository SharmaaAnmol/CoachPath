'use client';

import React, { useState, useEffect } from 'react';
import { fetchReadiness, fetchRecommendedJobs, fetchRoadmap } from '@/lib/api';
import { ReadinessScore, Job, RoadmapItem } from '@/lib/types';

export default function HomePage() {
  const [readiness, setReadiness] = useState<ReadinessScore | null>(null);
  const [jobs, setJobs] = useState<Job[]>([]);
  const [roadmapItems, setRoadmapItems] = useState<RoadmapItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const [rData, jData, rmData] = await Promise.all([
          fetchReadiness(),
          fetchRecommendedJobs(),
          fetchRoadmap(),
        ]);
        setReadiness(rData);
        setJobs(jData);
        setRoadmapItems(rmData.items);
      } catch (err) {
        console.error('Error fetching data:', err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  return (
    <div className="min-h-screen flex flex-col bg-[#0B1120] text-slate-100">
      <header className="border-b border-brand-border px-8 py-4 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-brand-purple to-brand-green flex items-center justify-center font-bold text-white">
            CP
          </div>
          <div>
            <h1 className="font-bold text-lg leading-none">CoachPath</h1>
            <span className="mono-label text-[10px] text-brand-purple">Bharat Hackathon 2.0 Edition</span>
          </div>
        </div>
        <div className="flex items-center space-x-2">
          <span className="text-xs text-brand-muted">Demo Persona:</span>
          <span className="font-medium text-xs text-white">Aarav Sharma (ML Engineer)</span>
        </div>
      </header>

      <main className="flex-1 max-w-7xl w-full mx-auto p-6 space-y-6">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Readiness Index */}
          <div className="bg-brand-card border border-brand-border rounded-xl p-6 flex flex-col justify-between">
            <div>
              <span className="mono-label text-brand-muted block">CAREER READINESS INDEX</span>
              <div className="my-6 text-center">
                <span className="text-5xl font-black text-brand-green">
                  {readiness ? `${readiness.overall}%` : '70%'}
                </span>
                <span className="mono-label text-[10px] text-brand-muted block mt-1">WEIGHTED BENCHMARK</span>
              </div>
            </div>
            <div className="space-y-2 text-xs">
              <div className="flex justify-between text-brand-muted">
                <span>Technical Skills (25%)</span>
                <span className="text-white">{readiness?.components.technical || 68}%</span>
              </div>
              <div className="flex justify-between text-brand-muted">
                <span>DSA / Problem Solving (15%)</span>
                <span className="text-white">{readiness?.components.dsa || 65}%</span>
              </div>
              <div className="flex justify-between text-brand-muted">
                <span>Production Projects (15%)</span>
                <span className="text-white">{readiness?.components.projects || 90}%</span>
              </div>
            </div>
          </div>

          {/* Biggest Lever Card */}
          <div className="lg:col-span-2 bg-gradient-to-r from-brand-card to-[#1A263D] border border-brand-purple/40 rounded-xl p-6 flex flex-col justify-between">
            <div>
              <span className="mono-label text-brand-purple font-semibold block mb-2">BIGGEST LEVER INSIGHT</span>
              <h2 className="text-xl font-bold text-white mb-2">
                {readiness?.biggest_lever.label || 'Core Technical & SQL Mastery'}
              </h2>
              <p className="text-xs text-brand-muted leading-relaxed mb-4">
                {readiness?.biggest_lever.recommendation || 'Focusing on Core Technical Skills can boost your readiness from 70% to 75%!'}
              </p>
            </div>
            <div className="flex gap-3">
              <a href="/web/index.html" className="px-4 py-2 bg-brand-purple text-white text-xs font-semibold rounded-lg hover:bg-brand-purple/90 transition">
                Open Full Interactive Workspace →
              </a>
            </div>
          </div>
        </div>

        {/* Top Matches Preview */}
        <div className="bg-brand-card border border-brand-border rounded-xl p-6">
          <span className="mono-label text-brand-muted block mb-4">TOP MATCHED ROLES</span>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {jobs.slice(0, 2).map((job) => (
              <div key={job.id} className="p-4 bg-brand-dark rounded-xl border border-brand-border space-y-2">
                <div className="flex justify-between items-start">
                  <div>
                    <h3 className="font-bold text-sm text-white">{job.title}</h3>
                    <p className="text-xs text-brand-muted">{job.company} · {job.location}</p>
                  </div>
                  <span className="px-2 py-0.5 rounded bg-brand-green/20 text-brand-green font-mono text-xs font-bold">
                    {job.match_score || 92}%
                  </span>
                </div>
                <p className="text-[11px] text-brand-muted/90">{job.match?.reason}</p>
              </div>
            ))}
          </div>
        </div>
      </main>
    </div>
  );
}
