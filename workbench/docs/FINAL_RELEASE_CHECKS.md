# Research Workbench finalisation: executed checks

**Release:** 1.2-final-interface, 24 October 2026.  
**Scope:** Consolidation of the verified repaired application, review usability and neutral product wording. No model upgrade or new answering architecture.

## Executed results

| Check | Result |
|---|---|
| Existing and added unit/integration tests | 98 passed; 0 failed; 0 skipped |
| Browser-component checks | 24 passed; no JavaScript page errors |
| Previously recorded questions reproduced | 67/67 |
| Factual blocks, selected claims, citations, source passages, statuses and missing-support messages | Unchanged for all 67 |
| Seeded original recorded runs | 67/67 byte-identical to the uploaded repaired batch |
| Original PDF hashes | 30/30 matched |
| Source catalogue | 1,202 passages, 99 claims, 191 supporting spans |
| Current application-owned text scan | 39 files; no requested tool-name/assistance-label matches |
| New human ratings or participant observations supplied | None |

## Changes verified

Search accepts question IDs, paper names/titles, question text and run IDs. Filtering respects version qualification before deduplication. The default prioritises the exact verified repaired hash tuple and current runs, not whichever old file happens to have a later timestamp. Historical versions remain accessible and labelled. More than 150 stored records remain discoverable.

Switching questions resets the four ratings, answerability choice, notes and PDF-confirmation box while retaining reviewer identity. The save operation records the exact selected run. Unsupported answers show retrieved snippets as related search results, collapsed by default, rather than implying they support an absent measurement.

Record migration was tested with isolated fixtures for byte preservation, idempotency, all three record categories, conflict refusal before copying, invalid records, symbolic links and exclusion of unrelated files. The old workspace is not edited. Synthetic browser ratings were created only inside a temporary directory and are not in this package.

## Browser execution boundary

Direct Chromium navigation failed with an environment-policy block. The successful 24-check run used the actual application components with fetch bridged to the actual local HTTP server. Thus component interactions, filtering, form handling, rendering, source-modal creation and HTTP responses were tested. This is not a claim of native Chrome navigation or embedded PDF rendering on the user's Mac. The optional Apple-silicon model was not executed here.

## What the regression counts mean

The frozen batch still has 52 explanation statuses, one explicitly partial response and 14 insufficient-support responses. These are status counts, not a measured accuracy percentage. The known questions influenced development. No independent reviewer, participant, time saving or course mark has been invented.

## Preservation and wording

Neutral product text replaces development-tool labels. Catalogue drafting is still accurately described as language-model-supported development, not independently authored human gold data. The original 30 papers, their extracted passages and the historical run records are untouched; terminology occurring in those original sources or archival records has not been erased. The earlier raw catalogue metadata remains recoverable from the original delivered inputs.

The current code and catalogue hashes are in `audit/validation_report.json`; immutable package files are checked by `tools/verify_release.py`. The original repaired archive is hashed in `evidence/manifest.json`.

## Assessment boundary

This is ready to freeze as the software deliverable. The supplied assessment also requires documented findings, stakeholder value, authentic teamwork and the final report. Those are not certified by software tests. See `docs/RUBRIC_MAP.md` for the supplied-criteria evidence map and the remaining non-software requirements.
