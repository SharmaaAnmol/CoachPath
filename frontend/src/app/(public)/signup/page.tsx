'use client';

import * as React from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card } from '@/components/ui/card';
import { Alert } from '@/components/ui/alert';
import { Sparkles, ArrowRight, ShieldCheck, Check, AlertCircle } from 'lucide-react';
import { TargetRole } from '@/types';
import { useAuth } from '@/hooks/use-auth';
import { ApiClientError } from '@/lib/api-client';
import { slideUp } from '@/lib/motion';

export default function SignupPage() {
  const router = useRouter();
  const { register, login, isAuthenticated, isLoading: isAuthLoading } = useAuth();

  const [name, setName] = React.useState('');
  const [email, setEmail] = React.useState('');
  const [password, setPassword] = React.useState('');
  const [persona, setPersona] = React.useState<'student' | 'grad' | 'early_pro'>('grad');
  const [targetRole, setTargetRole] = React.useState<TargetRole>('Full-Stack Engineer');

  const [isSubmitting, setIsSubmitting] = React.useState(false);
  const [submissionStep, setSubmissionStep] = React.useState<'idle' | 'registering' | 'signing_in'>('idle');
  const [errorMessage, setErrorMessage] = React.useState<React.ReactNode | null>(null);

  const roles: TargetRole[] = [
    'Full-Stack Engineer',
    'Frontend Engineer',
    'Backend Engineer',
    'DevOps / Platform Engineer',
    'Data Engineer',
    'Machine Learning Engineer',
    'Mobile Engineer',
  ];

  // If already authenticated, redirect to workspace
  React.useEffect(() => {
    if (!isAuthLoading && isAuthenticated) {
      router.replace('/dashboard');
    }
  }, [isAuthenticated, isAuthLoading, router]);

  // Client-side password rules validation
  const passwordChecks = React.useMemo(() => {
    return {
      length: password.length >= 8,
      upper: /[A-Z]/.test(password),
      lower: /[a-z]/.test(password),
      digit: /[0-9]/.test(password),
      special: /[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]/.test(password),
    };
  }, [password]);

  const isPasswordValid = Object.values(passwordChecks).every(Boolean);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage(null);

    const trimmedName = name.trim();
    const trimmedEmail = email.trim();

    if (!trimmedName) {
      setErrorMessage('Please enter your full name.');
      return;
    }

    if (!trimmedEmail) {
      setErrorMessage('Please enter a valid email address.');
      return;
    }

    if (!isPasswordValid) {
      setErrorMessage(
        'Password must be at least 8 characters and include uppercase, lowercase, numbers, and special characters.'
      );
      return;
    }

    setIsSubmitting(true);
    setSubmissionStep('registering');
    try {
      // 1. Register candidate account
      await register({
        full_name: trimmedName,
        email: trimmedEmail,
        password,
      });

      // 2. Establish immediate authenticated session
      setSubmissionStep('signing_in');
      try {
        await login({
          email: trimmedEmail,
          password,
        });
        router.push('/onboarding');
      } catch {
        // Fallback: If immediate login had an issue, route to login screen with success banner
        router.push(`/login?registered=true&email=${encodeURIComponent(trimmedEmail)}`);
      }
    } catch (err: unknown) {
      if (err instanceof ApiClientError) {
        if (err.status === 409) {
          setErrorMessage(
            <span>
              An account with this email address already exists.{' '}
              <Link href={`/login?email=${encodeURIComponent(trimmedEmail)}`} className="underline font-bold text-rose-700 dark:text-rose-300">
                Sign in here &rarr;
              </Link>
            </span>
          );
        } else if (err.status === 504 || err.status === 502) {
          setErrorMessage(
            <span>
              The staging server was waking up from sleep (cold start). Your account may have been created.{' '}
              <Link href={`/login?email=${encodeURIComponent(trimmedEmail)}`} className="underline font-bold text-rose-700 dark:text-rose-300">
                Click here to sign in
              </Link>{' '}
              or submit again.
            </span>
          );
        } else if (err.status === 422) {
          const detailMsg =
            err.details && err.details.length > 0
              ? err.details.map((d) => d.issue).join(' ')
              : err.message;
          setErrorMessage(detailMsg || 'Invalid registration details provided.');
        } else if (err.code === 'NETWORK_ERROR' || err.status === 0) {
          setErrorMessage(
            'Unable to connect to CoachPath backend server. Please wait 10 seconds while the cloud instance spins up and try again.'
          );
        } else {
          setErrorMessage(err.message || 'Registration could not be completed. Please try again.');
        }
      } else {
        setErrorMessage('An unexpected error occurred during account creation.');
      }
    } finally {
      setIsSubmitting(false);
      setSubmissionStep('idle');
    }
  };

  return (
    <div className="min-h-[85vh] flex items-center justify-center px-4 py-12 relative overflow-hidden bg-grid-subtle">
      {/* Ambient background glow */}
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 rounded-full bg-brand-500/10 blur-3xl pointer-events-none" />

      <motion.div
        initial="hidden"
        animate="visible"
        variants={slideUp}
        className="w-full max-w-lg space-y-6 relative z-10"
      >
        {/* Brand Header */}
        <div className="text-center space-y-2">
          <div className="inline-flex h-12 w-12 rounded-2xl bg-gradient-to-tr from-brand-600 to-purple-500 items-center justify-center text-white shadow-glow mx-auto mb-2">
            <Sparkles className="h-6 w-6" />
          </div>
          <h2 className="text-2xl font-bold tracking-tight text-slate-900 dark:text-white">
            Create Your Career Intelligence Profile
          </h2>
          <p className="text-xs text-slate-500 dark:text-slate-400">
            Validate your engineering skills, eliminate missing gaps, and match with tech roles.
          </p>
        </div>

        {/* Signup Form Card */}
        <Card className="p-6 sm:p-8 space-y-5 border-slate-200/90 shadow-elevated rounded-2xl">
          {errorMessage && (
            <Alert variant="destructive" title="Registration Error">
              {errorMessage}
            </Alert>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <Input
              label="Full Name"
              type="text"
              required
              disabled={isSubmitting}
              value={name}
              onChange={(e) => {
                setName(e.target.value);
                if (errorMessage) setErrorMessage(null);
              }}
              placeholder="e.g. Aarav Mehta"
              autoComplete="name"
            />

            <Input
              label="Email Address"
              type="email"
              required
              disabled={isSubmitting}
              value={email}
              onChange={(e) => {
                setEmail(e.target.value);
                if (errorMessage) setErrorMessage(null);
              }}
              placeholder="you@domain.com"
              autoComplete="email"
            />

            <div className="space-y-1.5">
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-700 dark:text-slate-300">
                Create Password
              </label>
              <input
                type="password"
                required
                disabled={isSubmitting}
                value={password}
                onChange={(e) => {
                  setPassword(e.target.value);
                  if (errorMessage) setErrorMessage(null);
                }}
                placeholder="At least 8 characters"
                autoComplete="new-password"
                className="flex h-10 w-full rounded-xl border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-500/20 disabled:bg-slate-100 disabled:opacity-60 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-100 dark:disabled:bg-slate-800 transition-colors"
              />

              {/* Password Complexity Checklist */}
              {password.length > 0 && (
                <div className="p-3 bg-slate-50 dark:bg-slate-900/50 rounded-xl border border-slate-200 dark:border-slate-800 space-y-1 text-[11px]">
                  <p className="font-semibold text-slate-600 dark:text-slate-400">Password requirements:</p>
                  <div className="grid grid-cols-2 gap-1 text-slate-500">
                    <span className={passwordChecks.length ? 'text-emerald-600 font-medium' : ''}>
                      {passwordChecks.length ? '✓' : '•'} 8+ characters
                    </span>
                    <span className={passwordChecks.upper ? 'text-emerald-600 font-medium' : ''}>
                      {passwordChecks.upper ? '✓' : '•'} Uppercase letter
                    </span>
                    <span className={passwordChecks.lower ? 'text-emerald-600 font-medium' : ''}>
                      {passwordChecks.lower ? '✓' : '•'} Lowercase letter
                    </span>
                    <span className={passwordChecks.digit ? 'text-emerald-600 font-medium' : ''}>
                      {passwordChecks.digit ? '✓' : '•'} Number
                    </span>
                    <span className={passwordChecks.special ? 'text-emerald-600 font-medium' : ''}>
                      {passwordChecks.special ? '✓' : '•'} Special character
                    </span>
                  </div>
                </div>
              )}
            </div>

            {/* Persona Selector */}
            <div className="space-y-1.5">
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-700 dark:text-slate-300">
                Current Career Stage
              </label>
              <div className="grid grid-cols-3 gap-2 text-xs">
                <button
                  type="button"
                  disabled={isSubmitting}
                  onClick={() => setPersona('student')}
                  className={`p-2.5 rounded-xl border text-center transition-all ${
                    persona === 'student'
                      ? 'border-brand-600 bg-brand-50 text-brand-700 font-semibold dark:bg-brand-950 dark:text-brand-300 shadow-sm'
                      : 'border-slate-200 text-slate-600 hover:bg-slate-50 dark:border-slate-700 dark:text-slate-300'
                  }`}
                >
                  Student
                </button>
                <button
                  type="button"
                  disabled={isSubmitting}
                  onClick={() => setPersona('grad')}
                  className={`p-2.5 rounded-xl border text-center transition-all ${
                    persona === 'grad'
                      ? 'border-brand-600 bg-brand-50 text-brand-700 font-semibold dark:bg-brand-950 dark:text-brand-300 shadow-sm'
                      : 'border-slate-200 text-slate-600 hover:bg-slate-50 dark:border-slate-700 dark:text-slate-300'
                  }`}
                >
                  Recent Grad
                </button>
                <button
                  type="button"
                  disabled={isSubmitting}
                  onClick={() => setPersona('early_pro')}
                  className={`p-2.5 rounded-xl border text-center transition-all ${
                    persona === 'early_pro'
                      ? 'border-brand-600 bg-brand-50 text-brand-700 font-semibold dark:bg-brand-950 dark:text-brand-300 shadow-sm'
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
                disabled={isSubmitting}
                onChange={(e) => setTargetRole(e.target.value as TargetRole)}
                className="flex h-10 w-full rounded-xl border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-500/20 disabled:bg-slate-100 disabled:opacity-60 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-100 dark:disabled:bg-slate-800 transition-colors"
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
                By continuing, you agree to CoachPath&apos;s Responsible AI Policy and human approval safeguards. We never contact recruiters without your explicit confirmation.
              </span>
            </div>

            <Button
              type="submit"
              variant="primary"
              className="w-full mt-2"
              isLoading={isSubmitting}
              disabled={isSubmitting}
            >
              {submissionStep === 'registering'
                ? 'Creating Account & Graph...'
                : submissionStep === 'signing_in'
                ? 'Authenticating Session...'
                : 'Initialize Profile Graph'}
              {submissionStep === 'idle' && <ArrowRight className="w-4 h-4 ml-1.5" />}
            </Button>
          </form>

          <div className="pt-4 border-t border-slate-100 dark:border-slate-800 text-center text-xs text-slate-500">
            Already have an account?{' '}
            <Link href="/login" className="font-semibold text-brand-600 hover:underline">
              Sign In
            </Link>
          </div>
        </Card>
      </motion.div>
    </div>
  );
}
