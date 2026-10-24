# Research Workbench · WIL Project 24

A local research assistant for inspecting and comparing methods in a bounded collection of
30 retrieval and retrieval-augmented-generation papers. It provides source-linked explanations,
original-passage search, a PDF library, saved-answer review and a timed task-pilot workflow.

**Current software:** `downloads/Research_Workbench.pyz` (portable executable archive).
**Readable current source:** `workbench/`.
**Earlier implementation:** `legacy/pre-presentation/rag_research_assistant/`.

## Run the final assistant

Python 3.10 or newer is required. The default application needs no paid API, model download,
GPU or third-party package installation. Download this repository through **Code → Download ZIP**,
extract it, then run from the extracted directory:

```sh
# macOS / Linux
python3 run.py
```

```powershell
# Windows
py -3 run.py
```

Alternatively, run `python3 downloads/Research_Workbench.pyz` directly. Do not unzip the `.pyz`.
The launcher opens a browser. Its preferred address is `http://127.0.0.1:8765`; when that port
is busy it tries another and prints the actual address. Keep the terminal open. Ctrl+C stops it.

This is a local application, not a public GitHub Pages website or shared online service.
The launcher stores runtime records under `~/Research_Workbench_Data/`. Existing workspaces
are not overwritten. Each teammate's saved ratings remain local until exported.

To check the packaged software without starting the site:

```sh
python3 run.py --check
```

To run from the readable source instead:

```sh
cd workbench
python3 app.py --open
```

## What is included

| Location | Contents |
|---|---|
| `downloads/` | Runnable final assistant; browser-upload-compatible archive compression |
| `workbench/` | Complete final application source, interface, 30 source PDFs, index, catalogue, tests and original repaired runs |
| `distribution_source/` | Unchanged portable launcher and manifest for inspecting/rebuilding the executable |
| `tools/rebuild_portable.py` | Rebuilds the portable archive from the same recorded assets |
| `evaluation/` | Original challenge/repaired result bundles, summaries and diagnostic reports |
| `legacy/pre-presentation/` | Historical eight-paper pipeline, original experiments, presentation and speaker script |
| `history/` | Unchanged original Git bundle, extracted commit ledger and recovery explanation |
| `docs/project-management/` | Privacy-minimised Trello evidence snapshot and its limitations |
| `docs/` | Packaging verification, evidence navigation and outstanding delivery items |

## What the assistant actually does

The default explanation path selects reusable paper-specific statements from a fixed catalogue
and composes them with their source references. It does not generate unrestricted prose on every
question. Original-passage search separately offers BM25, TF-IDF and a hybrid ranking.

The indexed collection contains 30 papers, 1,202 passages, 99 explanation units and 191 supporting
spans. The collection is deliberate, not an Apple-M4 hardware restriction. It is not a full-web
literature search service and has no arbitrary-PDF ingestion interface in this release.

The stored catalogue can contain imperfect paraphrases or miss details. Source IDs and passing
software checks do not prove factual correctness. Partial and insufficient-support results are
retained explicitly; the known HyDE case remains partial. See `workbench/MODEL_CARD.md` and
`workbench/docs/PROVENANCE_AND_HISTORY.md` for method/provenance and evaluation boundaries.

## Evaluation and reproducibility

The included repaired batch contains 67 known development/regression questions: 52 explanation
statuses, one partial response and 14 insufficient-support responses. Those are output states,
not an independently measured accuracy score. The challenge questions informed subsequent fixes.
No participant outcomes or completed human ratings have been fabricated.

Original result ZIPs are preserved in `evaluation/` and `workbench/evidence/`. The final software
was previously packaged with 118 tests; this repository packaging also rechecks that suite and
verifies that all application entry bytes are unchanged. See `docs/PACKAGING_VERIFICATION.md`.

## Team and project records

Roles below are those recorded in the supplied project README/Trello documentation. They do
not constitute independently verified authorship shares or replace the group's contribution record.

| Team member | Recorded responsibility |
|---|---|
| Chetan Bera | Scrum Master / project lead |
| Imranjit Singh Kohli | Data engineering and corpus preparation |
| Qiling Huang | Retrieval and machine-learning engineering |
| Dhanush Sridhar | Application development |
| Amritpal Singh Gill | DevOps and documentation |
| Deboprio Saha Argha | Quality assurance and evaluation |

Project board: https://trello.com/b/9hEOJ49W/case-study-wil-project-24

The team reported accidental deletion of an earlier remote repository. This repository-ready
upload is a recovery snapshot. The original 12-commit history is preserved in a bundle; uploading
that file does not automatically restore the old commit graph. Original author/date metadata is
unchanged. Current uploads must use their actual upload dates and authorised account identity.

## Rights, privacy and submission boundary

Keep this repository private while it contains supplied research PDFs whose individual
redistribution permissions have not all been independently checked. Grant the assessor appropriate
access. Preserve source credits and review `workbench/LICENSE_NOTES.md` before any public release.
No licence granting rights over third-party papers is asserted by this repository.

The Trello evidence file excludes private profile and email-routing metadata. Do not add API keys,
passwords, environment secrets, model caches or unrelated personal files.

The final report, final contribution documents, genuine individual reflections and any new local
human reviews/pilot observations are not supplied by this software package. Add actual final
materials when available; see `docs/REMAINING_DELIVERABLES.md`. No course mark is guaranteed.
