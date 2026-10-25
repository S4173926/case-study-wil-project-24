# Written-report evidence

This directory contains recorded outputs and recalculations supporting the Group 24 report. It combines the earlier report audit with the historical local-model evidence. Raw JSON/JSONL/CSV records, scripts, logs, original passages and probe response texts are preserved from the supplied archives.

## Stages

- `historical_8paper_20config_recalculated.json`: eight-paper / 24-question extractive comparisons.
- `historical_30paper_28config_recalculated.json`: later 30-paper / 40-question extractive comparisons.
- `historical_local_model_recalculated.json` and `historical_local_generation/`: the separately recorded local-model generation run and its source provenance.
- `matched_ablation_52.json`, `retrieval_comparison.csv`, `paired_routing_changes.json`: the final matched five-passage routing comparison on 42 quotation-labelled requests.
- `regression_equivalence.json` and `challenge_before_after.json`: known-case reproduction and challenge repairs.
- `supplementary_probes/`: protocol and full preserved responses for eight diagnostic cases.
- `integrity.json`, `label_inventory.json`, `software_tests.txt`: mechanical/source checks and the historical software-test log.
- `trello_audit.json`: analysis of the historical project-board export.

`provenance_snapshot/` preserves the exact documentation used in the earlier audit. Its historical wording and hashes are not assertions that every document in the current distribution has the same bytes. `source_integrity_for_this_delivery.json` records integrity for that earlier source delivery, and `report_quality_checks.json` belongs to the earlier compiled report. Neither certifies a later Overleaf export.

`reproduce_core_audit.py` is a reproduction tool. It has not been rerun to prepare this documentation edition. Known-question counts, quotation presence, code integrity and human-rated correctness remain distinct measures.
