# Distribution verification: 25 October 2026

## Scope

This edition consolidates the supplied GitHub upload kit and evidence addendum into one repository tree. Report-preparation instructions, upload wrappers and obsolete installer directions are removed. Project-facing documentation is edited for navigation and clarity. Accurate development provenance, original research attribution and evaluation limits are retained.

The application engine, tests, interface assets, catalogue entries, 30 source PDFs, extracted passages, question sets, original experimental archives, 67 stored runs and original Git bundle are unchanged. The root `run.py` wrapper has only a documentation/error-message update removing obsolete upload-batch wording. Its launch behaviour is unchanged.

## Integrity checks

- 221 protected original files were compared byte-for-byte with the supplied inputs and are unchanged.
- The portable archive contains 196 entries: 182 entries are byte-identical to the previous archive; the changed entries are documentation and manifests only.
- Two embedded report-preparation documents were removed; no runtime module, test, catalogue entry, PDF or recorded run was removed from the executable.
- The portable build ID is `portable-docs25-888681a885676878`. It separates the revised documentation payload from existing installed workspaces without changing historical run identities.
- `RELEASE_SHA256.json` and the portable payload manifest describe the current documentation edition. Historical validation logs retain their original run hashes and dates.
- The current repository manifest is `REPOSITORY_SHA256.json`; `python3 tools/verify_repository.py` checks it without executing models or experiments.

## Executed distribution checks

- Static parsing succeeded for 38 Python files, 148 existing JSON files and five JSONL files before final manifest generation.
- All 73 local Markdown links resolve to supplied files or directories.
- All recorded table rows in the six edited historical diagnostic reports are unchanged.
- The application engine's computed code hash remains `06d56dd7f41923fc9ffa5f4157e846ce0397b251517dfe34b625234040efea10`.
- The revised portable archive's help command succeeds with third-party site packages disabled.
- Source export to an isolated directory succeeds; all 193 payload files match their manifest hashes.
- All 43 pre-existing report-audit members, 30 original PDFs and 67 saved run files retain their original bytes.

Machine-readable results are in `distribution_checks.json`.

## Verification boundaries

No application test suite, answer-generation experiment, retrieval evaluation or participant study was rerun for this documentation edition. The existing 118-test result and historical regression results remain dated records, not newly generated results. No new native macOS/Windows or browser certification is asserted.

The records in `report-audit/provenance_snapshot/` and earlier integrity JSON files describe their original audit inputs. They are preserved historical records, not replacement manifests for this edition. The source-verification report's unavailable companion files are identified in `verification-2026-10-23/README.md`.

The file-level change ledger is `DOCUMENTATION_REVISION.json`. The archived Git bundle and recorded task timestamps have not been rewritten.
