export type TargetRole =
  | 'Full-Stack Engineer'
  | 'Frontend Engineer'
  | 'Backend Engineer'
  | 'DevOps / Platform Engineer'
  | 'Data Engineer'
  | 'Data Scientist'
  | 'Data Analyst'
  | 'Machine Learning Engineer'
  | 'AI Engineer'
  | 'Mobile Engineer'
  | 'Software Engineer';

export type SkillStatus = 'verified' | 'developing' | 'missing';

export interface SkillItem {
  id: string;
  name: string;
  category: 'Languages' | 'Frameworks' | 'Cloud & DevOps' | 'Databases' | 'Architecture' | 'Tools';
  proficiency: 'Beginner' | 'Intermediate' | 'Advanced' | 'Expert';
  status: SkillStatus;
  confidenceScore: number; // 0 - 100
  evidenceSource: 'Assessment' | 'Resume' | 'Project' | 'Self-Reported';
  lastEvaluated?: string;
}

export interface EducationEntry {
  id: string;
  institution: string;
  degree: string;
  fieldOfStudy: string;
  startDate: string;
  endDate?: string;
  grade?: string;
}

export interface ExperienceEntry {
  id: string;
  company: string;
  role: string;
  location: string;
  startDate: string;
  endDate?: string;
  current: boolean;
  description: string[];
  skillsUsed: string[];
}

export interface ProjectEntry {
  id: string;
  title: string;
  description: string;
  technologies: string[];
  githubUrl?: string;
  liveUrl?: string;
  verifiedEvidence: boolean;
}

export interface CertificationEntry {
  id: string;
  name: string;
  issuingOrganization: string;
  issueDate: string;
  credentialId?: string;
  credentialUrl?: string;
}

export interface UserCareerProfile {
  id: string;
  name: string;
  title: string;
  email: string;
  avatarUrl: string;
  targetRole: TargetRole;
  secondaryRoles: TargetRole[];
  yearsExperience: number;
  bio: string;
  location: string;
  education: EducationEntry[];
  experience: ExperienceEntry[];
  projects: ProjectEntry[];
  certifications: CertificationEntry[];
  skills: SkillItem[];
}

export interface AssessmentQuestion {
  id: string;
  prompt: string;
  codeSnippet?: string;
  options: string[];
  correctOptionIndex: number;
  explanation: string;
}

export interface Assessment {
  id: string;
  title: string;
  domain: string;
  skillName: string;
  difficulty: 'Beginner' | 'Intermediate' | 'Advanced';
  durationMinutes: number;
  questionCount: number;
  status: 'available' | 'in_progress' | 'completed';
  score?: number;
  completedAt?: string;
  questions?: AssessmentQuestion[];
}

export interface AssessmentCategoryItem {
  id: string;
  skill_id: string;
  title: string;
  description: string;
  time_limit_minutes: number;
  passing_threshold: number;
  question_count: number;
  user_status: 'available' | 'in_progress' | 'completed';
  user_best_score?: number | null;
  last_attempt_at?: string | null;
  attempt_count: number;
}

export interface AttemptQuestionPublic {
  id: string;
  index: number;
  prompt_text: string;
  code_snippet?: string | null;
  options: string[];
  difficulty: 'basic' | 'intermediate' | 'advanced';
  topic: string;
}

export interface AttemptSession {
  attempt_id: string;
  assessment_id: string;
  assessment_title: string;
  skill_id: string;
  skill_name: string;
  status: string;
  total_questions: number;
  time_limit_minutes: number;
  started_at: string;
  questions: AttemptQuestionPublic[];
  current_answers: Record<string, number>;
}

export interface TopicScore {
  topic: string;
  total: number;
  correct: number;
  percentage: number;
}

export interface DifficultyScore {
  total: number;
  correct: number;
  percentage: number;
}

export interface GradedQuestionResult {
  id: string;
  index: number;
  prompt_text: string;
  code_snippet?: string | null;
  options: string[];
  selected_option_index: number | null;
  correct_option_index: number;
  is_correct: boolean;
  explanation: string;
  difficulty: string;
  topic: string;
}

export interface AssessmentResultResponse {
  attempt_id: string;
  assessment_id: string;
  assessment_title: string;
  skill_id: string;
  skill_name: string;
  status: string;
  score_percentage: number;
  passed: boolean;
  passing_threshold: number;
  proficiency_band: 'Foundational' | 'Developing' | 'Proficient' | 'Strong' | string;
  strengths_summary: string;
  weaknesses_summary: string;
  remedial_milestones: Array<{
    topic: string;
    recommendation: string;
    priority: string;
  }>;
  topic_breakdown: TopicScore[];
  difficulty_breakdown: Record<string, DifficultyScore>;
  total_questions: number;
  correct_count: number;
  started_at: string;
  completed_at?: string;
  questions: GradedQuestionResult[];
}

export interface AttemptHistoryItem {
  attempt_id: string;
  assessment_id: string;
  assessment_title: string;
  skill_id: string;
  skill_name: string;
  status: string;
  score_percentage?: number | null;
  passed?: boolean | null;
  started_at: string;
  completed_at?: string | null;
}

export interface RoadmapTask {
  id: string;
  title: string;
  description: string;
  estimatedHours: number;
  status: 'completed' | 'in_progress' | 'upcoming';
  category: 'Skill Mastery' | 'System Project' | 'Portfolio Artifact' | 'Interview Drill';
  resourceTitle: string;
  resourceUrl: string;
  deliverableRequired: string;
  completedAt?: string;
}

export interface RoadmapPhase {
  id: string;
  phaseNumber: number;
  title: string;
  timeline: string;
  status: 'completed' | 'in_progress' | 'upcoming';
  progressPercentage: number;
  tasks: RoadmapTask[];
}

export interface JobMatchBreakdown {
  skillsScore: number;
  experienceScore: number;
  domainScore: number;
  roleSimilarityScore: number;
}

export interface JobListing {
  id: string;
  title: string;
  company: string;
  location: string;
  remoteType: 'Remote' | 'Hybrid' | 'On-site';
  salaryRange: string;
  matchScore: number; // 0 - 100
  postedDate: string;
  description: string;
  requirements: string[];
  matchedSkills: string[];
  missingSkills: string[];
  breakdown: JobMatchBreakdown;
  applicationDeadline?: string;
}

// ─────────────────────────────────────────────
// Phase 8B: Job Discovery & Market Intelligence Types
// ─────────────────────────────────────────────

export interface JobSkillItem {
  skill_id: string;
  name: string;
  category?: string;
  is_mandatory: boolean;
  confidence_score?: number;
  source_phrase?: string;
}

export type WorkplaceType = 'remote' | 'hybrid' | 'onsite';
export type EmploymentType = 'full_time' | 'contract' | 'part_time' | 'internship';
export type ExperienceTier = 'internship' | 'entry_level' | 'junior' | 'mid';
export type FreshnessStatus = 'active' | 'needs_refresh' | 'expired' | 'closed';

export interface JobOpportunity {
  id: string;
  external_id?: string;
  source: string;
  source_url?: string;
  title: string;
  normalized_title?: string;
  company_name: string;
  location: string;
  normalized_location?: string;
  remote_type: WorkplaceType;
  employment_type?: EmploymentType;
  role_id: string;
  experience_level: ExperienceTier;
  min_salary?: number;
  max_salary?: number;
  currency: string;
  description_markdown: string;
  responsibilities: string[];
  required_qualifications: string[];
  preferred_qualifications: string[];
  application_url: string;
  is_active: boolean;
  freshness_status: FreshnessStatus;
  last_verified_at?: string;
  data_quality_score?: number;
  posted_at: string;
  created_at: string;
  skills: JobSkillItem[];
}

export interface JobSearchQuery {
  role_id?: string;
  remote_type?: string;
  employment_type?: string;
  experience_level?: string;
  skill_id?: string;
  keyword?: string;
  freshness_status?: string;
  min_salary?: number;
  sort_by?: 'newest' | 'salary_high' | 'title_asc' | 'oldest';
  page?: number;
  page_size?: number;
}

export interface JobSearchResponse {
  items: JobOpportunity[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface TopSkillDemand {
  skill_id: string;
  name: string;
  category: string;
  job_count: number;
  percentage: number;
}

export interface SalaryInsights {
  sample_size: number;
  average_min_salary?: number;
  average_max_salary?: number;
  median_salary?: number;
  currency: string;
}

export interface MarketIntelligenceData {
  total_active_jobs: number;
  role_distribution: Record<string, number>;
  remote_distribution: Record<string, number>;
  experience_distribution: Record<string, number>;
  top_demanded_skills: TopSkillDemand[];
  salary_insights: SalaryInsights;
  is_provisional: boolean;
  provisional_reason?: string | null;
  generated_at: string;
}

export interface ManualJobImportPayload {
  title: string;
  company_name: string;
  location?: string;
  description_text: string;
  application_url?: string;
  source_url?: string;
  remote_type?: string;
  role_id?: string;
  experience_level?: string;
  min_salary?: number;
  max_salary?: number;
  currency?: string;
}

// ─── Group 9: Job Matching Types ─────────────────────────────────────

export type SkillMatchClassification =
  | 'MATCHED'
  | 'PARTIALLY_MATCHED'
  | 'MISSING'
  | 'UNKNOWN'
  | 'INSUFFICIENT_EVIDENCE';

export interface SkillMatchItem {
  skill_id: string;
  name: string;
  category: string;
  is_mandatory: boolean;
  classification: SkillMatchClassification;
  user_evidence_source?: 'assessment' | 'project_evidence' | 'extracted' | 'self_reported' | string;
  user_confidence: number;
  user_proficiency_tier?: 'unverified' | 'demonstrated' | 'proficient' | 'mastered' | string;
  assessment_score?: number;
  explanation: string;
}

export interface MatchScoreBreakdown {
  overall_score: number;
  skill_score: number;
  experience_score: number;
  project_score: number;
  location_score: number;
  preference_score: number;
  vector_score: number;
  evidence_coverage: number;
  is_provisional: boolean;
  weights: Record<string, number>;
  evaluated_factors: string[];
  unevaluated_factors: string[];
}

export interface JobMatchExplanation {
  summary: string;
  strengths: string[];
  gaps: string[];
  recommended_actions: string[];
}

export interface JobMatchResponse {
  match_id: string;
  job_id: string;
  career_profile_id: string;
  overall_score: number;
  breakdown: MatchScoreBreakdown;
  matched_skills: string[];
  matched_preferred_skills: string[];
  missing_skills: string[];
  unknown_skills: string[];
  skills_detail: SkillMatchItem[];
  explanation: JobMatchExplanation;
  scoring_version: string;
  is_stale: boolean;
  freshness_status: string;
  calculated_at: string;
}

export interface JobMatchExplanationDrawerResponse {
  job_id: string;
  overall_score: number;
  evidence_coverage: number;
  breakdown: Record<string, number>;
  matched_skills: string[];
  missing_skills: string[];
  matched_preferred_skills: string[];
  unknown_skills: string[];
  hiring_rationale: string;
  strengths: string[];
  gaps: string[];
  recommended_actions: string[];
  skills_detail: SkillMatchItem[];
}

export interface JobRecommendationItem {
  job: JobOpportunity;
  match: JobMatchResponse;
}

export interface JobRecommendationResponse {
  items: JobRecommendationItem[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
  scoring_version: string;
  generated_at: string;
}

export interface JobRecommendationQuery {
  min_score?: number;
  role_id?: string;
  remote_type?: 'remote' | 'hybrid' | 'onsite';
  include_provisional?: boolean;
  page?: number;
  page_size?: number;
}

export interface JobMatchBatchRefreshResponse {
  recalculated_count: number;
  status: string;
  scoring_version: string;
  message: string;
}

export interface ResumeDiffChange {
  id: string;
  section: string;
  originalText: string;
  suggestedText: string;
  rationale: string;
  evidenceReference: string;
  status: 'pending' | 'accepted' | 'rejected';
}

export interface ResumeVersion {
  id: string;
  versionName: string;
  targetJobTitle?: string;
  targetCompany?: string;
  createdAt: string;
  matchScoreBoost: number;
  changes: ResumeDiffChange[];
  fullMarkdown: string;
}

export type ApplicationStage = 'saved' | 'applied' | 'interviewing' | 'offered' | 'rejected';

export interface ApplicationItem {
  id: string;
  jobId: string;
  company: string;
  roleTitle: string;
  location: string;
  salary: string;
  stage: ApplicationStage;
  appliedDate?: string;
  nextStep?: string;
  matchScore: number;
  notes: string;
  contactName?: string;
}

export interface RecruiterContact {
  id: string;
  name: string;
  role: string;
  company: string;
  linkedInUrl: string;
  verifiedEmail?: string;
  relevanceReason: string;
  outreachDraftSubject: string;
  outreachDraftBody: string;
  copiedToClipboard: boolean;
}

export interface StarStory {
  situation: string;
  task: string;
  action: string;
  result: string;
}

export interface InterviewQuestionItem {
  id: string;
  question: string;
  category: 'Behavioral' | 'System Architecture' | 'Technical Deep-Dive' | 'Live Coding';
  difficulty: 'Standard' | 'Challenging' | 'Staff-Level';
  suggestedSTAR?: StarStory;
  keyTalkingPoints: string[];
}

export interface ScheduledInterview {
  id: string;
  company: string;
  role: string;
  roundType: 'Screening' | 'Technical' | 'System Design' | 'Hiring Manager';
  dateTime: string;
  interviewerName: string;
  interviewerTitle: string;
  prepCompletedPercentage: number;
  questions: InterviewQuestionItem[];
}

export interface ReadinessPillar {
  name: string;
  weight: number;
  score: number;
  status: 'strong' | 'moderate' | 'needs_focus';
  summary: string;
  recommendations: string[];
}

export interface CareerReadinessData {
  overallScore: number; // 0 - 100
  targetRole: TargetRole;
  pillars: {
    skillVerification: ReadinessPillar;
    practicalProjects: ReadinessPillar;
    marketRelevance: ReadinessPillar;
    interviewFluency: ReadinessPillar;
  };
  keyMilestonesCompleted: number;
  totalKeyMilestones: number;
}

// Authentication & Identity Types (Phase 3)
export interface AuthUser {
  id: string;
  email: string;
  role: 'candidate' | 'admin' | string;
  status: 'pending_verification' | 'active' | 'suspended' | 'deleted' | string;
  full_name?: string | null;
  created_at: string;
}

export interface RegisterPayload {
  email: string;
  password: string;
  full_name: string;
}

export interface RegisterResponse {
  user_id: string;
  email: string;
  status: string;
  message: string;
}

export interface LoginPayload {
  email: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  refresh_token?: string;
  user: AuthUser;
}

export interface RefreshTokenResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  refresh_token?: string;
}

export interface LogoutResponse {
  message: string;
}

// Career Profile Management Types (Phase 3C)
export interface RoleItem {
  id: string;
  title: string;
  description?: string | null;
  category?: string | null;
}

export interface UserProfileUpdatePayload {
  full_name?: string;
  headline?: string | null;
  location?: string | null;
  phone_number?: string | null;
  linkedin_url?: string | null;
  github_url?: string | null;
  portfolio_url?: string | null;
  bio?: string | null;
}

export interface CareerGoalsUpdatePayload {
  primary_role_id: string;
  secondary_role_id?: string | null;
  career_stage: string;
  work_preference: string;
  target_locations: string[];
  years_of_experience: number;
}

export interface CareerGoalsData {
  primary_role?: RoleItem | null;
  secondary_role?: RoleItem | null;
  career_stage: string;
  work_preference: string;
  target_locations: string[];
  years_of_experience: number;
}

export interface ProfileEducationEntry {
  id: string;
  institution_name: string;
  degree: string;
  field_of_study: string;
  start_date: string;
  end_date?: string | null;
  is_current: boolean;
  gpa?: number | null;
  created_at: string;
}

export interface ProfileEducationPayload {
  institution_name: string;
  degree: string;
  field_of_study: string;
  start_date: string;
  end_date?: string | null;
  is_current?: boolean;
  gpa?: number | null;
}

export interface ProfileExperienceEntry {
  id: string;
  company_name: string;
  role_title: string;
  location?: string | null;
  start_date: string;
  end_date?: string | null;
  is_current: boolean;
  bullet_points: string[];
  created_at: string;
}

export interface ProfileExperiencePayload {
  company_name: string;
  role_title: string;
  location?: string | null;
  start_date: string;
  end_date?: string | null;
  is_current?: boolean;
  bullet_points?: string[];
}

export interface ProfileProjectEntry {
  id: string;
  title: string;
  description: string;
  technologies: string[];
  github_url?: string | null;
  live_url?: string | null;
  bullet_points: string[];
  created_at: string;
}

export interface ProfileProjectPayload {
  title: string;
  description: string;
  technologies?: string[];
  github_url?: string | null;
  live_url?: string | null;
  bullet_points?: string[];
}

export interface ProfileCertificationEntry {
  id: string;
  name: string;
  issuing_organization: string;
  issue_date: string;
  expiration_date?: string | null;
  credential_id?: string | null;
  credential_url?: string | null;
  created_at: string;
}

export interface ProfileCertificationPayload {
  name: string;
  issuing_organization: string;
  issue_date: string;
  expiration_date?: string | null;
  credential_id?: string | null;
  credential_url?: string | null;
}

export interface MasterCareerProfile {
  profile_id: string;
  user_id: string;
  email: string;
  full_name: string;
  headline?: string | null;
  location?: string | null;
  phone_number?: string | null;
  linkedin_url?: string | null;
  github_url?: string | null;
  portfolio_url?: string | null;
  bio?: string | null;
  career_stage: string;
  primary_role?: RoleItem | null;
  secondary_role?: RoleItem | null;
  work_preference: string;
  target_locations: string[];
  years_of_experience: number;
  education: ProfileEducationEntry[];
  experience: ProfileExperienceEntry[];
  projects: ProfileProjectEntry[];
  certifications: ProfileCertificationEntry[];
  verified_skills_count: number;
  completeness_score: number;
}

// ─────────────────────────────────────────────
// Phase 4: AI Onboarding Types
// ─────────────────────────────────────────────

export type OnboardingStatus =
  | 'not_started'
  | 'in_progress'
  | 'awaiting_confirmation'
  | 'completed';

export interface StartOnboardingResponse {
  session_id: string;
  status: OnboardingStatus;
  is_resumed: boolean;
  first_question: string;
  first_question_category: string;
  message: string;
}

export interface OnboardingSessionData {
  session_id: string;
  status: OnboardingStatus;
  current_question: string | null;
  current_question_category: string | null;
  turn_count: number;
  started_at: string;
  last_activity_at: string;
  completed_at: string | null;
}

export interface OnboardingProgressData {
  session_id: string;
  status: OnboardingStatus;
  turn_count: number;
  areas_covered: string[];
  areas_remaining: string[];
  ready_to_summarize: boolean;
  current_question: string | null;
}

export interface ConversationTurn {
  turn_id: string;
  turn_number: number;
  question: string;
  question_category: string;
  user_response: string | null;
  responded_at: string | null;
  created_at: string;
}

export interface SubmitResponsePayload {
  response_text: string;
}

export interface SubmitResponseResult {
  turn_completed: ConversationTurn;
  next_question: string | null;
  next_question_category: string | null;
  session_status: OnboardingStatus;
  ready_to_summarize: boolean;
}

export interface OnboardingSummary {
  target_role?: string | null;
  career_stage?: string | null;
  current_education?: string | null;
  education_field?: string | null;
  years_of_experience?: number | null;
  current_or_recent_role?: string | null;
  current_company?: string | null;
  skills: string[];
  technologies: string[];
  notable_projects: string[];
  learning_hours_per_week?: number | null;
  preferred_learning_resources: string[];
  target_timeline_months?: number | null;
  industries_of_interest: string[];
  companies_of_interest: string[];
  min_salary_usd?: number | null;
  max_salary_usd?: number | null;
  career_goals?: string | null;
  work_preference?: string | null;
  target_locations: string[];
  missing_areas: string[];
  uncertain_fields: string[];
}

export interface OnboardingSummaryResponse {
  session_id: string;
  summary: OnboardingSummary;
  generated_at: string;
  is_confirmed: boolean;
  confirmed_at: string | null;
}

export interface ConfirmSummaryPayload {
  confirmed: boolean;
  edits?: OnboardingSummary | null;
}

// ─────────────────────────────────────────────
// Phase 5: Resume Ingestion & Parsing Types
// ─────────────────────────────────────────────

export type ResumeProcessingStatus =
  | 'uploaded'
  | 'processing'
  | 'parsing'
  | 'parsed'
  | 'needs_review'
  | 'failed';

export type ParsingErrorCategory =
  | 'UNSUPPORTED_FORMAT'
  | 'CORRUPTED_DOCUMENT'
  | 'DOCUMENT_ENCRYPTED'
  | 'EMPTY_DOCUMENT'
  | 'INSUFFICIENT_TEXT_OCR_REQUIRED'
  | 'FILE_TOO_LARGE'
  | 'AI_PROVIDER_UNAVAILABLE'
  | 'AI_TIMEOUT'
  | 'AI_OUTPUT_INVALID'
  | 'STORAGE_ERROR'
  | 'UNKNOWN';

export interface ResumeListItem {
  id: string;
  file_name: string;
  file_size_bytes: number;
  mime_type: string;
  status: ResumeProcessingStatus;
  is_primary: boolean;
  parsing_error?: string | null;
  parsing_error_category?: ParsingErrorCategory | null;
  parsed_at?: string | null;
  created_at: string;
  updated_at: string;
}

export interface ResumeListResponse {
  resumes: ResumeListItem[];
  total: number;
}

export interface ResumeDetailResponse extends ResumeListItem {
  user_id: string;
}

export interface ResumeUploadResponse {
  resume_id: string;
  file_name: string;
  file_size_bytes: number;
  mime_type: string;
  status: ResumeProcessingStatus;
  message: string;
  created_at: string;
}

export interface RetryParsingResponse {
  resume_id: string;
  status: ResumeProcessingStatus;
  message: string;
}

export interface EvidenceItem {
  section_name?: string | null;
  page_number?: number | null;
  supporting_excerpt?: string | null;
}

export interface ExtractedPersonalInfo {
  name?: string | null;
  email?: string | null;
  phone?: string | null;
  location?: string | null;
  linkedin_url?: string | null;
  github_url?: string | null;
  portfolio_url?: string | null;
}

export interface ExtractedEducation {
  institution: string;
  degree?: string | null;
  field_of_study?: string | null;
  start_date?: string | null;
  end_date?: string | null;
  grade_or_gpa?: string | null;
  highlights: string[];
  evidence?: EvidenceItem | null;
}

export interface ExtractedExperience {
  employer: string;
  job_title: string;
  start_date?: string | null;
  end_date?: string | null;
  is_current?: boolean;
  location?: string | null;
  responsibilities: string[];
  achievements: string[];
  evidence?: EvidenceItem | null;
}

export interface ExtractedSkill {
  name: string;
  category?: string | null;
  confidence_source?: string;
  evidence?: EvidenceItem | null;
}

export interface ExtractedProject {
  name: string;
  description?: string | null;
  technologies: string[];
  url?: string | null;
  highlights: string[];
  evidence?: EvidenceItem | null;
}

export interface ExtractedCertification {
  name: string;
  issuing_organization?: string | null;
  issue_date?: string | null;
  expiration_date?: string | null;
  credential_id?: string | null;
  evidence?: EvidenceItem | null;
}

export interface NormalizedSkillItem {
  skill_id: string;
  name: string;
  category: string;
  raw_matched: string;
}

export interface ParsedResumePreview {
  personal_info?: ExtractedPersonalInfo | null;
  education: ExtractedEducation[];
  experience: ExtractedExperience[];
  projects: ExtractedProject[];
  certifications: ExtractedCertification[];
  detected_skills: string[];
  normalized_skills: NormalizedSkillItem[];
  raw_unmatched_skills: string[];
  executive_summary?: string | null;
}

export interface ParsedResumeResponse {
  resume_id: string;
  status: ResumeProcessingStatus;
  file_name: string;
  extracted_preview?: ParsedResumePreview | null;
  requires_human_confirmation: boolean;
  parsed_at?: string | null;
  parsing_error?: string | null;
  parsing_error_category?: ParsingErrorCategory | null;
}

export interface ConfirmPersonalInfo {
  headline?: string | null;
  location?: string | null;
  phone_number?: string | null;
  linkedin_url?: string | null;
  github_url?: string | null;
  portfolio_url?: string | null;
  bio?: string | null;
}

export interface ConfirmEducationItem {
  institution_name: string;
  degree: string;
  field_of_study: string;
  start_date: string;
  end_date?: string | null;
  is_current: boolean;
  gpa?: number | null;
}

export interface ConfirmExperienceItem {
  company_name: string;
  role_title: string;
  location?: string | null;
  start_date: string;
  end_date?: string | null;
  is_current: boolean;
  bullet_points: string[];
}

export interface ConfirmProjectItem {
  title: string;
  description: string;
  technologies: string[];
  github_url?: string | null;
  live_url?: string | null;
  bullet_points: string[];
}

export interface ConfirmCertificationItem {
  name: string;
  issuing_organization: string;
  issue_date: string;
  expiration_date?: string | null;
  credential_id?: string | null;
  credential_url?: string | null;
}

export interface ResumeConfirmationPayload {
  personal_info?: ConfirmPersonalInfo | null;
  education: ConfirmEducationItem[];
  experience: ConfirmExperienceItem[];
  projects: ConfirmProjectItem[];
  certifications: ConfirmCertificationItem[];
  confirmed_skills: string[];
  make_primary?: boolean;
}

export interface ResumeMergeSummary {
  education_added: number;
  experience_added: number;
  projects_added: number;
  certifications_added: number;
  skills_added: number;
  profile_updated: boolean;
}

export interface ResumeConfirmationResponse {
  resume_id: string;
  status: string;
  message: string;
  merged_summary: ResumeMergeSummary;
  completeness_score: number;
}

// ===========================================================================
// Phase 10A/10B: Tailored Resume & Optimization Types
// ===========================================================================

export type TailoredResumeStatus = 'draft' | 'approved' | 'archived';
export type TailoredChangeType = 'addition' | 'rephrasing' | 'emphasis' | 'reordering' | 'omission';

export interface StructuredChangeItem {
  id: string;
  section: string;
  change_type: TailoredChangeType;
  original_text?: string | null;
  proposed_text: string;
  rationale: string;
  target_job_requirement?: string | null;
  supporting_evidence?: string | null;
  needs_clarification: boolean;
}

export interface OptimizationAnalysis {
  keyword_coverage: number;
  matched_keywords: string[];
  missing_keywords: string[];
  supported_skills: string[];
  missing_requirements: string[];
  readability_score?: number | null;
  formatting_recommendations: string[];
  actionable_suggestions: string[];
}

export interface DiffSummarySchema {
  changes: StructuredChangeItem[];
  additions_count: number;
  rephrasings_count: number;
  deletions_count: number;
  optimization_analysis?: OptimizationAnalysis | null;
  unsupported_claims: string[];
  model_metadata: Record<string, any>;
  candidate_notes?: string | null;
  accepted_sections: string[];
}

export interface ResumeTailorRequest {
  job_id?: string | null;
  job_description_text?: string | null;
  job_title?: string | null;
  company_name?: string | null;
  target_emphasis?: string[];
  user_notes?: string | null;
}

export interface TailoredResumeResponse {
  id: string;
  resume_id: string;
  target_job_id: string;
  version_number: number;
  status: TailoredResumeStatus;
  anti_hallucination_verified: boolean;
  tailored_content: ParsedResumePreview;
  diff_summary: DiffSummarySchema;
  approved_at?: string | null;
  created_at: string;
  updated_at: string;
}

export interface TailoredResumeListItem {
  id: string;
  resume_id: string;
  target_job_id: string;
  job_title?: string | null;
  company_name?: string | null;
  version_number: number;
  status: TailoredResumeStatus;
  anti_hallucination_verified: boolean;
  keyword_coverage?: number | null;
  changes_count: number;
  approved_at?: string | null;
  created_at: string;
  updated_at: string;
}

export interface TailoredResumeListResponse {
  items: TailoredResumeListItem[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface TailoredResumeUpdateRequest {
  tailored_content?: ParsedResumePreview;
  user_notes?: string | null;
}

export interface TailoredResumeApprovalRequest {
  accepted_sections: string[];
  user_confirmation: boolean;
}

export interface TailoredResumeDiffResponse {
  version_id: string;
  resume_id: string;
  target_job_id: string;
  status: string;
  changes: StructuredChangeItem[];
  additions_count: number;
  rephrasings_count: number;
  deletions_count: number;
  unsupported_claims: string[];
}

export interface TailoredResumeAnalysisResponse {
  version_id: string;
  target_job_id: string;
  job_title?: string | null;
  company_name?: string | null;
  optimization_analysis: OptimizationAnalysis;
  anti_hallucination_verified: boolean;
  unsupported_claims: string[];
}

// ===========================================================================
// Phase 6A/6B: Skill Gap Analysis Engine & Dashboard Types
// ===========================================================================

export type ProficiencyLevelNumber = 0 | 1 | 2 | 3 | 4;
export type ProficiencyTierName = 'unverified' | 'basic' | 'demonstrated' | 'proficient' | 'mastered';
export type SkillRequirementImportance = 'mandatory' | 'preferred' | 'bonus';
export type SkillCompetencyStatus = 'STRENGTH' | 'DEVELOPING' | 'GAP' | 'NOT_ASSESSED' | 'NOT_IN_PROFILE';
export type GapPriorityLevel = 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
export type GapActionType = 'TAKE_ASSESSMENT' | 'BUILD_PROJECT' | 'PRACTICE_TOPIC' | 'STUDY_TOPIC';
export type EvidenceProvenanceSource = 'assessment' | 'resume' | 'profile' | 'project';

export interface CanonicalSkillItem {
  id: string;
  name: string;
  category: string;
  description: string;
  synonyms: string[];
}

export interface RoleRequirementItem {
  skill_id: string;
  skill_name?: string | null;
  category?: string | null;
  importance: SkillRequirementImportance;
  min_proficiency: 'basic' | 'demonstrated' | 'proficient' | 'mastered';
  required_level: number;
  weight: number;
  rationale?: string | null;
}

export interface TargetRoleDetail {
  id: string;
  title: string;
  description: string;
  category: string;
  version: string;
  source: string;
  is_complete: boolean;
  requirements: RoleRequirementItem[];
}

export interface TargetRolesListResponse {
  roles: TargetRoleDetail[];
  total: number;
}

export interface SkillEvidenceItem {
  source: EvidenceProvenanceSource;
  title: string;
  description: string;
  score?: number | null;
  confidence_score: number;
  is_verified: boolean;
  date?: string | null;
}

export interface SkillCompetencyDetailItem {
  skill_id: string;
  skill_name: string;
  category: string;
  importance: SkillRequirementImportance;
  min_proficiency: 'basic' | 'demonstrated' | 'proficient' | 'mastered';
  required_level: number;
  current_level: number;
  current_tier: ProficiencyTierName;
  coverage_ratio: number;
  status: SkillCompetencyStatus;
  weight: number;
  rationale?: string | null;
  evidence_count: number;
  evidence_items: SkillEvidenceItem[];
  recommended_action?: string | null;
}

export interface PrioritizedGapItem {
  rank: number;
  skill_id: string;
  skill_name: string;
  priority: GapPriorityLevel;
  importance: string;
  required_level: number;
  current_level: number;
  reason: string;
  action_type: GapActionType;
  action_description: string;
  assessment_id?: string | null;
}

export interface RecommendedAssessmentItem {
  assessment_id: string;
  title: string;
  skill_id: string;
  reason: string;
  estimated_minutes: number;
  question_count: number;
}

export interface SkillGapAnalysisData {
  id: string;
  career_profile_id: string;
  role_id: string;
  role_title: string;
  is_current: boolean;
  role_version: string;
  algorithm_version: string;
  role_alignment_score: number;
  evidence_coverage_score: number;
  status: string;
  strongest_skills: string[];
  developing_skills: string[];
  skill_gaps: string[];
  missing_skills: string[];
  unassessed_skills: string[];
  skill_details: Record<string, SkillCompetencyDetailItem>;
  prioritized_gaps: PrioritizedGapItem[];
  recommended_assessments: RecommendedAssessmentItem[];
  explanation_narrative: string;
  calculated_at: string;
}

export interface SkillGapAnalysisSummaryItem {
  id: string;
  role_id: string;
  role_title: string;
  is_current: boolean;
  role_alignment_score: number;
  evidence_coverage_score: number;
  status: string;
  strongest_skills_count: number;
  developing_skills_count: number;
  skill_gaps_count: number;
  missing_skills_count: number;
  unassessed_skills_count: number;
  calculated_at: string;
}

export interface SkillGapHistoryResponse {
  items: SkillGapAnalysisSummaryItem[];
  total: number;
}

export interface SkillEvidenceDetailResponse {
  skill_id: string;
  skill_name: string;
  category: string;
  current_level: number;
  current_tier: string;
  is_verified: boolean;
  evidence_items: SkillEvidenceItem[];
}

// ─── Phase 7: Dynamic Milestone Roadmap Types ─────────────────────────

export interface ResourceUrlItem {
  title: string;
  url: string;
  type: string;
}

export interface RoadmapTaskItem {
  id: string;
  phase_id: string;
  skill_id?: string | null;
  skill_name?: string | null;
  title: string;
  description: string;
  learning_objective?: string | null;
  task_type: 'course' | 'reading' | 'practice' | 'project' | 'assessment';
  priority: 'critical' | 'high' | 'medium' | 'low';
  estimated_hours: number;
  resource_urls: ResourceUrlItem[];
  prerequisite_task_ids: string[];
  deliverable_requirement?: string | null;
  submission_url?: string | null;
  completion_criteria?: string | null;
  status: 'pending' | 'in_progress' | 'completed' | 'skipped';
  due_date?: string | null;
  completed_at?: string | null;
  order_index: number;
  source_gap_priority?: string | null;
}

export interface RoadmapPhaseItem {
  id: string;
  roadmap_id: string;
  title: string;
  description: string;
  objective?: string | null;
  estimated_hours: number;
  prerequisites?: string | null;
  completion_criteria?: string | null;
  status: 'pending' | 'in_progress' | 'completed';
  order_index: number;
  is_completed: boolean;
  tasks: RoadmapTaskItem[];
}

export interface RoadmapData {
  id: string;
  career_profile_id: string;
  target_role_id: string;
  target_role_title: string;
  skill_gap_analysis_id?: string | null;
  title: string;
  description?: string | null;
  version: number;
  is_active: boolean;
  status: string;
  generation_mode: string;
  weekly_hours: number;
  total_estimated_hours: number;
  total_tasks: number;
  completed_tasks: number;
  progress_percentage: number;
  start_date?: string | null;
  target_completion_date?: string | null;
  feasibility_status: 'feasible' | 'demanding' | 'unrealistic';
  feasibility_note?: string | null;
  phases: RoadmapPhaseItem[];
  created_at: string;
  updated_at: string;
}

export interface RoadmapProgressData {
  roadmap_id: string;
  target_role_id: string;
  target_role_title: string;
  total_tasks: number;
  completed_tasks: number;
  pending_tasks: number;
  progress_percentage: number;
  total_estimated_hours: number;
  completed_hours: number;
  remaining_hours: number;
  weekly_hours: number;
  estimated_weeks_remaining: number;
  current_phase_index: number;
  current_phase_title?: string | null;
  next_recommended_tasks: RoadmapTaskItem[];
}

export interface RoadmapGenerateRequestPayload {
  role_id?: string | null;
  weekly_hours?: number | null;
  target_timeline_months?: number | null;
  preferred_resources?: string[] | null;
  focus_areas?: string[] | null;
  force_regenerate?: boolean;
}

export interface UpdateRoadmapTaskPayload {
  status?: 'pending' | 'in_progress' | 'completed' | 'skipped' | null;
  submission_url?: string | null;
}

export interface RoadmapAdaptationData {
  roadmap_id: string;
  adapted: boolean;
  tasks_auto_completed: number;
  tasks_adjusted: number;
  message: string;
  roadmap: RoadmapData;
}

export interface RoadmapHistoryItem {
  id: string;
  target_role_id: string;
  target_role_title: string;
  version: number;
  is_active: boolean;
  status: string;
  generation_mode: string;
  weekly_hours: number;
  total_estimated_hours: number;
  total_tasks: number;
  completed_tasks: number;
  progress_percentage: number;
  created_at: string;
  updated_at: string;
}

export interface RoadmapHistoryResponse {
  items: RoadmapHistoryItem[];
  total: number;
}





