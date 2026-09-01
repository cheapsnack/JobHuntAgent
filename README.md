# Job Hunt Agent

A Claude Code agent for job hunting: tailors a one-page resume to each job description, scores fit, scrapes postings from job boards, drafts recruiter emails, and tracks everything on a dashboard.

Run it inside **Claude Code**. On first use the agent interviews you once
to build a reusable "base template" from your real experience. After that,
paste a job description and get a tailored, ATS-checked one-page PDF back.

---

## What you get

- A **locked one-page HTML/PDF resume template** (`templates/resume_base.html`).
  Layout and CSS never change; only the content does.
- A **bullet-library + per-job-spec** model (`scripts/build_resume.py`,
  `scripts/resume_specs.py`). Tailoring = selecting, ordering and rephrasing
  your *real* bullets toward a JD's own words. Nothing fabricated.
- A **mechanical QA gate** (`scripts/verify_resume.py`): fails a resume for
  more than one page, em/en dashes, too few bullets, too thin, banned
  filler, an unheld job-title claim, unverified `[estimate]` markers,
  non-ATS-parseable layout, or ligature glyphs that break literal keyword
  matching.
- A **one-page PDF compiler** with auto-fit (`scripts/compile_pdf.py`).
- An **onboarding interview** (`ONBOARDING.md`) the agent runs to set this
  up from your existing resume, then asks about salary, roles and locations.
- **API-key setup guides** (`docs/01_SETUP_API_KEYS.md`) for the optional
  Telegram digest, Gmail drafts, and a Supabase + Vercel approval dashboard.

---

## Quick start

1. Install prerequisites:
   - Python 3.10+
   - Google Chrome (used to render the PDF)
   ```bash
   pip install -r requirements.txt
   ```
2. Copy the config templates:
   ```bash
   cp config/profile.example.json config/profile.json
   cp config/resume_rules.example.json config/resume_rules.json
   ```
3. Open this folder in Claude Code and say:
   > **"Set up my base resume."**

   The agent follows `ONBOARDING.md`: asks for your current resume (or
   interviews you from scratch), fills the template, builds your bullet
   library, then asks about current/expected salary, notice period, target
   roles and preferred locations.
4. After onboarding, paste any job description and say **"tailor my resume
   for this."**

---

## Files map

| Path | Purpose | Core? |
|---|---|---|
| `CLAUDE.md` | Operating rules the agent follows | yes |
| `ONBOARDING.md` | The one-time interview | yes |
| `templates/resume_base.html` | The locked resume layout | yes |
| `templates/cover_letter_base.html` | Optional matching cover letter | no |
| `scripts/compile_pdf.py` | HTML -> one-page PDF | yes |
| `scripts/verify_resume.py` | Pass/fail QA gate | yes |
| `scripts/build_resume.py` | Assemble a resume from a spec | yes |
| `scripts/resume_specs.py` | One entry per application | yes |
| `config/profile.json` | Contact, roles, locations, salary | yes |
| `config/resume_rules.json` | Your name + fact/title rules for the QA gate | yes |
| `candidate_profile/` | Your resume PDF + verified extra facts | yes |
| `scripts/track.py` | Local SQLite application tracker | optional |
| `scripts/scrape.py` | Pull jobs from Greenhouse/Lever/Ashby (no API key) | optional |
| `scripts/score.py` | Store a fit/odds score + breakdown on a job | optional |
| `scripts/sync_supabase.py` | Sync tracker <-> hosted dashboard | optional |
| `scripts/telegram_setup.py` | Telegram digest of the review queue | optional |
| `scripts/gmail_auth.py` | Create outreach email drafts (never sends) | optional |
| `dashboard_app/` | Supabase + Vercel approval dashboard | optional |
| `docs/01_SETUP_API_KEYS.md` | Telegram, Gmail, SerpAPI, Supabase, Vercel | optional |
| `docs/02_BASE_RESUME_GUIDE.md` | Manual version of onboarding | reference |
| `docs/03_PIPELINE_OVERVIEW.md` | The optional tracking pipeline | optional |

---

## Privacy

`.gitignore` excludes everything with real personal data: `config/*.json`
(except `.example.` templates), `candidate_profile/*` (except examples),
`data/`, `resumes/`, `cover_letters/`, `JDs/`, and all API credentials.
Before pushing, run `git status` and confirm none of the real files are
staged.
