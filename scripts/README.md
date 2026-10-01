# Scripts

- `reproduce_results.py`: regenerates every quantitative result in `results/` from the public data.
- `audit_agreement.py`: reproduces the agreement statistics of the eligibility re-assessment, the final value audit and the second-reviewer check.
- `verify_checksums.py`: checks all files against `metadata/SHA256SUMS.tsv`.
- `build_checksums.py`: regenerates the checksum manifest after an intentional update.
- `validate_public_release.py`: checks for disallowed file types, text-bearing columns and local paths.
