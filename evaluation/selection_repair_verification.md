# Workbench selection repair: executed verification

**Version:** 1.1-clause-selection-repair  
**Scope:** Correction of the defects exposed by the submitted 15-question challenge. This is development/regression evidence, not independent accuracy.

## Changes

The existing application is retained. The update corrects nested paper-name matching, retains independent question clauses, selects claims separately for each paper and request, and records unmatched requests explicitly. It expands three existing source-linked explanations from the unchanged original papers: REPLUG's probability weighting, Atlas's reader architecture and SPLADE's effectiveness-efficiency trade-off. It does not change model weights or introduce paid services.

## Executed verification

| Check | Result |
|---|---|
| Reproduce original tests | 45 passed |
| Existing plus new regression tests | 70 passed, no skips |
| Known question batch | 52 original + 15 challenge questions executed |
| Original 52 output categories | Unchanged: 41 explanations, 1 partial, 10 insufficient |
| Previously opened challenge output categories | 11 explanations, 4 insufficient |
| Original PDF integrity | 30/30 matched |
| Source index | Unchanged, 1,202 passages |
| Curated catalogue | 99 claims, 191 exact supporting spans |
| Installer test | Staged copy and installed-copy tests passed; batch generated |
| Repeat application | Idempotent; no overwrite of earlier output batches |
| User modification safety | Modified original code rejected without overwrite |
| Forced verification failure | Replaced files rolled back to original bytes |
| Prior data preservation | A separate synthetic review sentinel remained unchanged |

The installer tests used isolated copies. No synthetic review or pilot observation is included in the delivered payload or counted as research data.

## Five specific corrections inspected

- **F03:** Explains what FLOPS regularisation targets and the possible retrieval-effectiveness versus efficiency trade-off.
- **F04:** Selects REPLUG's separate document-conditioned language-model passes and similarity-weighted next-token probability combination.
- **F07:** Includes both Atlas's joint-training finding and the reader's independent document encoding/decoder cross-attention. The training keyword no longer deletes the second request.
- **F08:** Scopes exactly RECOMP and CRAG. Includes selective compression/omission and confidence-based corrective action, web evidence and refinement.
- **F11:** Includes REPLUG and FiD rather than filtering out FiD because it lacks REPLUG's black-box property.

The original four unsupported challenge questions still receive insufficient-support responses. The earlier HyDE case remains explicitly partial. Clause coverage is a heuristic; correct status labels do not prove accurate and complete answers.

## Source confirmation

The three expanded summaries are supported by the unchanged pinned papers: REPLUG section 3.2 (`replug:s0010`), Atlas section 2.1 (`atlas:s0008`), and SPLADE's regularisation/trade-off discussion (`splade:s0011`, `splade:s0016`, `splade:s0017`). Original pages were visually inspected and source spans checked mechanically. All independent human-review fields remain pending.

## Boundaries

This correction was run locally on the default deterministic source-claim composer. The optional MLX selector was tested only through mock contract checks, not live Apple model inference. The frontend was not changed or newly browser-tested. HTTP integration tests ran. The subsequent supplied-run verification is recorded in `repaired67_verification.md`.

The 67 questions are now known development/regression material. No independent test score, human correctness score, stakeholder benefit is inferred from the output-category counts. Existing human scorecards remain blank.

## Relationship to this distribution

The current application already includes this selection repair. The historical installer is not needed to run this repository. The original repaired batch is preserved in `repaired67_original.zip` and in the application evidence directory. Earlier test counts in this record describe the repair-stage checks, not a new execution during documentation packaging.
