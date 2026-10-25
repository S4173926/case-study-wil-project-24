# Evidence index

The records below describe different implementations and evaluation stages. A later run does not retroactively change an earlier result, and a historical board snapshot is not a current task-status report.

| Evidence | Location | Interpretation |
|---|---|---|
| Current application | [`../workbench/`](../workbench/), [`../downloads/Research_Workbench.pyz`](../downloads/Research_Workbench.pyz) | Fixed-catalogue explanation composition and separate passage search |
| Original eight-paper prototype | [`../legacy/pre-presentation/rag_research_assistant/`](../legacy/pre-presentation/rag_research_assistant/) | 24 questions and archived configuration comparisons |
| Historical extractive results | [`../report-audit/historical_8paper_20config_recalculated.json`](../report-audit/historical_8paper_20config_recalculated.json), [`../report-audit/historical_30paper_28config_recalculated.json`](../report-audit/historical_30paper_28config_recalculated.json) | Recalculations from earlier per-question records; different collections and question sets |
| Historical local-model generation | [`../report-audit/historical_local_generation/`](../report-audit/historical_local_generation/), [`../report-audit/historical_local_model_recalculated.json`](../report-audit/historical_local_model_recalculated.json) | Archived Qwen2.5-0.5B-Instruct experiment, not the final default engine |
| Matched routing comparison | [`../report-audit/matched_ablation_52.json`](../report-audit/matched_ablation_52.json), [`../report-audit/retrieval_comparison.csv`](../report-audit/retrieval_comparison.csv), [`../report-audit/paired_routing_changes.json`](../report-audit/paired_routing_changes.json) | Six settings, 42 quotation-labelled requests, five returned passages |
| Challenge and repairs | [`../evaluation/`](../evaluation/), [`../report-audit/challenge_before_after.json`](../report-audit/challenge_before_after.json) | Failures and later repairs on known development cases |
| Regression reproduction | [`../report-audit/regression_equivalence.json`](../report-audit/regression_equivalence.json) | Reproduction of 67 recorded outputs on specified fields, not independent correctness |
| Source and software checks | [`../workbench/audit/`](../workbench/audit/), [`../report-audit/integrity.json`](../report-audit/integrity.json), [`PACKAGING_VERIFICATION.md`](PACKAGING_VERIFICATION.md) | Historical logs, hashes and defined test boundaries |
| Supplementary probes | [`../report-audit/supplementary_probes/`](../report-audit/supplementary_probes/) | Frozen diagnostic inputs and retained responses, including failures |
| Earlier 12-question reviews | [`verification-2026-10-23/`](verification-2026-10-23/) | First-run review and subsequent development/regression comparison |
| Historical source verification | [`verification-2026-10-23/VERIFIED_SOURCE_AUDIT.md`](verification-2026-10-23/VERIFIED_SOURCE_AUDIT.md) | Recorded source-integrity and quotation-presence checks; supporting-file availability is documented in that folder's README |
| Team process | [`project-management/`](project-management/) | Dated historical Trello record and its scope |
| Original Git history | [`../history/`](../history/) | Preserved bundle, ledger and explanation of the maintenance export |
| Current distribution checks | [`DISTRIBUTION_VERIFICATION.md`](DISTRIBUTION_VERIFICATION.md) | Documentation consistency, preserved-data hashes and archive integrity |

The unfilled human scorecard is an evaluation template, not an observation dataset. Historical diagnostic reviews identify their AI-assisted provenance. Their judgements are not independent human ratings.
