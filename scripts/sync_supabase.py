"""
Two-way sync between local data/jobs.db and the hosted Supabase copy.

    python scripts/sync_supabase.py pull    # hosted actions -> local  (run FIRST)
    python scripts/sync_supabase.py push    # local rows    -> hosted (run LAST)

Conflict rule: last-write-wins on updated_at. Every writer (this script, the
dashboard, track.py) stamps updated_at in UTC, so a row is only overwritten
if the other side is genuinely newer.

Needs config/supabase_project.json (see config/supabase_project.example.json).
"""
import json
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib import request, error

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "data" / "jobs.db"
PROJ_PATH = ROOT / "config" / "supabase_project.json"

SHARED = ["id", "company", "role_title", "source", "url", "jd_text", "location",
          "date_added", "applied_on", "match_score", "fit_score", "odds_score",
          "strengths", "weaknesses", "missing_keywords", "recruiter_email",
          "resume_pdf_path", "status", "notes", "updated_at"]


def proj():
    if not PROJ_PATH.exists():
        sys.exit("config/supabase_project.json not found - copy the .example.json")
    return json.loads(PROJ_PATH.read_text())


def rest(p, base_url, key):
    url = f"{base_url}/rest/v1/{p}"
    headers = {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "User-Agent": "jobhunt-agent-sync/1.0",
    }
    return url, headers


def http(method, url, headers, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = request.Request(url, data=data, headers=headers, method=method)
    try:
        with request.urlopen(req, timeout=30) as r:
            raw = r.read().decode()
            return json.loads(raw) if raw else []
    except error.HTTPError as e:
        sys.exit(f"{method} {url} -> {e.code}: {e.read().decode()[:300]}")


def parse_ts(s):
    if not s:
        return datetime.min.replace(tzinfo=timezone.utc)
    s = s.replace("Z", "+00:00")
    try:
        dt = datetime.fromisoformat(s)
    except ValueError:
        return datetime.min.replace(tzinfo=timezone.utc)
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def local():
    if not DB_PATH.exists():
        sys.exit("no data/jobs.db - run 'python scripts/track.py init'")
    c = sqlite3.connect(str(DB_PATH))
    c.row_factory = sqlite3.Row
    return c


def cmd_pull(cfg):
    base = f"https://{cfg['project_ref']}.supabase.co"
    url, headers = rest("jobs?select=*", base, cfg["service_role"])
    remote = http("GET", url, headers)
    c = local()
    changed = 0
    for r in remote:
        row = c.execute("SELECT status, updated_at FROM jobs WHERE id=?", (r["id"],)).fetchone()
        if not row:
            continue  # hosted-only rows are not pulled; add locally with track.py
        if parse_ts(r.get("updated_at")) <= parse_ts(row["updated_at"]):
            continue
        c.execute("UPDATE jobs SET status=?, notes=?, resume_pdf_path=?, updated_at=? WHERE id=?",
                  (r["status"], r.get("notes"), r.get("resume_pdf_path"),
                   r.get("updated_at"), r["id"]))
        changed += 1
    c.commit()
    c.close()
    print(f"pulled: {changed} row(s) updated from the dashboard")


def cmd_push(cfg):
    base = f"https://{cfg['project_ref']}.supabase.co"
    url, headers = rest("jobs?select=id,updated_at", base, cfg["service_role"])
    remote = {r["id"]: parse_ts(r.get("updated_at")) for r in http("GET", url, headers)}

    c = local()
    rows = [dict(r) for r in c.execute("SELECT * FROM jobs")]
    c.close()

    payload, skipped = [], 0
    for r in rows:
        rec = {k: r.get(k) for k in SHARED if k in r}
        if r["id"] in remote and parse_ts(r.get("updated_at")) < remote[r["id"]]:
            skipped += 1
            continue
        payload.append(rec)

    if payload:
        up_url, up_headers = rest("jobs", base, cfg["service_role"])
        up_headers["Prefer"] = "resolution=merge-duplicates"
        http("POST", up_url, up_headers, payload)
    print(f"pushed: {len(payload)} row(s) upserted, {skipped} skipped (newer on dashboard)")
    if skipped:
        print("  run 'pull' then 'push' again to reconcile.")


if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in ("pull", "push"):
        print(__doc__)
        sys.exit(1)
    cfg = proj()
    (cmd_pull if sys.argv[1] == "pull" else cmd_push)(cfg)
