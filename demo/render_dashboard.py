"""Render the demo database as a standalone HTML dashboard.

The shipped dashboard reads Supabase. For a screen recording we want zero
network calls, so this writes a self-contained file straight from SQLite.

    python demo/render_dashboard.py && start demo/dashboard.html
"""
import html
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from guard import assert_demo, assert_no_real_companies

DB = assert_demo()
OUT = Path(__file__).resolve().parent / "dashboard.html"
TODAY = datetime(2026, 9, 10, tzinfo=timezone.utc).date()

REVIEW = ("PENDING_REVIEW",)
TOAPPLY = ("APPROVED",)
PIPELINE = ("APPLIED", "EMAILED", "INTERVIEWING", "OFFER", "EMPLOYER_REJECTED")

LABEL = {
    "PENDING_REVIEW": "In review", "APPROVED": "Ready to apply", "APPLIED": "Applied",
    "EMAILED": "Emailed", "INTERVIEWING": "Interviewing", "OFFER": "Offer",
    "EMPLOYER_REJECTED": "Rejected", "REJECTED": "Passed",
}


def e(v):
    return html.escape(str(v)) if v is not None else ""


def chips(s, cls):
    if not s:
        return ""
    return "".join(f'<span class="chip {cls}">{e(p.strip())}</span>'
                   for p in str(s).split(";") if p.strip())


def dleft(deadline):
    if not deadline:
        return None
    try:
        return (datetime.fromisoformat(deadline).date() - TODAY).days
    except ValueError:
        return None


def job_card(r):
    fit, odds = r["fit_score"] or 0, r["odds_score"] or 0
    gap = fit - odds
    gapnote = (f'<div class="gap">Fit exceeds odds by {gap}. '
               f'The capability match is real and the screen is hard. Route via referral.</div>'
               if gap >= 10 else "")
    return f"""
    <article class="card">
      <div class="chead">
        <div>
          <h3>{e(r['company'])}</h3>
          <p class="role">{e(r['role_title'])}</p>
        </div>
        <div class="scores">
          <div class="sc"><b>{fit}</b><span>fit</span></div>
          <div class="sc alt"><b>{odds}</b><span>odds</span></div>
        </div>
      </div>
      <p class="meta">{e(r['location'])} &middot; <span class="st s-{e(r['status'])}">{LABEL.get(r['status'], r['status'])}</span></p>
      {gapnote}
      <div class="chips">{chips(r['strengths'], 'pos')}{chips(r['weaknesses'], 'neg')}</div>
    </article>"""


def main():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    jobs = con.execute("select * from jobs").fetchall()
    try:
        acts = con.execute("select * from actions where done=0").fetchall()
    except sqlite3.OperationalError:
        acts = []
    con.close()

    def sect(statuses, order_desc="fit_score"):
        rows = [r for r in jobs if r["status"] in statuses]
        rows.sort(key=lambda r: (r[order_desc] or 0), reverse=True)
        return "".join(job_card(r) for r in rows) or '<p class="empty">Nothing here.</p>'

    todo = sorted(acts, key=lambda a: (a["deadline"] or "9999"))
    todo_html = ""
    for a in todo:
        n = dleft(a["deadline"])
        if n is None:
            badge, cls = "no date", "later"
        elif n < 0:
            badge, cls = f"{abs(n)}d overdue", "over"
        elif n == 0:
            badge, cls = "due today", "over"
        else:
            badge, cls = f"{n}d left", "soon" if n <= 3 else "later"
        todo_html += f"""
        <article class="card todo">
          <div class="chead">
            <div><h3>{e(a['kind'])} &middot; {e(a['job_company'])}</h3></div>
            <span class="badge {cls}">{badge}</span>
          </div>
          <p class="detail">{e(a['detail'])}</p>
          <p class="meta">about {a['est_minutes']} min</p>
        </article>"""
    todo_html = todo_html or '<p class="empty">Nothing outstanding.</p>'

    counts = {
        "todo": len(acts),
        "review": sum(1 for r in jobs if r["status"] in REVIEW),
        "apply": sum(1 for r in jobs if r["status"] in TOAPPLY),
        "pipe": sum(1 for r in jobs if r["status"] in PIPELINE),
    }

    doc = f"""<!doctype html><html><head><meta charset="utf-8">
<title>JobHuntAgent - demo</title><meta name="viewport" content="width=device-width,initial-scale=1">
<style>
*{{box-sizing:border-box}}
body{{margin:0;font:15px/1.5 -apple-system,Segoe UI,Roboto,sans-serif;background:#f6f7f9;color:#14161a}}
.banner{{background:#b45309;color:#fff;text-align:center;padding:7px;font-weight:600;letter-spacing:.04em;font-size:13px}}
header{{padding:22px 28px 0;max-width:1100px;margin:0 auto}}
h1{{margin:0;font-size:21px}} .sub{{color:#666;margin:3px 0 16px;font-size:13px}}
nav{{display:flex;gap:4px;border-bottom:1px solid #dcdfe4;max-width:1100px;margin:0 auto;padding:0 28px}}
nav button{{border:0;background:none;padding:10px 15px;font:inherit;font-weight:600;color:#666;cursor:pointer;border-bottom:2px solid transparent}}
nav button.on{{color:#14161a;border-bottom-color:#14161a}}
nav .n{{background:#e6e8ec;border-radius:9px;padding:1px 7px;margin-left:6px;font-size:12px;color:#444}}
main{{max-width:1100px;margin:0 auto;padding:20px 28px 60px}}
.grid{{display:grid;gap:13px;grid-template-columns:repeat(auto-fill,minmax(330px,1fr))}}
.card{{background:#fff;border:1px solid #e2e5ea;border-radius:11px;padding:15px}}
.chead{{display:flex;justify-content:space-between;gap:12px;align-items:flex-start}}
h3{{margin:0;font-size:15.5px}} .role{{margin:2px 0 0;color:#555;font-size:13.5px}}
.scores{{display:flex;gap:7px;flex-shrink:0}}
.sc{{background:#eef6ff;border-radius:8px;padding:5px 9px;text-align:center;min-width:44px}}
.sc.alt{{background:#f0f0f4}} .sc b{{display:block;font-size:17px;line-height:1.1}}
.sc span{{font-size:10px;text-transform:uppercase;color:#667;letter-spacing:.05em}}
.meta{{color:#667;font-size:12.5px;margin:9px 0 0}}
.st{{padding:2px 8px;border-radius:20px;background:#eceff3;font-weight:600;font-size:11.5px}}
.s-INTERVIEWING{{background:#dcfce7;color:#15803d}} .s-EMPLOYER_REJECTED{{background:#fee2e2;color:#b91c1c}}
.s-APPROVED{{background:#e0edff;color:#1d4ed8}}
.gap{{margin:10px 0 0;padding:8px 10px;background:#fff7ed;border-left:3px solid #f59e0b;border-radius:5px;font-size:12.5px;color:#7c2d12}}
.chips{{margin-top:11px;display:flex;flex-wrap:wrap;gap:5px}}
.chip{{font-size:11.5px;padding:3px 8px;border-radius:20px}}
.pos{{background:#eaf7ee;color:#166534}} .neg{{background:#fdeeee;color:#9f1239}}
.badge{{font-size:11.5px;font-weight:700;padding:3px 9px;border-radius:20px;white-space:nowrap}}
.over{{background:#fee2e2;color:#b91c1c}} .soon{{background:#fef3c7;color:#92400e}} .later{{background:#eceff3;color:#555}}
.detail{{font-size:13px;color:#333;margin:9px 0 0}} .todo{{border-left:3px solid #b45309}}
.empty{{color:#889;font-size:14px}} section{{display:none}} section.on{{display:block}}
</style></head><body>
<div class="banner">DEMO DATA &mdash; every company, score and contact below is fictional</div>
<header><h1>JobHuntAgent</h1><p class="sub">Jane Doe &middot; local instance &middot; no network calls</p></header>
<nav>
  <button class="on" data-t="todo">To do<span class="n">{counts['todo']}</span></button>
  <button data-t="review">Review<span class="n">{counts['review']}</span></button>
  <button data-t="apply">To apply<span class="n">{counts['apply']}</span></button>
  <button data-t="pipe">Pipeline<span class="n">{counts['pipe']}</span></button>
</nav>
<main>
  <section id="todo" class="on"><div class="grid">{todo_html}</div></section>
  <section id="review"><div class="grid">{sect(REVIEW)}</div></section>
  <section id="apply"><div class="grid">{sect(TOAPPLY)}</div></section>
  <section id="pipe"><div class="grid">{sect(PIPELINE)}</div></section>
</main>
<script>
document.querySelectorAll('nav button').forEach(b=>b.onclick=()=>{{
  document.querySelectorAll('nav button').forEach(x=>x.classList.remove('on'));
  document.querySelectorAll('section').forEach(s=>s.classList.remove('on'));
  b.classList.add('on'); document.getElementById(b.dataset.t).classList.add('on');
}});
</script></body></html>"""

    OUT.write_text(doc, encoding="utf-8")
    assert_no_real_companies(DB)
    print(f"wrote {OUT}")
    print(f"  to do {counts['todo']} | review {counts['review']} | to apply {counts['apply']} | pipeline {counts['pipe']}")


if __name__ == "__main__":
    main()
