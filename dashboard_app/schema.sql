-- Supabase / Postgres schema for the approval dashboard.
-- Run this once in the Supabase SQL editor (see docs/01_SETUP_API_KEYS.md).
-- Mirrors the local SQLite schema created by scripts/track.py.

create table if not exists jobs (
    id                bigint generated always as identity primary key,
    company           text not null,
    role_title        text not null,
    source            text,
    url               text unique,
    jd_text           text,
    location          text,
    date_added        timestamptz not null default now(),
    applied_on        timestamptz,
    match_score       integer,
    fit_score         integer,
    odds_score        integer,
    strengths         text,
    weaknesses        text,
    missing_keywords  text,
    recruiter_email   text,
    resume_pdf_path   text,
    status            text not null default 'PENDING_REVIEW',
    notes             text,
    updated_at        timestamptz not null default now()
);

create index if not exists idx_jobs_status on jobs(status);

-- Status flow (enforced in application code, not the DB):
--   PENDING_REVIEW -> APPROVED | REJECTED -> EMAILED | APPLIED
--                  -> INTERVIEWING | OFFER | EMPLOYER_REJECTED | FAILED
--
-- REJECTED          = you passed on it            (shows as "Passed")
-- EMPLOYER_REJECTED = the company turned you down after you applied
