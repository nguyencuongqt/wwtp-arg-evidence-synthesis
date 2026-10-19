"""Generate metadata/SHA256SUMS.tsv for the public release."""

from __future__ import annotations

import csv
import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "metadata" / "SHA256SUMS.tsv"


def digest(path: Path) -> str:
    value = hashlib.sha256(canonical_bytes(path))
    return value.hexdigest()


def canonical_bytes(path: Path) -> bytes:
    """Normalize text line endings so the manifest is stable across operating systems."""
    data = path.read_bytes()
    return data.replace(b"\r\n", b"\n") if b"\0" not in data else data


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
            writer.writerow([digest(path), len(canonical_bytes(path)), path.relative_to(ROOT).as_posix()])
    print(f"Wrote checksums for {len(files)} files to {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
