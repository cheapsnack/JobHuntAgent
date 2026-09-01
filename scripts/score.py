"""
Store a fit/odds score and its breakdown on a tracked job.

The judgement is the agent's (Claude scores the JD against the six-dimension
rubric in CLAUDE.md). This script just records the result so the dashboard
can show it and so it can be re-derived later.

    python scripts/score.py show <id>
    python scripts/score.py set <id> --fit 72 --odds 64 \
        --breakdown "core 3 x.35, shape 3 x.20, domain 2 x.15, scope 3 x.15, tools 3 x.10, quals 3 x.05" \
        --strengths "Owns data products end to end; SQL + migration experience; MBA" \
        --weaknesses "No hands-on Kubernetes; wants 8+ yrs; observability domain is new"

    python scripts/score.py keywords <id> "kubernetes,terraform,sql,airflow,dbt"
        # quick literal-coverage check: which of these terms appear in the JD

The rubric (CLAUDE.md): rate each 0-4, multiply by weight, sum, x25.
  core 0.35, shape 0.20, domain 0.15, scope 0.15, tools 0.10, quals 0.05
Never score years-of-experience gaps. fit = background match.
odds = fit after employer-screen severity. A gap of 10+ means "apply via referral".
"""
import argparse
import re
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "data" / "jobs.db"


def conn():
    if not DB_PATH.exists():
        sys.exit("no data/jobs.db - run 'python scripts/track.py init'")
    c = sqlite3.connect(str(DB_PATH))
    c.row_factory = sqlite3.Row
    return c


def cmd_show(a):
    c = conn()
    r = c.execute("SELECT id, company, role_title, fit_score, odds_score, "
                  "strengths, weaknesses, notes FROM jobs WHERE id=?", (a.id,)).fetchone()
    c.close()
    if not r:
        sys.exit(f"no job {a.id}")
    for k in r.keys():
        print(f"  {k:<12} {r[k]}")


def cmd_set(a):
    c = conn()
    r = c.execute("SELECT notes FROM jobs WHERE id=?", (a.id,)).fetchone()
    if not r:
        sys.exit(f"no job {a.id}")
    fields = {"updated_at": datetime.now(timezone.utc).isoformat()}
    if a.fit is not None:
        fields["fit_score"] = a.fit
        fields["match_score"] = a.fit
    if a.odds is not None:
        fields["odds_score"] = a.odds
    if a.strengths is not None:
        fields["strengths"] = a.strengths
    if a.weaknesses is not None:
        fields["weaknesses"] = a.weaknesses
    if a.breakdown:
        line = f"SCORE {a.fit if a.fit is not None else '?'} = [{a.breakdown}] x25"
        existing = (r["notes"] or "").strip()
        fields["notes"] = f"{existing}\n\n{line}" if existing else line
    sets = ", ".join(f"{k}=?" for k in fields)
    c.execute(f"UPDATE jobs SET {sets} WHERE id=?", (*fields.values(), a.id))
    c.commit()
    c.close()
    print(f"job {a.id}: fit={a.fit} odds={a.odds}")


def cmd_keywords(a):
    c = conn()
    r = c.execute("SELECT jd_text FROM jobs WHERE id=?", (a.id,)).fetchone()
    c.close()
    if not r:
        sys.exit(f"no job {a.id}")
    jd = (r["jd_text"] or "").lower()
    if len(jd) < 50:
        print("  (no usable JD text on this row - paste the posting first)")
    for term in [t.strip() for t in a.terms.split(",") if t.strip()]:
        hit = re.search(r"\b" + re.escape(term.lower()) + r"\b", jd)
        print(f"  [{'x' if hit else ' '}] {term}")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("show")
    p.add_argument("id", type=int)
    p.set_defaults(fn=cmd_show)

    p = sub.add_parser("set")
    p.add_argument("id", type=int)
    p.add_argument("--fit", type=int)
    p.add_argument("--odds", type=int)
    p.add_argument("--breakdown")
    p.add_argument("--strengths")
    p.add_argument("--weaknesses")
    p.set_defaults(fn=cmd_set)

    p = sub.add_parser("keywords")
    p.add_argument("id", type=int)
    p.add_argument("terms", help="comma-separated terms to check against the JD")
    p.set_defaults(fn=cmd_keywords)

    args = ap.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
