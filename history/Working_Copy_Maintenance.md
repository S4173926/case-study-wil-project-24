# Original project: working-copy cleanup report

## Delivery

- `WIL_Original_Project_Cleaned.zip`: edited working export of the pre-presentation project.
- `WIL_Project_24_Original_History.bundle`: unchanged original Git-history bundle, supplied separately.
- `WIL_Original_Project_Change_Manifest.json`: per-file before/after hashes and the executed-check summary.

The original uploaded ZIP is untouched. This is the historical eight-paper project, not a replacement for the current 30-paper Workbench.

## Changes made

- Cleared development-tool labels from the speaker-script application metadata. No author was substituted; all body, style, table and relationship parts remain unchanged.
- Replaced the optional model backend name in the source and documentation with `remote` / `RemoteGenerator`.
- Removed the hard-coded remote model identifier. The optional backend now requires `RRA_REMOTE_MODEL` (or an explicitly supplied constructor argument) alongside the existing provider credentials. The provider SDK and request format remain unchanged.
- Replaced a machine-specific presentation-helper import with a local `apply_theme.js` and `theme.xml`. The included theme was extracted from the existing slide deck.
- Updated the version note so the maintenance export is not described as an untouched historical commit.

The cleaned ZIP contains **33 files**: 7 existing files were edited, 3 support files were added, and 23 existing files are unchanged. The history bundle is separately preserved.

## Text scan

Zero requested tool-name or assistance-label matches were found in the delivered working-tree text, filenames, notebook JSON, or decompressed Word/PowerPoint XML and relationship files. The scan covered 91 text/XML streams. Original chart images and notebook image outputs were not OCR-scanned. Normal technical descriptions of language-model research and runtime generation remain: the cleanup does not change what this project does or how it was developed.

The separate historical bundle was deliberately **not scrubbed**. It retains original authors, dates, messages and historical source files. Restoring that bundle restores the original records, not the cleaned working tree. No attribution or evaluation history has been fabricated or reassigned.

## Executed verification

| Check | Result |
|---|---|
| Python syntax | All 10 source files compile |
| JSON/JSONL/notebook structures | Parse successfully |
| Default extraction and abstention code | Unchanged abstract syntax |
| Remote request/response handling | Unchanged abstract syntax; naming/configuration adjusted |
| Existing offline tests not using BM25 | 10 pass in the original; same 10 pass in the cleaned copy |
| Targeted mocked remote-backend checks | 9 pass; no external model call |
| Presentation JavaScript | Syntax checks pass |
| Local theme helper | Executed on a copy; every decompressed PowerPoint part preserved |
| Existing slide deck | Byte-for-byte unchanged |
| Speaker script | Only two metadata XML parts change; all five rendered pages visually inspected |
| Recorded experiment results and question labels | Byte-for-byte unchanged |
| Original Git-history bundle | Complete history verifies; 12 commits; unchanged SHA-256 |
| Delivery ZIP | CRC integrity check passes; every packaged file matches tested bytes |

### Test boundaries

The full original pipeline suite was **not** run: `rank_bm25` is unavailable in this environment and a dependency installation attempt failed because network name resolution was unavailable. The 10-test subset used an import-only sentinel that raises if BM25 is instantiated; it did not implement or simulate BM25. The other 13 original tests were deselected, not counted as passing. This sentinel is not included in the project.

No real remote-model request was made. The full presentation build was not executed because React-related dependencies are unavailable here; the changed helper itself and JavaScript syntax were checked. Existing experiment files were preserved, not regenerated. This is a naming/metadata cleanup, not a new performance or assessment-readiness claim.

## Usage note

The default offline generator still uses the original commands. The optional backend's command-line name is now `--generator remote`; it requires the configured model identifier described in the project README. Do not overwrite the final Workbench with this historical project. Keep the original history alongside it for repository recovery.
