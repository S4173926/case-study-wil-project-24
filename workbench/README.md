# Research Workbench · Portable edition

A local research reading desk: compare methods, inspect original PDFs, save source-based reviews and measure research tasks.

## Start the single-file application

Python 3.10 or newer is required. The default application uses only the Python standard library. No model download, account, GPU, paid service, package installation, or internet connection is required.

macOS / Linux:

```sh
python3 Research_Workbench.pyz
```

Windows, with Python installed:

```powershell
py -3 Research_Workbench.pyz
```

The browser opens automatically. Read the printed address: if port 8765 is occupied, the launcher chooses the next available local port. Keep the terminal open; Ctrl+C stops the server.

## What the one file contains

The executable archive includes source code, responsive interface, 30 original research PDFs, 1,202 extracted passages, 99 reusable source-linked explanation units, tests, documentation and the 67 previously recorded repaired cases. It is one distribution file, not a claim that a website can run without a Python interpreter or local storage.

The application unpacks itself automatically into `~/Research_Workbench_Data/releases/<build-id>/`. That working directory holds the included documents and your saved records. No manual unzipping is needed. The original ZIPs and prior project folders are not modified.

A normal start copies valid saved runs/reviews/pilot records from neighbouring or Downloads folders named `WIL_Research_Workbench_Final` and `WIL_Research_Workbench`, and from earlier portable release directories. Identical records are not duplicated. Conflicting records are preserved separately in `results/import_conflicts` and identified in migration logs. It does not invent reviews or overwrite an existing review.

## Four pages

- **Ask & compare:** source-linked explanations or original-passage search; citations open exact excerpts and the original PDF.
- **Paper library:** filter the 30 papers and open their PDFs.
- **Human review:** searchable, version-aware saved runs; separate correctness, completeness, support and relevance ratings.
- **Stakeholder pilot:** consent, task timing including verification, actual submitted responses and subsequent review.

Submission-checklist and software-test pages are not in the interface. The corresponding documentation and real test results are retained in this archive. Short answer-specific uncertainty notices remain because source existence is not factual verification.

## Why 30 papers?

This is the chosen academic retrieval / RAG research collection, not a processor or memory limit. A bounded collection supports repeatable evaluation and inspectable sources. It does not cover all academic literature. There is no automatic web search or arbitrary-PDF ingestion button in this release. Expanding the collection requires indexing the new source, recording its provenance, creating/checking explanation units where appropriate, and reevaluating the system.

The default answer path retrieves and composes existing source-linked statements. It is not unrestricted language generation. The stored catalogue can have coverage gaps, incorrect paraphrases or insufficient material for a complex question. The system records explicit partial and insufficient-support states, but those states are heuristic rather than a semantic proof.

## Hardware and collaboration

The default app is platform-neutral Python intended for macOS (Intel or Apple silicon), Windows and Linux. Its execution is tested in the supplied Linux environment; native Windows and this Mac build have not been executed by the delivery audit. The older experimental Apple-specific adapter remains in the source archive for reproducibility, but is not exposed by this interface or required to start the app.

Localhost belongs to the computer running the program. This is not a public website or multi-user hosting service. Teammates can run the same file on their own computers and export their real records. No concurrent-user performance claim is made.

## Saved results

Use **Export evaluation bundle** to download actual saved runs, reviews and pilot observations. Existing ratings retain their original run IDs. Rating a source-linked explanation does not certify that a reviewer is independent. All 67 included questions have influenced development; do not report their status counts as independent accuracy.

## Useful optional commands

```sh
python3 Research_Workbench.pyz --check
python3 Research_Workbench.pyz --evaluate
python3 Research_Workbench.pyz --workspace ./my_workspace --no-import
python3 Research_Workbench.pyz --export-source ./Research_Workbench_Source
```

`--check` runs the packaged tests and corpus integrity checks. `--evaluate` records all 67 known regression questions in a new output directory, without assigning human scores. `--export-source` creates a new inspectable directory suitable for version control, never overwriting an existing target.

When working from an exported source directory, `python3 app.py --open` starts the same application.

## Verification and assessment boundaries

See `audit/PORTABLE_VERIFICATION.md` for executed checks, failures fixed during packaging and the browser-testing boundary. `docs/RUBRIC_MAP.md` and `docs/REPORT_ASSEMBLY.md` remain reference documents, not webpages or claims that a mark has been earned.

Do not equate a successful software test with a correct answer, a source ID with claim support, or a timed response with measured stakeholder benefit. Actual report content, project history, team contributions, and observed task outcomes remain separate evidence.

Original source PDFs, research text and historical evaluation records are retained unmodified. Licensing and provenance are documented in `LICENSE_NOTES.md`, `MODEL_CARD.md`, and `docs/PROVENANCE_AND_HISTORY.md`.
