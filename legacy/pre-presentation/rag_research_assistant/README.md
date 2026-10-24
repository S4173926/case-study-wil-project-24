# Source-grounded RAG research assistant: evaluation prototype

A small, end-to-end version of the project plan. It lets a team **compare methods across a
curated set of open-access papers** and **measure** how often the assistant retrieves the right
passage, cites the right paper, stays faithful to its sources, and declines questions the corpus
cannot answer.

```
corpus/manifest.json ──fetch──▶ corpus/pdfs + corpus.lock.json   (pinned: arXiv version + SHA-256)
        │
     ingest   two-column reordering, header/footer + reference removal, hyphen repair,
        │     per-page quality flags (symbol-heavy / near-empty pages → inspect before indexing)
        ▼
data/processed/*.json ──chunk──▶ fixed-200 | fixed-400 | sentence-150 | section-150
                          │
                     retrieve    bm25 | tfidf | dense | hybrid (RRF)
                          │
                     generate    extractive (offline) | remote model, with [paper:chunk] citations
                          │      + abstention gate: "INSUFFICIENT_EVIDENCE"
                          ▼
eval/questions.jsonl ──evaluate──▶ results/latest.json ──report──▶ results/report.html
```

## Corpus (8 arXiv papers on retrieval-augmented QA)

| id | paper | why it's in the set |
|---|---|---|
| walert | Walert (arXiv 2401.07216) | the baseline system to reproduce |
| rag | Lewis et al., Retrieval-Augmented Generation (2005.11401) | the RAG model |
| dpr | Karpukhin et al., Dense Passage Retrieval (2004.04906) | dense bi-encoder retriever |
| colbert | Khattab & Zaharia, ColBERT (2004.12832) | late-interaction retriever |
| fid | Izacard & Grave, Fusion-in-Decoder (2007.01282) | reader over many passages |
| realm | Guu et al., REALM (2002.08909) | retrieval-augmented pre-training |
| ragas | Es et al., RAGAS (2309.15217) | RAG evaluation metrics |
| selfrag | Asai et al., Self-RAG (2310.11511) | adaptive retrieval and self-critique |

These papers share a lot of vocabulary (retriever, passages, dense, BM25, Wikipedia). That's
deliberate: it creates the risk the project is about, where a method or number gets attributed
to the wrong paper. `fetch` checks every arXiv ID against the expected title before downloading.

## First results (corpus `17baac618aa0`, 17 answerable + 7 unsupported questions, k = 5)

| | Walert-style baseline `fixed-200/bm25` | best `fixed-400/hybrid+route` |
|---|---|---|
| Recall@5 | 0.59 | **0.71** |
| MRR | **0.42** | 0.32 |
| Paper recall@5 | 0.97 | **1.00** |
| Citation precision (right paper cited) | 0.81 | **1.00** |
| Unsupported questions flagged | 6 / 7 | **7 / 7** |
| Answerable questions wrongly refused | 1 / 17 | 1 / 17 |

"Best" is chosen by recall@k + citation precision + unsupported flagged − false abstain. Selecting by MRR
alone picks `fixed-400/tfidf`, which answers 3 of the 7 unsupported questions. The full grid and every
per-question answer are in `results/report.html`.

What the error analysis showed:

* **Wrong-paper retrieval was the main failure.** For *"Which retrieval models did **Walert** use…"*
  the RAG paper's chunks outranked Walert's, because "retrieval" and "RAG" appear in every paper and
  outweigh the paper name. Comparison questions often retrieved only one of their two papers. The fix
  is `+route`, which shares the top-k slots among the papers a question names (see
  `retrieval.PaperRouter`). It raised citation precision to 1.00 for every chunker. **Caveat:** the fix
  was designed after seeing failures on this same question set, so confirm it on a held-out set before
  claiming the gain.
* **The dense model (MiniLM) alone is the weakest retriever here** (Recall@5 0.35–0.47). A
  general-purpose sentence encoder struggles to tell apart papers that share one vocabulary. BM25
  and hybrid do better.
* **Bigger chunks inflate recall.** `fixed-400` makes about 170 chunks versus about 490 for
  `sentence-150`, so each chunk is more likely to contain a quote. Compare chunkers at equal
  context budget (k × chunk size) before choosing one.
* **Remaining misses are mostly vocabulary mismatch.** *"out-of-knowledge-base questions"* vs
  *"out of KB"*, and *"quality aspects"* vs *"Faithfulness refers to…"*. Query expansion or a
  stronger/fine-tuned dense encoder is the next thing to try.
* **Extraction issues found and fixed during ingestion:** section numbers set as separate lines,
  author affiliations detected as section headings ("3 Inria, Paris"), a centred abstract read after
  the introduction, figure labels ("MaxSim MaxSim MaxSim") and footnote URLs inserted mid-sentence.
  Still open: garbled equations (DPR's loss), a font that drops the "u" in "Query" (ColBERT prints
  "Qery"), and "dual-encoder" joined to "dualencoder" by the hyphen repair.
* **Citation support is low (0.16–0.25)** even when retrieval succeeds. The extractive generator picks
  the sentence that overlaps the question most, which is often not the evidence sentence. That is the
  gap an LLM generator (`--generator remote`) should close. Measure it before relying on it.

## Run it

```bash
pip install -r requirements.txt
python -m rra.cli fetch        # needs access to arxiv.org / export.arxiv.org
python -m rra.cli ingest       # prints chars / sections / pages flagged for review per paper
python -m rra.cli validate     # every ground-truth quote must exist in the ingested text
python -m rra.cli experiment   # 4 chunkers x 4 retrievers + abstention-threshold sweep
python -m rra.cli report       # open results/report.html
python -m rra.cli ask "How does ColBERT score a passage?" --config section-150/hybrid
python -m rra.cli experiment --generator remote --configs fixed-200/bm25 fixed-400/hybrid+route   # needs ANTHROPIC_API_KEY and RRA_REMOTE_MODEL
python -m pytest -q            # pipeline tests on synthetic PDFs (no network needed)
```

### Optional remote generation

The default extractive generator runs offline. The optional `--generator remote` backend
retains the existing provider SDK and request format. Configure `ANTHROPIC_API_KEY` and
`RRA_REMOTE_MODEL` in your own environment; never commit access credentials. The model
identifier must be supported by that provider. No model identifier is hard-coded in this
working copy. The recorded September results remain extractive results; this cleanup does
not validate a remote model or change those historical measurements.

### Presentation source

The existing PowerPoint remains unchanged. To rebuild it, install the JavaScript dependencies
listed in `presentation/BUILD.md` and run `node build.js` from the presentation directory.
The theme helper and theme XML now live beside the build script, so no private absolute path
is required.

## Ground truth (`eval/questions.jsonl`)

24 questions, written **before** tuning:

* 13 single-paper questions (3 about Walert), e.g. *"What training negatives does DPR use?"*
* 4 cross-paper comparisons, e.g. *"How do DPR and ColBERT differ in how they encode queries and passages?"*
* 7 unsupported questions that the system should decline (topics outside the corpus, or details
  the papers don't report)

Each answerable question lists its **expected papers** and one or more **short verbatim evidence
quotes**. Any chunk that contains a quote counts as relevant, so the labels still work when you
change the chunker. `validate` stops a run if a quote no longer appears in the ingested text. That
catches PDF-extraction regressions, and it also catches ground-truth entries that were wrong to
begin with. The current quotes were copied from the ingested text and all validate against corpus
`17baac618aa0`.

## Metrics

| metric | question it answers |
|---|---|
| Recall@k, MRR | Did retrieval surface a passage that actually contains the evidence? How high did it rank? |
| Paper recall@k | For comparison questions, were **all** the papers involved retrieved? |
| Citation precision | Share of cited chunks that come from a paper the question is about (wrong-paper attribution) |
| Citation support | Share of cited chunks that contain the expected evidence |
| Faithfulness | Share of answer sentences whose content words appear in the chunk they cite (a lexical proxy; swap in an NLI model or an LLM judge later) |
| Unsupported flagged / false abstain | The trade-off for declining to answer, swept over the threshold τ in the report |

Every failure gets one error label: `retrieval_miss`, `wrong_paper_cited`,
`unfaithful_sentence`, `comparison_incomplete`, `false_abstain`, or `answered_unsupported`. The
report shows how many of each the baseline and the best configuration produce. That table is the
starting point for error analysis.

## Design notes

* **Baseline** `fixed-200/bm25` follows Walert's RAG setup as its paper describes it: passage
  retrieval with Okapi BM25 (k1 = 1.2, b = 0.75; Walert also tried DPR) and top-k up to 5. Walert
  indexed a FAQ knowledge base, not papers, so this is Walert-*style*. Once the team has reproduced
  Walert itself, match its settings here and keep the name.
* **The extractive generator** copies retrieved sentences. That makes it faithful by construction,
  so retrieval and abstention can be measured without LLM variance. Switch to `--generator remote`
  to measure generation. The configured remote model gets the same passages and must cite a chunk id per sentence or
  reply `INSUFFICIENT_EVIDENCE`.
* **Dense retrieval** uses `sentence-transformers` if it's installed. Otherwise it falls back to
  an offline LSA embedding. The report shows which one ran.
* **Traceability:** every run is saved as `results/run-<timestamp>.json`, stamped with the corpus
  version and a hash of the question file. Two runs are only comparable if both stamps match.
