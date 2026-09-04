# Interview-prep report generator

An optional companion to the resume kit. When the user has an interview
lined up, the agent builds a company-researched, candidate-accurate prep
report and compiles it to a PDF in `interview_prep/` (git-ignored) with
`scripts/compile_pdf.py`, the same renderer the resumes use.

It works for **any company, any role, any domain** - product, engineering,
data, sales, consulting, operations. Nothing here is product-management
specific; the frameworks and question types adapt to the actual role.

Trigger it when the user says "interview prep", "prep me for the <company>
interview", names a company they are interviewing with, or pastes an
existing prep doc (their own, or one made for someone else) and asks to
redo it for themselves.

---

## Ground rules (same standard as the resumes)

1. **Never reuse another candidate's facts.** If an existing document is
   given as a starting point, treat its candidate-specific content
   (background, stories, name, employer history, "why this company") as
   **structure only**. Every fact about the candidate is rebuilt from the
   user's real sources. Company research (products, SWOT, leadership, news,
   competitors) can be refreshed and reused - it is about the company, not
   the person.
2. **Ground every candidate claim in real sources**: the base resume in
   `candidate_profile/`, `candidate_profile/verified_facts.md`, the tailored
   resume for this job in `resumes/` if one exists, and the tracker row if
   `track.py` is in use. Never invent a metric, employer, or credential.
3. **Use the real JD**, not a guessed one. Check `JDs/<Company>_<Role>.md`,
   then the tracker's stored JD text, then ask the user to paste it.
4. **Score gaps honestly - for the user's own preparation.** For every JD
   requirement the candidate does not clearly meet, say so in the document:
   acknowledge once, bridge with the closest real evidence, move on. Do not
   manufacture an experience-year gap that is not real - check the actual
   tenure math. (Gaps are handled here for preparation only. They are never
   scripted into an outbound pitch - see Section 6.)
5. **No em-dashes or en-dashes** - spaced hyphen or rewrite.
6. **Refresh company facts thoroughly, do not skim.** Anything more than a
   few weeks old is re-verified this pass or clearly marked as carried over.
7. **This is not the one-page rule.** A thorough single-role prep runs long
   - a full resume walkthrough, role-appropriate frameworks, a company and
   competitor deep dive, and a strategic teardown typically land in the
   20-30 page range. Do not pad to a number, do not compress real detail to
   look short.

---

## Source discipline: flag every fact, never hallucinate

Interview prep fails a specific way: the candidate repeats a fabricated
funding number or "recent news" item in the room and it collapses on the
first follow-up, which is worse than not having the fact. Treat every stated
fact as carrying a source, and treat "could not find this" as a valid,
common, correct answer.

**Every factual claim gets a confidence badge, rendered inline** (a small
coloured `<span>`; define the classes in the report CSS once, and put a
short legend near the top of the company section).

*Source-strength (for a fact researched this pass):*

| Badge | Meaning |
|---|---|
| **VERIFIED** | Company primary source (their filing, press release, careers page for a claim about themselves), or something the user told the agent directly with a date. Repeat with full confidence. |
| **REPORTED** | A credible independent third party: mainstream press, an established data vendor, an analyst house. Solid, not the company's own word. |
| **ESTIMATED** | Not stated anywhere; triangulated from real indirect data (e.g. headcount from LinkedIn + a revenue-per-head benchmark). Show the basis inline. |
| **INFERRED** | A strategic read, not a fact. Reasoned but unconfirmed - label it and tell the user to validate it in the interview. |

*Provenance (can combine with the above):*

| Badge | Meaning |
|---|---|
| **CARRIED OVER** | Reused from a prior prep pass and not re-checked. Note the date last verified. |
| **COULD NOT VERIFY** | Actively looked for and not found, or found only in a low-trust source. State it in the document, do not omit the topic silently. |

**The badge is not a licence to guess.** ESTIMATED and INFERRED label
unavoidable uncertainty honestly - they never make a fabricated number feel
sanctioned. If there is no real indirect data to triangulate from, the
answer is "not publicly disclosed", not an ESTIMATED badge on a number
borrowed from a comparable company.

Concrete rules that follow:

- **Never state a specific number** - funding, valuation, revenue, headcount,
  growth rate, comp band, founding year, customer count - unless a real
  source for that exact number was found this pass. An ESTIMATED badge is
  allowed only when the document shows the indirect data the estimate is
  built from.
- **Never carry an ESTIMATED or INFERRED number up into a summary sentence
  as if it were fact.** The executive summary and the recall sheet repeat
  only VERIFIED / REPORTED figures. This is the specific way the badge
  system fails: a hedged number three sections deep gets laundered into a
  confident headline.
- **Never invent an interviewer's name, title, background, or a quote.** If
  the user names an interviewer and nothing turns up, say "no public profile
  found - confirm with the recruiter".
- **Keep the company's own framing separate from independently-verified
  fact.** "Their careers page says they are the market leader" is a weaker
  claim than "an independent source confirms it" - phrase each to make clear
  which it is.
- **A blocked, empty, or stale fetch is reported, not backfilled.** If a
  review site blocks the fetch or a press page returns nothing recent, say
  exactly that in the section rather than moving on as if it were complete.
- **When unsure whether a fact is solid, understate.** "Reportedly closed a
  round in [year], per [source]" beats a bare confident figure.

---

## Inputs to gather before writing

1. **Company, role, domain.** Infer the domain from the JD/title - it
   decides which frameworks and question types belong in Section 1.
2. **The real JD** (see ground rule 3).
3. **The tailored resume for this job** if one exists - it already carries
   the fit-check, missing keywords, and score that feed Section 4.
4. **Interview stage/format** if the user mentions it (round, video vs
   in-person, interviewer name). If unknown, write "confirm with recruiter".
5. **Fresh company research against a fixed checklist** - work every item,
   do not skip one because "it probably does not matter for this role":
   - **Business fundamentals** - what they actually sell (their precise
     terms), the revenue model, ownership structure, and any real financials.
   - **Market position** - named competitors researched from *their own*
     sites and press, any signal on relative scale, and the growth
     trajectory (expanding, flat, layoffs, hiring freeze).
   - **Leadership and org** - founders/CEO background and public writing,
     recent leadership changes, team size if a real source states it.
   - **Recent developments (last ~6 months)** - launches, funding,
     partnerships, restructuring, from the company's own press *and* an
     independent search, most recent first. If nothing, say so.
   - **Culture and process signals** - stated values from the careers page,
     and separately, independently reported culture themes and interview-
     process detail (rounds, typical questions, timeline). Review sites often
     block automated fetches; when they do, say so and fall back to search.
   - **Role/team context** - the hiring manager or team on the JD or
     LinkedIn, where the team sits in the org, anything public about the
     specific product this role owns.
   - **Verification pass on secondary claims** - cross-check any award,
     certification, or metric against a second independent source before
     stating it.

---

## Output structure

Write one HTML file under `scratchpad/`, then compile with
`python scripts/compile_pdf.py <scratch.html> interview_prep/<Name>_<Company>_InterviewPrep.pdf`.

1. **Cover page** - title, company, role, candidate, stage, applied date if
   known, prepared date.

2. **Section 1 - Resume Q&A**, in three explicit layers (call this out in a
   how-to box): **company/role-specific**, **general craft questions for the
   actual domain**, **technical-depth questions for the actual domain**.
   - A 90-second opener script.
   - **A one-line narrative arc for the company** the candidate can memorise
     and use as the throughline of any "what do you know about us" answer.
   - **A full end-to-end resume walkthrough** - one Q&A per employer, role,
     internship and degree in chronological order, plus the reasoning behind
     any career pivot. Do not skip short roles.
   - **6-10 STAR stories** across different competencies (ownership,
     ambiguity/0-to-1, conflict, failure, tight deadlines, mentoring, saying
     no to scope). Vary the story per competency.
   - **A frameworks cheat-sheet table matched to the role's domain** - never
     default to product frameworks for a non-product role. By domain, e.g.:
     - *Product*: RICE, MoSCoW, Kano, North Star/OKRs, CIRCLES, JTBD.
     - *Sales/GTM*: MEDDIC/MEDDPICC, BANT, Challenger, ICP/TAM-SAM-SOM.
     - *Consulting/strategy*: MECE, issue trees, Porter's Five Forces, 3Cs,
       hypothesis-driven problem solving.
     - *Data/analytics*: the analytics maturity ladder, A/B testing
       fundamentals, funnel/cohort analysis, significance basics.
     - *Engineering*: system-design fundamentals for the role's stack,
       SDLC/CI-CD, relevant architecture patterns.
     - *Operations/program*: RACI, critical path, Lean/Six Sigma, Kanban/WIP.
     Pair it with a **second table mapping the candidate's real process
     vocabulary and tools** (from their actual resume) to where they used
     each. Never list a framework without connecting it to real experience.
   - **5+ general craft/case questions** for the discipline, plus the
     popular generic questions for it (the equivalents of "favourite
     product", "why this field", "biggest weakness", estimation).
   - **A technical concepts primer** when the role is AI-native/AI-adjacent
     (ML vs GenAI, LLM basics, agent vs agentic, RAG, prompting vs
     fine-tuning, hallucination and how the discipline designs around it).
     For non-AI roles, substitute the technical primer the JD's must-haves
     actually call for, or skip it.
   - **3-5 gap questions addressed head-on**, from the JD-vs-resume
     fit-check - acknowledge once, bridge with real evidence, do not
     apologise twice.
   - **2-3 fit/motivation questions.**
   - **Likely questions the candidate will actually be asked, with answer
     frames.** 6-10, predicted from the JD, the discipline, the stage, and
     the company's current situation. For each: the question as it will be
     phrased, then a 3-4 bullet frame (structure + the real evidence to hang
     on it + where to land). Distinct from the gap questions - this is the
     "walk me through what you know about us", "first 90 days", "why are you
     leaving" set.
   - **8-10 questions for the candidate to ask the interviewer**, grouped
     (role/team, strategy/market, product specifics, culture/growth), each
     anchored to a specific researched fact. For each, give two companions:
     - **Why ask** - what it reveals or signals.
     - **Listen for** - what a strong answer from the interviewer sounds
       like, with a concrete marker where one exists.
     Add a short **sequencing tip** (open with a strategy question for
     altitude, go deep on 2-3 craft questions, close with one that lets them
     sell the role; save the sharpest operating-model question for the
     senior round) and a 3-4 item **questions to avoid** list specific to
     this company.

3. **Section 2 - Company and Role Deep Dive**: overview, products/services
   named precisely, financials/funding if real, SWOT, leadership,
   values-alignment table, culture/interview-process notes, competitors
   (from the competitors' own materials), recent news dated most-recent-
   first, salary reference if findable.
   - **Strategic teardown subsection**: a consultant-style read of the
     company's *actual* current business model, then **3 grounded,
     evidence-based ideas** for new revenue streams, products, or strategic
     moves - each with the gap it addresses, the supporting evidence, rough
     sizing logic, and a natural non-pitchy way to raise it (as an answer to
     "any questions or ideas for us", not an unprompted monologue). Tie at
     least one idea to the candidate's real background where a genuine
     connection exists. Structure it to be usable under pressure:
     - **Priority-tier the ideas P0 / P1 / P2** with a one-line reason, so
       the candidate leads with the strongest.
     - **Competitive-response table**: for each of the 2-3 realest threats,
       "if <competitor> wins on <axis>, the company should respond with
       <move>". This is the highest-signal thing to have ready for "what
       worries you about our position".
     - **Investor / board thesis line**: from the funding history, the
       investors, and what they have said publicly, infer what the founders
       and board care about right now - therefore what this interview is
       likely to test. One short paragraph, tagged INFERRED.

4. **Section 3 - Cultural Fit Narrative**: a "why this company" story
   grounded in specific research (not generic enthusiasm), a working-style
   fit table, a table mapping the candidate's real experience to the
   company's *current* stated needs, and a Day 1-90 plan.

5. **Section 4 - Experience-JD Fit**: a requirement-to-evidence table
   covering every must-have and nice-to-have in the real JD, with an honest
   rating (Strong / Partial / Gap) per row; strongest differentiators; gaps
   handled with acknowledge-bridge-close; logistics (location, visa, salary
   anchor, follow-up reminder).

6. **Section 5 - Sources and Notes**: a real accounting, by topic
   (financials, leadership, news, competitors, culture, role/team): what is
   **VERIFIED** this pass (with source), what is only **REPORTED** or
   **ESTIMATED** (with the source or triangulation basis), what is **CARRIED
   OVER** (with the date), what is **COULD NOT VERIFY**. Call out any
   blocked or empty fetch. Close by noting that all candidate-specific
   content was built from the user's real sources, not any template or prior
   candidate's document.

7. **Section 6 - Recall sheet and 30-second positioning**: the one page the
   candidate skims in the car park. Four compact blocks:
   - **Numbers to have on recall** - the few figures worth knowing cold,
     each still carrying its confidence badge.
   - **Names to know** - interviewers if known, plus founders / CEO / hiring
     manager / key execs, one line each.
   - **Phrases they use** - the company's own vocabulary and product names,
     to mirror in the room instead of generic terms.
   - **30-second positioning** - the tight verbal pitch of why the candidate
     fits this specific role: 2-3 real strengths and the one genuine thing
     the company gets from them. No volunteered gaps.

Reuse only the HTML/CSS skeleton across companies (cover page, section
dividers, callout boxes, the confidence-badge classes) - never the candidate
content or the company research.

### Optional: interactive HTML companion

If the user asks for something to click through on a laptop during prep,
build a **single self-contained `.html` file** alongside the PDF (all CSS
and JS inline, no build step, no external requests), saved as
`interview_prep/<Name>_<Company>_InterviewPrep.html`. Same content, plus a
sticky scrollspy nav, a checkable list for the "questions to ask" section
with a progress count, and a print button. Do not introduce a framework or a
`package.json`. The PDF stays the primary output and the default thing sent.

---

## After generating

- Compile the PDF, check the page count is sane (not 1 page, not 200), and
  skim-render a couple of pages to confirm tables are not garbled.
- Spot-check the confidence badges: every specific number carries one, and
  no ESTIMATED/INFERRED figure has leaked into the recall sheet or a summary
  sentence as if it were fact.
- Show the user the result with a one-line summary of what is honestly
  strong vs gapped for this role.
- Do not log this to the tracker - it is prep material, not a pipeline
  stage change.
