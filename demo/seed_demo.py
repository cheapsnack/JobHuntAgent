"""Seed the demo instance with fictional data.

Every company, URL and person here is invented. Nothing traces to a real
employer, a real application or a real recruiter.

    python demo/seed_demo.py          # wipe and reseed
"""
import sqlite3
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from guard import assert_demo, assert_no_real_companies

DB = assert_demo()
NOW = datetime(2026, 9, 10, tzinfo=timezone.utc)


def d(days_ago: int) -> str:
    return (NOW - timedelta(days=days_ago)).isoformat()


def brk(fit, core, shape, domain, scope, tools, quals, extra=""):
    return (
        f"SCORE {fit} = [core {core} x.35, shape {shape} x.20, domain {domain} x.15, "
        f"scope {scope} x.15, tools {tools} x.10, quals {quals} x.05] x25{extra}"
    )


JD_ONBOARDING = """Northwind Logistics - Product Manager, Customer Onboarding

We move freight for mid-market shippers. Onboarding a new shipper takes six
weeks and touches sales, solutions engineering, compliance and support. Today
it runs on a shared spreadsheet and four inboxes. Roughly one in five
onboardings slips past its committed go-live date and nobody can say why until
the customer escalates.

You will own the internal onboarding product end to end.

What you will do
- Run discovery with the implementation team and with shippers who have been
  through onboarding in the last two quarters
- Define the milestone model: what a stage is, who owns it, what unblocks it
- Build the status view leadership currently asks for over email every Monday
- Instrument time-in-stage so slippage is visible before it is escalated
- Write PRDs and acceptance criteria, run sprint planning and UAT with a team
  of eight engineers and one designer

What we are looking for
- 2+ years in product, or a former founder who has built and shipped
- Comfort with SQL and with defining success metrics from scratch
- Experience taking a manual, spreadsheet-driven process into a product
- Someone who will talk to customers directly rather than through a proxy

Nice to have
- Background in logistics, professional services automation, or any domain
  where a project has stages and a committed date
"""

JD_PROVIDER = """Beacon Health - Product Manager, Provider Onboarding

Beacon Health credentials and onboards clinical providers for regional payer
networks. Credentialing is regulated, slow and almost entirely manual.

Responsibilities
- Own the provider onboarding workflow from application through activation
- Reduce median time to activation, currently 47 days
- Partner with compliance to keep an auditable trail on every state change
- Define and track the activation funnel

Requirements
- 6+ years of product management experience, of which 3+ in US healthcare
- Deep familiarity with NCQA credentialing standards and CAQH
- Prior ownership of a regulated workflow product
- Registered nurse or clinical background strongly preferred
"""

JD_STUB = """Corvus Analytics is hiring a Product Manager. Bengaluru. Come build
the future of data with us. Competitive salary and equity."""

# company, role, location, status, fit, odds, days_ago, applied_days_ago,
# strengths, weaknesses, missing, recruiter, jd, notes_extra
ROWS = [
    ("Northwind Logistics", "Product Manager, Customer Onboarding", "Bengaluru", "INTERVIEWING", 86, 86, 24, 21,
     "Owned an analytics platform end to end for ~200 staff|Took a manual Excel process into a product|Writes PRDs and runs UAT with engineering",
     "No logistics domain experience|Team of 8 is larger than she has led",
     "freight,TMS", None, JD_ONBOARDING,
     "\nRound 2 scheduled. Onboarding-slippage problem maps directly to the catalogue work."),
    ("Beacon Health", "Product Manager, Provider Onboarding", "Remote", "APPROVED", 84, 62, 9, None,
     "Regulated-workflow ownership at a bank|Approval and access workflows shipped end to end|Activation-funnel metrics are her strongest suit",
     "No US healthcare domain|No NCQA or CAQH exposure|Asks for a clinical background",
     "NCQA,CAQH,HL7", "hiring@beaconhealth.example", JD_PROVIDER,
     "\nFIT-ODDS GAP 22. Capability match is real, the screen is hard. Apply via referral, not cold."),
    ("Kestrel Pay", "Product Manager, Payments", "Bengaluru", "APPLIED", 78, 74, 31, 28,
     "Financial services domain|Owned reconciliation reporting|SQL daily",
     "No card-scheme experience|Smaller team than posted", "ISO8583", None, None, ""),
    ("Lumen Grid", "Product Manager, Data Platform", "Hyderabad", "APPROVED", 76, 71, 6, None,
     "Shipped a data catalogue adopted by 100 users|Subscription and access workflows|Migration prioritisation",
     "No streaming or Kafka exposure|Platform team is engineer-heavy", "kafka,dbt", None, None, ""),
    ("Solstice HR", "Product Manager, Employee Onboarding", "Remote", "APPLIED", 74, 72, 19, 16,
     "Manual-to-product conversion is the exact story|Cross-functional delivery|Discovery with real users",
     "HR tech is a new domain|No multi-tenant experience", "HRIS,SCIM", None, None, ""),
    ("Ardent Cloud", "Product Manager, Cost Platform", "Bengaluru", "APPROVED", 73, 69, 8, None,
     "Founding member of a cost-management practice|Chargeback and allocation design|Persona-based dashboards",
     "Wants hands-on Terraform|Vendor-facing scope is broader", "terraform", "talent@ardentcloud.example", None, ""),
    ("Harbourline", "Manager, Strategy and Operations", "Chennai", "PENDING_REVIEW", 71, 71, 3, None,
     "Root-cause analysis on a 50-system migration|Board-level reporting|Lean Six Sigma",
     "No marketplace experience|Ops scope is people-heavy", "", None, None, ""),
    ("Vantage Freight", "Associate Product Manager", "Bengaluru", "PENDING_REVIEW", 69, 69, 2, None,
     "APM level fits her lineage|Analytics platform ownership|Comfortable with ambiguity",
     "Domain is new|Smaller comp band than target", "", None, None, ""),
    ("Tessellate", "Senior Product Manager, Platform", "Remote", "REJECTED", 72, 48, 12, None,
     "Platform thinking is genuine|Metrics definition",
     "Senior title she has never held|Asks 8+ years against 5", "",
     None, None,
     "\nLEVEL GATE. Tier B employer asking for a Senior PM lineage. Rejected on level, not on fit."),
    ("Corvus Analytics", "Product Manager", "Bengaluru", "PENDING_REVIEW", 55, 55, 1, None,
     "Data domain is adjacent", "No JD to assess against", "",
     None, JD_STUB,
     "\nJD QUALITY = none (under 200 chars). fit_raw 71 capped to 55. Recovering the JD lifts the cap automatically."),
    ("Pelagic Systems", "Product Manager, Integrations", "Remote", "EMPLOYER_REJECTED", 70, 66, 58, 55,
     "API-adjacent product work|Partner-facing delivery", "Integration work was pipelines, not partner APIs",
     "webhooks", None, None, "\nRejection received 2026-08-29, no reason given."),
    ("Ironbark Retail", "Product Manager, Merchant Tools", "Bengaluru", "EMPLOYER_REJECTED", 67, 61, 62, 60,
     "Merchant-facing analytics|Prioritisation under constraint", "No commerce background", "", None, None, ""),
    ("Quillon Software", "Product Owner", "Pune", "REJECTED", 64, 64, 15, None,
     "Backlog and acceptance criteria are daily work", "Pune is outside the accepted location list", "",
     None, None, "\nLOCATION GATE. Not a fit judgement."),
    ("Cinder Labs", "Founding Product Manager", "Remote", "APPROVED", 75, 75, 5, None,
     "Zero to one MVP built from a blank page|First-principles problem solving",
     "Stealth, so the problem space is unverifiable", "", "preet@cinderlabs.example", None, ""),
    ("Marlowe Bank", "Product Manager, Digital Channels", "Chennai", "APPLIED", 79, 73, 26, 23,
     "Retail banking product launched end to end|Persona and workflow analysis",
     "Mobile-first channel work is new", "", None, None, ""),
    ("Thornfield Group", "Chief of Staff", "Bengaluru", "APPLIED", 77, 74, 22, 20,
     "Board-level decks|Operating rhythm|Moves between the model and the memo",
     "No people-ops ownership", "", "brent@thornfield.example", None, ""),
    ("Aster Mobility", "Product Manager, Driver Experience", "Hyderabad", "PENDING_REVIEW", 68, 66, 4, None,
     "Gig-worker product discovery is directly relevant|Launch experience",
     "Two-sided marketplace dynamics are new", "", None, None, ""),
    ("Halyard Systems", "Product Manager, Professional Services", "Remote", "APPROVED", 80, 76, 7, None,
     "PSA is adjacent to delivery work she has run|Stage-gate and milestone modelling|Time-in-stage instrumentation",
     "No PSA tooling experience|Services margin is a new metric", "PSA",
     "recruiting@halyard.example", None,
     "\nRecruiter email present. Historic +10 odds boost NOT applied - the evidence for it was circular and it is flagged unvalidated."),
    ("Bellweather Insurance", "Product Manager, Claims", "Remote", "REJECTED", 58, 52, 20, None,
     "Workflow product ownership", "Actuarial depth is a hard requirement she does not meet", "actuarial",
     None, None, "\nDIMENSION 1 FLOOR applied. Core skill rated 1, so capped at 50."),
    ("Cobalt Freight", "Program Manager, Operations", "Chennai", "PENDING_REVIEW", 66, 66, 3, None,
     "Programme structure|Stakeholder management across functions", "Ops-heavy, less product surface", "",
     None, None, ""),
    ("Verdant Foods", "Product Manager, Supply Chain", "Bengaluru", "REJECTED", 54, 54, 18, None,
     "Analytics and forecasting", "No supply-chain systems background|Plant-floor exposure expected", "SAP APO",
     None, None, ""),
    ("Sable Legal", "Product Manager, Workflow", "Remote", "PENDING_REVIEW", 70, 68, 5, None,
     "Approval workflows and audit trails", "Legal domain is new", "", None, None, ""),
    ("Onyx Telecom", "Senior Product Manager", "Mumbai", "REJECTED", 69, 45, 25, None,
     "Telecom-adjacent reporting", "Mumbai is outside the accepted list|Senior title lineage", "",
     None, None, "\nTwo independent gates: location and level."),
    ("Greystone Capital", "Product Manager, Portfolio Tools", "Bengaluru", "APPLIED", 81, 75, 35, 32,
     "Profitability reporting across a large book|Financial modelling|SQL",
     "Buy-side workflows are new", "", None, None, ""),
    ("Lantern Health", "Associate Product Manager", "Remote", "APPROVED", 72, 72, 10, None,
     "APM level fits|Discovery and user research", "Healthcare domain is new", "", None, None, ""),
    ("Calderwood Freight", "Product Manager, Onboarding", "Chennai", "PENDING_REVIEW", 82, 80, 2, None,
     "Onboarding workflow is the closest match in the pipeline|Manual-to-product conversion|Time-in-stage metrics",
     "Freight domain is new", "", None, None, ""),
    ("Cascade Analytics", "Product Manager, Reporting", "Hyderabad", "APPLIED", 75, 71, 40, 37,
     "Reporting latency reduction is a direct match|Migration scoping", "BI tooling stack differs", "looker",
     None, None, ""),
    ("Fernwood Edu", "Product Manager, Learning", "Remote", "REJECTED", 51, 51, 30, None,
     "Product lifecycle ownership", "No edtech or pedagogy background|Content ops is core here", "LMS",
     None, None, ""),
    ("Adamant Security", "Product Manager, Platform", "Remote", "REJECTED", 49, 44, 28, None,
     "Platform and access-control adjacency", "Security depth is a hard requirement|Wants prior SOC exposure",
     "SIEM,SOC", None, None, ""),
    ("Wrenfield Retail", "Product Manager, Store Systems", "Bengaluru", "PENDING_REVIEW", 67, 65, 6, None,
     "Store-level reporting adjacency|Rollout planning", "Retail systems are new", "", None, None, ""),
]

ACTIONS = [
    ("INTERVIEW", d(-2), 60, "Northwind Logistics round 2. Product sense and a written exercise on the onboarding milestone model.", "Northwind Logistics"),
    ("ASSESSMENT", d(-4), 45, "Halyard Systems take-home. Define the activation funnel for a services onboarding product.", "Halyard Systems"),
    ("SEND", d(-1), 10, "Beacon Health outreach draft is written and waiting. Needs a referral path first, given the 22-point fit-odds gap.", "Beacon Health"),
    ("FORM", d(-6), 25, "Calderwood Freight application form. Asks for notice period and expected compensation.", "Calderwood Freight"),
    ("TASK", d(1), 30, "Cinder Labs asked for a one-page note on how you would find the first ten users. OVERDUE.", "Cinder Labs"),
]


def main():
    con = sqlite3.connect(DB)
    cols = {r[1] for r in con.execute("pragma table_info(jobs)")}
    con.execute("delete from jobs")

    for (co, role, loc, status, fit, odds, ago, applied_ago, strengths, weaknesses,
         missing, recruiter, jd, extra) in ROWS:
        core = 4 if fit >= 80 else 3 if fit >= 65 else 2 if fit >= 55 else 1
        notes = brk(fit, core, core, core - 1, core, core - 1, 4) + extra
        rec = {
            "company": co,
            "role_title": role,
            "source": "demo",
            "url": f"https://careers.{co.split()[0].lower()}.example/jobs/{abs(hash(role)) % 9000 + 1000}",
            "jd_text": jd,
            "location": loc,
            "date_added": d(ago),
            "applied_on": d(applied_ago) if applied_ago else None,
            "match_score": odds,
            "fit_score": fit,
            "odds_score": odds,
            "strengths": strengths.replace("|", "; "),
            "weaknesses": weaknesses.replace("|", "; "),
            "missing_keywords": missing,
            "recruiter_email": recruiter,
            "resume_pdf_path": "resumes/Jane_Acme_ProductManager.pdf" if status in
                               ("APPROVED", "APPLIED", "INTERVIEWING", "EMPLOYER_REJECTED") else None,
            "status": status,
            "notes": notes,
            "updated_at": d(ago),
        }
        use = {k: v for k, v in rec.items() if k in cols}
        con.execute(
            f"insert into jobs ({','.join(use)}) values ({','.join('?' * len(use))})",
            list(use.values()),
        )

    con.execute("""
        create table if not exists actions (
            id integer primary key autoincrement,
            kind text not null, deadline text, est_minutes integer,
            detail text, job_company text, done integer not null default 0,
            done_at text, created_at text not null
        )""")
    con.execute("delete from actions")
    for kind, dl, mins, detail, comp in ACTIONS:
        con.execute(
            "insert into actions (kind,deadline,est_minutes,detail,job_company,created_at)"
            " values (?,?,?,?,?,?)",
            (kind, dl[:10], mins, detail, comp, d(7)),
        )

    con.commit()
    n = con.execute("select count(*) from jobs").fetchone()[0]
    a = con.execute("select count(*) from actions").fetchone()[0]
    print(f"seeded {n} jobs, {a} actions into {DB}")
    for st, c in con.execute("select status,count(*) from jobs group by status order by 2 desc"):
        print(f"   {st:20} {c}")
    con.close()
    assert_no_real_companies(DB)
    print("guard: no real company names present")


if __name__ == "__main__":
    main()
