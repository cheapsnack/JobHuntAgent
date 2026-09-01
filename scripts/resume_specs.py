"""
Per-application resume specs. Consumed by build_resume.py.

One entry per job you apply to. Tailoring = choosing which real bullets from
the library in build_resume.py to include, in what order, plus a summary and
skills block tuned to the JD's own wording. Nothing invented.

Each spec:
    "slug":    short id, used for the scratch filename
    "output":  default output path
    "summary": 3-4 lines. Never opens by claiming a title the candidate has
               never held.
    "order":   role keys (from ROLE_HEADERS), most JD-relevant first
    "bullets": {role_key: [bullet_key, ...]} - >= 12 bullets total
    "skills":  one of the SKILLS_* blocks from build_resume.py

The entry below is EXAMPLE DATA for a fictional candidate. Replace it.
"""
from build_resume import SKILLS_PRODUCT, SKILLS_STRATEGY  # noqa: F401

SPECS = {
    "acme": {
        "slug": "acme",
        "output": "resumes/Jane_Acme_ProductManager.pdf",
        "summary": (
            "Product-focused analyst and MBA with more than five years turning "
            "discovery into shipped products across financial services and internal "
            "tooling. Owned an analytics platform used by around 200 staff end to "
            "end, shipped a data catalogue adopted by 100 users, and defined the "
            "success metrics leadership prioritized investment against. Strong in "
            "user research, data-driven prioritization, cross-functional delivery "
            "and agile execution."
        ),
        "order": ["a", "c", "b"],
        "bullets": {
            "a": ["platform", "discovery", "catalogue", "specs", "metrics", "xfn"],
            "c": ["founding", "book", "audiences", "savings", "reviews"],
            "b": ["model", "framework"],
        },
        "skills": SKILLS_PRODUCT,
    },
}
