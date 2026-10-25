# Repaired 67-question batch: verification and decision

**Source:** `repair_regression67_20261024T061234_38643.zip`  
**Build:** `1.1-clause-selection-repair`  
**Assessment type:** AI-assisted technical regression audit. Not independent human accuracy evaluation.

## Decision

The five specific content/routing defects identified in the earlier 15-question challenge are resolved in the submitted repaired outputs. This judgment is based on the displayed text and its included supporting source passages, not just status labels. This finding does not establish that every answer is complete, that the system generalises to unseen questions.

The uploaded archive and previous result archives were not changed. The application was reconstructed in an isolated audit directory from the original delivery plus the existing repair payload. No new software repair is supplied by this review.

## Executed checks

| Check | Result |
|---|---:|
| Recorded question runs | 67, all distinct run IDs |
| Explanation output states | 52 |
| Explicitly partial output states | 1 |
| Insufficient-support output states | 14 |
| Mac staged tests in supplied log | 70 passed |
| Mac installed-copy tests in supplied log | 70 passed |
| Reproduced tests in audit environment | 70 passed |
| Packaged-file integrity in audit copy | 230 matched, no mismatches |
| Original PDF hashes in audit copy | 30/30 matched |
| Catalogue | 99 claims, 191 exact evidence spans |
| Deterministic response replay | 67/67 matched selected content/planning/source fields |
| Displayed claim blocks / distinct claims | 100 / 69 |
| Displayed claim-to-source references checked | 153, no mechanical mismatch |
| Rows with human reviewer identity in uploaded scorecard | 0/67 |
| Logged optional model calls in this batch | 0 |

Reproduction excluded changing run IDs, timestamps, execution time and evaluation metadata. It included displayed claims, selected sources, source text, planning, missing requests, warnings and coverage records. Mechanical provenance verifies source identity and text, not semantic entailment. Successful tests are not independent answer-accuracy scores.

## Before and after

| Batch | Before | After |
|---|---|---|
| Original 52 | 41 explanations, 1 partial, 10 insufficient | Same output-state counts for the same questions |
| Challenge 15 | 7 explanations, 4 partial, 4 insufficient | 11 explanations, 4 insufficient |

F07 was already marked complete before the repair; its actual text was missing the reader mechanism. The new text adds that mechanism without a status change. This is why status counts cannot substitute for checking responses.

Eighteen of the original 52 records changed their selected/order of claims, comparison fields or missing-request text. Unchanged counts do **not** mean all answer text is identical. Inspection of the changed selection examples found that removed blocks were generally extra background, such as REALM masking when the request concerned its learning signal. This is not an exhaustive independently scored no-regression claim.

## Targeted correction checks

| Question | Previously identified fault | Current result |
|---|---|---|
| F03 | Missing effectiveness-efficiency trade-off | Required trade-off is explicitly included |
| F04 | Missing how document-conditioned predictions are combined | Separate passes and weighted next-token probability average included |
| F07 | Training clause answered; reader clause omitted | Both training motivation and reader architecture included |
| F08 | Spurious third paper and incomplete corrective actions | Exactly RECOMP + CRAG; key actions included |
| F11 | FiD omitted from comparison | Both methods and the black-box distinction included |

### F03: SPLADE efficiency trade-off

**Run:** `20261024T061244_5a15a78c0e`

**Question:** What does the FLOPS regularizer in SPLADE try to reduce, and what trade-off does it create between retrieval quality and efficiency?

**Review:** The output explains the operations proxy, pressure on average term activations, sparse-index efficiency and possible effectiveness loss. It resolves the previously omitted trade-off.

**Supporting source records checked:** `splade:s0011; splade:s0001; splade:s0016; splade:s0017`. These are the corpus passage IDs included in the recorded output.

**Recorded answer:**

- **splade:** SPLADE's FLOPS regulariser approximates the operations needed to score query-document representations, which are related to retrieval time. It penalises high average term activations to encourage a more balanced sparse index. Increasing sparsity pressure can reduce retrieval work and index size, but can also sacrifice retrieval effectiveness; its strength therefore controls an effectiveness-efficiency trade-off rather than guaranteeing an accuracy improvement. Sources: `splade:s0011`, `splade:s0001`, `splade:s0016`, `splade:s0017`

### F04: REPLUG prediction combination

**Run:** `20261024T061244_c609903f7a`

**Question:** How does REPLUG combine language-model predictions when several different retrieved documents are relevant to the same question?

**Review:** The output explicitly describes separate document-conditioned passes and a similarity-weighted average of next-token distributions. It no longer substitutes a generic black-box description for the requested mechanism.

**Supporting source records checked:** `replug:s0010`. These are the corpus passage IDs included in the recorded output.

**Recorded answer:**

- **replug:** REPLUG prepends each retrieved document separately to the input context and runs the frozen language model separately for each document. It combines the resulting next-token probability distributions using a similarity-weighted average: document weights are the exponentiated document-context similarity scores, normalised across the retrieved set. This uses several documents without concatenating them all into one input window. Sources: `replug:s0010`

### F07: Atlas two-part request

**Run:** `20261024T061244_ca5c645480`

**Question:** Why does Atlas jointly pre-train its retriever and reader, and how does its reader make use of multiple retrieved passages?

**Review:** Both clauses are now addressed: the few-shot-performance motivation for joint pre-training and the FiD reader mechanism. The training rationale is concise, not an exhaustive analysis of the training objectives.

**Supporting source records checked:** `atlas:s0003; atlas:s0008`. These are the corpus passage IDs included in the recorded output.

**Recorded answer:**

- **atlas:** Atlas jointly pre-trains its retriever and reader components. The paper finds this joint pre-training important for few-shot downstream performance and studies different pre-training objectives and schemes. Sources: `atlas:s0003`

- **atlas:** Atlas pairs a dense retriever with a T5 sequence-to-sequence reader using Fusion-in-Decoder. The reader concatenates the query to each retrieved document and encodes each document independently. It concatenates those encoder outputs, and its decoder uses cross-attention over the combined representations to generate the answer. The system is designed for few-shot knowledge-intensive tasks. Sources: `atlas:s0003`, `atlas:s0008`

### F08: RECOMP versus CRAG

**Run:** `20261024T061244_8f154dedce`

**Question:** When retrieved information is noisy, how do RECOMP and Corrective RAG (CRAG) differ in what they do before the model generates its answer?

**Review:** Scope is exactly recomp and crag. The answer covers compression and selective omission, and the evaluator-driven Correct/Incorrect/Ambiguous actions, web evidence and refinement.

**Supporting source records checked:** `recomp:s0001; recomp:s0002; recomp:s0003; crag:s0001; crag:s0009`. These are the corpus passage IDs included in the recorded output.

**Recorded answer:**

- **recomp:** When retrieved documents are irrelevant to the input or offer no additional useful information to the language model, RECOMP can return an empty string, or empty summary. In that case no retrieved summary is added to the model input. This is selective augmentation, not a requirement to use every retrieved document. Sources: `recomp:s0001`, `recomp:s0002`

- **recomp:** RECOMP adds a Retrieve–Compress–Prepend step before a language model answers. It turns the retrieved documents into a shorter, query-focused textual summary and prepends that summary to the model input. The intervention is a shorter textual input before downstream generation. Sources: `recomp:s0002`, `recomp:s0003`

- **crag:** Corrective RAG (CRAG) uses a lightweight evaluator to score the relevance of retrieved documents to the query. Its confidence assessment selects a Correct, Incorrect or Ambiguous action: refine retrieved knowledge when it is judged correct, discard inadequate retrieval and seek web evidence when it is incorrect, or combine refined internal and external evidence when the judgment is ambiguous. Sources: `crag:s0001`, `crag:s0009`

- **crag:** CRAG uses a decompose–then–recompose procedure to refine retrieved documents: it focuses on useful information and filters irrelevant material before generation. Sources: `crag:s0001`

### F11: REPLUG versus FiD

**Run:** `20261024T061244_41e9e8f4af`

**Question:** How do REPLUG and Fusion-in-Decoder combine information from multiple documents, and which method works with a frozen black-box language model?

**Review:** Both papers are explained. It contrasts probability-distribution combination with decoder-side attention, and identifies REPLUG as using a frozen black-box model.

**Supporting source records checked:** `replug:s0010; replug:s0001; fid:s0007`. These are the corpus passage IDs included in the recorded output.

**Recorded answer:**

- **replug:** REPLUG prepends each retrieved document separately to the input context and runs the frozen language model separately for each document. It combines the resulting next-token probability distributions using a similarity-weighted average: document weights are the exponentiated document-context similarity scores, normalised across the retrieved set. This uses several documents without concatenating them all into one input window. Sources: `replug:s0010`

- **replug:** REPLUG treats the language model as a frozen black box. It augments the model by prepending retrieved documents to its input, rather than modifying the language model to add a specialised cross-attention architecture. Sources: `replug:s0001`

- **fid:** Fusion-in-Decoder (FiD) concatenates the question with each retrieved passage and its title, then encodes each passage independently. The decoder attends across the concatenated encoded representations of all passages to generate the answer. Evidence is therefore fused in the decoder, rather than by jointly encoding all passages. Sources: `fid:s0007`

## Remaining limitations

- **q18 / HyDE remains partial.** It contains a broad secondary-survey summary rather than a detailed explanation. The earlier audit identified a more specific existing survey passage. The repair did not address that item. It must not be counted as a full successful answer.
- **All 67 are now known development/regression questions.** The 15 challenge questions influenced this repair. Retesting them measures defect correction, not blind generalisation.
- **The default system composes curated claims.** No live Qwen generation is present in these run records. These results are not evidence of a newly trained or improved generative model.
- **Coverage is still heuristic.** A complete-looking status does not prove that every intended detail is covered. Some adequate outputs are terse, and some retain unnecessary background.
- **Refusals stay cautious.** All 14 benchmark-labelled unsupported questions have an insufficient-support state with no factual claim blocks. The wording sometimes only says that no supported explanation could be assembled; this is not a formal proof of absence from all research literature.
- **No independent human ratings or user-benefit measurements are established by this archive.** Blank human fields were kept blank. This audit must not be relabelled as a human study.

## Review status

The accompanying scorecard has no completed independent human ratings. The question-to-run register below identifies the repaired outputs for source-based review. Review correctness, completeness, support, relevance and participant task outcomes remain distinct from deterministic reproduction. Any later observations require their own dated source records.

## Question-to-run register

| ID | Output state | Run ID | Question |
|---|---|---|---|
| q01 | source_linked_explanation | `20261024T061243_5963a49da8` | What training negatives does Dense Passage Retrieval use? |
| q02 | source_linked_explanation | `20261024T061243_20d600d637` | How does ColBERT compute the relevance score between a query and a document? |
| q03 | source_linked_explanation | `20261024T061243_e9ba92308e` | What is the difference between RAG-Sequence and RAG-Token? |
| q04 | source_linked_explanation | `20261024T061243_1b23fee399` | What serves as the non-parametric memory in the RAG model? |
| q05 | source_linked_explanation | `20261024T061243_4d86af95c8` | How does Fusion-in-Decoder combine multiple retrieved passages? |
| q06 | source_linked_explanation | `20261024T061243_7118a5d309` | What learning signal is used to pre-train the REALM knowledge retriever? |
| q07 | source_linked_explanation | `20261024T061243_ecf5769d21` | Which quality aspects does RAGAS measure for retrieval augmented generation? |
| q08 | source_linked_explanation | `20261024T061243_4af197bf5c` | What are reflection tokens in Self-RAG used for? |
| q09 | source_linked_explanation | `20261024T061243_9f27d7c1af` | Which two chatbot approaches were implemented in Walert? |
| q10 | source_linked_explanation | `20261024T061243_ec15b1fb87` | Which retrieval models did Walert experiment with in its RAG pipeline? |
| q11 | source_linked_explanation | `20261024T061243_91e0299c8e` | How did Walert perform on out-of-knowledge-base questions? |
| q12 | source_linked_explanation | `20261024T061243_11ea1171b5` | How does REALM keep its document index up to date while the retriever parameters change during pre-training? |
| q13 | source_linked_explanation | `20261024T061244_1e8ed90172` | Why does RAGAS describe its evaluation as reference-free? |
| q14 | source_linked_explanation | `20261024T061244_127f07f93b` | How do DPR and ColBERT differ in how they encode queries and passages for retrieval? |
| q15 | source_linked_explanation | `20261024T061244_794e42b528` | Which retrieval methods do RAG and Fusion-in-Decoder use to fetch supporting passages? |
| q16 | source_linked_explanation | `20261024T061244_7eef346185` | How do RAGAS and Self-RAG each check whether a generated answer is supported by the retrieved passages? |
| q17 | source_linked_explanation | `20261024T061244_44fa17ef8f` | How do REALM and RAG differ in when the retriever is trained? |
| q18 | partial | `20261024T061244_d0c073abbb` | How does HyDE generate hypothetical documents for zero-shot dense retrieval? |
| u02 | insufficient | `20261024T061244_edfae989a8` | What is the monthly cloud hosting cost of deploying ColBERT on Kubernetes? |
| u03 | insufficient | `20261024T061244_8d957d55de` | Which paper in the collection evaluates retrieval on chest X-ray radiology reports? |
| u04 | insufficient | `20261024T061244_09d4b73975` | How does GraphRAG build community summaries from a knowledge graph? |
| u05 | insufficient | `20261024T061244_d90e2d4a44` | What sourdough fermentation schedule is recommended for rye flour? |
| u06 | insufficient | `20261024T061244_b0511b7ada` | What Kubernetes autoscaling policy did the Walert team use for peak enrolment weeks? |
| u07 | insufficient | `20261024T061244_bba1c1c2c5` | What learning rate was used to fine-tune the RAGAS judge model? |
| n01 | source_linked_explanation | `20261024T061244_61cdf70f8c` | How large is RETRO's retrieval database? |
| n02 | source_linked_explanation | `20261024T061244_fcc3365c8e` | What does Contriever find works better than the inverse Cloze task? |
| n03 | source_linked_explanation | `20261024T061244_86dc48da8e` | How does ColBERTv2 reduce the space footprint of late interaction? |
| n04 | source_linked_explanation | `20261024T061244_bbc3420a27` | According to Lost in the Middle, where in the input context do language models use relevant information best? |
| n05 | source_linked_explanation | `20261024T061244_2c227bca00` | When does FLARE retrieve documents to regenerate a sentence? |
| n06 | source_linked_explanation | `20261024T061244_3628f4d920` | What component does CRAG use to assess the quality of retrieved documents? |
| n07 | source_linked_explanation | `20261024T061244_85d91a10e5` | How does REPLUG give retrieved documents to the language model? |
| n08 | source_linked_explanation | `20261024T061244_2dd0703b95` | How many datasets does the BEIR benchmark include? |
| n09 | source_linked_explanation | `20261024T061244_e0b9d8637b` | How does ANCE select hard training negatives? |
| n10 | source_linked_explanation | `20261024T061244_03d486fd4f` | How many training examples does Atlas need to reach over 42% accuracy on Natural Questions? |
| n11 | source_linked_explanation | `20261024T061244_fae824c7d4` | Which method retrieves from a database of 2 trillion tokens? |
| n12 | source_linked_explanation | `20261024T061244_0d175e7c50` | Which approach masks out low-confidence tokens before using a sentence as a retrieval query? |
| c01 | source_linked_explanation | `20261024T061244_bb1255f0ed` | How do RAGAS and ARES differ in how they score RAG systems? |
| c02 | source_linked_explanation | `20261024T061244_4ff21e9f2f` | How does ColBERTv2 improve on ColBERT? |
| c03 | source_linked_explanation | `20261024T061244_0d71d524eb` | How do Self-RAG and CRAG each judge whether retrieved documents are useful? |
| u08 | insufficient | `20261024T061244_7d59130abd` | How does ColPali retrieve documents from page images? |
| H01 | source_linked_explanation | `20261024T061244_c5d3f1c557` | How does ORQA train a retriever without labelled supporting passages, and what task does it use to pre-train that retriever? |
| H02 | source_linked_explanation | `20261024T061244_e676699ae7` | Under what circumstances can RECOMP leave out retrieved context entirely, and what does the compressor output? |
| H03 | source_linked_explanation | `20261024T061244_ccf9f10319` | In monoT5, how is a query–document pair turned into a numerical relevance score for ranking? |
| H04 | source_linked_explanation | `20261024T061244_1b1ab01432` | How is the small query rewriter trained in Rewrite-Retrieve-Read when the retriever and reader are frozen? |
| H05 | source_linked_explanation | `20261024T061244_0d4ac97873` | How do SPLADE and Contriever differ in their retrieval representations and learning approach? |
| H06 | source_linked_explanation | `20261024T061244_0cfea9d798` | How does monoBERT calculate a passage-relevance score compared with monoT5? |
| H07 | source_linked_explanation | `20261024T061244_a1b31a361e` | How do RECOMP and Fusion-in-Decoder (FiD) differ in what they do with retrieved passages before an answer is generated? |
| H08 | source_linked_explanation | `20261024T061244_a4c5942e5e` | How do Rewrite-Retrieve-Read and Demonstrate–Search–Predict (DSP) use language models to influence the search queries they send to retrieval? |
| H09 | source_linked_explanation | `20261024T061244_6ff3b017a5` | What exactly do BEIR and ARES evaluate, and how is their evaluation methodology different? |
| H10 | insufficient | `20261024T061244_f14f1cd3e3` | How many kilowatt-hours of electricity were required to train the final SPLADE ranking model? |
| H11 | insufficient | `20261024T061244_0e3ea3b34b` | What prompt-injection attack success rate did RECOMP report for malicious instructions embedded in retrieved passages? |
| H12 | insufficient | `20261024T061244_dd8cfee3a5` | What precise nDCG@10 difference between SPLADE and Contriever was measured on a shared Kannada legal-document retrieval benchmark? |
| F01 | source_linked_explanation | `20261024T061244_7c854fce11` | Why can Fusion-in-Decoder process more retrieved passages without making the encoder attend over all passages jointly? Explain where information from different passages is combined. |
| F02 | source_linked_explanation | `20261024T061244_7e93400145` | How does GTR make its query and passage encoders larger without increasing the size of the final retrieval embeddings? |
| F03 | source_linked_explanation | `20261024T061244_5a15a78c0e` | What does the FLOPS regularizer in SPLADE try to reduce, and what trade-off does it create between retrieval quality and efficiency? |
| F04 | source_linked_explanation | `20261024T061244_c609903f7a` | How does REPLUG combine language-model predictions when several different retrieved documents are relevant to the same question? |
| F05 | source_linked_explanation | `20261024T061244_753a6ffe87` | In In-Context RALM, what is retrieval stride? What changes when the system retrieves more frequently? |
| F06 | source_linked_explanation | `20261024T061244_4453aa1c29` | How does RAGAS estimate answer relevance without comparing the generated answer to a human-written reference answer? |
| F07 | source_linked_explanation | `20261024T061244_ca5c645480` | Why does Atlas jointly pre-train its retriever and reader, and how does its reader make use of multiple retrieved passages? |
| F08 | source_linked_explanation | `20261024T061244_8f154dedce` | When retrieved information is noisy, how do RECOMP and Corrective RAG (CRAG) differ in what they do before the model generates its answer? |
| F09 | source_linked_explanation | `20261024T061244_3fabdb74b4` | Compare RETRO and In-Context RALM: how is external retrieved text incorporated into language-model processing in each system? |
| F10 | source_linked_explanation | `20261024T061244_a6ceb3143b` | What different evaluation goals are served by BEIR and the LoTTE benchmark introduced with ColBERTv2? |
| F11 | source_linked_explanation | `20261024T061244_41e9e8f4af` | How do REPLUG and Fusion-in-Decoder combine information from multiple documents, and which method works with a frozen black-box language model? |
| F12 | insufficient | `20261024T061244_66e846c20d` | What measured p95 response latency did this Research Workbench achieve with 100 simultaneous users on an Apple M4 Mac? If no such measurement exists in the indexed collection, say so. |
| F13 | insufficient | `20261024T061244_fbda18791e` | What exact cost per 1,000 queries was measured for RECOMP running on AWS in Sydney in October 2026? Answer only if that deployment measurement is supported by a source. |
| F14 | insufficient | `20261024T061244_c3e301a36b` | Which paper in this 30-paper collection reports improved diabetic-retinopathy diagnosis accuracy from using ColBERTv2? Cite the experiment or state that the collection does not establish it. |
| F15 | insufficient | `20261024T061244_6b2af1558d` | Does the indexed research prove that deployed retrieval-augmented generation systems have zero hallucinations? Identify the supporting experiment and error count, or explain why that claim is unsupported. |

## Reproducibility identifiers

```json
{
  "uploaded_zip_sha256": "198e03ea30b613c73bc8b6d7f1d1f2bfd8624c87b413b73b44ff5215ca47cd15",
  "build_hashes": {
    "corpus": "b3ed27e2a3bca8d2b2d3d2961bb69cd5dac86529500a8ee3ce9798ae29815f57",
    "knowledge": "a3ce95a2eacc71571e7c37ac9a252003140614ad35f80ced8ce7f14279984b13",
    "code": "93743fd7df0f0b0907331b23f87f79ebe85dd8c6e834c9077d9c69d2de7a90e8"
  }
}
```
