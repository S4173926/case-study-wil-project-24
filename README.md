# Research Workbench

**RMIT COSC2669/COSC2816 · WIL Project 24 · Education and research**

Research Workbench is a local application for inspecting and comparing methods in a bounded collection of 30 information-retrieval and retrieval-augmented-generation papers. It combines source-linked explanations, original-passage search, PDF inspection, saved-answer review and a research-task evaluation interface.

The default explanation engine selects and combines statements from a fixed, source-linked catalogue. It is distinct from the project's earlier language-model generation experiments. Source links support inspection; they do not certify answer correctness or completeness.

## Run

Python 3.10 or newer is required. The default application uses the Python standard library and does not require a model download, GPU, paid API or external service.

From the repository directory:

```sh
# macOS / Linux
python3 run.py
```

```powershell
# Windows
py -3 run.py
```

The launcher opens a browser at `http://127.0.0.1:8765`, or prints another local port when that address is occupied. Keep the terminal open while using the application; `Ctrl+C` stops it. The executable can also be started with `python3 downloads/Research_Workbench.pyz`. The `.pyz` is an executable Python archive, not an archive that needs manual extraction.

Saved records are stored under `~/Research_Workbench_Data/`. The launcher retains earlier local workspaces and preserves conflicting imported records separately. This is a local application, not a hosted multi-user website.

To run the readable source instead:

```sh
cd workbench
python3 app.py --open
```

## Repository guide

| Location | Contents |
|---|---|
| [`downloads/Research_Workbench.pyz`](downloads/Research_Workbench.pyz) | Portable application |
| [`workbench/`](workbench/) | Application source, interface, 30 source PDFs, passage index, catalogue, tests and 67 stored regression runs |
| [`distribution_source/`](distribution_source/) | Portable launcher and payload manifest |
| [`tools/`](tools/) | Package rebuilding and repository-integrity utilities |
| [`evaluation/`](evaluation/) | Original challenge and repaired-result archives, diagnostic analyses and the unfilled review template |
| [`report-audit/`](report-audit/) | Matched retrieval comparison, historical recalculations, local-model evidence and supplementary probes |
| [`docs/verification-2026-10-23/`](docs/verification-2026-10-23/) | Historical 12-question reviews and source-corpus verification report |
| [`legacy/pre-presentation/`](legacy/pre-presentation/) | Earlier eight-paper pipeline, recorded experiments, presentation and speaker script |
| [`docs/project-management/`](docs/project-management/) | Privacy-minimised historical Trello record |
| [`history/`](history/) | Original Git bundle and commit ledger |

Start with the [evidence index](docs/EVIDENCE_INDEX.md) for the relationship between recorded findings and their supporting files.

## Evaluation scope

The final collection contains 1,202 passages, 99 explanation units and 191 supporting spans. In the recorded five-passage comparison, BM25 retrieved a labelled quotation for 25 of 42 eligible requests without routing and 31 with routing. Labelled evidence from every expected paper was retrieved for 24 of 42 requests with routing. These are evidence-retrieval measures, not factual-answer accuracy.

The stored repaired batch contains 52 explanation states, one partial state and 14 insufficient-support states across 67 known questions. Historical software verification recorded 118 passing tests. Known-case reproduction, software integrity, semantic answer quality and participant benefit are separate measures. The evidence includes remaining false refusals and incomplete responses; no independent participant-outcome dataset accompanies this release.

The earlier local-model run is preserved separately in [`report-audit/historical_local_generation/`](report-audit/historical_local_generation/). Its results must not be attributed to the final catalogue-based engine.

## Verification and reproducibility

Check the supplied repository files without executing the application or experiments:

```sh
python3 tools/verify_repository.py
```

The following optional commands reproduce software checks or record another known-question batch:

```sh
python3 run.py --check
python3 run.py --evaluate
```

`--evaluate` creates a new output directory. The preserved result files remain the evidence for the report's existing measurements. The [distribution verification record](docs/DISTRIBUTION_VERIFICATION.md) distinguishes the present documentation/package checks from earlier software test runs.

## Team and project records

| Team member | Recorded role |
|---|---|
| Chetan Bera | Scrum Master / project lead |
| Imranjit Singh Kohli | Data engineering and corpus preparation |
| Qiling Huang | Retrieval and machine-learning engineering |
| Dhanush Sridhar | Application development |
| Amritpal Singh Gill | DevOps and documentation |
| Deboprio Saha Argha | Quality assurance and evaluation |

[Trello board](https://trello.com/b/9hEOJ49W/case-study-wil-project-24) · [Group Overleaf workspace](https://www.overleaf.com/project/6a82504d8e51f4412a5f06d4)

The archived Trello snapshot is a dated process record, not a claim about the live board's current state. The original 12-commit Git history is retained in a bundle separately from the repository's recovery commits. The written report and signed submission documents are separate assessment materials, not generated by this application.
