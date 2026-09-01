"""
Build a tailored resume from templates/resume_base.html. The CSS is never touched.

Why this exists:
    Hand-written resumes drift - the CSS gets re-invented per session and content
    gets cut to force one page. This module makes the layout fixed and the
    content the only variable. Only the text between the CONTENT markers changes.

Tailoring means SELECTING and ORDERING real bullets from the library below, and
re-labelling skills lines to mirror a JD's own terminology. Nothing is invented.
If a JD needs something you have not done, the honest answer is the bullet does
not exist.

Usage:
    python scripts/build_resume.py --list
    python scripts/build_resume.py --spec acme --out resumes/Jane_Acme.pdf

-----------------------------------------------------------------------------
EVERYTHING BELOW THE LINE IS EXAMPLE CONTENT for a fictional candidate.
During onboarding (see ONBOARDING.md) the agent replaces the bullet library,
ROLE_HEADERS, CERTS and the SKILLS_* blocks with YOUR real experience.
-----------------------------------------------------------------------------
"""
import argparse
import html
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = ROOT / "templates" / "resume_base.html"
SCRATCH = ROOT / "scratchpad"

# --------------------------------------------------------------- bullet library
# Keyed real bullets, one dict per employer. EXAMPLE DATA - replace during
# onboarding. Every bullet: "accomplished X, as measured by Y, by doing Z"
# where a real metric exists. One line, two max. No invented numbers.
ROLE_A = {
    "platform": "Owned the end-to-end roadmap for an internal analytics platform used by around 200 staff, covering discovery, definition and launch, and cut median report load time from 60 seconds to under 7 across two quarters.",
    "discovery": "Ran discovery for a new self-serve reporting product, including 20 user interviews, persona and workflow analysis and competitor benchmarking, and translated the findings into a prioritized PRD that was taken through to launch.",
    "catalogue": "Shipped a data catalogue with subscribe, access and approval workflows that replaced a manual request process, drove adoption to around 100 active users in three months, and iterated on access rules based on real usage.",
    "specs": "Wrote product specifications including PRDs, user stories and acceptance criteria, wireframed flows, and ran sprint planning, backlog grooming and UAT cycles with a 6-engineer team and business stakeholders.",
    "metrics": "Defined the success metrics leadership prioritized investment against, and led a migration of core reporting off a legacy stack that cut refresh latency from T+30 days to T+2 for the leadership team.",
    "xfn": "Acted as the decision owner for the platform across engineering, design, data and business teams, running weekly syncs, championing product trade-offs and driving root-cause analysis on production issues.",
}
ROLE_B = {
    "model": "Built a forecasting model over more than two years of operational data, validated at around 93 percent accuracy, and presented the results and recommendations to senior finance and operations leadership.",
    "framework": "Designed a risk-based customer segmentation framework projected to cut overdue accounts by around 25 percent, which was recognized by the division head and adopted for the following planning cycle.",
}
ROLE_C = {
    "founding": "Helped stand up a new practice area from inception as a founding team member, defining the operating model that was later reused across other teams, and earned two performance awards over four years.",
    "savings": "Drove cost-optimization levers across client accounts, including commitment planning and purchasing best practices, and unlocked more than 300 thousand dollars a year in recurring savings.",
    "reviews": "Ran cost and architecture reviews across large multi-cloud estates and delivered rightsizing recommendations that contributed to more than one million dollars a year in savings for a Fortune 500 client.",
    "book": "Managed financials for more than 150 client accounts within a book worth over 20 million dollars a year, owning the monthly billing cycle for 500-plus stakeholders and leading a team of five.",
    "audiences": "Rebuilt a single failing spend report into three separate views on the same data for leadership, finance and engineering, each one cut to the specific decision that group was actually making.",
}

ROLE_HEADERS = {
    "a": ("Acme Corp - Senior Analyst, Product", "Jun'24 - Present"),
    "b": ("Globex - Analyst, Strategy (Internship)", "Apr'23 - May'23"),
    "c": ("Initech Consulting - Consultant", "Aug'19 - Mar'23"),
}
LIBRARY = {"a": ROLE_A, "b": ROLE_B, "c": ROLE_C}

CERTS = ("Lean Six Sigma Green Belt (Issuing Body), Cloud Practitioner (2022), "
         "Scrum Product Owner (2023)")

SKILLS_PRODUCT = [
    ("Product & Strategy", "Product lifecycle from discovery to launch, user research and interviews, PRDs and user stories, roadmap and prioritization, KPIs and OKRs, Agile and Scrum delivery, go-to-market"),
    ("Data & Analytics", "SQL, data modelling, ETL pipelines, product and funnel analytics, forecasting and statistical modelling, financial modelling"),
    ("Platforms & Tools", "Jira, Confluence, Azure DevOps, Figma, Power BI, cloud platforms including AWS, GCP and Azure"),
    ("Domain", "Financial services, enterprise data platforms, internal tooling and reporting products"),
]
SKILLS_STRATEGY = [
    ("Strategy & Operations", "Commercial and P&L analysis, prioritization under constraint, executive and board communication, operating-model design, KPIs and OKRs, go-to-market planning"),
    ("Data & Analytics", "SQL, data modelling, MI and profitability reporting, forecasting and statistical modelling, financial modelling"),
    ("Platforms & Tools", "Jira, Confluence, Figma, Power BI, cloud platforms including AWS, GCP and Azure"),
    ("Domain", "Financial services, cloud cost management and FinOps, enterprise data platforms"),
]

# ----------------------------------------------------------------- render / build

def render(spec: dict) -> str:
    doc = TEMPLATE.read_text(encoding="utf-8")

    summary = " ".join(spec["summary"].split())
    doc = re.sub(r'(<div class="summary">)(.*?)(</div>)',
                 lambda m: m.group(1) + "\n  " + html.escape(summary, quote=False) + "\n" + m.group(3),
                 doc, count=1, flags=re.S)

    blocks, total = [], 0
    for role_key in spec["order"]:
        heading, dates = ROLE_HEADERS[role_key]
        keys = spec["bullets"][role_key]
        items = "\n".join(
            f"  <li>{html.escape(LIBRARY[role_key][k], quote=False)}</li>" for k in keys)
        total += len(keys)
        blocks.append(
            f'<div class="row">\n'
            f'  <div class="left">{heading}</div>\n'
            f'  <div class="right">{dates}</div>\n'
            f'</div>\n<ul>\n{items}\n</ul>')
    if total < 12:
        raise ValueError(f"{spec['slug']}: only {total} bullets, floor is 12")

    work = "<h2>Work Experience</h2>\n\n" + "\n\n".join(blocks)
    doc = re.sub(r"<h2>Work Experience</h2>.*?(?=<!-- CONTENT: skills)",
                 work + "\n\n", doc, count=1, flags=re.S)

    lines = "\n".join(
        f'<div class="skill"><b>{html.escape(label)}:</b> {html.escape(text, quote=False)}</div>'
        for label, text in spec["skills"])
    lines += f'\n<div class="skill"><b>Certifications:</b> {html.escape(CERTS, quote=False)}</div>'
    doc = re.sub(r'(<h2>Skills &amp; Tools</h2>\n).*?(?=\n</body>)',
                 lambda m: m.group(1) + lines, doc, count=1, flags=re.S)
    return doc


def build(spec: dict, out_pdf: Path) -> bool:
    SCRATCH.mkdir(parents=True, exist_ok=True)
    html_path = SCRATCH / f"resume_{spec['slug']}.html"
    html_path.write_text(render(spec), encoding="utf-8")

    out_pdf.parent.mkdir(parents=True, exist_ok=True)
    compiled = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "compile_pdf.py"),
         str(html_path), str(out_pdf), "--fit"],
        capture_output=True, text=True)
    if compiled.returncode != 0:
        print(f"  COMPILE FAILED: {compiled.stderr.strip()[:300]}")
        return False

    verify = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "verify_resume.py"), str(out_pdf)],
        capture_output=True, text=True)
    passed = verify.stdout.lstrip().startswith("PASS")
    print(f"  {'PASS' if passed else 'FAIL'}  {out_pdf.name}")
    if not passed:
        for line in verify.stdout.splitlines():
            if line.strip().startswith("x"):
                print(f"        {line.strip()}")
    return passed


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from resume_specs import SPECS

    ap = argparse.ArgumentParser()
    ap.add_argument("--spec")
    ap.add_argument("--out")
    ap.add_argument("--list", action="store_true")
    args = ap.parse_args()

    if args.list:
        for slug, spec in SPECS.items():
            print(f"  {slug:<16}{spec.get('output', '(no default output)')}")
        return 0

    if not args.spec or args.spec not in SPECS:
        ap.error("pass --spec <slug> (see --list)")

    spec = SPECS[args.spec]
    out = Path(args.out) if args.out else ROOT / spec["output"]
    print(f"{args.spec} -> {out.name}")
    return 0 if build(spec, out) else 1


if __name__ == "__main__":
    sys.exit(main())
