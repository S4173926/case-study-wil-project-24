# Preserved development history

[`Original_History.bundle`](Original_History.bundle) preserves the original 12-commit history, including its original author identities, dates, messages and file contents. [`COMMIT_LOG.tsv`](COMMIT_LOG.tsv) is the unedited extracted ledger. Eight commits touch the group RAG project; the bundle also contains an earlier individual-assignment stage.

The active legacy directory contains a maintenance export of the eight-paper project, not an exact checkout of the original branch. Its differences are documented in [`Working_Copy_Maintenance.md`](Working_Copy_Maintenance.md). The unrelated banking/marketing files from the earlier individual-assignment stage remain only in the original history.

The repository was consolidated following the team's reported loss of an earlier remote. Retaining a bundle as a file preserves historical evidence but does not itself restore those commits to the current branch. Commit metadata does not determine individual contribution percentages.

To inspect the original branch in a separate directory, run from the repository root:

```sh
git clone --branch pre-presentation history/Original_History.bundle recovered-original
```

The current 30-paper application is in `workbench/` and `downloads/`, not in this historical branch.
