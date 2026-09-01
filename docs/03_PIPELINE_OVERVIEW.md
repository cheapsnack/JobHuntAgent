# Optional job-tracking pipeline

The resume kit works with no database and no keys. This layer adds
tracking, a phone digest, email drafts, and a hosted approval dashboard.
Set it up only if you want it.

## Local tracker — `scripts/track.py`

A single SQLite file, `data/jobs.db`, is the source of truth on your
machine.

```bash
python scripts/track.py init
python scripts/track.py add --company "Acme" --role "Product Manager" \
    --url "https://acme.com/jobs/123" --location "Remote" --source manual
python scripts/track.py list PENDING_REVIEW
python scripts/track.py set 4 APPROVED --resume resumes/Jane_Acme.pdf
python scripts/track.py set 4 APPLIED --note "applied via referral"
```

Status flow:
```
PENDING_REVIEW -> APPROVED | REJECTED -> EMAILED | APPLIED
               -> INTERVIEWING | OFFER | EMPLOYER_REJECTED | FAILED
```
`REJECTED` = you passed. `EMPLOYER_REJECTED` = the company turned you
down after you applied.

## Scraping jobs — `scripts/scrape.py`

Pulls postings from public Greenhouse / Lever / Ashby job boards. **No API
key** — these are the same endpoints the company career pages use.

```bash
cp config/job_sources.example.json config/job_sources.json   # edit the watchlist + filters
python scripts/scrape.py --dry-run       # preview matches
python scripts/scrape.py                 # add new matches as PENDING_REVIEW
```

Edit `config/job_sources.json`: `title_keywords`, `location_keywords`, and
the `boards` list (company + ats + token, where the token is the slug in
`boards.greenhouse.io/TOKEN`, `jobs.lever.co/TOKEN` or
`jobs.ashbyhq.com/TOKEN`).

Most large Indian firms run their own ATS and are not reachable this way —
paste those JDs to the agent directly, or write a poller that calls
`python scripts/track.py add ...`.

## Scoring — `scripts/score.py`

The agent scores a JD against the six-dimension rubric in `CLAUDE.md`
(that judgement needs an LLM). This script records the result so the
dashboard can show it:

```bash
python scripts/score.py set 4 --fit 72 --odds 64 \
  --breakdown "core 3 x.35, shape 3 x.20, domain 2 x.15, scope 3 x.15, tools 3 x.10, quals 3 x.05" \
  --strengths "Owns data products end to end; SQL + migration experience" \
  --weaknesses "No hands-on Kubernetes; wants 8+ yrs; observability is new"
python scripts/score.py keywords 4 "kubernetes,terraform,sql,dbt"   # literal JD coverage
```

`fit_score`, `odds_score`, `strengths`, `weaknesses` are the columns the
dashboard card shows.

## Telegram digest — `scripts/telegram_setup.py`

`docs/01` Step 1. Gives you `test` and `digest`. Schedule `digest` daily
for a morning list.

## Gmail drafts — `scripts/gmail_auth.py`

`docs/01` Step 2. Creates outreach email **drafts** with your resume
attached. This kit never sends mail.

## Hosted dashboard — Supabase + Vercel

`docs/01` Steps 4 and 5.

- `dashboard_app/schema.sql` — run once in Supabase
- `dashboard_app/` — deploy to Vercel (`index.html` + `api/*.js`)
- `scripts/sync_supabase.py pull` / `push` — move data between local
  SQLite and Supabase. **Pull first, push last, every session.**

Three tabs — Review (Approve / Pass), To Apply (Mark applied), Pipeline
(status table). Buttons write to Supabase; `pull` brings those decisions
back to `data/jobs.db`.

## Going further

`scrape.py` covers Greenhouse / Lever / Ashby. For Google Jobs (SerpAPI,
`docs/01` Step 3), Workday, or other career portals, add your own poller
that ends by calling `python scripts/track.py add ...` — that is the one
entry point everything else reads from.
