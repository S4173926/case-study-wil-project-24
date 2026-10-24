# Final software release notes

## Release 1.2

This consolidates the verified selection repair and improves the review workflow. It does not replace the answering architecture.

### User-visible changes

Type to filter recorded runs by question identifier, paper, question text or run identifier. The default shows the compatible current/repaired answer set and one latest record per question, with explicit historical-version access. The selected run's full identity is displayed. Rating fields and source confirmation reset on a run change; the reviewer identity remains available. Unrelated retrieval snippets on unsupported queries are collapsed and labelled. Neutral wording replaces development-tool labels in product copy.

### Preservation

The original PDFs, indexed passage text, claim text, supporting quotes, old run IDs and timestamps are unchanged. The received regression archive is retained byte-for-byte. Existing local reviews and pilot observations are copied, not deleted or altered, by the launcher. Earlier batch archives stay in the earlier workspace.

### Validation limits

An existing suite plus new record-index, migration and UI tests is executed before packaging. The 67 repaired outputs are reproduced and compared semantically. Browser component checks exercise the actual application code through its actual HTTP API, but direct browser navigation is blocked in the audit environment. Native Mac launch and embedded PDF rendering still use the user's existing browser environment. No new model-download step is introduced.
