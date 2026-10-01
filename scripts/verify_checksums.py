"""Verify repository files against metadata/SHA256SUMS.tsv."""

from __future__ import annotations

import csv
import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "metadata/SHA256SUMS.tsv"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    failures: list[str] = []
    with MANIFEST.open(encoding="utf-8", newline="") as handle:
        rows = csv.DictReader(handle, delimiter="\t")
        for row in rows:
            path = ROOT / row["path"]
            if not path.is_file():
                failures.append(f"MISSING  {row['path']}")
                continue
            actual = sha256(path)
            if actual.lower() != row["sha256"].lower():
                failures.append(f"CHANGED  {row['path']}")
            if path.stat().st_size != int(row["bytes"]):
                failures.append(f"SIZE     {row['path']}")
    if failures:
        raise SystemExit("Checksum verification failed:\n" + "\n".join(failures))
    print("PASS: all files listed in metadata/SHA256SUMS.tsv match.")


if __name__ == "__main__":
    main()
