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

## Scoring fields (optional)

`fit_score`, `odds_score`, `strengths`, `weaknesses` are optional columns
the dashboard shows if present. Have the agent score a JD against
`CLAUDE.md`'s fit-check rubric and write them with `track.py`, or fill
them yourself. There is no automatic scorer in this kit.

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

## Discovery (not included)

Automated pulling from ATS job boards, career portals, and Google Jobs is
**not** part of this kit. Add your own pollers that call `track.py add`,
or paste JDs to the agent directly and let it log them.
