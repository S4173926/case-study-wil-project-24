# WIL Project 24 — source-corpus verification and answer-audit handoff

**Review provenance:** AI-assisted technical analysis; not independent human adjudication. Documentation edition: 25 October 2026; original results retained.

**23 October 2026.** All work was performed on a separate copy of the Phase 1 project. The original ZIP, original question labels, and saved results were not modified.

## 1. Integrity: PASS

- Uploaded archive `source_pdfs_verified.zip` contains **30 PDFs**, a lockfile, and a manifest.
- The uploaded lockfile and manifest are **byte-identical** to those in the Phase 1 working copy.
- **30/30** PDF files match the recorded SHA-256 digest in the pinned lockfile. All 30 can be opened and read with PyMuPDF.
- The benchmark contains **40 questions**: 33 answerable, 7 unsupported. It has **48 recorded evidence passages**.
- With punctuation- and layout-tolerant text normalisation, **48/48** quoted passages appear in the indicated original PDFs. The exact PDF page numbers are recorded in `gold_evidence_source_locations.csv`.

**Methodological distinction:** an exact quote's *presence* in a PDF does not establish that the passage is sufficient evidence for a question, nor that a generated answer is correct. The initial strict matching produced 19/48 because hyphens, punctuation, ligatures and PDF text ordering introduced false negatives. The second match normalises alphanumeric text, while preserving paper ID and locating the exact contiguous word sequence. No gold label was silently changed.

## 2. Substantive errors found in archived answers

The `priority_cases.csv` file documents eight source-checked failures in the selected archived system. These are **examples**, not a statistically representative human-scored error rate.

| Question | Saved answer mode | What the original source shows | Problem with archived response |
|---|---|---|---|
| `n04` | Local LLM | *Lost in the Middle*, PDF p1, reports better use of evidence at the **beginning or end** of long contexts | Saved answer says **middle**; direct factual contradiction |
| `q10` | Local LLM | *Walert*, PDF p3, evaluated **BM25** and **DPR** retrievers | Saved answer names the separate **Intent-Based and RAG** chatbot approaches instead |
| `q15` | Local LLM | *RAG*, PDF p3, describes the retriever based on **DPR**; *Fusion-in-Decoder*, PDF p3, evaluates **BM25 and DPR** | Saved answer incorrectly attributes both to RAG and omits DPR from FiD |
| `q17` | Local LLM | *REALM*, PDF p1, proposes retriever pre-training with masked language modelling; *RAG*, PDF p3, initializes a DPR-based retriever and trains jointly | Saved answer confuses initialization and timing |
| `c01` | Local LLM | *RAGAS* and *ARES* differ in use of LLM-based reference-free evaluation versus fine-tuned judges with labeled calibration | Saved response gives ARES details, not a two-sided comparison |
| `q07` | Extractive | *RAGAS*, PDF p3, discusses faithfulness, answer relevance, and context relevance | Saved response talks about "three" aspects without naming them |
| `q03` | Extractive | *RAG*, PDF p3, distinguishes RAG-Sequence versus RAG-Token | Extracted mathematical fragments obscure rather than explain the difference |
| `c02` | Local LLM | *ColBERTv2*, PDF p1, describes residual compression and improved quality over ColBERT | Saved response does not provide the principal differentiating mechanism |

These observations corroborate the earlier warning that **correct-paper citation rate is not factual-answer correctness**. Overall answer accuracy was not independently established by this source-presence audit.

## 3. Files and purposes

- `verified_paper_inventory.csv`: every paper ID, exact version, hash status and PDF page count.
- `gold_evidence_source_locations.csv`: all 48 evidence labels with source PDFs and pages. Leave human judgments blank until adjudicated.
- `selected_answer_review_worklist.csv`: 80 existing answers (40 questions × extractive/LLM), alongside human-review fields. The old evaluation metrics are included for traceability, not treated as human validity scores.
- `priority_cases.csv`: source-checked examples to use in regression tests and report error analysis.
- `source_verification_summary.json`: machine-readable integrity summary.
- `verify_corpus_and_build_worklist.py`: repeatable verification script. Dependencies: PyMuPDF, Python 3.10+. Does not install or run the RAG model.

## 4. Limits of this audit

The source-presence audit establishes that the 48 labelled quotation strings can be located in the indicated PDFs after tolerant normalisation. It does not independently establish that each label is sufficient to answer its question, that every generated answer is correct, or that each originally reported extraction defect has been repaired. The eight source-checked answer failures are diagnostic examples, not a population-level accuracy estimate.

The reference-answer review worklist was unfilled at the time of this audit. Independent source-based answer ratings and validation on new questions would be distinct further studies. No such completed observations are represented by the source hashes or quotation-presence count.

Companion files named in the original audit are not part of the supplied evidence addendum; see the availability note in this directory's README. Their numerical contents have not been reconstructed for this edition.
