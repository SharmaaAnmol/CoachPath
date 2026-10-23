'use client';

import * as React from 'react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import {
  CheckCircle2,
  Edit3,
  Sparkles,
  ArrowRight,
  Briefcase,
  GraduationCap,
  Code,
  Clock,
  MapPin,
  Target,
  AlertTriangle,
  RotateCcw,
} from 'lucide-react';
import { OnboardingSummary } from '@/types';

export interface CareerSummaryReviewProps {
  summary: OnboardingSummary;
  onConfirm: (edits?: OnboardingSummary | null) => Promise<void>;
  isConfirming: boolean;
}

export function CareerSummaryReview({
  summary,
  onConfirm,
  isConfirming,
}: CareerSummaryReviewProps) {
  const [isEditing, setIsEditing] = React.useState(false);
  const [editedSummary, setEditedSummary] = React.useState<OnboardingSummary>({ ...summary });

  // Update local edit state when summary prop updates
  React.useEffect(() => {
    setEditedSummary({ ...summary });
  }, [summary]);

  const handleArrayChange = (
    field: keyof OnboardingSummary,
    valueString: string
  ) => {
    const items = valueString
      .split(',')
      .map((item) => item.trim())
      .filter(Boolean);
    setEditedSummary((prev) => ({
      ...prev,
      [field]: items,
    }));
  };

  const handleTextChange = (field: keyof OnboardingSummary, value: string) => {
    setEditedSummary((prev) => ({
      ...prev,
      [field]: value.trim() === '' ? null : value,
    }));
  };

  const handleNumberChange = (
    field: keyof OnboardingSummary,
    value: string
  ) => {
    const num = parseFloat(value);
    setEditedSummary((prev) => ({
      ...prev,
      [field]: isNaN(num) ? null : num,
    }));
  };

  const handleReset = () => {
    setEditedSummary({ ...summary });
    setIsEditing(false);
  };

  const handleConfirmAction = async () => {
    if (isEditing) {
      await onConfirm(editedSummary);
    } else {
      await onConfirm(null);
    }
  };

  const displayData = isEditing ? editedSummary : summary;

  return (
    <Card className="border-purple-200 dark:border-purple-900 shadow-elevated">
      <CardHeader className="bg-gradient-to-r from-purple-50 via-indigo-50/50 to-transparent dark:from-purple-950/30 dark:via-slate-900 dark:to-transparent border-b border-purple-100 dark:border-slate-800">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="space-y-1">
            <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-purple-100 dark:bg-purple-950 text-purple-700 dark:text-purple-300 text-xs font-semibold">
              <Sparkles className="w-3.5 h-3.5" />
              <span>AI Synthesized Career Profile</span>
            </div>
            <CardTitle className="text-xl sm:text-2xl font-bold tracking-tight">
              Review Your Career Blueprint
            </CardTitle>
            <CardDescription>
              We structured your conversation into an actionable career profile. Review, edit if needed, and confirm to update your profile.
            </CardDescription>
          </div>

          <div className="flex items-center gap-2 shrink-0">
            {isEditing ? (
              <Button
                type="button"
                variant="outline"
                size="sm"
                onClick={handleReset}
                disabled={isConfirming}
              >
                <RotateCcw className="w-3.5 h-3.5 mr-1" />
                Cancel Edits
              </Button>
            ) : (
              <Button
                type="button"
                variant="outline"
                size="sm"
                onClick={() => setIsEditing(true)}
                disabled={isConfirming}
              >
                <Edit3 className="w-3.5 h-3.5 mr-1" />
                Edit Summary
              </Button>
            )}
          </div>
        </div>
      </CardHeader>

      <CardContent className="p-5 sm:p-6 space-y-6">
        {/* Missing or Uncertain notice */}
        {displayData.missing_areas && displayData.missing_areas.length > 0 && (
          <div className="p-3.5 rounded-xl bg-amber-50 dark:bg-amber-950/30 border border-amber-200 dark:border-amber-800 text-amber-800 dark:text-amber-300 text-xs flex items-start gap-2.5">
            <AlertTriangle className="w-4 h-4 shrink-0 mt-0.5 text-amber-600 dark:text-amber-400" />
            <div>
              <p className="font-semibold">Optional areas skipped:</p>
              <p className="mt-0.5 text-amber-700 dark:text-amber-400">
                {displayData.missing_areas.join(', ')}. You can fill these in anytime later in your Career Profile.
              </p>
            </div>
          </div>
        )}

        {/* 1. Target Role & Career Stage */}
        <div className="rounded-xl border border-slate-200/90 dark:border-slate-800 p-4 space-y-3">
          <div className="flex items-center gap-2 text-sm font-semibold text-slate-800 dark:text-slate-200">
            <Target className="w-4 h-4 text-purple-600" />
            <span>Target Role & Stage</span>
          </div>

          {isEditing ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <Input
                label="Target Role"
                value={editedSummary.target_role || ''}
                onChange={(e) => handleTextChange('target_role', e.target.value)}
                placeholder="e.g. Backend Developer"
              />
              <div className="space-y-1.5">
                <label className="block text-xs font-semibold uppercase tracking-wider text-slate-700 dark:text-slate-300">
                  Career Stage
                </label>
                <select
                  value={editedSummary.career_stage || 'early_career'}
                  onChange={(e) => handleTextChange('career_stage', e.target.value)}
                  className="flex h-10 w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 focus:border-brand-500 focus:ring-2 focus:ring-brand-500/20 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-100"
                >
                  <option value="student">Student / In College</option>
                  <option value="recent_graduate">Recent Graduate</option>
                  <option value="early_career">Early Career (1-3 yrs)</option>
                  <option value="mid_career">Mid Career (3+ yrs)</option>
                </select>
              </div>
            </div>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm">
              <div>
                <span className="text-xs text-slate-500 dark:text-slate-400 block">Primary Target Role</span>
                <span className="font-semibold text-slate-900 dark:text-white text-base">
                  {displayData.target_role || 'Not specified'}
                </span>
              </div>
              <div>
                <span className="text-xs text-slate-500 dark:text-slate-400 block">Career Stage</span>
                <Badge variant="intelligence" size="md" className="capitalize mt-1">
                  {displayData.career_stage?.replace(/_/g, ' ') || 'Early Career'}
                </Badge>
              </div>
            </div>
          )}
        </div>

        {/* 2. Education & Experience */}
        <div className="rounded-xl border border-slate-200/90 dark:border-slate-800 p-4 space-y-3">
          <div className="flex items-center gap-2 text-sm font-semibold text-slate-800 dark:text-slate-200">
            <GraduationCap className="w-4 h-4 text-purple-600" />
            <span>Education & Background</span>
          </div>

          {isEditing ? (
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <Input
                label="Education Level"
                value={editedSummary.current_education || ''}
                onChange={(e) => handleTextChange('current_education', e.target.value)}
                placeholder="e.g. Bachelor of Science"
              />
              <Input
                label="Field of Study"
                value={editedSummary.education_field || ''}
                onChange={(e) => handleTextChange('education_field', e.target.value)}
                placeholder="e.g. Computer Science"
              />
              <Input
                label="Years of Experience"
                type="number"
                step="0.5"
                value={editedSummary.years_of_experience ?? ''}
                onChange={(e) => handleNumberChange('years_of_experience', e.target.value)}
                placeholder="e.g. 1.5"
              />
            </div>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-sm">
              <div>
                <span className="text-xs text-slate-500 dark:text-slate-400 block">Education</span>
                <span className="font-medium text-slate-800 dark:text-slate-200">
                  {displayData.current_education || 'Not specified'}
                  {displayData.education_field ? ` in ${displayData.education_field}` : ''}
                </span>
              </div>
              <div>
                <span className="text-xs text-slate-500 dark:text-slate-400 block">Experience Level</span>
                <span className="font-medium text-slate-800 dark:text-slate-200">
                  {displayData.years_of_experience !== null && displayData.years_of_experience !== undefined
                    ? `${displayData.years_of_experience} year${displayData.years_of_experience === 1 ? '' : 's'}`
                    : 'Entry / No prior work experience'}
                </span>
              </div>
              <div>
                <span className="text-xs text-slate-500 dark:text-slate-400 block">Recent Role</span>
                <span className="font-medium text-slate-800 dark:text-slate-200">
                  {displayData.current_or_recent_role || 'None listed'}
                  {displayData.current_company ? ` at ${displayData.current_company}` : ''}
                </span>
              </div>
            </div>
          )}
        </div>

        {/* 3. Skills & Technologies */}
        <div className="rounded-xl border border-slate-200/90 dark:border-slate-800 p-4 space-y-3">
          <div className="flex items-center gap-2 text-sm font-semibold text-slate-800 dark:text-slate-200">
            <Code className="w-4 h-4 text-purple-600" />
            <span>Technical Skills & Tools</span>
          </div>

          {isEditing ? (
            <div className="space-y-4">
              <Input
                label="Primary Skills (comma-separated)"
                value={(editedSummary.skills || []).join(', ')}
                onChange={(e) => handleArrayChange('skills', e.target.value)}
                placeholder="Python, SQL, System Design, REST APIs"
              />
              <Input
                label="Technologies & Frameworks (comma-separated)"
                value={(editedSummary.technologies || []).join(', ')}
                onChange={(e) => handleArrayChange('technologies', e.target.value)}
                placeholder="FastAPI, PostgreSQL, Docker, Git"
              />
            </div>
          ) : (
            <div className="space-y-3">
              <div>
                <span className="text-xs text-slate-500 dark:text-slate-400 block mb-1.5">Confirmed Skills</span>
                <div className="flex flex-wrap gap-1.5">
                  {displayData.skills && displayData.skills.length > 0 ? (
                    displayData.skills.map((skill) => (
                      <Badge key={skill} variant="default" size="sm">
                        {skill}
                      </Badge>
                    ))
                  ) : (
                    <span className="text-xs text-slate-400 italic">None stated</span>
                  )}
                </div>
              </div>

              <div>
                <span className="text-xs text-slate-500 dark:text-slate-400 block mb-1.5">Technologies & Tools</span>
                <div className="flex flex-wrap gap-1.5">
                  {displayData.technologies && displayData.technologies.length > 0 ? (
                    displayData.technologies.map((tech) => (
                      <Badge key={tech} variant="secondary" size="sm">
                        {tech}
                      </Badge>
                    ))
                  ) : (
                    <span className="text-xs text-slate-400 italic">None stated</span>
                  )}
                </div>
              </div>
            </div>
          )}
        </div>

        {/* 4. Projects & Learning Commitment */}
        <div className="rounded-xl border border-slate-200/90 dark:border-slate-800 p-4 space-y-3">
          <div className="flex items-center gap-2 text-sm font-semibold text-slate-800 dark:text-slate-200">
            <Clock className="w-4 h-4 text-purple-600" />
            <span>Projects & Learning Commitment</span>
          </div>

          {isEditing ? (
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <Input
                label="Weekly Learning Hours"
                type="number"
                value={editedSummary.learning_hours_per_week ?? ''}
                onChange={(e) => handleNumberChange('learning_hours_per_week', e.target.value)}
                placeholder="e.g. 15"
              />
              <Input
                label="Timeline (months)"
                type="number"
                value={editedSummary.target_timeline_months ?? ''}
                onChange={(e) => handleNumberChange('target_timeline_months', e.target.value)}
                placeholder="e.g. 6"
              />
              <Input
                label="Projects (comma-separated)"
                value={(editedSummary.notable_projects || []).join(', ')}
                onChange={(e) => handleArrayChange('notable_projects', e.target.value)}
                placeholder="E-commerce API, Portfolio Site"
              />
            </div>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-sm">
              <div>
                <span className="text-xs text-slate-500 dark:text-slate-400 block">Weekly Commitment</span>
                <span className="font-medium text-slate-800 dark:text-slate-200">
                  {displayData.learning_hours_per_week ? `${displayData.learning_hours_per_week} hrs/week` : 'Flexible'}
                </span>
              </div>
              <div>
                <span className="text-xs text-slate-500 dark:text-slate-400 block">Target Timeline</span>
                <span className="font-medium text-slate-800 dark:text-slate-200">
                  {displayData.target_timeline_months ? `${displayData.target_timeline_months} months` : 'Open'}
                </span>
              </div>
              <div>
                <span className="text-xs text-slate-500 dark:text-slate-400 block">Notable Projects</span>
                <span className="font-medium text-slate-800 dark:text-slate-200">
                  {displayData.notable_projects && displayData.notable_projects.length > 0
                    ? displayData.notable_projects.join(', ')
                    : 'None mentioned'}
                </span>
              </div>
            </div>
          )}
        </div>

        {/* 5. Preferences & Career Goals */}
        <div className="rounded-xl border border-slate-200/90 dark:border-slate-800 p-4 space-y-3">
          <div className="flex items-center gap-2 text-sm font-semibold text-slate-800 dark:text-slate-200">
            <MapPin className="w-4 h-4 text-purple-600" />
            <span>Preferences & Career Goals</span>
          </div>

          {isEditing ? (
            <div className="space-y-4">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div className="space-y-1.5">
                  <label className="block text-xs font-semibold uppercase tracking-wider text-slate-700 dark:text-slate-300">
                    Work Preference
                  </label>
                  <select
                    value={editedSummary.work_preference || 'remote'}
                    onChange={(e) => handleTextChange('work_preference', e.target.value)}
                    className="flex h-10 w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 focus:border-brand-500 focus:ring-2 focus:ring-brand-500/20 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-100"
                  >
                    <option value="remote">Remote</option>
                    <option value="hybrid">Hybrid</option>
                    <option value="onsite">On-Site</option>
                    <option value="flexible">Flexible</option>
                  </select>
                </div>
                <Input
                  label="Target Locations (comma-separated)"
                  value={(editedSummary.target_locations || []).join(', ')}
                  onChange={(e) => handleArrayChange('target_locations', e.target.value)}
                  placeholder="e.g. Bangalore, Remote, New York"
                />
              </div>
              <Textarea
                label="Long-Term Career Goals"
                value={editedSummary.career_goals || ''}
                onChange={(e) => handleTextChange('career_goals', e.target.value)}
                placeholder="e.g. Land a Backend Engineer role at a high-growth SaaS startup."
                rows={2}
              />
            </div>
          ) : (
            <div className="space-y-2 text-sm">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <span className="text-xs text-slate-500 dark:text-slate-400 block">Work Mode</span>
                  <span className="font-medium capitalize text-slate-800 dark:text-slate-200">
                    {displayData.work_preference || 'Flexible'}
                  </span>
                </div>
                <div>
                  <span className="text-xs text-slate-500 dark:text-slate-400 block">Target Locations</span>
                  <span className="font-medium text-slate-800 dark:text-slate-200">
                    {displayData.target_locations && displayData.target_locations.length > 0
                      ? displayData.target_locations.join(', ')
                      : 'Any location'}
                  </span>
                </div>
              </div>
              {displayData.career_goals && (
                <div className="pt-2">
                  <span className="text-xs text-slate-500 dark:text-slate-400 block">Career Goal Statement</span>
                  <p className="text-slate-700 dark:text-slate-300 italic text-xs leading-relaxed mt-0.5">
                    &ldquo;{displayData.career_goals}&rdquo;
                  </p>
                </div>
              )}
            </div>
          )}
        </div>
      </CardContent>

      <CardFooter className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-slate-50/80 dark:bg-slate-900/60 p-5 rounded-b-xl border-t border-slate-100 dark:border-slate-800">
        <div className="text-xs text-slate-500 dark:text-slate-400 flex items-center gap-1.5">
          <CheckCircle2 className="w-4 h-4 text-emerald-500 shrink-0" />
          <span>
            {isEditing
              ? 'Your custom edits will be applied directly to your Career Profile.'
              : 'Confirming will save this career baseline to your persistent profile.'}
          </span>
        </div>

        <div className="flex items-center gap-2.5 w-full sm:w-auto">
          {isEditing && (
            <Button
              type="button"
              variant="outline"
              size="md"
              onClick={handleReset}
              disabled={isConfirming}
              className="w-1/2 sm:w-auto"
            >
              Cancel
            </Button>
          )}

          <Button
            type="button"
            variant="intelligence"
            size="md"
            isLoading={isConfirming}
            onClick={handleConfirmAction}
            className="w-full sm:w-auto px-6"
          >
            <Sparkles className="w-4 h-4 mr-2" />
            <span>{isEditing ? 'Confirm & Apply Edits' : 'Confirm & Build Profile'}</span>
            <ArrowRight className="w-4 h-4 ml-2" />
          </Button>
        </div>
      </CardFooter>
    </Card>
  );
}
