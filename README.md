# Job Hunt Agent

An agentic job-search system built in Claude Code, where the rules the
agent must follow are **checks in code, not sentences in a prompt**. It
tailors a one-page resume to each job description, scores fit on an
auditable rubric, scrapes postings, drafts recruiter emails (never sends
them), and tracks every application through to an outcome on a dashboard.

Run it inside **Claude Code**. On first use the agent interviews you once
to build a reusable "base template" from your real experience. After that,
paste a job description and get a tailored, ATS-checked one-page PDF back.

## Why it is built this way

Most "AI resume" tools optimise for generating text. This one optimises for
**not shipping a mistake**, because a fabricated bullet or a two-page resume
sent to a real employer cannot be recalled. The design rules that follow
came from real failures during the author's own eight-week run, each turned
into a mechanical check the moment it happened. The full list is in
[`docs/05_DESIGN_DECISIONS.md`](docs/05_DESIGN_DECISIONS.md).

- **Guardrails as code.** A resume is "done" only when `verify_resume.py`
  passes: one page, no dashes, enough real content, no unheld title claim,
  ATS-parseable, no ligature glyphs. The agent cannot mark work finished by
  saying so.
- **Provenance over trust.** Every bullet in a built resume must trace to a
  phrase that literally appears in the candidate's source files. The builder
  refuses to compile otherwise. "Never invent a bullet" is a check, not a
  rule to remember.
- **Two scores, never blended.** `fit` measures how well the background
  matches the JD; `odds` measures the chance of clearing that employer's
  screen. A wide gap means "apply via referral", not "skip".
- **Score what you actually read.** Scored on a stub JD, roles looked
  *better* than on the full posting (the less the agent knew, the higher it
  scored). Fit is now capped by how much JD text existed at scoring time,
  and the cap lifts automatically when the real posting is recovered.
- **Human in the loop where it matters.** The agent drafts emails; the user
  sends. The agent builds resumes; the user approves from a phone. Nothing
  outbound happens without a person pressing the button.
- **Measured on outcomes, not activity.** The scoreboard's North Star is
  interviews per ten applications, with cohorts by score band, employer tier
  and channel, and a validation test that refuses to draw a conclusion
  under 25 resolved applications.

## What it produced

From the author's own run (eight weeks, one candidate, India and Gulf
product and strategy roles). These are real numbers, including the modest
ones; the honest reading is that the system is strong evidence of
disciplined AI-product operation and thin evidence, so far, that tailoring
beats a good base resume. That experiment is still running.

| Measure | Value |
|---|---|
| Postings logged / scored | 2,100+ / 1,300+ |
| Tailored resumes built, all passing the QA gate | 280+ |
| Applications sent | 159 |
| Reached an interview | 9 (0.6 per 10 sent) |
| Score validation | 65+ odds band replied at 22.8% vs 15.4% below it (n=79 / 13) |
| Guardrails added after a real incident | 7 |

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
- A **fit-check rubric** the agent scores each JD against before tailoring,
  recorded on the job with `scripts/score.py` (fit vs. odds, plus a
  re-derivable breakdown).

### Optional pipeline (no keys needed to start)

- A **job scraper** (`scripts/scrape.py`) that pulls postings from public
  Greenhouse / Lever / Ashby boards, filtered by your title and location
  keywords. **No API key.**
- A **local tracker** (`scripts/track.py`, SQLite) that every other piece
  reads from and writes to.
- **Gmail draft** creation for recruiter outreach (`scripts/gmail_auth.py`)
  — drafts only, it never sends.
- A **Telegram digest** of your review queue (`scripts/telegram_setup.py`).
- A **web approval dashboard** (`dashboard_app/`, Supabase + Vercel) —
  Approve / Pass / Mark-applied from your phone, synced back to the tracker.
- **Setup guides** for every key, one step at a time
  (`docs/01_SETUP_API_KEYS.md`).

### Optional interview prep

- An **interview-prep report generator** (`docs/04_INTERVIEW_PREP_GUIDE.md`):
  when you have an interview booked, the agent researches the company,
  rebuilds every candidate claim from your real profile, and compiles a
  thorough prep PDF - resume walkthrough, STAR stories, domain frameworks,
  a company and competitor deep dive, likely questions with answer frames,
  and a strategic teardown. Every fact carries a confidence badge.

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
5. (Optional) Turn on tracking and discovery:
   ```bash
   python scripts/track.py init
   cp config/job_sources.example.json config/job_sources.json   # edit companies + keywords
   python scripts/scrape.py --dry-run
   ```
   See `docs/03_PIPELINE_OVERVIEW.md`, then `docs/01_SETUP_API_KEYS.md` for
   Telegram / Gmail / the dashboard.

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
| `config/job_sources.json` | Watchlist + title/location filters for the scraper | optional |
| `scripts/score.py` | Store a fit/odds score + breakdown on a job | optional |
| `scripts/sync_supabase.py` | Sync tracker <-> hosted dashboard | optional |
| `scripts/telegram_setup.py` | Telegram digest of the review queue | optional |
| `scripts/gmail_auth.py` | Create outreach email drafts (never sends) | optional |
| `dashboard_app/` | Supabase + Vercel approval dashboard | optional |
| `docs/01_SETUP_API_KEYS.md` | Telegram, Gmail, SerpAPI, Supabase, Vercel | optional |
| `docs/02_BASE_RESUME_GUIDE.md` | Manual version of onboarding | reference |
| `docs/03_PIPELINE_OVERVIEW.md` | The optional tracking pipeline | optional |
| `docs/04_INTERVIEW_PREP_GUIDE.md` | The optional interview-prep report generator | optional |
| `docs/05_DESIGN_DECISIONS.md` | The incidents behind each guardrail, and what was measured | reference |
| `demo/` | A seeded, fictional demo instance for screenshots and walkthroughs | reference |

---

## Privacy

`.gitignore` excludes everything with real personal data: `config/*.json`
(except `.example.` templates), `candidate_profile/*` (except examples),
`data/`, `resumes/`, `cover_letters/`, `JDs/`, and all API credentials.
Before pushing, run `git status` and confirm none of the real files are
staged.
