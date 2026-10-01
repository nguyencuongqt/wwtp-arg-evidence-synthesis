"""Fail when the public release contains disallowed content or file types."""

from __future__ import annotations

import csv
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN_SUFFIXES = {".doc", ".docx", ".pdf", ".tif", ".tiff", ".pyc", ".xlsx"}
FORBIDDEN_PARTS = {"__pycache__", ".venv", "superseded", "archive", "full_text", "publisher_pdfs"}
FORBIDDEN_COLUMNS = re.compile(
    r"(evidence_quote|evidence_span|source_text|full.?text|abstract|human_notes|source_detail|source_location)",
    re.IGNORECASE,
)
LOCAL_PATH = re.compile(r"(?:[A-Za-z]:\\\\[^\\n]|/Users/|/home/)")


def main() -> None:
    failures: list[str] = []
    for path in ROOT.rglob("*"):
        rel = path.relative_to(ROOT)
        if any(part.lower() in FORBIDDEN_PARTS for part in rel.parts):
            failures.append(f"forbidden path: {rel.as_posix()}")
        if not path.is_file():
            continue
        if path.suffix.lower() in FORBIDDEN_SUFFIXES:
            failures.append(f"forbidden file type: {rel.as_posix()}")
        if path.suffix.lower() == ".csv":
            with path.open("r", encoding="utf-8-sig", newline="") as handle:
                header = next(csv.reader(handle), [])
            bad = [name for name in header if FORBIDDEN_COLUMNS.search(name)]
            if bad:
                failures.append(f"forbidden columns in {rel.as_posix()}: {bad}")
        if path.resolve() != Path(__file__).resolve() and path.suffix.lower() in {".md", ".py", ".yml", ".yaml", ".cff", ".txt"}:
            text = path.read_text(encoding="utf-8", errors="replace")
            if LOCAL_PATH.search(text):
                failures.append(f"local absolute path in {rel.as_posix()}")
    if failures:
        raise SystemExit("Public-release validation failed:\n" + "\n".join(failures))
    print("PASS: no forbidden files, columns, caches, or local absolute paths found.")


if __name__ == "__main__":
    main()
