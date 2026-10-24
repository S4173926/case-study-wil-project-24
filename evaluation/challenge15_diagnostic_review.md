# Research Workbench: 15-question challenge-run audit

**Run received:** `fresh15_20261024T164105.zip`  
**Study date:** 24 October 2026  
**Status:** Assistant-authored source-based diagnostic review, **not independent human accuracy validation**, not a university mark forecast.

## Executive decision

**The application is running and behaves cautiously when unsupported, but it is NOT yet defensible to call its autonomous answer selection highest-band-ready.** The batch exposes source-selection and completeness-detection defects, including failures where the correct explanation is already in the system's own curated catalogue. Preserve this ZIP as an immutable challenge run.

## Recorded outputs (mechanical, directly from ZIP)

- **15 / 15** question-run records supplied, 15 distinct run IDs.
- **7** recorded `source_linked_explanation` statuses, **4** `partial`, **4** `insufficient`.
- **20** claim blocks displayed; **27** claim-to-source references, all resolved to citation records in the supplied outputs. This tests mechanical source attribution, not whether statements answer the question.
- The user's uploaded `human_scorecard.csv` has blank reviewer and rating fields. **Human accuracy: not measured.**
- All runs report the same corpus, code, and knowledge hashes; no sign of a changed build within this batch.

## Provisional answer adequacy (assistant diagnostic assessment, not a measured accuracy rate)

Among **11 answerable questions**, 6 appear substantially adequate for the question asked, 3 are visibly incomplete, and 2 substantially fail to answer the central request. All 4 constructed unsupported questions receive cautious refusal. These judgments are based on the emitted answers, linked excerpts and focused inspection of relevant original PDFs. They must not be entered as independent human reviewer scores.

| ID | Workbench status | Diagnostic verdict | Key finding |
|---|---|---|---|
| F01 FiD encoder/decoder | Complete | **Adequate** | Correctly states passage-wise encoding and decoder-side fusion; paper method section supports it. |
| F02 GTR embedding bottleneck | Complete | **Adequate, concise** | Larger dual encoder with fixed embedding bottleneck; paper discusses constant dimension and dot product. Could be more specific. |
| F03 SPLADE FLOPS | Partial | **Incomplete** | Identifies FLOPS as an operations proxy but does not explain stronger sparsity/efficiency pressure versus potential effectiveness losses. |
| F04 REPLUG document combination | Partial | **Misses key answer** | Describes frozen black-box LM only. Does **not** mention separate document-conditioned forward passes followed by similarity-weighted averaging of next-token probability distributions. This is in the original paper's §3.2 and in Workbench's F11 response. |
| F05 In-Context RALM stride | Complete | **Adequate** | Defines generated-token interval between retrievals and overhead versus improvement when retrieval is more frequent. |
| F06 RAGAS answer relevance | Complete | **Adequate** | Gives generated-question embedding comparison, distinguishes reference-free scoring from research validation. Contains extra context, but core mechanism is correct. |
| F07 Atlas retriever/reader | Complete | **Misses key answer** | States joint pre-training is important but omits the reader's actual multi-passage processing via FiD, with independent per-document encoding and decoder cross-attention. The original Atlas paper explains this. **False-complete status.** |
| F08 RECOMP vs CRAG | Partial | **Incomplete** | States compression versus decompose/recompose, but misses CRAG retrieval-evaluator confidence branches and web-search correction, as well as RECOMP selective omission. Additionally misidentifies `rag` as a third named paper because of the phrase “Corrective RAG.” |
| F09 RETRO vs In-Context RALM | Complete | **Adequate** | Explains RETRO's retrieved chunks/cross-attention versus unchanged-LM input prepending in In-Context RALM. Some extra unrelated detail. |
| F10 BEIR vs LoTTE | Complete | **Adequate but high-level** | Gives heterogeneous zero-shot evaluation versus long-tail, natural user-topic retrieval. More LoTTE design details would strengthen explanation. |
| F11 REPLUG vs FiD | Partial | **Incomplete** | Provides REPLUG's actual multi-document ensemble but omits FiD entirely despite its correct FiD explanation in F01 of the **same** run. |
| F12 Concurrent latency | Insufficient | **Appropriate cautious refusal** | The batch contains no supported 100-user p95 deployment measurement. |
| F13 RECOMP cloud cost | Insufficient | **Appropriate cautious refusal** | No verified Sydney AWS cost per 1,000 queries. |
| F14 Diabetic-retinopathy claim | Insufficient | **Appropriate cautious refusal** | No validated biomedical ColBERTv2 accuracy experiment in indexed collection. |
| F15 Zero hallucinations | Insufficient | **Appropriate cautious refusal** | No experiment establishes zero hallucinations across deployed RAG systems. A direct explanation of non-proof would improve UX. |

## Source confirmations beyond the app's own status labels

1. **REPLUG** original paper, §3.2 “Input Reformulation”: it prepends each retrieved document separately to the prompt, runs the frozen LM separately, and calculates a **similarity-weighted average of next-token probabilities** over the retrieved documents. The weights are normalized exponentiated retrieval similarity scores. F04 fails to explain this, while F11 selects a catalogue entry that does.
2. **Atlas** original paper: its retrieval-augmented T5 reader uses **Fusion-in-Decoder**. The retrieved documents are independently encoded with the query, and concatenated encoder outputs are attended to by the decoder. F07 does not mention this despite being asked specifically.
3. **CRAG** original paper: a retrieval evaluator selects **Correct / Incorrect / Ambiguous** actions based on confidence. Weak retrieved evidence can cause **web-search correction**, while retrieved content is also refined by decomposing and recomposing. F08 only mentions refinement and misses the branching correction strategy.
4. **LoTTE** in ColBERTv2 paper: a resource focused on natural user queries about long-tail topics, complementary to BEIR, with topic-stratified evaluation. F10's broad explanation matches this framing.
5. **SPLADE** original paper: the FLOPS regulariser approximates retrieval scoring operations and incentivizes a better-balanced sparse index; adjusting sparsity strength changes the effectiveness–efficiency trade-off. F03 is incomplete in its response to the second part.

## Verified engineering failure patterns

**A. False completeness:** A full-answer status means the selected claims cover crude keyword-derived facets, not the real multi-clause user question. F07 is the clearest counterexample.

**B. Inconsistent use of existing knowledge:** F04 misses a REPLUG ensemble claim selected in F11. F11 misses FiD's explanation already selected in F01. A larger model is not required to fix these two examples: retrieval/planner selection and coverage must be addressed.

**C. Paper name routing:** The question “Corrective RAG (CRAG)” causes the planner to include the generic RAG paper unnecessarily. The router needs to distinguish method names from generic technical labels.

**D. Weak useful refusal text:** F12–F15 avoid fabrication but frequently say only that no matching curated claim was found. This does not fully answer user instructions such as “state that the collection does not establish it.” Refusal decisions are good; refusal wording can improve.

**E. Curation trade-off:** Outputs are deterministic compositions of an AI-curated claim catalogue, not live generative inference or independent proof of source fidelity. Previously repeated questions influenced curation. This run is a useful post-freeze challenge, but it is now **development/regression material** once used to diagnose or tune the system.

## Specific release acceptance checks (before another ZIP)

1. F04: output must explicitly state *separate document-conditioned LM passes and similarity-weighted probability ensemble*, cited to REPLUG §3.2.
2. F07: output must include both *why joint retriever+reader pre-training matters* and *how the FiD reader jointly attends to representations of independently encoded passages*. Status must not be `source_linked_explanation` if either part is missing.
3. F08: paper scope must be exactly **RECOMP + CRAG**, and answer must distinguish *compress / possibly omit* versus *confidence-based corrective action, web search and evidence refinement*.
4. F11: output must cover **both** REPLUG and FiD, including the explicit document-combination distinction and black-box property.
5. F03: explain FLOPS/sparsity pressure, indexing/retrieval cost and possible retrieval-quality trade-off.
6. After engineering changes, run a **batch** of all 52 development cases and this frozen F01–F15 challenge as regression checks, **but do not describe passing them as unbiased generalization**. Reserve new blinded questions assembled and sourced by an independent reviewer after code freeze.

## Implications for the 25-mark report

The project is promising: the corpus, provenance machinery and appropriate abstention work. But **these findings prevent an honest claim that the assistant is already at full-marks readiness.** Address the multi-clause coverage defects before freezing the final system, then conduct independent source-based reviews and actual stakeholder timing/accuracy comparisons. Distinguish model-selection behavior from completeness, answer correctness and source attribution. The final rubric also requires a convincing project scope, methodology, quantitative findings, genuine business/stakeholder benefit, authentic teamwork, and the final report. Software improvements alone cannot secure those marks.

**No code modifications were made in this audit.** Original submitted ZIP remains unmodified.
