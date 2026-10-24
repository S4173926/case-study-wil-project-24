# Project-management evidence snapshot

The supplied Trello export has 26 cards and 6 members.
Card list positions: {'To-Do': 2, 'In-Progress': 1, 'Blocked': 2, 'Done': 21}. A list position is recorded state, not independent
proof that the corresponding implementation or deliverable is complete.

Recorded board activity ends at `2026-10-02T05:44:57.589Z`. The export was supplied on
24 October 2026, but that does not turn the old activity dates into current progress.
Card creation dates in the supplied actions: {'2026-10-02': 20, '2026-08-23': 6}.
Many September sprint descriptions were entered retrospectively on 2 October.
They must not be represented as continuous contemporaneous September tracking.

`trello_evidence_redacted.json` is a shareable subset derived from the supplied export.
It preserves task text, assignments, list positions and activity timestamps, while
excluding card-to-email addresses, profile account identifiers, avatar metadata,
background URLs and the invitation record. The unmodified source hash is recorded.
The original source JSON is not included because it contains private account metadata.

The board contains historical blockers and retrospective notes. Their presence documents
what was recorded, not that a blocker is still unresolved or a claimed metric is verified.
The original experimental outputs are retained separately in the legacy project.

The historical Git bundle is in `../../history/`. A task assignment is not evidence of a
specific person writing every associated line of code; no contribution shares, mentoring
meetings or team reflections have been invented in this package.
