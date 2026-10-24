# WIL Project 24: cleaned pre-presentation working copy

This working copy is derived from commit `4699843`, the last change before the presentation
("Presentation: add closing slide on the scaling roadmap"). It contains limited maintenance
edits and is not byte-identical to that historical commit. The later 30-paper corpus, local
model experiments and current Workbench are not included in this pre-presentation snapshot.

| Path | What it is |
| --- | --- |
| `rag_research_assistant/` | The RAG project at the 8-paper stage: pipeline code (`rra/`), corpus manifest and lock, 24 test questions, results, tests |
| `rag_research_assistant/results/latest.json`, `report.html` | The 8-paper evaluation shown in the presentation |
| `rag_research_assistant/presentation/` | The 7-slide deck with speaker notes, and `build.js` that generates it |
| `speaker-script/WIL-Project-24-Speaker-Script.docx` | The speaker script for Dhanush, Imranjit and Chetan |
| `README.md`, `analysis.ipynb`, `*.csv`, `*.png` (top level) | Files that were already in the repository before the RAG project (uploaded in August) |
| Companion `WIL_Project_24_Original_History.bundle` (provided separately) | Original complete Git history, unchanged. Clone with `git clone -b pre-presentation WIL_Project_24_Original_History.bundle recovered-project`. |

Run it: `cd rag_research_assistant`, `pip install -r requirements.txt`, then `python -m rra.cli fetch`,
`python -m rra.cli ingest`, `python -m rra.cli experiment` and `python -m rra.cli report`.

## Preservation and changes

The original Git bundle is supplied separately without changing commit authors, dates, messages
or file history. Restoring it restores the original historical files, not this cleaned working
copy. This source export is not a replacement for the historical bundle.

The recorded evaluation results, question set, corpus manifests, original PowerPoint,
notebook, datasets and chart images are unchanged. The speaker-script body and layout files
are unchanged; only document application metadata was cleared. Current source and README
use `remote` for the optional configured model backend. The presentation build uses a local
theme helper instead of a machine-specific path. No authorship has been reassigned.
