"""
Pull job postings from public ATS job boards (Greenhouse, Lever, Ashby).
No API key needed. Adds new matches to data/jobs.db as PENDING_REVIEW.

    python scripts/scrape.py            # fetch all boards in config/job_sources.json
    python scripts/scrape.py --dry-run  # show what would be added, write nothing
    python scripts/scrape.py --company Ramp

Config: config/job_sources.json (see config/job_sources.example.json).
Filtering: a posting is kept only if its title matches one of title_keywords
AND (location_keywords is empty OR its location matches one of them).

Most large Indian companies run their own ATS and are NOT reachable here.
For those, paste the JD to the agent directly, or add your own poller that
calls: python scripts/track.py add ...
"""
import argparse
import json
import re
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib import request, error

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "data" / "jobs.db"
CFG_PATH = ROOT / "config" / "job_sources.json"

UA = {"User-Agent": "Mozilla/5.0 (jobhunt-agent scrape.py)"}


def get_json(url):
    try:
        req = request.Request(url, headers=UA)
        with request.urlopen(req, timeout=30) as r:
            return json.loads(r.read().decode())
    except (error.HTTPError, error.URLError, json.JSONDecodeError) as e:
        print(f"  ! fetch failed: {url}\n    {e}")
        return None


def strip_html(s):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", s or "")).strip()


def fetch_greenhouse(token):
    data = get_json(f"https://boards-api.greenhouse.io/v1/boards/{token}/jobs?content=true")
    out = []
    for j in (data or {}).get("jobs", []):
        out.append({
            "title": j.get("title", ""),
            "location": (j.get("location") or {}).get("name", ""),
            "url": j.get("absolute_url", ""),
            "jd": strip_html(j.get("content", "")),
        })
    return out


def fetch_lever(token):
    data = get_json(f"https://api.lever.co/v0/postings/{token}?mode=json")
    out = []
    for j in data or []:
        cats = j.get("categories") or {}
        out.append({
            "title": j.get("text", ""),
            "location": cats.get("location", ""),
            "url": j.get("hostedUrl", ""),
            "jd": strip_html(j.get("descriptionPlain") or j.get("description", "")),
        })
    return out


def fetch_ashby(token):
    data = get_json(f"https://api.ashbyhq.com/posting-api/job-board/{token}?includeCompensation=true")
    out = []
    for j in (data or {}).get("jobs", []):
        out.append({
            "title": j.get("title", ""),
            "location": j.get("location", ""),
            "url": j.get("jobUrl", ""),
            "jd": strip_html(j.get("descriptionPlain") or j.get("descriptionHtml", "")),
        })
    return out


FETCHERS = {"greenhouse": fetch_greenhouse, "lever": fetch_lever, "ashby": fetch_ashby}


def matches(posting, title_kw, loc_kw):
    title = posting["title"].lower()
    if title_kw and not any(k.lower() in title for k in title_kw):
        return False
    if loc_kw:
        loc = posting["location"].lower()
        if not any(k.lower() in loc for k in loc_kw):
            return False
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--company", help="only this company from the config")
    args = ap.parse_args()

    if not CFG_PATH.exists():
        sys.exit("config/job_sources.json not found - copy the .example.json")
    cfg = json.loads(CFG_PATH.read_text())
    title_kw = cfg.get("title_keywords", [])
    loc_kw = cfg.get("location_keywords", [])
    boards = cfg.get("boards", [])
    if args.company:
        boards = [b for b in boards if b["company"].lower() == args.company.lower()]

    if not DB_PATH.exists() and not args.dry_run:
        sys.exit("no data/jobs.db - run 'python scripts/track.py init' first")

    conn = None
    if not args.dry_run:
        conn = sqlite3.connect(str(DB_PATH))

    added = skipped = seen = 0
    for b in boards:
        fetcher = FETCHERS.get(b["ats"])
        if not fetcher:
            print(f"unknown ats '{b['ats']}' for {b['company']}")
            continue
        print(f"{b['company']} ({b['ats']}/{b['token']})")
        for p in fetcher(b["token"]):
            if not p["url"] or not matches(p, title_kw, loc_kw):
                continue
            seen += 1
            line = f"  + {p['title']}  [{p['location'] or '?'}]"
            if args.dry_run:
                print(line)
                added += 1
                continue
            try:
                conn.execute(
                    "INSERT INTO jobs (company, role_title, source, url, jd_text, "
                    "location, date_added, status, updated_at) "
                    "VALUES (?,?,?,?,?,?,?,'PENDING_REVIEW',?)",
                    (b["company"], p["title"], b["ats"], p["url"], p["jd"][:20000],
                     p["location"], datetime.now(timezone.utc).isoformat(),
                     datetime.now(timezone.utc).isoformat()))
                conn.commit()
                print(line)
                added += 1
            except sqlite3.IntegrityError:
                skipped += 1  # already in the DB (unique url)

    if conn:
        conn.close()
    verb = "would add" if args.dry_run else "added"
    print(f"\n{seen} matched, {verb} {added}, {skipped} already tracked")


if __name__ == "__main__":
    main()
