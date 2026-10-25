'use client';

import * as React from 'react';
import Link from 'next/link';
import { useRouter, useSearchParams } from 'next/navigation';
import { motion } from 'framer-motion';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card } from '@/components/ui/card';
import { Alert } from '@/components/ui/alert';
import { Sparkles, ArrowRight, ShieldCheck } from 'lucide-react';
import { useAuth } from '@/hooks/use-auth';
import { ApiClientError } from '@/lib/api-client';
import { slideUp } from '@/lib/motion';

function LoginForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const redirectUrl = searchParams.get('redirect') || '/dashboard';
  const wasRegistered = searchParams.get('registered') === 'true';
  const prefilledEmail = searchParams.get('email') || '';

  const { login, isAuthenticated, isLoading: isAuthLoading } = useAuth();

  const [email, setEmail] = React.useState(prefilledEmail || 'aarav.mehta@example.com');
  const [password, setPassword] = React.useState('Password123!');
  const [isSubmitting, setIsSubmitting] = React.useState(false);
  const [errorMessage, setErrorMessage] = React.useState<string | null>(null);
  const [successMessage, setSuccessMessage] = React.useState<string | null>(
    wasRegistered ? 'Account created successfully! Please sign in with your credentials.' : null
  );

  // If already authenticated, redirect to workspace
  React.useEffect(() => {
    if (!isAuthLoading && isAuthenticated) {
      router.replace(redirectUrl);
    }
  }, [isAuthenticated, isAuthLoading, router, redirectUrl]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage(null);

    const trimmedEmail = email.trim();
    if (!trimmedEmail) {
      setErrorMessage('Please enter your email address.');
      return;
    }
    if (!password) {
      setErrorMessage('Please enter your password.');
      return;
    }

    setIsSubmitting(true);
    try {
      await login({
        email: trimmedEmail,
        password,
      });
      router.push(redirectUrl);
    } catch (err: unknown) {
      if (err instanceof ApiClientError) {
        if (err.status === 401) {
          setErrorMessage('Invalid email or password. Please verify your credentials.');
        } else if (err.status === 429) {
          setErrorMessage('Too many failed login attempts. Please wait 15 minutes before trying again.');
        } else if (err.status === 403) {
          setErrorMessage('This account has been suspended. Please contact support.');
        } else if (err.code === 'NETWORK_ERROR' || err.status === 0) {
          setErrorMessage('Unable to connect to CoachPath backend. Please verify the service is running.');
        } else {
          setErrorMessage(err.message || 'An unexpected error occurred. Please try again.');
        }
      } else {
        setErrorMessage('Unable to complete sign-in. Please try again later.');
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDemoFill = () => {
    setEmail('aarav.mehta@example.com');
    setPassword('Password123!');
    setErrorMessage(null);
  };

  return (
    <div className="min-h-[85vh] flex items-center justify-center px-4 py-12 relative overflow-hidden bg-grid-subtle">
      {/* Ambient background glow */}
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 rounded-full bg-brand-500/10 blur-3xl pointer-events-none" />

      <motion.div
        initial="hidden"
        animate="visible"
        variants={slideUp}
        className="w-full max-w-md space-y-6 relative z-10"
      >
        {/* Brand Header */}
        <div className="text-center space-y-2">
          <div className="inline-flex h-12 w-12 rounded-2xl bg-gradient-to-tr from-brand-600 to-purple-500 items-center justify-center text-white shadow-glow mx-auto mb-2">
            <Sparkles className="h-6 w-6" />
          </div>
          <h2 className="text-2xl font-bold tracking-tight text-slate-900 dark:text-white">
            Welcome Back to CoachPath
          </h2>
          <p className="text-xs text-slate-500 dark:text-slate-400">
            Sign in to access your career profile, skill roadmaps, and job matches.
          </p>
        </div>

        {/* Login Form Card */}
        <Card className="p-6 sm:p-8 space-y-5 border-slate-200/90 shadow-elevated rounded-2xl">
          {/* Registration Success Banner */}
          {successMessage && (
            <Alert variant="success" title="Account Ready">
              {successMessage}
            </Alert>
          )}

          {/* Error Banner */}
          {errorMessage && (
            <Alert variant="destructive" title="Authentication Failed">
              {errorMessage}
            </Alert>
          )}

          {/* Demo Helper Banner */}
          <div className="p-3 rounded-xl bg-purple-50/70 dark:bg-purple-950/40 border border-purple-200 dark:border-purple-800 flex items-center justify-between text-xs">
            <div className="flex items-center gap-2 text-purple-900 dark:text-purple-300">
              <ShieldCheck className="w-4 h-4 text-purple-600 shrink-0" />
              <span>Explore as Demo Candidate</span>
            </div>
            <button
              type="button"
              onClick={handleDemoFill}
              className="text-[11px] font-bold text-brand-600 dark:text-brand-400 hover:underline shrink-0"
            >
              Auto-Fill
            </button>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
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

            <div className="space-y-1">
              <div className="flex justify-between items-center">
                <label className="block text-xs font-semibold uppercase tracking-wider text-slate-700 dark:text-slate-300">
                  Password
                </label>
                <Link
                  href="/login"
                  onClick={(e) => {
                    e.preventDefault();
                    setErrorMessage('Password recovery is available via administrator or support in development.');
                  }}
                  className="text-[11px] text-brand-600 hover:underline"
                >
                  Forgot password?
                </Link>
              </div>
              <input
                type="password"
                required
                disabled={isSubmitting}
                value={password}
                onChange={(e) => {
                  setPassword(e.target.value);
                  if (errorMessage) setErrorMessage(null);
                }}
                autoComplete="current-password"
                className="flex h-10 w-full rounded-xl border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-500/20 disabled:bg-slate-100 disabled:opacity-60 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-100 dark:disabled:bg-slate-800 transition-colors"
              />
            </div>

            <div className="flex items-center text-xs text-slate-600 dark:text-slate-400">
              <input
                type="checkbox"
                id="remember"
                defaultChecked
                disabled={isSubmitting}
                className="rounded border-slate-300 text-brand-600 focus:ring-brand-500 mr-2"
              />
              <label htmlFor="remember">Keep me signed in on this device</label>
            </div>

            <Button
              type="submit"
              variant="primary"
              className="w-full"
              isLoading={isSubmitting}
              disabled={isSubmitting}
            >
              Sign In to Workspace <ArrowRight className="w-4 h-4 ml-1.5" />
            </Button>
          </form>

          <div className="pt-4 border-t border-slate-100 dark:border-slate-800 text-center text-xs text-slate-500">
            Don&apos;t have an account yet?{' '}
            <Link href="/signup" className="font-semibold text-brand-600 hover:underline">
              Create an account
            </Link>
          </div>
        </Card>
      </motion.div>
    </div>
  );
}

export default function LoginPage() {
  return (
    <React.Suspense
      fallback={
        <div className="min-h-[80vh] flex items-center justify-center">
          <div className="w-8 h-8 rounded-full border-2 border-brand-500 border-t-transparent animate-spin" />
        </div>
      }
    >
      <LoginForm />
    </React.Suspense>
  );
}
