"""Generate metadata/SHA256SUMS.tsv for the public release."""

from __future__ import annotations

import csv
import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "metadata" / "SHA256SUMS.tsv"


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def main() -> None:
    files = [
        path
        for path in ROOT.rglob("*")
        if path.is_file()
        and path != OUTPUT
        and ".git" not in path.relative_to(ROOT).parts
        and "__pycache__" not in path.parts
        and path.suffix.lower() != ".pyc"
    ]
    with OUTPUT.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, delimiter="\t", lineterminator="\n")
        writer.writerow(["sha256", "bytes", "path"])
        for path in sorted(files):
            writer.writerow([digest(path), path.stat().st_size, path.relative_to(ROOT).as_posix()])
    print(f"Wrote checksums for {len(files)} files to {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
