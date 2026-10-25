# Evaluation records

| File | Contents |
|---|---|
| [`challenge15_before_repair.zip`](challenge15_before_repair.zip) | Original 15-question challenge batch, before the resulting repairs |
| [`challenge15_diagnostic_review.md`](challenge15_diagnostic_review.md) | Source-based diagnostic review of that batch |
| [`selection_repair_verification.md`](selection_repair_verification.md) | Recorded implementation changes and verification scope |
| [`repaired67_original.zip`](repaired67_original.zip) | Original repaired batch, including answers, sources and its unfilled human scorecard |
| [`repaired67_summary.json`](repaired67_summary.json) | Original summary for convenient inspection |
| [`repaired67_verification.md`](repaired67_verification.md) | Technical regression audit and question-to-run register |
| [`human_scorecard_unfilled.csv`](human_scorecard_unfilled.csv) | Unfilled review instrument, not completed observations |

The analyses are AI-assisted technical diagnostics, not independent human ratings. The challenge questions became development material when their failures informed changes. The repaired batch contains 52 explanation states, one partial state and 14 insufficient-support states; these are software states, not accuracy percentages.

The current source includes the same original repaired records in [`../workbench/results/runs/`](../workbench/results/runs/) and their original archive in [`../workbench/evidence/`](../workbench/evidence/). Historical eight-paper results are in [`../legacy/pre-presentation/rag_research_assistant/results/`](../legacy/pre-presentation/rag_research_assistant/results/). Additional dated comparisons and historical generation evidence are indexed in [`../report-audit/README.md`](../report-audit/README.md).

An optional new regression run can be recorded from the repository root with `python3 run.py --evaluate`. This creates new outputs and does not replace the archived evidence. Independent participant outcomes or completed human-rating datasets are not included in this package.
