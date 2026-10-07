'use client';

import * as React from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card } from '@/components/ui/card';
import { Sparkles, ArrowRight, ShieldCheck } from 'lucide-react';
import { TargetRole } from '@/types';

export default function SignupPage() {
  const router = useRouter();
  const [name, setName] = React.useState('');
  const [email, setEmail] = React.useState('');
  const [password, setPassword] = React.useState('');
  const [persona, setPersona] = React.useState<'student' | 'grad' | 'early_pro'>('grad');
  const [targetRole, setTargetRole] = React.useState<TargetRole>('Full-Stack Engineer');
  const [isLoading, setIsLoading] = React.useState(false);

  const roles: TargetRole[] = [
    'Full-Stack Engineer',
    'Frontend Engineer',
    'Backend Engineer',
    'DevOps / Platform Engineer',
    'Data Engineer',
    'Machine Learning Engineer',
    'Mobile Engineer',
  ];

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setTimeout(() => {
      router.push('/dashboard');
    }, 600);
  };

  return (
    <div className="min-h-[85vh] flex items-center justify-center px-4 py-12">
      <div className="w-full max-w-lg space-y-6">
        {/* Brand Header */}
        <div className="text-center space-y-2">
          <div className="inline-flex h-12 w-12 rounded-2xl bg-gradient-to-tr from-brand-600 to-purple-500 items-center justify-center text-white shadow-md mx-auto mb-2">
            <Sparkles className="h-6 w-6" />
          </div>
          <h2 className="text-2xl font-bold tracking-tight text-slate-900 dark:text-white">
            Create Your Career Intelligence Profile
          </h2>
          <p className="text-xs text-slate-500 dark:text-slate-400">
            Join CoachPath to validate your skills, discover missing gaps, and match with top tech roles.
          </p>
        </div>

        {/* Signup Form Card */}
        <Card className="p-6 sm:p-8 space-y-5 border-slate-200/90 shadow-elevated">
          <form onSubmit={handleSubmit} className="space-y-4">
            <Input
              label="Full Name"
              type="text"
              required
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g. Aarav Mehta"
            />

            <Input
              label="Email Address"
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@university.edu or you@work.com"
            />

            <Input
              label="Create Password"
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="At least 8 characters"
            />

            {/* Persona Selector */}
            <div className="space-y-1.5">
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-700 dark:text-slate-300">
                Current Career Stage
              </label>
              <div className="grid grid-cols-3 gap-2 text-xs">
                <button
                  type="button"
                  onClick={() => setPersona('student')}
                  className={`p-2.5 rounded-lg border text-center transition-all ${
                    persona === 'student'
                      ? 'border-brand-600 bg-brand-50 text-brand-700 font-semibold dark:bg-brand-950 dark:text-brand-300'
                      : 'border-slate-200 text-slate-600 hover:bg-slate-50 dark:border-slate-700 dark:text-slate-300'
                  }`}
                >
                  Student
                </button>
                <button
                  type="button"
                  onClick={() => setPersona('grad')}
                  className={`p-2.5 rounded-lg border text-center transition-all ${
                    persona === 'grad'
                      ? 'border-brand-600 bg-brand-50 text-brand-700 font-semibold dark:bg-brand-950 dark:text-brand-300'
                      : 'border-slate-200 text-slate-600 hover:bg-slate-50 dark:border-slate-700 dark:text-slate-300'
                  }`}
                >
                  Recent Grad
                </button>
                <button
                  type="button"
                  onClick={() => setPersona('early_pro')}
                  className={`p-2.5 rounded-lg border text-center transition-all ${
                    persona === 'early_pro'
                      ? 'border-brand-600 bg-brand-50 text-brand-700 font-semibold dark:bg-brand-950 dark:text-brand-300'
                      : 'border-slate-200 text-slate-600 hover:bg-slate-50 dark:border-slate-700 dark:text-slate-300'
                  }`}
                >
                  Early Pro (1-3 YOE)
                </button>
              </div>
            </div>

            {/* Target Role Selector */}
            <div className="space-y-1.5">
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-700 dark:text-slate-300">
                Primary Target Role
              </label>
              <select
                value={targetRole}
                onChange={(e) => setTargetRole(e.target.value as TargetRole)}
                className="flex h-10 w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-500/20 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-100"
              >
                {roles.map((role) => (
                  <option key={role} value={role}>
                    {role}
                  </option>
                ))}
              </select>
            </div>

            <div className="flex items-start gap-2 pt-1 text-xs text-slate-500 dark:text-slate-400">
              <ShieldCheck className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
              <span>
                By continuing, you agree to CoachPath&apos;s Responsible AI Policy and human approval safeguards. We never spam recruiters on your behalf.
              </span>
            </div>

            <Button
              type="submit"
              variant="primary"
              className="w-full mt-2"
              isLoading={isLoading}
            >
              Initialize Profile Graph <ArrowRight className="w-4 h-4 ml-1.5" />
            </Button>
          </form>

          <div className="pt-4 border-t border-slate-100 dark:border-slate-800 text-center text-xs text-slate-500">
            Already have an account?{' '}
            <Link href="/login" className="font-semibold text-brand-600 hover:underline">
              Sign In
            </Link>
          </div>
        </Card>
      </div>
    </div>
  );
}
