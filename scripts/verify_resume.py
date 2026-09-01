"""
Automated resume QA gate. Run on EVERY compiled resume PDF before it is
treated as final, sent, or attached to an application.

    python scripts/verify_resume.py resumes/Name_Acme.pdf
    python scripts/verify_resume.py --all            # audit everything in resumes/
    python scripts/verify_resume.py --all --unsent   # skip already-submitted (needs data/jobs.db)

Exit code 0 = pass, 1 = at least one FAIL.

Personalisation (your name, required/banned facts, banned title claims,
density floors) is read from config/resume_rules.json - see
config/resume_rules.example.json.
"""
import argparse
import json
import os
import re
import sqlite3
import sys
from pathlib import Path

import pypdf

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "data" / "jobs.db"
RULES_PATH = ROOT / "config" / "resume_rules.json"

SUBMITTED = ("APPLIED", "EMAILED", "INTERVIEWING", "OFFER", "EMPLOYER_REJECTED")

DEFAULTS = {
    "candidate_name": "",
    "min_bullets": 12,
    "min_words": 600,
    "max_words": 750,
    "required_facts": [],
    "banned_facts": [],
    "banned_title_claims": [],
    "banned_phrases": [
        "successfully", "results-driven", "proven track record",
        "think outside the box", "wear many hats", "dynamic self-starter",
    ],
}

BANNED_CHARS = {"—": "em-dash", "–": "en-dash"}

LEAK_MARKERS = ("compile_pdf", "verify_resume.py", "scripts/", "REGRESSION",
                "CSS below is locked", "CONTENT:", "DO NOT invent CSS",
                "MEASURED CAPACITY")

LIGATURES = {"ﬀ": "ff", "ﬁ": "fi", "ﬂ": "fl",
             "ﬃ": "ffi", "ﬄ": "ffl", "ﬅ": "st", "ﬆ": "st"}


def load_rules() -> dict:
    rules = dict(DEFAULTS)
    if RULES_PATH.exists():
        raw = json.loads(RULES_PATH.read_text(encoding="utf-8"))
        rules.update({k: v for k, v in raw.items() if not k.startswith("_")})
    else:
        print("  ~ config/resume_rules.json not found - using defaults, name "
              "check disabled. Copy config/resume_rules.example.json.")
    return rules


def extract(pdf_path):
    reader = pypdf.PdfReader(str(pdf_path))
    text = "".join(p.extract_text() or "" for p in reader.pages)
    fonts = set()
    for page in reader.pages:
        fdict = page.get("/Resources", {}).get("/Font", {}) or {}
        for key in fdict:
            base = str(fdict[key].get_object().get("/BaseFont") or "")
            fonts.add(base.split("+")[-1])
    return reader, text, fonts


def count_bullets(text):
    match = re.search(r"WORK EXPERIENCE(.*?)(SKILLS|$)", text, re.S | re.I)
    body = match.group(1) if match else ""
    return len(re.findall(r"\.\s*\n", body)) + (1 if body.rstrip().endswith(".") else 0)


def check(pdf_path, rules):
    fails, warns = [], []
    try:
        reader, text, fonts = extract(pdf_path)
    except Exception as exc:
        return [f"unreadable PDF: {exc}"], []

    if len(reader.pages) != 1:
        fails.append(f"{len(reader.pages)} pages (must be exactly 1)")

    if len(text.strip()) < 500:
        fails.append("no usable text layer - ATS cannot parse this (image-only?)")

    leaked = [m for m in LEAK_MARKERS if m in text]
    if leaked:
        fails.append("TEMPLATE TEXT LEAKED into the PDF (found: "
                     + ", ".join(leaked[:3])
                     + ") - an HTML comment closed early; check for a nested '-->'")

    name = (rules.get("candidate_name") or "").strip().upper()
    if name:
        head = text.strip()[:120].upper()
        if name not in head:
            fails.append(f"page does not start with the candidate name "
                         f"({name!r}) - got: {text.strip()[:60]!r}")

    found_ligs = {g: text.count(g) for g in LIGATURES if g in text}
    if found_ligs:
        detail = ", ".join(f"{LIGATURES[g]} x{n}" for g, n in found_ligs.items())
        samples = re.findall(r"\S*[ﬀ-ﬆ]\S*", text)[:3]
        safe = []
        for w in samples:
            for g, a in LIGATURES.items():
                w = w.replace(g, f"[{a}]")
            safe.append(w)
        fails.append(f"ligature glyphs in the text layer ({detail}) - an ATS doing "
                     f"literal matching cannot find these words: {safe}. "
                     f"Add 'font-variant-ligatures: none' to the template body.")

    for ch, label in BANNED_CHARS.items():
        if ch in text:
            sample = re.findall(r".{0,28}" + re.escape(ch) + r".{0,28}", text)[:2]
            fails.append(f"{label} present: {sample}")

    words = len(text.split())
    bullets = count_bullets(text)
    if bullets < rules["min_bullets"]:
        fails.append(f"{bullets} bullets (floor is {rules['min_bullets']})")
    if words < rules["min_words"]:
        fails.append(f"{words} words (floor is {rules['min_words']}) - page will read thin")
    if words > rules["max_words"]:
        warns.append(f"{words} words (over {rules['max_words']}) - check it is not cramped")

    for pattern in rules["required_facts"]:
        if not re.search(pattern, text):
            fails.append(f"missing required fact: {pattern}")
    for pattern in rules["banned_facts"]:
        if re.search(pattern, text):
            fails.append(f"banned fact present: {pattern}")

    summary = re.search(r"SUMMARY\s*\n(.{0,160})", text, re.S | re.I)
    if summary:
        for pattern in rules["banned_title_claims"]:
            if re.search(pattern, summary.group(1), re.I):
                fails.append(f"summary opens by claiming a banned title ({pattern})")

    if "[estimate" in text.lower():
        fails.append("contains an unverified [estimate - verify before sending] marker")

    for phrase in rules["banned_phrases"]:
        if re.search(r"\b" + re.escape(phrase) + r"\b", text, re.I):
            warns.append(f"filler phrase: '{phrase}'")

    return fails, warns


def submitted_files():
    if not DB.exists():
        return set()
    try:
        conn = sqlite3.connect(str(DB))
        rows = conn.execute(
            "select resume_pdf_path from jobs where status in (%s)"
            % ",".join("?" * len(SUBMITTED)), SUBMITTED)
        return {os.path.basename(r[0]) for r in rows if r[0]}
    except sqlite3.Error:
        return set()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf", nargs="*", help="resume PDF(s) to check")
    ap.add_argument("--all", action="store_true", help="check every PDF in resumes/")
    ap.add_argument("--unsent", action="store_true",
                    help="with --all, skip resumes already submitted (reads data/jobs.db)")
    args = ap.parse_args()

    rules = load_rules()

    if args.all:
        targets = sorted((ROOT / "resumes").glob("*.pdf"))
        if args.unsent:
            frozen = submitted_files()
            targets = [t for t in targets if t.name not in frozen]
    else:
        targets = [Path(p) for p in args.pdf]

    if not targets:
        ap.error("nothing to check - pass a PDF path or --all")

    bad = 0
    for path in targets:
        fails, warns = check(path, rules)
        if fails:
            bad += 1
            print(f"FAIL  {path.name}")
            for f in fails:
                print(f"        x {f}")
            for w in warns:
                print(f"        ~ {w}")
        elif warns:
            print(f"WARN  {path.name}")
            for w in warns:
                print(f"        ~ {w}")
        else:
            print(f"PASS  {path.name}")

    print(f"\n{len(targets) - bad}/{len(targets)} passed")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
