import {
  UserCareerProfile,
  SkillItem,
  Assessment,
  RoadmapPhase,
  JobListing,
  ResumeVersion,
  ApplicationItem,
  RecruiterContact,
  ScheduledInterview,
  CareerReadinessData,
} from '@/types';

export const mockProfile: UserCareerProfile = {
  id: 'usr_aarav_01',
  name: 'Aarav Mehta',
  title: 'Full-Stack Software Engineer',
  email: 'aarav.mehta@example.com',
  avatarUrl: 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150&auto=format&fit=crop&q=80',
  targetRole: 'Full-Stack Engineer',
  secondaryRoles: ['Backend Engineer', 'DevOps / Platform Engineer'],
  yearsExperience: 2.5,
  bio: 'Product-focused full-stack engineer passionate about low-latency distributed APIs, modern React architectures, and robust PostgreSQL schemas.',
  location: 'San Francisco, CA (Hybrid / Remote)',
  education: [
    {
      id: 'edu_1',
      institution: 'University of Washington',
      degree: 'B.S. in Computer Science',
      fieldOfStudy: 'Software Engineering & Database Systems',
      startDate: '2019-09',
      endDate: '2023-06',
      grade: '3.82 GPA',
    },
  ],
  experience: [
    {
      id: 'exp_1',
      company: 'Apex Cloud Solutions',
      role: 'Full-Stack Software Engineer',
      location: 'Seattle, WA',
      startDate: '2023-07',
      current: true,
      description: [
        'Architected and deployed asynchronous task processing pipelines handling 250,000+ daily webhooks with 99.98% reliability.',
        'Migrated legacy monolithic endpoints to modular RESTful microservices using FastAPI, Redis caching, and PostgreSQL.',
        'Built dynamic dashboard interfaces in Next.js 14 and Tailwind CSS, reducing average page load latency by 42%.',
      ],
      skillsUsed: ['TypeScript', 'React', 'Node.js', 'PostgreSQL', 'Docker', 'Redis'],
    },
    {
      id: 'exp_2',
      company: 'Novatech Labs',
      role: 'Software Engineering Intern',
      location: 'Bellevue, WA',
      startDate: '2022-06',
      endDate: '2022-09',
      current: false,
      description: [
        'Developed end-to-end telemetry reporting widgets used by 45 internal enterprise customer support teams.',
        'Engineered SQL query optimization scripts that decreased 95th percentile database query times by 35%.',
      ],
      skillsUsed: ['Python', 'PostgreSQL', 'React', 'Git'],
    },
  ],
  projects: [
    {
      id: 'proj_1',
      title: 'Distributed Event Broker & Metrics Exporter',
      description:
        'A high-throughput pub/sub prototype leveraging Redis Streams and WebSockets to broadcast live server metrics to connected web clients.',
      technologies: ['TypeScript', 'Node.js', 'Redis', 'WebSockets', 'Docker'],
      githubUrl: 'https://github.com/aaravmehta/distributed-metrics-broker',
      liveUrl: 'https://metrics-broker-demo.vercel.app',
      verifiedEvidence: true,
    },
    {
      id: 'proj_2',
      title: 'QueryLens: PostgreSQL Slow-Query Analyzer',
      description:
        'Developer CLI tool that parses raw PostgreSQL EXPLAIN ANALYZE traces and suggests optimal compound indexes.',
      technologies: ['TypeScript', 'PostgreSQL', 'Node.js'],
      githubUrl: 'https://github.com/aaravmehta/querylens-pg',
      verifiedEvidence: true,
    },
  ],
  certifications: [
    {
      id: 'cert_1',
      name: 'AWS Certified Solutions Architect – Associate',
      issuingOrganization: 'Amazon Web Services',
      issueDate: '2023-11',
      credentialId: 'AWS-ASA-894102',
    },
  ],
  skills: [], // Referenced from mockSkills
};

export const mockSkills: SkillItem[] = [
  // Verified Strengths
  {
    id: 'skl_ts',
    name: 'TypeScript',
    category: 'Languages',
    proficiency: 'Advanced',
    status: 'verified',
    confidenceScore: 92,
    evidenceSource: 'Assessment',
    lastEvaluated: '2026-09-15',
  },
  {
    id: 'skl_react',
    name: 'React / Next.js',
    category: 'Frameworks',
    proficiency: 'Advanced',
    status: 'verified',
    confidenceScore: 88,
    evidenceSource: 'Assessment',
    lastEvaluated: '2026-09-18',
  },
  {
    id: 'skl_node',
    name: 'Node.js / Express',
    category: 'Frameworks',
    proficiency: 'Advanced',
    status: 'verified',
    confidenceScore: 86,
    evidenceSource: 'Resume',
    lastEvaluated: '2026-09-12',
  },
  {
    id: 'skl_pg',
    name: 'PostgreSQL & SQL Tuning',
    category: 'Databases',
    proficiency: 'Advanced',
    status: 'verified',
    confidenceScore: 84,
    evidenceSource: 'Assessment',
    lastEvaluated: '2026-09-20',
  },
  {
    id: 'skl_docker',
    name: 'Docker & Containerization',
    category: 'Cloud & DevOps',
    proficiency: 'Intermediate',
    status: 'verified',
    confidenceScore: 78,
    evidenceSource: 'Project',
    lastEvaluated: '2026-09-10',
  },
  {
    id: 'skl_rest',
    name: 'RESTful API Architecture',
    category: 'Architecture',
    proficiency: 'Advanced',
    status: 'verified',
    confidenceScore: 90,
    evidenceSource: 'Resume',
    lastEvaluated: '2026-09-14',
  },
  // Developing Skills
  {
    id: 'skl_redis',
    name: 'Redis In-Memory Caching',
    category: 'Databases',
    proficiency: 'Intermediate',
    status: 'developing',
    confidenceScore: 65,
    evidenceSource: 'Project',
    lastEvaluated: '2026-09-22',
  },
  {
    id: 'skl_sysdesign',
    name: 'Distributed Systems & Scaling',
    category: 'Architecture',
    proficiency: 'Intermediate',
    status: 'developing',
    confidenceScore: 60,
    evidenceSource: 'Self-Reported',
    lastEvaluated: '2026-09-05',
  },
  {
    id: 'skl_graphql',
    name: 'GraphQL API Design',
    category: 'Architecture',
    proficiency: 'Intermediate',
    status: 'developing',
    confidenceScore: 58,
    evidenceSource: 'Self-Reported',
    lastEvaluated: '2026-08-30',
  },
  // Missing Skills (Identified Gaps for Target Senior Roles)
  {
    id: 'skl_k8s',
    name: 'Kubernetes Cluster Orchestration',
    category: 'Cloud & DevOps',
    proficiency: 'Beginner',
    status: 'missing',
    confidenceScore: 15,
    evidenceSource: 'Self-Reported',
  },
  {
    id: 'skl_otel',
    name: 'Distributed Tracing (OpenTelemetry)',
    category: 'Cloud & DevOps',
    proficiency: 'Beginner',
    status: 'missing',
    confidenceScore: 20,
    evidenceSource: 'Self-Reported',
  },
  {
    id: 'skl_kafka',
    name: 'Apache Kafka Event Streams',
    category: 'Databases',
    proficiency: 'Beginner',
    status: 'missing',
    confidenceScore: 10,
    evidenceSource: 'Self-Reported',
  },
];

mockProfile.skills = mockSkills;

export const mockAssessments: Assessment[] = [
  {
    id: 'asmt_ts_core',
    title: 'TypeScript Advanced Type System & Generics',
    domain: 'Software Engineering Core',
    skillName: 'TypeScript',
    difficulty: 'Advanced',
    durationMinutes: 25,
    questionCount: 15,
    status: 'completed',
    score: 92,
    completedAt: '2026-09-15',
  },
  {
    id: 'asmt_pg_tune',
    title: 'PostgreSQL Indexing Strategies & Query Optimization',
    domain: 'Database Engineering',
    skillName: 'PostgreSQL & SQL Tuning',
    difficulty: 'Intermediate',
    durationMinutes: 30,
    questionCount: 18,
    status: 'completed',
    score: 84,
    completedAt: '2026-09-20',
  },
  {
    id: 'asmt_redis_streams',
    title: 'Redis Caching Patterns, Eviction & Streams',
    domain: 'In-Memory Data Structures',
    skillName: 'Redis In-Memory Caching',
    difficulty: 'Intermediate',
    durationMinutes: 20,
    questionCount: 12,
    status: 'available',
  },
  {
    id: 'asmt_sys_design_micro',
    title: 'System Design: Resilient Microservices & Rate Limiting',
    domain: 'Distributed Architecture',
    skillName: 'Distributed Systems & Scaling',
    difficulty: 'Advanced',
    durationMinutes: 45,
    questionCount: 20,
    status: 'available',
  },
  {
    id: 'asmt_k8s_foundations',
    title: 'Kubernetes Workloads, Ingress & Deployments',
    domain: 'Cloud Infrastructure',
    skillName: 'Kubernetes Cluster Orchestration',
    difficulty: 'Beginner',
    durationMinutes: 25,
    questionCount: 15,
    status: 'available',
  },
];

export const mockRoadmapPhases: RoadmapPhase[] = [
  {
    id: 'ph_1',
    phaseNumber: 1,
    title: 'High-Performance Caching & Data Consistency',
    timeline: 'Weeks 1 – 3 (Current)',
    status: 'in_progress',
    progressPercentage: 75,
    tasks: [
      {
        id: 'tsk_101',
        title: 'Master Cache-Aside and Write-Through Strategies in Redis',
        description: 'Implement distributed locking with Redlock and evaluate race conditions during cache invalidation.',
        estimatedHours: 6,
        status: 'completed',
        category: 'Skill Mastery',
        resourceTitle: 'Redis University: Real-Time Cache Architectures',
        resourceUrl: 'https://university.redis.io',
        deliverableRequired: 'Code review artifact implementing Redis cache aside with TTL and fallback.',
        completedAt: '2026-09-25',
      },
      {
        id: 'tsk_102',
        title: 'Build Distributed Rate Limiter with Sliding Window Counter',
        description: 'Create an Express/FastAPI middleware implementing sliding log rate limiting using Redis Sorted Sets.',
        estimatedHours: 8,
        status: 'completed',
        category: 'System Project',
        resourceTitle: 'System Design Primer: Rate Limiting Algorithms',
        resourceUrl: 'https://github.com/donnemartin/system-design-primer',
        deliverableRequired: 'Automated test suite verifying 1,000 req/min threshold enforcement.',
        completedAt: '2026-10-02',
      },
      {
        id: 'tsk_103',
        title: 'Take Redis Architecture Diagnostic Assessment',
        description: 'Verify conceptual mastery across key eviction policies (LRU, LFU) and pub/sub message loss semantics.',
        estimatedHours: 2,
        status: 'in_progress',
        category: 'Interview Drill',
        resourceTitle: 'CoachPath Assessment Suite: Redis In-Memory Architectures',
        resourceUrl: '/assessments',
        deliverableRequired: 'Achieve score >= 80% to calibrate confidence to Verified status.',
      },
    ],
  },
  {
    id: 'ph_2',
    phaseNumber: 2,
    title: 'Distributed Event Streaming & Observability',
    timeline: 'Weeks 4 – 6',
    status: 'upcoming',
    progressPercentage: 10,
    tasks: [
      {
        id: 'tsk_201',
        title: 'Apache Kafka Partitioning & Idempotent Consumer Patterns',
        description: 'Model guaranteed order processing across distributed partitions with dead-letter queue recovery.',
        estimatedHours: 12,
        status: 'in_progress',
        category: 'Skill Mastery',
        resourceTitle: 'Confluent Developer: Kafka Internals Deep Dive',
        resourceUrl: 'https://developer.confluent.io',
        deliverableRequired: 'Working Docker Compose setup with consumer group rebalance simulation.',
      },
      {
        id: 'tsk_202',
        title: 'Implement OpenTelemetry Distributed Context Propagation',
        description: 'Instrument HTTP and async worker services with W3C TraceContext headers.',
        estimatedHours: 10,
        status: 'upcoming',
        category: 'Portfolio Artifact',
        resourceTitle: 'OpenTelemetry Node.js / Python Integration Docs',
        resourceUrl: 'https://opentelemetry.io',
        deliverableRequired: 'Jaeger tracing screenshot demonstrating trace span linking across 3 microservices.',
      },
    ],
  },
  {
    id: 'ph_3',
    phaseNumber: 3,
    title: 'Production Infrastructure & System Design Mastery',
    timeline: 'Weeks 7 – 9',
    status: 'upcoming',
    progressPercentage: 0,
    tasks: [
      {
        id: 'tsk_301',
        title: 'Deploy Multi-Container App to Kubernetes Minikube / EKS',
        description: 'Author manifests for Deployment, ClusterIP Service, Ingress Controller, and Horizontal Pod Autoscaler.',
        estimatedHours: 14,
        status: 'upcoming',
        category: 'System Project',
        resourceTitle: 'Kubernetes Official Docs: Production Workloads',
        resourceUrl: 'https://kubernetes.io/docs',
        deliverableRequired: 'Helm chart repository and automated rolling update log.',
      },
      {
        id: 'tsk_302',
        title: 'Simulate Staff-Level System Design Interview: Global E-Commerce',
        description: 'Practice interactive whiteboarding answering latency constraints, data sharding, and CDN caching.',
        estimatedHours: 4,
        status: 'upcoming',
        category: 'Interview Drill',
        resourceTitle: 'CoachPath Question Bank: Distributed Systems',
        resourceUrl: '/interviews',
        deliverableRequired: 'Audio/Transcript self-evaluation against STAR rubric.',
      },
    ],
  },
];

export const mockJobs: JobListing[] = [
  {
    id: 'job_stripe_01',
    title: 'Senior Full-Stack Engineer, Connect Infrastructure',
    company: 'Stripe',
    location: 'San Francisco, CA / Seattle, WA',
    remoteType: 'Hybrid',
    salaryRange: '$185,000 – $235,000 + Equity',
    matchScore: 94,
    postedDate: '2026-10-04',
    description:
      'We are looking for engineers to design and scale the next generation of Stripe Connect payment routing infrastructure. You will work across modern React frontends, robust Node/Ruby distributed services, and high-reliability PostgreSQL datastores.',
    requirements: [
      '3+ years professional experience building web applications at scale',
      'Strong expertise in TypeScript, React, and Node.js',
      'Solid foundation in relational database schema design and SQL optimization',
      'Experience with distributed caching (Redis) and high availability',
    ],
    matchedSkills: ['TypeScript', 'React', 'Node.js', 'PostgreSQL & SQL Tuning', 'RESTful API Architecture', 'Docker'],
    missingSkills: ['Kubernetes Cluster Orchestration'],
    breakdown: {
      skillsScore: 95,
      experienceScore: 90,
      domainScore: 96,
      roleSimilarityScore: 94,
    },
    applicationDeadline: '2026-10-25',
  },
  {
    id: 'job_linear_02',
    title: 'Product Engineer (Full-Stack)',
    company: 'Linear',
    location: 'San Francisco, CA',
    remoteType: 'Remote',
    salaryRange: '$170,000 – $210,000 + 0.15% Equity',
    matchScore: 91,
    postedDate: '2026-10-02',
    description:
      'Linear is crafting modern product management software. We care deeply about keyboard navigation, offline synchronization, and sub-100ms response times. You will help build our collaborative desktop and web clients.',
    requirements: [
      'Deep mastery of TypeScript, React component lifecycles, and Tailwind CSS',
      'Experience with client-side synchronization engines and local-first architecture',
      'Proficiency designing predictable REST and WebSocket event APIs',
    ],
    matchedSkills: ['TypeScript', 'React / Next.js', 'Node.js / Express', 'RESTful API Architecture'],
    missingSkills: ['GraphQL API Design', 'Distributed Systems & Scaling'],
    breakdown: {
      skillsScore: 92,
      experienceScore: 88,
      domainScore: 94,
      roleSimilarityScore: 90,
    },
    applicationDeadline: '2026-10-28',
  },
  {
    id: 'job_vercel_03',
    title: 'Backend / Platform Engineer',
    company: 'Vercel',
    location: 'San Francisco, CA',
    remoteType: 'Remote',
    salaryRange: '$175,000 – $220,000 + Equity',
    matchScore: 87,
    postedDate: '2026-09-29',
    description:
      'Help power the edge network and build serverless infrastructure for millions of developers worldwide. You will maintain microservices, write low-latency middleware, and ensure five-nines availability.',
    requirements: [
      'Strong proficiency with TypeScript / Node.js and distributed cloud environments',
      'Hands-on experience with containerization, telemetry, and observability',
      'Demonstrated understanding of HTTP/2, edge routing, and caching primitives',
    ],
    matchedSkills: ['TypeScript', 'Node.js', 'Docker', 'RESTful API Architecture', 'PostgreSQL'],
    missingSkills: ['Distributed Tracing (OpenTelemetry)', 'Kubernetes'],
    breakdown: {
      skillsScore: 85,
      experienceScore: 86,
      domainScore: 90,
      roleSimilarityScore: 88,
    },
    applicationDeadline: '2026-11-01',
  },
  {
    id: 'job_datadog_04',
    title: 'Software Engineer II – Telemetry Pipeline',
    company: 'Datadog',
    location: 'New York, NY',
    remoteType: 'Hybrid',
    salaryRange: '$165,000 – $205,000 + Stock',
    matchScore: 81,
    postedDate: '2026-09-24',
    description:
      'Datadog processes trillions of events daily. As a backend engineer on the ingestion team, you will build pipelines that collect, buffer, and index metrics, traces, and logs from customer servers.',
    requirements: [
      'Solid systems programming experience with distributed message streams',
      'Understanding of Kafka, event buffering, and backpressure handling',
      'Commitment to automated testing and reliable CI/CD delivery',
    ],
    matchedSkills: ['TypeScript', 'Docker', 'RESTful API Architecture'],
    missingSkills: ['Apache Kafka Event Streams', 'Distributed Tracing (OpenTelemetry)', 'Kubernetes'],
    breakdown: {
      skillsScore: 78,
      experienceScore: 82,
      domainScore: 84,
      roleSimilarityScore: 80,
    },
    applicationDeadline: '2026-10-31',
  },
];

export const mockResumeVersion: ResumeVersion = {
  id: 'res_v2_stripe',
  versionName: 'Tailored for Stripe (Connect Infrastructure)',
  targetJobTitle: 'Senior Full-Stack Engineer',
  targetCompany: 'Stripe',
  createdAt: '2026-10-05',
  matchScoreBoost: 12, // From 82% to 94%
  changes: [
    {
      id: 'diff_1',
      section: 'Work Experience – Apex Cloud Solutions',
      originalText:
        'Worked on backend services and database queries for webhooks, fixing slow queries when traffic spiked.',
      suggestedText:
        'Architected asynchronous webhook ingestion engine handling 250,000+ daily events, tuning PostgreSQL B-tree indices to eliminate query bottlenecks and sustain 99.98% uptime.',
      rationale:
        'Quantifies throughput and highlights proven PostgreSQL optimization skills that directly match Stripe Connect requirements, without hallucinating unverified claims.',
      evidenceReference: 'Verified in Project: QueryLens & Assessment: PostgreSQL Indexing (84%)',
      status: 'accepted',
    },
    {
      id: 'diff_2',
      section: 'Skills Summary',
      originalText: 'Skills: JavaScript, Node, React, Databases, AWS, Git',
      suggestedText:
        'Languages & Frameworks: TypeScript (Strong), React 18, Node.js\nDatastores & Infrastructure: PostgreSQL (EXPLAIN tuning), Redis Caching, Docker, AWS (Solutions Architect Associate)',
      rationale:
        'Groups skills hierarchically to pass enterprise ATS keyword parsers while explicitly calling out verified certifications.',
      evidenceReference: 'AWS Certified Solutions Architect & Verified Skill: TypeScript (92%)',
      status: 'accepted',
    },
    {
      id: 'diff_3',
      section: 'Projects – Distributed Event Broker',
      originalText: 'A project using Redis and WebSockets for server metrics.',
      suggestedText:
        'Engineered an open-source distributed metrics exporter leveraging Redis Streams and sliding-window rate limiting to stream telemetry to 500+ concurrent WebSockets clients.',
      rationale:
        'Explicitly mentions Redis Streams and sliding-window rate limits, which are high-value keywords for payment network microservices.',
      evidenceReference: 'Verified GitHub Project: distributed-metrics-broker',
      status: 'pending',
    },
  ],
  fullMarkdown: `# Aarav Mehta
**Full-Stack Software Engineer** | San Francisco, CA | aarav.mehta@example.com | [GitHub](https://github.com/aaravmehta)

---

### Professional Summary
Full-stack software engineer with 2.5+ years experience building low-latency web applications and distributed backend microservices. Proven track record optimizing relational schemas in PostgreSQL, instrumenting Redis caching pipelines, and crafting responsive UI systems in Next.js and TypeScript.

---

### Technical Skills
- **Languages:** TypeScript, JavaScript, SQL, Python
- **Frontend:** React, Next.js (App Router), Tailwind CSS, State Management
- **Backend & Cloud:** Node.js, Express, FastAPI, Docker, AWS (Certified Solutions Architect Associate)
- **Databases & Caching:** PostgreSQL (Query Tuning, Indexing), Redis (Streams, Distributed Locks)

---

### Experience
**Apex Cloud Solutions** — Full-Stack Software Engineer *(July 2023 – Present)*
- Architected asynchronous webhook ingestion engine handling 250,000+ daily events, tuning PostgreSQL B-tree indices to eliminate query bottlenecks and sustain 99.98% uptime.
- Deployed modular REST microservices with Redis caching, reducing tail latency by 35%.
- Built analytics dashboards in Next.js 14 and Tailwind CSS, improving core web vitals by 42%.

---

### Selected Projects
**Distributed Event Broker & Metrics Exporter** *(TypeScript, Node.js, Redis, Docker)*
- Engineered an open-source distributed metrics exporter leveraging Redis Streams and sliding-window rate limiting to stream telemetry to 500+ concurrent WebSockets clients.

**QueryLens: PostgreSQL Slow-Query Analyzer** *(TypeScript, PostgreSQL)*
- CLI utility parsing raw EXPLAIN ANALYZE execution trees and suggesting compound index candidates.
`,
};

export const mockApplications: ApplicationItem[] = [
  {
    id: 'app_1',
    jobId: 'job_stripe_01',
    company: 'Stripe',
    roleTitle: 'Senior Full-Stack Engineer, Connect Infrastructure',
    location: 'San Francisco, CA',
    salary: '$185k - $235k',
    stage: 'interviewing',
    appliedDate: '2026-10-04',
    nextStep: 'System Design & Architecture Deep Dive (Tomorrow, 2:00 PM)',
    matchScore: 94,
    notes: 'Tailored resume v2 submitted. Recruiter Sarah Jenkins responded within 24 hours.',
    contactName: 'Sarah Jenkins (Technical Talent Lead)',
  },
  {
    id: 'app_2',
    jobId: 'job_linear_02',
    company: 'Linear',
    roleTitle: 'Product Engineer (Full-Stack)',
    location: 'Remote',
    salary: '$170k - $210k',
    stage: 'applied',
    appliedDate: '2026-10-05',
    nextStep: 'Waiting for initial portfolio & resume screening review',
    matchScore: 91,
    notes: 'Submitted link to QueryLens GitHub repository showcasing craftsmanship.',
  },
  {
    id: 'app_3',
    jobId: 'job_vercel_03',
    company: 'Vercel',
    roleTitle: 'Backend / Platform Engineer',
    location: 'Remote',
    salary: '$175k - $220k',
    stage: 'saved',
    nextStep: 'Complete Roadmap Phase 1 before submitting tailored resume',
    matchScore: 87,
    notes: 'Plan to highlight AWS Solutions Architect and Redis caching benchmarks.',
  },
  {
    id: 'app_4',
    jobId: 'job_datadog_04',
    company: 'Datadog',
    roleTitle: 'Software Engineer II – Telemetry Pipeline',
    location: 'New York, NY',
    salary: '$165k - $205k',
    stage: 'saved',
    nextStep: 'Waiting to complete Kafka event streams task in Phase 2',
    matchScore: 81,
    notes: 'Requires Kafka experience; will finish task 201 before applying.',
  },
];

export const mockRecruiters: RecruiterContact[] = [
  {
    id: 'rec_1',
    name: 'Sarah Jenkins',
    role: 'Staff Technical Talent Lead',
    company: 'Stripe',
    linkedInUrl: 'https://linkedin.com/in/sarah-jenkins-tech',
    verifiedEmail: 'sjenkins@stripe.com',
    relevanceReason: 'Direct recruiter for Connect Infrastructure and Core Payments engineering teams.',
    outreachDraftSubject: 'Aarav Mehta – Full-Stack Engineer candidate for Stripe Connect Infra',
    outreachDraftBody:
      'Hi Sarah,\n\nI noticed Stripe is expanding the Connect Infrastructure team. Over the past 2.5 years at Apex Cloud, I designed our asynchronous event ingestion pipeline scaling past 250k daily webhooks while maintaining 99.98% reliability.\n\nI recently completed an in-depth project analyzing PostgreSQL query plans and benchmarked Redis streaming architectures. Given Stripe Connect’s focus on payment routing and extreme reliability, I would love to connect for 10 minutes to discuss how my background aligns with your team’s upcoming roadmap.\n\nBest regards,\nAarav Mehta\nGitHub: github.com/aaravmehta',
    copiedToClipboard: true,
  },
  {
    id: 'rec_2',
    name: 'Marcus Chen',
    role: 'Engineering Recruiting Lead',
    company: 'Linear',
    linkedInUrl: 'https://linkedin.com/in/marcus-chen-linear',
    verifiedEmail: 'marcus@linear.app',
    relevanceReason: 'Hiring product engineers with obsessive focus on UI speed and TypeScript craftsmanship.',
    outreachDraftSubject: 'Full-Stack Product Engineer application – Aarav Mehta',
    outreachDraftBody:
      'Hi Marcus,\n\nI’ve followed Linear’s product journey closely and love your focus on zero-latency interactions and clean UI architectures. As a full-stack engineer, I specialize in TypeScript, modern React component performance, and clean SQL backends.\n\nI built QueryLens, an open-source tool analyzing PostgreSQL execution plans, and have been practicing local-first state synchronization patterns. I’d love to submit my tailored portfolio for the Product Engineer role.\n\nThanks,\nAarav Mehta',
    copiedToClipboard: false,
  },
  {
    id: 'rec_3',
    name: 'Elena Rostova',
    role: 'Senior Technical Recruiter',
    company: 'Vercel',
    linkedInUrl: 'https://linkedin.com/in/elena-rostova-vercel',
    verifiedEmail: 'elena.r@vercel.com',
    relevanceReason: 'Leading sourcing for Next.js platform and backend edge infrastructure engineers.',
    outreachDraftSubject: 'Backend / Platform Engineer – Aarav Mehta',
    outreachDraftBody:
      'Hi Elena,\n\nI am a certified AWS Solutions Architect and full-stack engineer who builds high-throughput services with TypeScript and Docker. I love Vercel’s edge platform and have spent significant time benchmarking Redis distributed caching against cold-start latencies.\n\nI would be excited to learn more about the team’s current priorities for the Backend / Platform Engineer position.\n\nBest,\nAarav Mehta',
    copiedToClipboard: false,
  },
];

export const mockScheduledInterviews: ScheduledInterview[] = [
  {
    id: 'int_1',
    company: 'Stripe',
    role: 'Senior Full-Stack Engineer, Connect Infrastructure',
    roundType: 'System Design',
    dateTime: 'Tomorrow at 2:00 PM EST',
    interviewerName: 'David K. & Priya S.',
    interviewerTitle: 'Staff Infrastructure Engineers',
    prepCompletedPercentage: 80,
    questions: [
      {
        id: 'q_1',
        question:
          'Design an idempotent webhook delivery system handling 500,000 events/sec with retry backoff and exactly-once delivery guarantees.',
        category: 'System Architecture',
        difficulty: 'Staff-Level',
        suggestedSTAR: {
          situation:
            'At Apex Cloud, our customers experienced intermittent duplicate charges due to unacknowledged webhook timeouts during network degradation.',
          task: 'I was tasked with redesigning the ingestion pipeline to guarantee idempotency and graceful exponential backoff.',
          action:
            'Introduced unique idempotency keys in Redis with 24-hour TTLs, wrapped Postgres transaction commits in atomic blocks, and designed a dead-letter queue with jittered exponential backoff.',
          result:
            'Eliminated 100% of duplicate event processing while scaling pipeline capacity to 250k+ daily events with 99.98% uptime.',
        },
        keyTalkingPoints: [
          'Mention distributed locking with Redis Redlock vs. single-instance keys.',
          'Address database transactional boundaries with outbox pattern.',
          'Explain why true exactly-once processing across network partitions requires consumer idempotency.',
        ],
      },
      {
        id: 'q_2',
        question:
          'Walk us through how you would optimize a PostgreSQL query taking 3.5 seconds on a table with 20 million rows.',
        category: 'Technical Deep-Dive',
        difficulty: 'Challenging',
        keyTalkingPoints: [
          'Run EXPLAIN (ANALYZE, BUFFERS) to inspect sequential scans vs index scans.',
          'Check for missing composite indexes or non-sargable WHERE predicates (e.g. UPPER() functions).',
          'Evaluate table bloat and autovacuum tuning parameters.',
          'Consider partitioning if time-series data is segmented by calendar month.',
        ],
      },
      {
        id: 'q_3',
        question:
          'Tell me about a time you strongly disagreed with an architectural decision made by a senior teammate and how you navigated it.',
        category: 'Behavioral',
        difficulty: 'Standard',
        suggestedSTAR: {
          situation:
            'A team lead advocated for adopting an unproven NoSQL document store to handle audit logs to bypass SQL schema migrations.',
          task: 'I needed to evaluate the long-term reliability and query needs without causing friction or slowing the project.',
          action:
            'Set up a prototype benchmark measuring operational cost, ACID compliance, and team familiarity. Demonstrated that PostgreSQL JSONB with GIN indexing satisfied all flexible schema needs while preserving transactions.',
          result:
            'The team unanimously adopted the PostgreSQL JSONB approach, saving an estimated 3 weeks of DevOps provisioning and zero migration issues.',
        },
        keyTalkingPoints: [
          'Focus on collaborative data-driven benchmarking over ego.',
          'Highlight respect for delivery deadlines and operational simplicity.',
        ],
      },
    ],
  },
];

export const mockReadinessData: CareerReadinessData = {
  overallScore: 78,
  targetRole: 'Full-Stack Engineer',
  keyMilestonesCompleted: 7,
  totalKeyMilestones: 9,
  pillars: {
    skillVerification: {
      name: 'Verified Skill Competency',
      weight: 0.35,
      score: 82,
      status: 'strong',
      summary:
        'Strong validated scores across TypeScript (92%), React (88%), and PostgreSQL (84%). Ready for high-bar engineering screens.',
      recommendations: [
        'Complete the Redis In-Memory Architecture assessment to verify caching competency.',
        'Target Kubernetes foundations in Roadmap Phase 3 to unlock senior DevOps requirements.',
      ],
    },
    practicalProjects: {
      name: 'Demonstrated Engineering Evidence',
      weight: 0.25,
      score: 75,
      status: 'moderate',
      summary:
        'Two strong verified GitHub projects demonstrating distributed metrics and SQL query tuning.',
      recommendations: [
        'Finalize OpenTelemetry tracing instrumented repository to showcase production observability.',
        'Add live demo URL with latency benchmark graphs to QueryLens repository.',
      ],
    },
    marketRelevance: {
      name: 'Target Market Alignment',
      weight: 0.25,
      score: 85,
      status: 'strong',
      summary:
        '94% match for top tier tech firms (Stripe, Linear). Resume tailored with high keyword semantic alignment.',
      recommendations: [
        'Apply tailored resume v2 to Stripe Connect Infrastructure before Oct 25 deadline.',
        'Reach out to Marcus Chen at Linear via personalized draft.',
      ],
    },
    interviewFluency: {
      name: 'Interview & STAR Preparedness',
      weight: 0.15,
      score: 70,
      status: 'moderate',
      summary:
        'Completed System Design idempotency STAR preparation for upcoming Stripe round. Behavioral stories drafted.',
      recommendations: [
        'Review the PostgreSQL 20M row EXPLAIN ANALYZE deep-dive talking points.',
        'Practice STAR responses out loud using the STAR structured drill notes.',
      ],
    },
  },
};
