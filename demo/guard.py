"""DEMO_MODE guard.

The point of this file: make it impossible to point demo tooling at your real
pipeline by accident. Screen-recording or sharing the real database would
expose live employer rows, fit scores and recruiters' personal email
addresses.

Every demo script imports and calls assert_demo() before touching anything.

The load-bearing check is containment: the database must live inside this
demo folder. A relative path that escapes the folder is the realistic way
this goes wrong, and that check catches it regardless of where your real
pipeline happens to be installed.

The canary check is a second, optional net. Put one name per line in
`demo/real_employers.txt` (gitignored) listing companies that appear in your
REAL pipeline. If any of them turns up in the demo database, the demo data is
not fictional and the guard fails. See real_employers.example.txt.
"""
from pathlib import Path
import re
import sys

DEMO_ROOT = Path(__file__).resolve().parent.parent
DEMO_DB = DEMO_ROOT / "data" / "jobs.db"
CANARY_FILE = Path(__file__).resolve().parent / "real_employers.txt"


def _canaries() -> list[str]:
    """Names that must never appear in demo data. Empty if unconfigured."""
    if not CANARY_FILE.exists():
        return []
    return [
        line.strip()
        for line in CANARY_FILE.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]


def assert_demo(db_path: Path | None = None) -> Path:
    """Return the demo DB path, or exit loudly."""
    db = Path(db_path).resolve() if db_path else DEMO_DB

    try:
        db.relative_to(DEMO_ROOT)
    except ValueError:
        sys.exit(
            f"DEMO GUARD: refusing to run.\n"
            f"  db resolves to : {db}\n"
            f"  demo root is   : {DEMO_ROOT}\n"
            f"The database is outside the demo folder."
        )
    return db


def assert_no_real_companies(db: Path) -> None:
    """Post-seed check: demo data must be entirely fictional."""
    names_to_avoid = _canaries()
    if not names_to_avoid or not db.exists():
        return

    import sqlite3

    con = sqlite3.connect(db)
    try:
        rows = con.execute("select company from jobs").fetchall()
    except sqlite3.OperationalError:
        return
    finally:
        con.close()

    present = {r[0] for r in rows if r[0]}
    # Whole-word match, not raw substring. A two-letter employer like "EY"
    # otherwise fires on "Greystone", and "ADA" on "Adamant" - false alarms
    # that train you to ignore the guard, which is worse than no guard.
    hits = [
        c for c in names_to_avoid
        if any(re.search(rf"\b{re.escape(c)}\b", n, re.IGNORECASE) for n in present)
    ]
    if hits:
        sys.exit(f"DEMO GUARD: real employer names found in demo DB: {hits}")


if __name__ == "__main__":
    db = assert_demo()
    assert_no_real_companies(db)
    n = len(_canaries())
    print(f"OK  demo root : {DEMO_ROOT}")
    print(f"OK  demo db   : {db}")
    print(
        f"OK  canaries  : {n} configured"
        if n
        else "--  canaries  : none configured (see real_employers.example.txt)"
    )
