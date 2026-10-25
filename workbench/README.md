# Research Workbench application

A local research reading desk for comparing methods, inspecting original PDFs, reviewing saved answers and recording research-task observations.

## Start from source

Python 3.10 or newer is required. The default path uses only the Python standard library.

From this directory:

```sh
python3 app.py --open
```

For the portable distribution, run `python3 run.py` from the repository root or `python3 downloads/Research_Workbench.pyz`. The launcher chooses an available local port, normally 8765, and opens the browser. `Ctrl+C` stops the server.

The portable archive extracts into a version-specific directory under `~/Research_Workbench_Data/`. It preserves earlier workspaces and imports compatible existing records conservatively. Conflicting records are retained separately rather than overwritten. A source launch stores its records in this application's `results/` directory.

## Application pages

- **Ask & compare:** bounded source-linked explanations and original-passage search.
- **Paper library:** the 30 included papers and their original PDFs.
- **Human review:** saved run selection and separate correctness, completeness, support and relevance ratings.
- **Stakeholder pilot:** consent, task timing, submitted responses and subsequent review.

The source collection has 1,202 passages, 99 explanation units and 191 supporting spans. The default explanation engine composes existing source-linked statements; it does not perform unrestricted runtime generation. BM25, TF-IDF and hybrid original-passage search are separate from claim selection. The collection is fixed; there is no automatic web search or arbitrary-PDF ingestion interface.

## Saved records

**Export evaluation bundle** exports the actual saved runs, reviews and pilot observations. Local records are not automatically shared between computers. Reviewer relationships, original run IDs and pending review states are retained. The included 67 questions influenced development; their output states are not independent accuracy labels.

## Portable options

Run these commands from the repository root:

```sh
python3 downloads/Research_Workbench.pyz --help
python3 downloads/Research_Workbench.pyz --check
python3 downloads/Research_Workbench.pyz --evaluate
python3 downloads/Research_Workbench.pyz --workspace ./my_workspace --no-import
python3 downloads/Research_Workbench.pyz --export-source ./Research_Workbench_Source
```

`--check` executes packaged software and integrity checks. `--evaluate` records another run of the 67 known questions without creating human scores. `--export-source` copies the bundled source into a new directory and refuses to overwrite an existing destination.

## Scope and provenance

The default runtime is intended for macOS, Windows and Linux. The historical verification logs record Linux execution and explicitly state the native-platform and browser-testing limits. An optional historical Apple-silicon adapter is retained in source but is not required by the default interface.

The catalogue may omit facts, select insufficient material or contain imperfect paraphrases. Original PDFs remain available for source checking. Passing software tests, valid citation IDs and repeatable outputs are distinct from semantic correctness or measured user benefit.

See [MODEL_CARD.md](MODEL_CARD.md), [LICENSE_NOTES.md](LICENSE_NOTES.md), [the provenance record](docs/PROVENANCE_AND_HISTORY.md) and [the historical portable verification report](audit/PORTABLE_VERIFICATION.md).
