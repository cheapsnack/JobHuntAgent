"""
Convert a resume HTML file to PDF using headless Chrome print-to-pdf.

Usage:
    python scripts/compile_pdf.py <input.html> <output.pdf>
    python scripts/compile_pdf.py <input.html> <output.pdf> --fit

--fit guarantees a one-page result. It compiles, counts pages, and if the
output spills past page 1 it shrinks the type scale in small steps and
recompiles until it fits (or gives up and says so loudly).

Resumes should always be built with --fit.
"""
import datetime
import shutil
import subprocess
import sys
from pathlib import Path

CHROME_CANDIDATES = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/usr/bin/google-chrome",
    "/usr/bin/google-chrome-stable",
    "/usr/bin/chromium",
    "/usr/bin/chromium-browser",
    "/snap/bin/chromium",
]


def find_chrome() -> str:
    for candidate in CHROME_CANDIDATES:
        if Path(candidate).exists():
            return candidate
    for name in ("chrome", "google-chrome", "google-chrome-stable",
                 "chromium", "chromium-browser"):
        found = shutil.which(name)
        if found:
            return found
    raise FileNotFoundError(
        "Chrome/Chromium not found. Install Google Chrome, or edit "
        "CHROME_CANDIDATES in this file to point at your browser."
    )


FIT_STEPS = [1.0, 0.98, 0.96, 0.94, 0.92, 0.90, 0.88, 0.85]

FIT_CSS = """
<style id="autofit">
  body {{ font-size: {size:.2f}pt !important; line-height: {lh:.3f} !important; }}
</style>
"""

BASE_SIZE = 10.4
BASE_LH = 1.21


def page_count(pdf_path: Path) -> int:
    import pypdf
    return len(pypdf.PdfReader(str(pdf_path)).pages)


def compile_fit(html_path: str, pdf_path: str) -> None:
    src = Path(html_path).resolve()
    html = src.read_text(encoding="utf-8")
    work = src.parent / (src.stem + ".autofit.html")
    try:
        for scale in FIT_STEPS:
            injected = FIT_CSS.format(size=BASE_SIZE * scale, lh=BASE_LH * scale)
            work.write_text(html.replace("</head>", injected + "</head>"), encoding="utf-8")
            compile_pdf(str(work), pdf_path)
            pages = page_count(Path(pdf_path))
            if pages == 1:
                if scale < 1.0:
                    print(f"  (auto-fit: type scaled to {scale:.0%} to hold one page)")
                return
            print(f"  (auto-fit: {pages} pages at {scale:.0%}, shrinking)")
        raise RuntimeError(
            "Could not fit one page even at 85% type scale. The content is too "
            "long - cut a bullet or tighten wording rather than shrinking further."
        )
    finally:
        work.unlink(missing_ok=True)


def _preserve_existing(pdf_path: Path) -> None:
    if not pdf_path.exists():
        return
    keep = pdf_path.parent / "_archive" / "overwritten"
    keep.mkdir(parents=True, exist_ok=True)
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    dest = keep / f"{pdf_path.stem}.{stamp}.pdf"
    shutil.copy2(pdf_path, dest)
    print(f"  (previous version preserved -> _archive/overwritten/{dest.name})")


def compile_pdf(html_path: str, pdf_path: str) -> None:
    html_path = Path(html_path).resolve()
    pdf_path = Path(pdf_path).resolve()
    if not html_path.exists():
        raise FileNotFoundError(f"HTML source not found: {html_path}")
    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    _preserve_existing(pdf_path)

    chrome = find_chrome()
    cmd = [
        chrome, "--headless", "--disable-gpu", "--no-pdf-header-footer",
        f"--print-to-pdf={pdf_path}", html_path.as_uri(),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    if result.returncode != 0 or not pdf_path.exists():
        raise RuntimeError(
            f"Chrome PDF export failed (code {result.returncode}).\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )
    print(f"Wrote {pdf_path}")


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if a != "--fit"]
    if len(args) != 2:
        print(__doc__)
        sys.exit(1)
    if "--fit" in sys.argv:
        compile_fit(args[0], args[1])
    else:
        compile_pdf(args[0], args[1])
