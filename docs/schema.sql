-- CoachPath Database Schema (Supabase PostgreSQL + pgvector)
-- Bharat Hackathon 2.0 - AI-Powered Career Intelligence & Job Application Assistant

-- Enable pgvector extension for semantic job matching and RAG retrieval
create extension if not exists vector;

-- 1. profiles (one per user, the central AI context)
create table if not exists profiles (
    user_id uuid primary key,
    full_name text not null,
    target_role text not null,
    target_timeline_months int default 4,
    education_level text,             -- e.g. 'final_year_btech', 'tier_2_3_college'
    experience_level text,            -- 'fresher', '0-2', '2-5'
    hours_per_weekday numeric default 2.0,
    hours_per_weekend numeric default 5.0,
    learning_resources text[] default array['free_only'], -- 'free_only', 'nptel', 'swayam', 'youtube'
    interested_companies text[] default array[]::text[],
    interested_industries text[] default array[]::text[],
    desired_salary_min int default 600000,   -- INR ₹ LPA
    desired_salary_max int default 1500000,  -- INR ₹ LPA
    location text default 'Bengaluru, India',
    work_mode text default 'hybrid',         -- 'remote', 'hybrid', 'onsite'
    onboarding_complete boolean default false,
    updated_at timestamptz default now()
);

-- 2. user_skills (skills claimed or verified)
create table if not exists user_skills (
    id uuid primary key default gen_random_uuid(),
    user_id uuid references profiles(user_id) on delete cascade,
    skill text not null,
    self_level text default 'beginner',       -- beginner / intermediate / advanced
    assessed_level text,                      -- verified by assessment: beginner / intermediate / advanced
    assessed_score int,                       -- 0-100
    last_assessed_at timestamptz,
    unique(user_id, skill)
);

-- 3. user_projects
create table if not exists user_projects (
    id uuid primary key default gen_random_uuid(),
    user_id uuid references profiles(user_id) on delete cascade,
    title text not null,
    description text,
    tech text[],
    link text
);

-- 4. assessments & questions
create table if not exists assessments (
    id uuid primary key default gen_random_uuid(),
    user_id uuid references profiles(user_id) on delete cascade,
    skill text not null,
    status text default 'in_progress',       -- in_progress / completed
    knowledge int default 0,
    problem_solving int default 0,
    practical int default 0,
    industry_readiness int default 0,
    overall int default 0,
    created_at timestamptz default now()
);

create table if not exists assessment_questions (
    id uuid primary key default gen_random_uuid(),
    assessment_id uuid references assessments(id) on delete cascade,
    qtype text not null,                     -- mcq / code / sql / short
    prompt text not null,
    options jsonb,
    answer_key jsonb,
    user_answer text,
    score int,
    feedback text,
    dimension text                           -- Knowledge / Problem Solving / Practical Skills / Industry Readiness
);

-- 5. roadmaps & roadmap_items
create table if not exists roadmaps (
    id uuid primary key default gen_random_uuid(),
    user_id uuid references profiles(user_id) on delete cascade,
    version int default 1,
    generated_at timestamptz default now(),
    is_active boolean default true
);

create table if not exists roadmap_items (
    id uuid primary key default gen_random_uuid(),
    roadmap_id uuid references roadmaps(id) on delete cascade,
    month int not null,
    week int not null,
    title text not null,
    skill text not null,
    priority text not null,                  -- required / improve / recommended / strong
    resources jsonb,                         -- [{"title": "...", "url": "...", "type": "free"}]
    est_hours int not null,
    status text default 'todo'               -- todo / in_progress / completed
);

-- 6. jobs (with vector embeddings)
create table if not exists jobs (
    id uuid primary key default gen_random_uuid(),
    source text not null,                    -- Adzuna / Remotive / Greenhouse / Lever / Seed
    external_id text unique,
    title text not null,
    company text not null,
    location text not null,
    work_mode text default 'hybrid',
    salary_min int,                          -- INR ₹ LPA
    salary_max int,
    description text not null,
    apply_url text not null,
    required_skills text[],
    experience_required text,
    embedding vector(384),                   -- 384-dim all-MiniLM-L6-v2 or text-embedding
    posted_at timestamptz default now(),
    fetched_at timestamptz default now()
);

-- 7. job_matches (explainable scoring)
create table if not exists job_matches (
    user_id uuid references profiles(user_id) on delete cascade,
    job_id uuid references jobs(id) on delete cascade,
    score int not null,                      -- 0-100 weighted score
    breakdown jsonb not null,                -- {skills: 40, semantic: 15, experience: 15, projects: 10, location: 10, salary: 5, edu: 5}
    matched_skills text[],
    missing_skills text[],
    reason text not null,
    primary key (user_id, job_id)
);

-- 8. resumes
create table if not exists resumes (
    id uuid primary key default gen_random_uuid(),
    user_id uuid references profiles(user_id) on delete cascade,
    kind text not null,                      -- master / tailored
    label text not null,                     -- e.g. 'Master Resume', 'ML Engineer Tailored'
    parent_id uuid references resumes(id),
    file_path text,
    content jsonb not null,                  -- structured JSON resume
    target_job_id uuid references jobs(id),
    ats_score int default 0,
    created_at timestamptz default now()
);

-- 9. applications (the tracker)
create table if not exists applications (
    id uuid primary key default gen_random_uuid(),
    user_id uuid references profiles(user_id) on delete cascade,
    job_id uuid references jobs(id),
    company text not null,
    role text not null,
    job_url text,
    resume_id uuid references resumes(id),
    match_score int,
    status text default 'saved',             -- saved / applied / recruiter_contacted / response / interview / offer / rejected
    applied_on date,
    response text,
    notes text,
    created_at timestamptz default now(),
    updated_at timestamptz default now()
);

-- 10. outreach drafts
create table if not exists outreach (
    id uuid primary key default gen_random_uuid(),
    user_id uuid references profiles(user_id) on delete cascade,
    application_id uuid references applications(id) on delete cascade,
    recruiter_name text,
    recruiter_role text,
    channel text default 'LinkedIn',
    draft text not null,
    status text default 'draft',             -- draft / approved / sent / discarded
    approved_at timestamptz
);

-- 11. interviews & prep items
create table if not exists interviews (
    id uuid primary key default gen_random_uuid(),
    user_id uuid references profiles(user_id) on delete cascade,
    application_id uuid references applications(id) on delete cascade,
    starts_at timestamptz not null,
    ends_at timestamptz,
    round text not null,                     -- Technical Round 1, System Design, HR
    itype text not null,                     -- video, on-site, phone
    topics text[],
    ics_path text
);

create table if not exists prep_items (
    id uuid primary key default gen_random_uuid(),
    interview_id uuid references interviews(id) on delete cascade,
    title text not null,
    done boolean default false,
    skill text
);

-- 12. readiness snapshots
create table if not exists readiness_snapshots (
    id uuid primary key default gen_random_uuid(),
    user_id uuid references profiles(user_id) on delete cascade,
    overall int not null,
    technical int not null,
    dsa int not null,
    projects int not null,
    resume int not null,
    interview int not null,
    industry int not null,
    job_readiness int not null,
    created_at timestamptz default now()
);

-- 13. audit log (Responsible AI & human approval gates)
create table if not exists audit_log (
    id bigserial primary key,
    user_id uuid references profiles(user_id) on delete cascade,
    action text not null,                    -- application_approved, outreach_approved, data_exported, data_deleted
    entity text not null,
    entity_id uuid,
    payload jsonb,
    approved_by_user boolean default true,
    created_at timestamptz default now()
);

-- Row Level Security (RLS)
alter table profiles enable row level security;
alter table user_skills enable row level security;
alter table user_projects enable row level security;
alter table assessments enable row level security;
alter table roadmaps enable row level security;
alter table job_matches enable row level security;
alter table resumes enable row level security;
alter table applications enable row level security;
alter table outreach enable row level security;
alter table interviews enable row level security;
alter table readiness_snapshots enable row level security;
alter table audit_log enable row level security;
