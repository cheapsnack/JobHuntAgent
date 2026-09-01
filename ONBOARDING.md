# Onboarding — the agent runs this once

Goal: turn the user's real experience into a reusable base template
(`templates/resume_base.html` content + `scripts/build_resume.py` bullet
library) and a filled `config/profile.json`.

Agent: work through the phases in order. Ask questions in small batches,
wait for answers, confirm before writing files. Never invent a fact — if the
user does not give you a number or detail, leave it out or ask again.

---

## Phase 1 — Get the base resume

Ask:

> Do you have an existing resume you want me to work from? Share the file
> (PDF or DOCX) or paste its text. If not, we will build it from scratch
> and I will interview you.

**If they share a resume:**
1. Save it to `candidate_profile/<firstname>_base_resume.pdf`.
2. Read it and extract, into a summary you show back for confirmation:
   full name, email, phone, LinkedIn, city; each role (employer, title,
   dates, every bullet); education; skills and tools; certifications
   (name + issuer + year).
3. Ask the user to correct anything wrong or missing.

**If they have no resume:** interview role by role. For each: employer,
title, dates, what they owned, and for every achievement "is there a real
number attached to this?" Capture only what they confirm.

---

## Phase 2 — Build the bullet library

For each employer, turn confirmed achievements into **6-8 one-line
bullets**, each shaped *"accomplished X, as measured by Y, by doing Z"*
where a real metric exists. Cut filler words.

Write them into `scripts/build_resume.py`:
- one dict per employer (`ROLE_A`, `ROLE_B`, ...), keyed by short slugs
- `ROLE_HEADERS` — the "Employer - Title" and date string per role
- `LIBRARY` — maps each role slug to its dict
- `CERTS` — the certifications line
- the `SKILLS_*` blocks — 3-4 labelled lines, one variant per role family
  the user targets

Confirm the bullet wording with the user before saving.

---

## Phase 3 — Fill the template and rules

1. `templates/resume_base.html` — replace the placeholder header, summary,
   education and skills blocks with the user's real content. **Do not touch
   the CSS.** The summary must not open by claiming a title the user has
   never held.
2. `config/resume_rules.json` — set `candidate_name`, `required_facts`,
   `banned_facts`, `banned_title_claims`, and the density floors if the
   user's layout genuinely supports fewer bullets.

---

## Phase 4 — Salary, roles, locations

Ask, in one batch:

> A few preferences so I can match and tailor accurately:
> 1. **Current CTC / salary** (or "prefer not to say")
> 2. **Expected CTC / salary**
> 3. **Notice period or earliest joining date**
> 4. **Target job titles** — the roles you actually want
> 5. **Preferred locations**, in priority order, and whether you will relocate
> 6. **Current location** (may differ from preferred)
> 7. **Minimum acceptable salary**

Write these into `config/profile.json`: `contact`, `target_titles`,
`locations`, `location_priority`, `current_location`, `will_relocate`,
`min_salary`, `current_ctc`, `expected_ctc`, `earliest_join_date`,
`years_experience`, `domains`.

Also start `candidate_profile/verified_facts.md` with a "Compensation and
availability" section holding those answers, plus the note: **state these
only where an employer actually asks.**

---

## Phase 5 — Test build

1. Create one example spec in `scripts/resume_specs.py` (use a real JD the
   user is interested in, or a representative one).
2. Run:
   ```bash
   python scripts/build_resume.py --spec <slug> --out resumes/<Name>_<Company>.pdf
   python scripts/verify_resume.py resumes/<Name>_<Company>.pdf
   ```
3. If it does not say `PASS`, fix the content (add a real bullet, tighten
   wording) until it does. Then open the PDF and read it back.
4. Show the user the result and confirm the format looks right.

---

## Phase 6 — Point to optional setup

> The resume workflow is ready. If you also want automated tracking, a
> phone digest, or a hosted approval dashboard, see
> `docs/01_SETUP_API_KEYS.md` — it walks through Telegram, Gmail, Supabase
> and Vercel one at a time. All optional.
