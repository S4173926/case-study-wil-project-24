"""Command line entry point.

    python -m rra.cli fetch                  # download + pin the corpus (needs arxiv.org)
    python -m rra.cli ingest                 # PDF -> data/processed/*.json + quality report
    python -m rra.cli validate               # check every ground-truth quote exists in the ingested text
    python -m rra.cli experiment             # chunking x retrieval grid + abstention sweep -> results/
    python -m rra.cli experiment --generator remote --configs section-150/hybrid
    python -m rra.cli ask "How does ColBERT score a passage?"
    python -m rra.cli report                 # results/report.html
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from dataclasses import asdict
from pathlib import Path

from . import chunking, evaluate, fetch, generate, ingest, retrieval

ROOT = Path(__file__).resolve().parent.parent
PDFS = ROOT / "corpus" / "pdfs"
PROCESSED = ROOT / "data" / "processed"
QUESTIONS = ROOT / "eval" / "questions.jsonl"
RESULTS = ROOT / "results"
BASELINE = "fixed-200/bm25"  # Walert-style: passage windows + Okapi BM25 (k1=1.2, b=0.75), no document structure


SELECTION_RULE = "recall@k + citation precision + unsupported flagged - false abstain (tie-break: MRR)"


def selection_score(m: dict, k: int) -> float:
    """The project's priorities: find the evidence, cite the right paper, and don't answer without evidence."""
    return (m[f"recall@{k}"] or 0) + (m["citation_precision"] or 0) + (m["abstain_correct"] or 0) - (m["false_abstain"] or 0)


def make_generator(name: str, chunks, tau: float):
    idf = generate.Idf(chunks)
    if name == "remote":
        return generate.RemoteGenerator(idf, tau)
    return generate.ExtractiveGenerator(idf, tau)


def run_config(docs, questions, chunker: str, retr: str, gen: str, k: int, tau: float) -> dict:
    chunks = chunking.STRATEGIES[chunker](docs)
    by_id = {c.chunk_id: c for c in chunks}
    r = retrieval.build(retr, chunks)
    g = make_generator(gen, chunks, tau)
    results = []
    for q in questions:
        top = [c for c, _ in r.search(q["question"], k)]
        results.append(evaluate.score_question(q, top, g.answer(q["question"], top), by_id))
    return {"config": f"{chunker}/{retr}", "chunker": chunker, "retriever": r.name, "generator": g.name,
            "k": k, "tau": tau, "n_chunks": len(chunks),
            "metrics": evaluate.aggregate(results, k), "questions": [asdict(x) for x in results]}


def cmd_experiment(args):
    docs = ingest.load_docs(PROCESSED)
    questions = evaluate.load_questions(QUESTIONS)
    problems = evaluate.validate_ground_truth(questions, docs)
    if problems and not args.allow_invalid_gt:
        print("Ground truth does not match the ingested corpus (fix questions or ingestion first):")
        print("\n".join("  " + p for p in problems))
        sys.exit(1)

    configs = args.configs or [f"{c}/{r}" for c in chunking.STRATEGIES for r in retrieval.RETRIEVERS]
    runs = []
    for cfg in configs:
        c, r = cfg.split("/")
        run = run_config(docs, questions, c, r, args.generator, args.k, args.tau)
        runs.append(run)
        m = run["metrics"]
        print(f"{cfg:22s} R@{args.k}={m[f'recall@{args.k}']:.2f} MRR={m['mrr']:.2f} "
              f"cite={m['citation_precision']} faith={m['faithfulness']} "
              f"abstain_ok={m['abstain_correct']} false_abstain={m['false_abstain']}")

    best = max(runs, key=lambda x: (selection_score(x["metrics"], args.k), x["metrics"]["mrr"]))
    c, r = best["config"].split("/")
    sweep = []
    for tau in [0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]:
        m = run_config(docs, questions, c, r, "extractive", args.k, tau)["metrics"]
        sweep.append({"tau": tau, "abstain_correct": m["abstain_correct"], "false_abstain": m["false_abstain"]})

    out = {
        "run_id": time.strftime("%Y%m%d-%H%M%S"),
        "corpus_version": fetch.corpus_version(),
        "questions_sha": hashlib.sha256(QUESTIONS.read_bytes()).hexdigest()[:12],
        "baseline": BASELINE, "best": best["config"], "k": args.k, "selection_rule": SELECTION_RULE,
        "ground_truth_problems": problems,
        "runs": runs, "tau_sweep": {"config": best["config"], "points": sweep},
    }
    RESULTS.mkdir(exist_ok=True)
    (RESULTS / f"run-{out['run_id']}.json").write_text(json.dumps(out, indent=1))
    (RESULTS / "latest.json").write_text(json.dumps(out, indent=1))
    print(f"best={best['config']}  saved results/run-{out['run_id']}.json")


def cmd_ask(args):
    docs = ingest.load_docs(PROCESSED)
    c, r = args.config.split("/")
    chunks = chunking.STRATEGIES[c](docs)
    top = [ch for ch, _ in retrieval.build(r, chunks).search(args.question, args.k)]
    ans = make_generator(args.generator, chunks, args.tau).answer(args.question, top)
    print(ans.text, f"\n\n(evidence coverage {ans.coverage:.2f})")
    for ch in top:
        print(f"  [{ch.chunk_id}] p.{ch.page} {ch.section[:40]!r}: {ch.text[:110]}...")


def main(argv=None):
    p = argparse.ArgumentParser(prog="rra")
    sub = p.add_subparsers(dest="cmd", required=True)
    f = sub.add_parser("fetch")
    f.add_argument("--force", action="store_true")
    sub.add_parser("ingest")
    sub.add_parser("validate")
    e = sub.add_parser("experiment")
    e.add_argument("--configs", nargs="*")
    e.add_argument("--generator", default="extractive", choices=["extractive", "remote"])
    e.add_argument("--k", type=int, default=5)
    e.add_argument("--tau", type=float, default=0.6)
    e.add_argument("--allow-invalid-gt", action="store_true")
    a = sub.add_parser("ask")
    a.add_argument("question")
    a.add_argument("--config", default="section-150/hybrid")
    a.add_argument("--generator", default="extractive", choices=["extractive", "remote"])
    a.add_argument("--k", type=int, default=5)
    a.add_argument("--tau", type=float, default=0.6)
    sub.add_parser("report")
    args = p.parse_args(argv)

    if args.cmd == "fetch":
        fetch.fetch(args.force)
    elif args.cmd == "ingest":
        ingest.ingest_all(PDFS, PROCESSED, fetch.paper_titles())
    elif args.cmd == "validate":
        problems = evaluate.validate_ground_truth(evaluate.load_questions(QUESTIONS), ingest.load_docs(PROCESSED))
        print("\n".join(problems) or "all evidence quotes found in the ingested corpus")
        sys.exit(1 if problems else 0)
    elif args.cmd == "experiment":
        cmd_experiment(args)
    elif args.cmd == "ask":
        cmd_ask(args)
    elif args.cmd == "report":
        from .report import write_report
        print(write_report(json.loads((RESULTS / "latest.json").read_text()), RESULTS / "report.html"))


if __name__ == "__main__":
    main()
