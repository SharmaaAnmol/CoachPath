export type TargetRole =
  | 'Full-Stack Engineer'
  | 'Frontend Engineer'
  | 'Backend Engineer'
  | 'DevOps / Platform Engineer'
  | 'Data Engineer'
  | 'Machine Learning Engineer'
  | 'Mobile Engineer';

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
