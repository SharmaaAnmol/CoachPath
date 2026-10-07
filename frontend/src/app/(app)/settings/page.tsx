'use client';

import * as React from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Modal } from '@/components/ui/modal';
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

export default function SettingsPage() {
  const [humanApprovalGate, setHumanApprovalGate] = React.useState(true);
  const [emailAlerts, setEmailAlerts] = React.useState(true);
  const [isDeleteModalOpen, setIsDeleteModalOpen] = React.useState(false);

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
          <Input label="Full Name" defaultValue="Aarav Mehta" />
          <Input label="Email Address" defaultValue="aarav.mehta@example.com" />
        </div>
        <div className="pt-2 flex justify-end">
          <Button size="sm" variant="primary">
            Save Account Details
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
        <div className="flex items-center gap-2">
          <Download className="w-5 h-5 text-indigo-600" />
          <h3 className="text-base font-bold text-slate-900 dark:text-white">
            Data Portability & Export (GDPR Art. 20)
          </h3>
        </div>
        <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed">
          Download a complete, structured JSON export of your career graph, skill diagnostics, roadmap logs, and resume versions.
        </p>

        <div className="flex flex-wrap items-center gap-3 pt-2">
          <Button
            size="sm"
            variant="outline"
            onClick={() => alert('Exporting full user career graph JSON...')}
          >
            <Download className="w-3.5 h-3.5 mr-1.5" /> Export Career Graph (JSON)
          </Button>
          <Button
            size="sm"
            variant="outline"
            onClick={() => alert('Exporting all resume versions Markdown...')}
          >
            <Download className="w-3.5 h-3.5 mr-1.5" /> Export Resumes (Markdown)
          </Button>
        </div>
      </Card>

      {/* Danger Zone: Account Deletion */}
      <Card className="p-6 border-rose-200 dark:border-rose-900/50 bg-rose-50/20 dark:bg-rose-950/10 space-y-4">
        <div className="flex items-center gap-2 text-rose-600 font-bold">
          <AlertTriangle className="w-5 h-5" />
          <h3 className="text-base">Danger Zone: Permanent Account Deletion</h3>
        </div>
        <p className="text-xs text-slate-600 dark:text-slate-300 leading-relaxed">
          In compliance with the Right to Erasure, permanently delete your account, stored resumes, assessment attempts, and activity history. This action cannot be reversed.
        </p>
        <div>
          <Button
            size="sm"
            variant="destructive"
            onClick={() => setIsDeleteModalOpen(true)}
          >
            <Trash2 className="w-3.5 h-3.5 mr-1.5" /> Delete Account & Purge Data
          </Button>
        </div>
      </Card>

      {/* Delete Confirmation Modal */}
      <Modal
        isOpen={isDeleteModalOpen}
        onClose={() => setIsDeleteModalOpen(false)}
        title="Confirm Account & Data Deletion"
        description="Are you absolutely sure you want to permanently delete your CoachPath account?"
        footer={
          <div className="flex justify-end gap-2">
            <Button size="sm" variant="outline" onClick={() => setIsDeleteModalOpen(false)}>
              Cancel
            </Button>
            <Button
              size="sm"
              variant="destructive"
              onClick={() => {
                alert('Account and data purged permanently.');
                setIsDeleteModalOpen(false);
              }}
            >
              Permanently Delete
            </Button>
          </div>
        }
      >
        <p className="text-xs text-slate-600 dark:text-slate-300">
          This will permanently purge your profile, test records, and resume diffs from our databases. This action is irreversible.
        </p>
      </Modal>
    </div>
  );
}
