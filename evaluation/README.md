# Evaluation evidence

- `repaired67_original.zip`: immutable uploaded 67-question repaired run, including individual
  answers, sources and the original unfilled human scorecard.
- `repaired67_summary.json`: the original summary copied out for convenient inspection.
- `challenge15_before_repair.zip`: original post-freeze challenge run before its failures
  informed the repair. It is now development/regression material, not an unused holdout.
- `*_verification.md` and `challenge15_diagnostic_review.md`: previously delivered technical
  review records. These are developer diagnostics, not independent human scores.
- `human_scorecard_unfilled.csv`: supplied blank scorecard, not completed observations.

The current application also includes the original repaired run records in
`../workbench/results/runs/` and its immutable original batch in
`../workbench/evidence/original_repaired_regression67.zip`.
Historical eight-paper results are in
`../legacy/pre-presentation/rag_research_assistant/results/`.

The repaired batch has 52 explanation statuses, one partial status and 14 insufficient-support
statuses. These are NOT accuracy grades. The code and catalogue were developed using these
questions. The later constrained composer is not a model-only improvement over the old generator.

No new human ratings, participants, pilot time savings or unseen-question accuracy results
are included. Reviews saved only on a teammate's laptop are not available in this delivery.
Those may be exported separately, checked for consent/privacy, and added as dated observations.

To collect another regression run (not required merely to install the application):

```sh
python3 run.py --evaluate
```

To inspect source-level retrieval ablations:

```sh
cd workbench
python3 -m workbench.cli ablation --questions eval/all52_development.jsonl --out results/ablation-new.json
```

Use a new output path and keep previous results unchanged. A test pass, valid citation ID or
nonempty answer must not be reported as independently established factual correctness.
