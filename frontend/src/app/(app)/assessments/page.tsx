'use client';

import * as React from 'react';
import { mockAssessments } from '@/lib/mock/data';
import { Assessment } from '@/types';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { AssessmentCard } from '@/components/ui/assessment-card';
import { Tabs } from '@/components/ui/tabs';
import { Modal } from '@/components/ui/modal';
import {
  ClipboardCheck,
  CheckCircle2,
  Clock,
  Award,
  Sparkles,
  HelpCircle,
  Play,
  RotateCcw,
} from 'lucide-react';

export default function AssessmentsPage() {
  const [filter, setFilter] = React.useState('all');
  const [activeModalAssessment, setActiveModalAssessment] = React.useState<Assessment | null>(null);
  const [selectedOption, setSelectedOption] = React.useState<number | null>(null);
  const [hasSubmittedAnswer, setHasSubmittedAnswer] = React.useState(false);

  const completed = mockAssessments.filter((a) => a.status === 'completed');
  const available = mockAssessments.filter((a) => a.status === 'available');

  const filteredList = mockAssessments.filter((a) => {
    if (filter === 'completed') return a.status === 'completed';
    if (filter === 'available') return a.status === 'available';
    return true;
  });

  const filterTabs = [
    { id: 'all', label: 'All Diagnostic Tests', badge: mockAssessments.length },
    { id: 'available', label: 'Available to Take', badge: available.length },
    { id: 'completed', label: 'Completed & Calibrated', badge: completed.length },
  ];

  const handleStart = (asmt: Assessment) => {
    setActiveModalAssessment(asmt);
    setSelectedOption(null);
    setHasSubmittedAnswer(false);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-slate-900 dark:text-white">
            Diagnostic Skill Assessments
          </h2>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
            Deterministic evaluation calibrated to calibrate self-reported confidence into verified market credentials.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Badge variant="verified" size="md">
            <CheckCircle2 className="w-3.5 h-3.5 mr-1" /> 2 Skills Calibrated
          </Badge>
        </div>
      </div>

      {/* Tabs */}
      <Tabs tabs={filterTabs} activeTab={filter} onChange={setFilter} />

      {/* Assessments Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredList.map((asmt) => (
          <AssessmentCard
            key={asmt.id}
            assessment={asmt}
            onStart={handleStart}
          />
        ))}
      </div>

      {/* Interactive Assessment Modal Runner */}
      {activeModalAssessment && (
        <Modal
          isOpen={!!activeModalAssessment}
          onClose={() => setActiveModalAssessment(null)}
          title={`Diagnostic Runner: ${activeModalAssessment.title}`}
          description={`Skill: ${activeModalAssessment.skillName} • Difficulty: ${activeModalAssessment.difficulty} • Question 1 of ${activeModalAssessment.questionCount}`}
          maxWidth="2xl"
          footer={
            <div className="flex items-center justify-between w-full">
              <span className="text-xs text-slate-400">
                Deterministic autograding engine &bull; No LLM hallucination
              </span>
              <div className="flex items-center gap-2">
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => setActiveModalAssessment(null)}
                >
                  Exit Test
                </Button>
                {!hasSubmittedAnswer ? (
                  <Button
                    size="sm"
                    variant="primary"
                    disabled={selectedOption === null}
                    onClick={() => setHasSubmittedAnswer(true)}
                  >
                    Submit Answer
                  </Button>
                ) : (
                  <Button
                    size="sm"
                    variant="primary"
                    onClick={() => {
                      alert('Diagnostic completed! Calibrated score recorded to PostgreSQL profile.');
                      setActiveModalAssessment(null);
                    }}
                  >
                    Complete Assessment
                  </Button>
                )}
              </div>
            </div>
          }
        >
          <div className="space-y-4 text-xs sm:text-sm">
            {/* Question Prompt */}
            <div className="p-4 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 space-y-3">
              <p className="font-semibold text-slate-900 dark:text-white leading-relaxed">
                When scaling a high-throughput API with distributed caching in Redis, which technique best prevents cache stampedes (dog-piling effect) during the simultaneous expiration of hot keys?
              </p>

              {/* Code Snippet Box */}
              <div className="rounded-lg bg-slate-900 text-slate-100 p-3 font-mono text-xs overflow-x-auto">
                <pre>{`// Scenario: High-traffic product endpoint (50,000 req/sec)
const productKey = "product:sku_90412";
const cachedProduct = await redis.get(productKey);

if (!cachedProduct) {
  // Vulnerability: 5,000 concurrent requests query the database at once!
  const product = await db.query("SELECT * FROM products WHERE id = $1", [id]);
  await redis.set(productKey, JSON.stringify(product), "EX", 300);
}`}</pre>
              </div>
            </div>

            {/* Answer Options */}
            <div className="space-y-2">
              <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                Select the architecturally sound mitigation:
              </div>

              {[
                'Deploy Redis Cluster with 10 replicas and disable TTL expiration entirely.',
                'Implement distributed mutex locking (Redlock) or probabilistic early expiration (XFetch algorithm).',
                'Increase PostgreSQL connection pool size to 10,000 concurrent sockets.',
                'Switch the caching data layer from Redis to client-side localStorage in React.',
              ].map((opt, idx) => (
                <button
                  key={idx}
                  type="button"
                  disabled={hasSubmittedAnswer}
                  onClick={() => setSelectedOption(idx)}
                  className={`w-full p-3 rounded-xl border text-left text-xs transition-all flex items-start gap-3 ${
                    selectedOption === idx
                      ? hasSubmittedAnswer
                        ? idx === 1
                          ? 'border-emerald-500 bg-emerald-50 text-emerald-900 dark:bg-emerald-950/40 dark:text-emerald-200 font-semibold'
                          : 'border-rose-500 bg-rose-50 text-rose-900 dark:bg-rose-950/40 dark:text-rose-200'
                        : 'border-brand-600 bg-brand-50 text-brand-900 dark:bg-brand-950/40 dark:text-brand-200 font-medium'
                      : 'border-slate-200 hover:bg-slate-50 dark:border-slate-800 dark:hover:bg-slate-800/50 text-slate-700 dark:text-slate-300'
                  }`}
                >
                  <span className="font-mono font-bold">{String.fromCharCode(65 + idx)}.</span>
                  <span className="flex-1">{opt}</span>
                </button>
              ))}
            </div>

            {/* Explanation Breakdown after submission */}
            {hasSubmittedAnswer && (
              <div className="p-4 rounded-xl bg-emerald-50/80 dark:bg-emerald-950/40 border border-emerald-300 dark:border-emerald-800 space-y-2 animate-in fade-in">
                <div className="flex items-center gap-2 font-bold text-emerald-800 dark:text-emerald-300 text-xs">
                  <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                  <span>Correct! Option B is the industry standard pattern.</span>
                </div>
                <p className="text-xs text-slate-600 dark:text-slate-300 leading-relaxed">
                  Distributed mutex locking guarantees only one worker repopulates the cache while others wait. Alternatively, probabilistic early expiration refreshes the cache asynchronously before hard TTL expiration.
                </p>
              </div>
            )}
          </div>
        </Modal>
      )}
    </div>
  );
}
