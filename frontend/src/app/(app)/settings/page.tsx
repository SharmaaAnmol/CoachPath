'use client';

import * as React from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import {
  Settings,
  Shield,
  Download,
  Trash2,
  Lock,
  CheckCircle2,
  Bell,
  AlertTriangle,
} from 'lucide-react';
import { useAuth } from '@/hooks/use-auth';
import { profileClient } from '@/lib/profile-client';

export default function SettingsPage() {
  const { user, refreshUser } = useAuth();
  const [fullName, setFullName] = React.useState(user?.full_name || '');
  const [isSaving, setIsSaving] = React.useState(false);
  const [savedSuccess, setSavedSuccess] = React.useState(false);
  const [humanApprovalGate, setHumanApprovalGate] = React.useState(true);
  const [emailAlerts, setEmailAlerts] = React.useState(true);

  React.useEffect(() => {
    if (user?.full_name) {
      setFullName(user.full_name);
    }
  }, [user?.full_name]);

  const handleSaveAccount = async () => {
    if (!fullName.trim()) return;
    setIsSaving(true);
    try {
      await profileClient.updatePersonalProfile({ full_name: fullName.trim() });
      await refreshUser();
      setSavedSuccess(true);
      setTimeout(() => setSavedSuccess(false), 3000);
    } catch (err) {
      console.error('Failed to update account name:', err);
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="space-y-6 max-w-4xl">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold text-slate-900 dark:text-white">
          Settings & Privacy Controls
        </h2>
        <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
          Manage your account credentials, AI guardrails, notifications, and data ownership rights.
        </p>
      </div>

      {/* Account Profile Card */}
      <Card className="p-6 space-y-4">
        <h3 className="text-base font-bold text-slate-900 dark:text-white">
          Account Information
        </h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
          <Input
            label="Full Name"
            value={fullName}
            onChange={(e) => setFullName(e.target.value)}
            placeholder="Your Full Name"
          />
          <Input
            label="Email Address"
            value={user?.email || ''}
            disabled
            helperText="Managed via authentication provider"
          />
        </div>
        <div className="pt-2 flex items-center justify-between">
          {savedSuccess ? (
            <span className="text-xs text-emerald-600 font-semibold flex items-center gap-1">
              <CheckCircle2 className="w-3.5 h-3.5" /> Details saved successfully!
            </span>
          ) : (
            <div />
          )}
          <Button
            size="sm"
            variant="primary"
            onClick={handleSaveAccount}
            disabled={isSaving}
          >
            {isSaving ? 'Saving...' : 'Save Account Details'}
          </Button>
        </div>
      </Card>

      {/* Responsible AI & Human Guardrails */}
      <Card className="p-6 space-y-5">
        <div className="flex items-center gap-2">
          <Shield className="w-5 h-5 text-purple-600" />
          <h3 className="text-base font-bold text-slate-900 dark:text-white">
            AI Guardrails & Human-in-the-Loop Policies
          </h3>
        </div>

        <div className="space-y-4 text-xs">
          {/* Toggle 1 */}
          <div className="flex items-center justify-between p-3.5 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200/80 dark:border-slate-700/60">
            <div className="space-y-0.5 max-w-lg">
              <div className="font-bold text-slate-900 dark:text-white">
                Enforce Human Copy-Confirmation on Recruiter Messages
              </div>
              <p className="text-slate-500 dark:text-slate-400">
                Requires manual copy-to-clipboard before sending outreach drafts. Completely prevents bot spam.
              </p>
            </div>
            <input
              type="checkbox"
              checked={humanApprovalGate}
              onChange={(e) => setHumanApprovalGate(e.target.checked)}
              className="h-5 w-5 rounded border-slate-300 text-brand-600 focus:ring-brand-500 cursor-pointer"
            />
          </div>

          {/* Toggle 2 */}
          <div className="flex items-center justify-between p-3.5 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200/80 dark:border-slate-700/60">
            <div className="space-y-0.5 max-w-lg">
              <div className="flex items-center gap-2 font-bold text-slate-900 dark:text-white">
                Two-Pass Anti-Hallucination Resume Auditor
                <Badge variant="verified" size="sm">Mandatory</Badge>
              </div>
              <p className="text-slate-500 dark:text-slate-400">
                Audits all generated resume diffs against verified profile and test evidence. Cannot be disabled.
              </p>
            </div>
            <span className="font-mono text-emerald-600 font-bold text-xs">Locked ON</span>
          </div>

          {/* Toggle 3 */}
          <div className="flex items-center justify-between p-3.5 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200/80 dark:border-slate-700/60">
            <div className="space-y-0.5 max-w-lg">
              <div className="font-bold text-slate-900 dark:text-white">
                Interview Prep & Milestone Email Alerts
              </div>
              <p className="text-slate-500 dark:text-slate-400">
                Receive notifications 24 hours prior to scheduled interview rounds.
              </p>
            </div>
            <input
              type="checkbox"
              checked={emailAlerts}
              onChange={(e) => setEmailAlerts(e.target.checked)}
              className="h-5 w-5 rounded border-slate-300 text-brand-600 focus:ring-brand-500 cursor-pointer"
            />
          </div>
        </div>
      </Card>

      {/* Data Ownership & Export */}
      <Card className="p-6 space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
          <div className="flex items-center gap-2">
            <Download className="w-5 h-5 text-indigo-600" />
            <h3 className="text-base font-bold text-slate-900 dark:text-white">
              Data Portability & Export
            </h3>
          </div>
          <Badge variant="outline" size="sm" className="text-amber-700 bg-amber-50 border-amber-200 dark:bg-amber-950/40 dark:border-amber-800 dark:text-amber-300 w-fit">
            Scheduled for Phase 16
          </Badge>
        </div>
        <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed">
          Self-service structured data export is currently in development. Once implemented in Phase 16, candidates will be able to download a verified JSON archive of their career profile, diagnostic test records, roadmap logs, and resume versions.
        </p>

        <div className="p-3.5 rounded-xl bg-slate-50 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-700 text-xs text-slate-600 dark:text-slate-400 leading-relaxed">
          <p>
            <strong className="text-slate-800 dark:text-slate-200">Current Status:</strong> Automated export endpoints are not yet connected in this preview release. If you need a full export of your personal profile data before Phase 16 activation, please submit a request to the platform administrator.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-3 pt-1">
          <Button
            size="sm"
            variant="outline"
            disabled
            aria-disabled="true"
            title="Automated export is scheduled for Phase 16"
          >
            <Download className="w-3.5 h-3.5 mr-1.5" /> Export Career Graph (Unavailable)
          </Button>
          <Button
            size="sm"
            variant="outline"
            disabled
            aria-disabled="true"
            title="Automated export is scheduled for Phase 16"
          >
            <Download className="w-3.5 h-3.5 mr-1.5" /> Export Resumes (Unavailable)
          </Button>
        </div>
      </Card>

      {/* Danger Zone: Account Deletion */}
      <Card className="p-6 border-slate-200 dark:border-slate-800 bg-slate-50/40 dark:bg-slate-900/20 space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
          <div className="flex items-center gap-2 text-slate-800 dark:text-slate-200 font-bold">
            <AlertTriangle className="w-5 h-5 text-amber-600" />
            <h3 className="text-base">Danger Zone: Permanent Account Deletion</h3>
          </div>
          <Badge variant="outline" size="sm" className="text-amber-700 bg-amber-50 border-amber-200 dark:bg-amber-950/40 dark:border-amber-800 dark:text-amber-300 w-fit">
            Scheduled for Phase 16
          </Badge>
        </div>
        <p className="text-xs text-slate-600 dark:text-slate-400 leading-relaxed">
          Self-service account deletion is currently unavailable in this preview release. A safe and irreversible purge requires an orchestrated backend workflow across 37 relational tables, file storage repositories, vector index registries, and active session caches.
        </p>

        <div className="p-3.5 rounded-xl bg-amber-50/70 dark:bg-amber-950/30 border border-amber-200 dark:border-amber-800/60 text-xs text-amber-900 dark:text-amber-200 leading-relaxed">
          <p>
            <strong className="text-amber-950 dark:text-amber-100">Action Unavailable:</strong> Automated self-service deletion will be activated in Phase 16 with password re-authentication and multi-tier verification. If you require immediate account and data removal, please contact the administrative team.
          </p>
        </div>

        <div>
          <Button
            size="sm"
            variant="destructive"
            disabled
            aria-disabled="true"
            title="Self-service account deletion is scheduled for Phase 16"
          >
            <Trash2 className="w-3.5 h-3.5 mr-1.5" /> Delete Account & Purge Data (Unavailable)
          </Button>
        </div>
      </Card>
    </div>
  );
}
