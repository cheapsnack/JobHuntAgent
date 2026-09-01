# Base resume guide (manual reference)

`ONBOARDING.md` is the version the agent runs for you. This is the same
process written out, for when you want to do a step by hand.

The golden rule: **tailoring never invents anything.** It selects,
reorders, and rephrases your real bullets toward a job's own words.

---

## 1. Put your resume in `candidate_profile/`

```
candidate_profile/<firstname>_base_resume.pdf
```
Point `config/profile.json` -> `resume.base_resume_pdf` at it.

## 2. Write `candidate_profile/verified_facts.md`

Copy `verified_facts.example.md`. Capture real facts not in the PDF:
certs, quantified metrics, strong interview stories, current location,
current/expected salary, notice period, and anything you have decided
**not** to claim.

## 3. Adapt `templates/resume_base.html`

Edit **only** the text between the `<!-- CONTENT: ... -->` markers:
header, summary, education, skills lines. **Do not touch the CSS** -
`font-family`, `font-size`, `margin`, `line-height` are locked. The
summary must not open by claiming a title you have never held. Never
write a nested `<!--` or `-->` inside the header comment block.

## 4. Build your bullet library in `scripts/build_resume.py`

Replace `ROLE_A/ROLE_B/ROLE_C`, `ROLE_HEADERS`, `LIBRARY`, `CERTS` and
the `SKILLS_*` blocks with your real content:
- one dict per employer, keyed by short slugs
- each bullet one line (two max), shaped *"accomplished X, as measured by
  Y, by doing Z"* where a real metric exists
- 6-8 bullets per major role
- one `SKILLS_*` block per role family you target

## 5. Fill `config/resume_rules.json`

Copy `resume_rules.example.json`. Set `candidate_name`, `required_facts`,
`banned_facts`, `banned_title_claims`.

## 6. Create a spec and build

Add an entry to `scripts/resume_specs.py` for a real job, then:
```bash
python scripts/build_resume.py --spec <slug> --out resumes/<Name>_<Company>.pdf
python scripts/verify_resume.py resumes/<Name>_<Company>.pdf
```

## 7. The verifier is the finish line

`verify_resume.py` must print `PASS`. It checks one page, no em/en
dashes, bullet and word floors, required/banned facts, no banned title
claim, no `[estimate]` markers, ATS-parseable layout, no ligature
glyphs, and that the page starts with your name.

If it fails on length: tighten wording or add a real bullet. **Never**
cut real content to force one page and never shrink the locked CSS -
`compile_pdf.py --fit` already scales type to fit. Then open the PDF and
read it once.

## 8. Never rebuild a sent resume

Once a resume is with an employer (`track.py` status APPLIED / EMAILED /
INTERVIEWING / OFFER / EMPLOYER_REJECTED), the file is frozen.

---

## Fit-check before you tailor at all

Score the JD's hard requirements (named skills, tools, domain, degree
field, certifications) against your background. **Do not count
years-of-experience gaps** - employers flex on level. If more than half
the must-haves have zero grounding anywhere in your profile, skip the job
and note why. Otherwise tailor honestly and flag the specific gaps.
