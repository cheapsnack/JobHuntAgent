# Design decisions, and the incidents behind them

This file exists because the interesting part of an agentic system is not
what it does when everything goes right. It is what happens the first time
the agent is confidently wrong, and whether that failure can happen twice.

Every rule below started as a prose instruction. Every one was ignored at
least once. The pattern that finally held: **turn the rule into a check that
fails**, so compliance stops depending on the model remembering.

Names, employers and figures from the author's run are generalised. The
shapes of the failures are exact.

---

## 1. A sample can prove a problem exists. It can never prove one does not.

**What happened.** Six job rows had company names that did not match their
URLs. The agent spot-checked three, found them clean, and reported the
corruption as "isolated". It was a clean off-by-one across all six, and
three resumes had already been built for the wrong companies.

**The rule.** If the cost of being wrong is a wrong resume, a wrong
application, or a deleted row, check every affected row. If exhaustive
checking is impractical, say so and report the finding as unverified.

**Where it lives.** In the operating rules the agent loads every session,
and in the habit of the audit scripts reporting counts of *everything*
checked, never a sample.

## 2. Preview before any bulk mutation

**What happened.** A cleanup ran `UPDATE ... WHERE company LIKE '%unparsed%'`
to clear junk alert-email rows. It also matched 13 links the user had pasted
by hand that were waiting for a JD fetch, and rejected them all.

**The rule.** Before any write touching more than one row, `SELECT` the
matched rows and read them. A pattern that matches two kinds of row is a
bug, not a shortcut. `bulk_update`-style helpers are dry-run by default.

## 3. Verify identity before building a resume

**What happened.** See incident 1. A stored company name is not evidence
that the posting is what the row says it is.

**The rule.** A resume may only be built for a posting whose live URL was
fetched this session and whose company and role match the row. No JD text
and no fetchable URL means no resume, and the row is flagged for recapture.

**Where it lives.** The tracker refuses to advance a row to APPROVED or
APPLIED when its JD text is under 200 characters.

## 4. The rule must be a check, or it is a wish

**What happened.** Six fields were declared mandatory on every scored row.
Two days later, 251 of 259 live rows were missing at least one. In the same
period the resume verifier, which is code that fails, had near-perfect
compliance.

**The rule.** `update_status()` refuses to move a row forward without a fit
score, an odds score, a location, strengths, weaknesses and a re-derivable
score breakdown. Prose compliance went from 2% to 100% the day it became a
function.

## 5. Provenance: every bullet traces to a source phrase

**What happened.** The load-bearing rule of the whole system, "never invent
a bullet", was enforced only by a human reading the PDF. A reworded fact or
a plausible-sounding hand-typed bullet would pass every other check.

**The rule.** Each bullet in the library carries a source id and an anchor
phrase that must literally appear in the candidate's source files. The
builder refuses to compile a spec that fails. An audit script checks the
whole corpus; the day it went in, 201 of 201 specs passed with zero content
changes. The point was to lock the property, not to fix a break.

## 6. The page must start with the candidate's name

**What happened.** A template comment contained the literal string
`<!-- CONTENT: ... -->`. The nested `-->` closed the comment early, and
every following line of build instructions rendered as visible text above
the candidate's name. The verifier passed both resumes, because leaked text
only makes a page look denser. One was sent before a human caught it.

**The rule.** The verifier now fails on any template or build text in the
PDF, and requires the first token on the page to be the candidate's name.
And: always read a finished resume back visually once. A verifier catches
what it has been told to catch.

## 7. Never mark an outcome without matching company, role AND date

**What happened.** The user said "those two rejected me" about two old
email replies. The outcome tracker had already flagged both as "names a
different role than this row". The flag was read and overridden. Both marks
were wrong: one rejection belonged to a different row, the other to an
application that had never been logged. One row's applied date was a month
*after* the rejection it was supposedly attached to.

**The rule.** Before writing an employer outcome, the role title in the
evidence must match the row and the timeline must be possible. A tracker
warning is a stop sign. This applies to a direct instruction from the user
too: "I got rejected" says an outcome happened, not which row it happened
to.

---

## Scoring: what was measured, and what changed because of it

**Two scores, never blended.** A single match score hid the distinction
that actually drives decisions. `fit` is the six-dimension rubric result,
employer-agnostic. `odds` applies employer-tier severity, level gates and
knockouts. A gap of 10+ points is a referral signal, not a reason to skip.

**Information availability was inflating scores.** Mean fit by how much JD
text existed at scoring time, across 708 scored rows:

| JD available | rows | mean fit |
|---|---|---|
| full (2,500+ chars) | 501 | 34 |
| partial (900 to 2,499) | 56 | 68 |
| stub (200 to 899) | 43 | 60 |
| none | 108 | 41 |

A thirty-point spread from nothing but how much the agent could read. The
rubric itself was calibrated; it was being run on inputs it was never
designed for. Fit is now capped by JD quality (stub = 69, so a human always
looks; none = 55, the skip bar), the uncapped value is kept, and recovering
the real posting lifts the cap automatically.

**A boost that measured the system's own behaviour.** A +10 odds bonus for
postings carrying a recruiter email was justified by "6.9x more likely to
reach applied/emailed". Those states are decisions the pipeline makes, not
the employer. Against actual employer replies the effect was absent. The
bonus stays as a labelled, untested hypothesis until enough outcomes
resolve, and the scoreboard's validation test refuses to conclude anything
under 25 resolved applications. Wiring an unvalidated multiplier into a
score is exactly how that "6.9x" got documented in the first place.

**Ghost-job signals flag, never score.** Repost detection, watch spans and
re-sighting counts accumulate on the row. None of them touch a score until
they are validated against outcomes.

## Operating an agent, not just prompting one

- **Heartbeats prove liveness; nothing proves the negative.** A process
  probe reported the message listener dead for two days while it was
  demonstrably consuming messages. The listener now stamps its own
  heartbeat; a fresh stamp is trusted over any probe.
- **A config nothing reads looks exactly like a config that works.**
  Fourteen verified portal entries sat in a JSON file for days while the
  poller built its list from a hard-coded dict. When adding an entry, run
  the consumer and confirm the entry appears in its output.
- **Not pushing an update is not the same as removing what is already
  there.** A retention filter that merely skipped rejected rows on push left
  stale copies on the dashboard forever. Purge is a separate step.
- **Timestamps need a timezone or they are not timestamps.** A text
  `updated_at` column written as UTC by one client and local time by another
  made a stale dashboard row beat a fresh local one by 5.5 hours, and
  reverted a real status change while it was being watched.
- **Count what reached the stage, not what is at the stage.** The North
  Star counted rows whose *current* status was "interviewing", so every
  interview that ended in a rejection dropped out of the numerator. It read
  3 when 9 applications had interviewed. Milestones are dated columns now.
- **Task prompts drift.** A scheduled task's prompt is a second copy of the
  rules. When a rule changes, grep the task prompts for the old value.

## What is deliberately not here

No LangGraph-style state machine, no LaTeX, no aggregator APIs, no voice
interface. The gap this system closed relative to comparable open-source
agents was verification instrumentation, not orchestration. Everything
above is plain Python, SQLite and a locked HTML template, because the
constraint was never generating documents. It was never sending a wrong
one.
