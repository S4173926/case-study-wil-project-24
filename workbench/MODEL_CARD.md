# Research Workbench system card

## Purpose and intended users

Support students and researchers who need to inspect and compare methods within a fixed collection of 30 information-retrieval and retrieval-augmented-generation papers. The tool is not an exhaustive literature search service or a factual-certification service.

## Default method

Named-paper matching and clause/facet planning select reusable, paper-specific claims from a fixed catalogue. A TF-IDF claim index ranks the candidates. Composition reuses existing claim text, retaining its source identifiers and pages. Unsupported requested details are reported rather than invented. Original-source search separately provides BM25, TF-IDF and their reciprocal-rank fusion over the same passages.

The source-search selector does not change the claim-index scoring rule. The interface labels this distinction. The optional existing local Qwen model can select allowed claim IDs; it cannot write new factual sentences in this output path. The historical RAG prototypes and this constrained alternative use different answering mechanisms.

## Provenance

The catalogue contains 99 language-model-drafted claim units that received source-based development checks. Exact supporting spans and paper hashes are mechanically checked. Independent source-review status remains pending in the catalogue. Real user ratings, when entered, are separately recorded against individual run IDs. They do not silently change catalogue-level review status.

## Evaluation

All 67 previously used questions are development/regression cases. The 15 later challenge questions became development material when their failures informed the selection repair. The runtime does not load answer keys, but that separation does not remove prior development exposure. Availability, citation-ID validity, source coverage, factual correctness and completeness are distinct measures.

## Limits

The finite catalogue can omit details present in the underlying PDFs. Lexical planning can misunderstand complicated questions, negation or unnamed references. Correctly selected statements can still be incomplete. The remaining HyDE case is explicitly partial because this catalogue uses a secondary survey rather than an independently indexed original HyDE paper. Source extraction can distort equations and reading order; original PDFs remain the authority.

Software tests do not establish independent answer accuracy, participant benefit or production load performance. The optional Apple-silicon model path was not run in the finalisation environment. The default deterministic engine was executed.

## Version and storage

Release 1.2 retains the repaired answering logic and factual catalogue, changing review usability and application wording. Previous runs retain original hashes, timestamps and raw contents. The default review selector recognises the exact verified repaired hash tuple. Other historical versions remain accessible with a warning.

The server is local-only with restricted routes, escaped rendered content and a same-origin write token. These controls and their tests are not a comprehensive independent security audit. Project records and local observations retain their recorded provenance and review status.
