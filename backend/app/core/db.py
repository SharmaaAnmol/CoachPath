import sqlite3
import json
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
from app.core.config import settings

def get_connection():
    """Returns a SQLite connection configured with Row factory."""
    conn = sqlite3.connect(str(settings.DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes local database tables matching docs/schema.sql."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.executescript("""
    CREATE TABLE IF NOT EXISTS profiles (
        user_id TEXT PRIMARY KEY,
        full_name TEXT NOT NULL,
        target_role TEXT NOT NULL,
        target_timeline_months INTEGER DEFAULT 4,
        education_level TEXT,
        experience_level TEXT,
        hours_per_weekday REAL DEFAULT 2.0,
        hours_per_weekend REAL DEFAULT 5.0,
        learning_resources TEXT DEFAULT '["free_only"]',
        interested_companies TEXT DEFAULT '[]',
        interested_industries TEXT DEFAULT '[]',
        desired_salary_min INTEGER DEFAULT 600000,
        desired_salary_max INTEGER DEFAULT 1500000,
        location TEXT DEFAULT 'Bengaluru, India',
        work_mode TEXT DEFAULT 'hybrid',
        onboarding_complete BOOLEAN DEFAULT 0,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS user_skills (
        id TEXT PRIMARY KEY,
        user_id TEXT,
        skill TEXT NOT NULL,
        self_level TEXT DEFAULT 'beginner',
        assessed_level TEXT,
        assessed_score INTEGER,
        last_assessed_at TIMESTAMP,
        UNIQUE(user_id, skill),
        FOREIGN KEY(user_id) REFERENCES profiles(user_id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS user_projects (
        id TEXT PRIMARY KEY,
        user_id TEXT,
        title TEXT NOT NULL,
        description TEXT,
        tech TEXT DEFAULT '[]',
        link TEXT,
        FOREIGN KEY(user_id) REFERENCES profiles(user_id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS assessments (
        id TEXT PRIMARY KEY,
        user_id TEXT,
        skill TEXT NOT NULL,
        status TEXT DEFAULT 'in_progress',
        knowledge INTEGER DEFAULT 0,
        problem_solving INTEGER DEFAULT 0,
        practical INTEGER DEFAULT 0,
        industry_readiness INTEGER DEFAULT 0,
        overall INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES profiles(user_id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS assessment_questions (
        id TEXT PRIMARY KEY,
        assessment_id TEXT,
        qtype TEXT NOT NULL,
        prompt TEXT NOT NULL,
        options TEXT,
        answer_key TEXT,
        user_answer TEXT,
        score INTEGER,
        feedback TEXT,
        dimension TEXT,
        FOREIGN KEY(assessment_id) REFERENCES assessments(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS roadmaps (
        id TEXT PRIMARY KEY,
        user_id TEXT,
        version INTEGER DEFAULT 1,
        generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        is_active BOOLEAN DEFAULT 1,
        FOREIGN KEY(user_id) REFERENCES profiles(user_id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS roadmap_items (
        id TEXT PRIMARY KEY,
        roadmap_id TEXT,
        month INTEGER NOT NULL,
        week INTEGER NOT NULL,
        title TEXT NOT NULL,
        skill TEXT NOT NULL,
        priority TEXT NOT NULL,
        resources TEXT DEFAULT '[]',
        est_hours INTEGER NOT NULL,
        status TEXT DEFAULT 'todo',
        FOREIGN KEY(roadmap_id) REFERENCES roadmaps(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS jobs (
        id TEXT PRIMARY KEY,
        source TEXT NOT NULL,
        external_id TEXT UNIQUE,
        title TEXT NOT NULL,
        company TEXT NOT NULL,
        location TEXT NOT NULL,
        work_mode TEXT DEFAULT 'hybrid',
        salary_min INTEGER,
        salary_max INTEGER,
        description TEXT NOT NULL,
        apply_url TEXT NOT NULL,
        required_skills TEXT DEFAULT '[]',
        experience_required TEXT,
        posted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS job_matches (
        user_id TEXT,
        job_id TEXT,
        score INTEGER NOT NULL,
        breakdown TEXT NOT NULL,
        matched_skills TEXT DEFAULT '[]',
        missing_skills TEXT DEFAULT '[]',
        reason TEXT NOT NULL,
        PRIMARY KEY (user_id, job_id),
        FOREIGN KEY(user_id) REFERENCES profiles(user_id) ON DELETE CASCADE,
        FOREIGN KEY(job_id) REFERENCES jobs(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS resumes (
        id TEXT PRIMARY KEY,
        user_id TEXT,
        kind TEXT NOT NULL,
        label TEXT NOT NULL,
        parent_id TEXT,
        file_path TEXT,
        content TEXT NOT NULL,
        target_job_id TEXT,
        ats_score INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES profiles(user_id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS applications (
        id TEXT PRIMARY KEY,
        user_id TEXT,
        job_id TEXT,
        company TEXT NOT NULL,
        role TEXT NOT NULL,
        job_url TEXT,
        resume_id TEXT,
        match_score INTEGER,
        status TEXT DEFAULT 'saved',
        applied_on DATE,
        response TEXT,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES profiles(user_id) ON DELETE CASCADE,
        FOREIGN KEY(job_id) REFERENCES jobs(id)
    );

    CREATE TABLE IF NOT EXISTS outreach (
        id TEXT PRIMARY KEY,
        user_id TEXT,
        application_id TEXT,
        recruiter_name TEXT,
        recruiter_role TEXT,
        channel TEXT DEFAULT 'LinkedIn',
        draft TEXT NOT NULL,
        status TEXT DEFAULT 'draft',
        approved_at TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES profiles(user_id) ON DELETE CASCADE,
        FOREIGN KEY(application_id) REFERENCES applications(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS interviews (
        id TEXT PRIMARY KEY,
        user_id TEXT,
        application_id TEXT,
        starts_at TIMESTAMP NOT NULL,
        ends_at TIMESTAMP,
        round TEXT NOT NULL,
        itype TEXT NOT NULL,
        topics TEXT DEFAULT '[]',
        ics_path TEXT,
        FOREIGN KEY(user_id) REFERENCES profiles(user_id) ON DELETE CASCADE,
        FOREIGN KEY(application_id) REFERENCES applications(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS prep_items (
        id TEXT PRIMARY KEY,
        interview_id TEXT,
        title TEXT NOT NULL,
        done BOOLEAN DEFAULT 0,
        skill TEXT,
        FOREIGN KEY(interview_id) REFERENCES interviews(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS readiness_snapshots (
        id TEXT PRIMARY KEY,
        user_id TEXT,
        overall INTEGER NOT NULL,
        technical INTEGER NOT NULL,
        dsa INTEGER NOT NULL,
        projects INTEGER NOT NULL,
        resume INTEGER NOT NULL,
        interview INTEGER NOT NULL,
        industry INTEGER NOT NULL,
        job_readiness INTEGER NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES profiles(user_id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS audit_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        action TEXT NOT NULL,
        entity TEXT NOT NULL,
        entity_id TEXT,
        payload TEXT,
        approved_by_user BOOLEAN DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES profiles(user_id) ON DELETE CASCADE
    );
    """)
    conn.commit()
    conn.close()
