"""
Local job tracker - SQLite. The single source of truth on your machine;
the hosted dashboard is a mirror of this (see scripts/sync_supabase.py).

    python scripts/track.py init
    python scripts/track.py add --company "Acme" --role "Product Manager" \
        --url https://... --location "Remote" --source manual
    python scripts/track.py list [STATUS]
    python scripts/track.py show <id>
    python scripts/track.py set <id> <STATUS> [--resume resumes/Name_Acme.pdf] [--note "..."]

Statuses:
    PENDING_REVIEW -> APPROVED | REJECTED -> EMAILED | APPLIED
                   -> INTERVIEWING | OFFER | EMPLOYER_REJECTED | FAILED
"""
import argparse
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "data" / "jobs.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company TEXT NOT NULL,
    role_title TEXT NOT NULL,
    source TEXT,
    url TEXT,
    jd_text TEXT,
    location TEXT,
    date_added TEXT NOT NULL,
    applied_on TEXT,
    match_score INTEGER,
    fit_score INTEGER,
    odds_score INTEGER,
    strengths TEXT,
    weaknesses TEXT,
    missing_keywords TEXT,
    recruiter_email TEXT,
    resume_pdf_path TEXT,
    status TEXT NOT NULL DEFAULT 'PENDING_REVIEW',
    notes TEXT,
    updated_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs(status);
CREATE UNIQUE INDEX IF NOT EXISTS idx_jobs_url ON jobs(url) WHERE url IS NOT NULL;
"""

VALID = {"PENDING_REVIEW", "APPROVED", "REJECTED", "EMAILED", "APPLIED",
         "INTERVIEWING", "OFFER", "EMPLOYER_REJECTED", "FAILED"}
SENT = {"EMAILED", "APPLIED", "INTERVIEWING", "OFFER", "EMPLOYER_REJECTED"}


def now():
    return datetime.now(timezone.utc).isoformat()


def conn():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    c = sqlite3.connect(str(DB_PATH))
    c.row_factory = sqlite3.Row
    c.executescript(SCHEMA)
    return c


def cmd_init(_):
    conn().close()
    print(f"initialised {DB_PATH}")


def cmd_add(a):
    c = conn()
    try:
        cur = c.execute(
            "INSERT INTO jobs (company, role_title, source, url, jd_text, location, "
            "date_added, recruiter_email, status, updated_at) "
            "VALUES (?,?,?,?,?,?,?,?,'PENDING_REVIEW',?)",
            (a.company, a.role, a.source, a.url, a.jd, a.location, now(),
             a.recruiter_email, now()))
        c.commit()
        print(f"added job {cur.lastrowid}: {a.company} - {a.role}")
    except sqlite3.IntegrityError:
        row = c.execute("SELECT id FROM jobs WHERE url=?", (a.url,)).fetchone()
        print(f"already tracked as job {row['id']}")
    finally:
        c.close()


def cmd_list(a):
    c = conn()
    q = "SELECT id, company, role_title, location, status, fit_score, match_score FROM jobs"
    params = ()
    if a.status:
        q += " WHERE status=?"
        params = (a.status.upper(),)
    q += " ORDER BY id DESC"
    for r in c.execute(q, params):
        score = r["fit_score"] or r["match_score"] or "-"
        print(f"  {r['id']:>4}  {r['status']:<17} {str(score):>4}  "
              f"{r['company']} - {r['role_title']}  [{r['location'] or '?'}]")
    c.close()


def cmd_show(a):
    c = conn()
    r = c.execute("SELECT * FROM jobs WHERE id=?", (a.id,)).fetchone()
    c.close()
    if not r:
        sys.exit(f"no job {a.id}")
    for k in r.keys():
        v = r[k]
        if k == "jd_text" and v:
            v = f"<{len(v)} chars>"
        print(f"  {k:<16} {v}")


def cmd_set(a):
    status = a.status.upper()
    if status not in VALID:
        sys.exit(f"invalid status. one of: {', '.join(sorted(VALID))}")
    c = conn()
    r = c.execute("SELECT * FROM jobs WHERE id=?", (a.id,)).fetchone()
    if not r:
        sys.exit(f"no job {a.id}")
    if r["status"] in SENT and status != r["status"]:
        print(f"  ! job {a.id} is already {r['status']} (out to the employer). "
              f"Continuing, but do not rebuild its resume.")
    fields = {"status": status, "updated_at": now()}
    if status in SENT and not r["applied_on"]:
        fields["applied_on"] = now()
    if a.resume:
        fields["resume_pdf_path"] = a.resume
    if a.note:
        existing = (r["notes"] or "").strip()
        fields["notes"] = f"{existing}\n\n{a.note}" if existing else a.note
    sets = ", ".join(f"{k}=?" for k in fields)
    c.execute(f"UPDATE jobs SET {sets} WHERE id=?", (*fields.values(), a.id))
    c.commit()
    c.close()
    print(f"job {a.id}: {r['status']} -> {status}")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    sub.add_parser("init").set_defaults(fn=cmd_init)

    p = sub.add_parser("add")
    p.add_argument("--company", required=True)
    p.add_argument("--role", required=True)
    p.add_argument("--url")
    p.add_argument("--location")
    p.add_argument("--source", default="manual")
    p.add_argument("--jd", dest="jd")
    p.add_argument("--recruiter-email", dest="recruiter_email")
    p.set_defaults(fn=cmd_add)

    p = sub.add_parser("list")
    p.add_argument("status", nargs="?")
    p.set_defaults(fn=cmd_list)

    p = sub.add_parser("show")
    p.add_argument("id", type=int)
    p.set_defaults(fn=cmd_show)

    p = sub.add_parser("set")
    p.add_argument("id", type=int)
    p.add_argument("status")
    p.add_argument("--resume")
    p.add_argument("--note")
    p.set_defaults(fn=cmd_set)

    args = ap.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
