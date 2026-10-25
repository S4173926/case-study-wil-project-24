# Phase 9 vs Phase 7: 12-question live review

**Review provenance:** AI-assisted technical analysis; not independent human adjudication. Documentation edition: 25 October 2026; original results retained.

Date: 23 October 2026

## Scope and methodological caution

The same assistant-authored twelve questions were run on Phase 7, then rerun on Phase 9 after engineering changes. Phase 9 had already been developed with access to these questions, so the second run is a **development/regression evaluation**, not an independent held-out test. The app's evidence-coverage score is lexical and cannot be interpreted as factual correctness, probability of truth, or answer completeness. The Phase 9 output is an evidence-display mode, not a polished, validated answer-writing mode.

The table below is a manual review of the outputs supplied by the user, not an independent human adjudication. 'Strong core evidence' means the displayed quotations support the main response ingredients, not that the software generated a complete answer. 'Partial' means relevant evidence was surfaced but important details were missing or distracting passages were displayed.

## Observed outcomes

| Measure | Phase 7 | Phase 9 | Interpretation |
|---|---:|---:|---|
| Answerable questions blocked | 4/9 | 0/9 | Fewer false blocks despite low lexical overlap |
| Answerable questions displaying cited excerpts | 5/9 | 9/9 | Coverage of evidence *display*, not answer correctness |
| Unsupported numerical requests not answered with fabricated numbers | 3/3 | 3/3 | Conservative behavior observed on these three examples only |
| Answerable questions with strong core evidence (Phase 9 reviewer assessment) | Not independently rescored | 6/9 | H01, H02, H03, H06, H07, H08 |
| Answerable questions with partial/incomplete selected evidence (Phase 9 reviewer assessment) | Not independently rescored | 3/9 | H04, H05, H09 |
| Independently human-validated complete answers | Not established | Not established | Further evaluation required |

## Case-by-case manual audit

| ID | Phase 7 | Phase 9 reviewer verdict | Specific observation |
|---|---|---|---|
| H01 ORQA | Blocked (coverage .52) | Strong core evidence | Now shows answer-string-pair supervision, inverse cloze task pretraining, and question encoder fine-tuning; excerpts aren't a synthesized explanation. |
| H02 RECOMP | Blocked (.48) | Strong core evidence | Correctly selects irrelevance/unhelpfulness and empty-summary selective augmentation; good direct support. |
| H03 monoT5 | Blocked (.42) | Strong core evidence | Displays restricted softmax over the 'true'/'false' token logits, which supports the numerical relevance score. |
| H04 Rewrite-Retrieve-Read | Partial excerpts | Partial | Finds policy-gradient/reward-based fine-tuning but omits the warm-up phase using pseudo queries from the selected quotations, although that is visible in retrieved source. |
| H05 SPLADE vs Contriever | Generic comparison | Partial | Displays sparse SPLADE vs dense, contrastively trained Contriever; however selects generic multilingual statements instead of Contriever's specific dense representations/positive-pair training. |
| H06 monoBERT vs monoT5 | Blocked (.04) | Strong core evidence | Displays BERT [CLS] binary classifier probability vs T5 target-word logits/softmax; the coverage score remains extremely low, showing why it should not alone block answers. |
| H07 RECOMP vs FiD | Incorrect FiD excerpt | Strong core evidence | Now shows FiD passage-level encoding/decoder fusion vs RECOMP pre-generation compression; previous FiD quote was about dataset setup. |
| H08 DSP vs rewriting | Distracting RePlug excerpt | Strong core evidence | Now shows DSP demonstrations, multihop query transformation and rewritten conversational queries vs separately RL-trained small query rewriter. Text still requires synthesis. |
| H09 BEIR vs ARES | Partial | Partial | Shows BEIR as retrieval benchmark with 18 datasets and ARES's PPI, but selected excerpts omit ARES's three dimensions and synthetic judge-training details; some excerpts are fragmentary. |
| H10 SPLADE training electricity | No displayed answer | No fabricated number | Explicit explanation that exact measurement terms were not found; does not prove the requested number is absent globally. |
| H11 RECOMP prompt injection rate | No displayed answer | No fabricated number | Exact attack-success-rate request remains withheld with evidence-limitation explanation. |
| H12 Kannada legal-document benchmark | No displayed answer | No fabricated number | No invented nDCG@10 difference; exact dataset/measurement not established. |

## Engineering conclusions

**What improved:** Phase 9 decouples a crude lexical-overlap metric from the choice to display evidence. It conducts targeted within-paper searches and retains source identifiers. All nine answerable questions now display excerpts, and all three unsupported numerical requests still withhold invented figures.

**What has not been demonstrated:** Complete, accurate, independently checked natural-language answers; robust abstention on arbitrary unsupported claims; measurable generation accuracy; or a generalization gain on untouched questions. All outputs are source excerpts, many prefixed with 'not an independently verified answer'.

**Evidence-selection fixes still justified:**

- H04: include warm-up on filtered pseudo-labelled rewrites as well as reader-reward policy gradient.
- H05: rank mechanistic Contriever snippets (dense embeddings, dot-product ranking, cropping and contrastive negatives) above generic multilingual claims; preserve SPLADE's sparse lexical expansion and FLOPS regularization.
- H09: show ARES's synthetic-data-fine-tuned lightweight judges, context relevance, faithfulness and answer relevance, plus prediction-powered inference and human validation; juxtapose BEIR's zero-shot retrieval evaluation and ranking metrics.
- For all comparisons: require one or more concrete method claims from **each** paper before presenting a purported comparison. Distinguish displayed evidence from generated answers and from claim-level entailment validation.

## Development implications

The recorded Phase 7 and Phase 9 outputs support a before/after account of evidence display and false blocking. Complete synthesis, source support and independent final-question performance remain separate evaluation questions. Reusing these twelve cases for subsequent development does not make a later rerun an unseen test.
