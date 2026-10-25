"""Evaluation against the labelled question set (eval/questions.jsonl).

Each question lists its expected supporting passages as short verbatim evidence quotes. A chunk is
*relevant* when it contains one of those quotes (after whitespace/case/hyphen normalisation), so the
ground truth is written once, before tuning, and stays valid whichever chunker is used.

Metrics
  recall@k          answerable Qs with >=1 relevant chunk in the top k
  mrr               mean reciprocal rank of the first relevant chunk
  paper_recall@k    share of expected papers represented in the top k (matters for comparisons)
  citation_precision share of cited chunks that come from an expected paper
  citation_support  share of cited chunks that actually contain expected evidence
  faithfulness      share of answer sentences whose content words are covered by their cited chunk
  abstain_correct   unsupported Qs correctly flagged ("insufficient evidence")
  false_abstain     answerable Qs wrongly refused
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

from .chunking import Chunk
from .generate import Answer
from .retrieval import tokenize


def norm(text: str) -> str:
    text = text.lower().replace("‐", "-").replace("–", "-").replace("ﬁ", "fi").replace("ﬂ", "fl")
    text = re.sub(r"-\s+", "-", text)
    return re.sub(r"[^a-z0-9%.\-]+", " ", text).strip()


def load_questions(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def is_relevant(chunk: Chunk, q: dict) -> bool:
    t = norm(chunk.text)
    return any(ev["paper"] == chunk.paper_id and norm(ev["quote"]) in t for ev in q.get("evidence", []))


def validate_ground_truth(questions: list[dict], docs: list[dict]) -> list[str]:
    """Every evidence quote must exist in the ingested text of its paper. Run after every ingestion change."""
    text = {d["paper_id"]: norm(" ".join(s["text"] for s in d["sections"])) for d in docs}
    problems = []
    for q in questions:
        for ev in q.get("evidence", []):
            if ev["paper"] not in text:
                problems.append(f"{q['id']}: paper {ev['paper']!r} not in corpus")
            elif norm(ev["quote"]) not in text[ev["paper"]]:
                problems.append(f"{q['id']}: quote not found in {ev['paper']}: {ev['quote']!r}")
    return problems


def faithful(sentence: str, cited: list[Chunk], threshold: float = 0.6) -> bool:
    words = set(tokenize(re.sub(r"\[[^\]]+\]", "", sentence)))
    if not words or not cited:
        return False
    ctx = set(t for c in cited for t in tokenize(c.text))
    return len(words & ctx) / len(words) >= threshold


@dataclass
class QResult:
    qid: str
    qtype: str
    retrieved: list[str]
    first_relevant_rank: int | None
    papers_hit: float
    answer: str
    abstained: bool
    citation_precision: float | None
    citation_support: float | None
    faithfulness: float | None
    error: str


def score_question(q: dict, retrieved: list[Chunk], ans: Answer, by_id: dict[str, Chunk]) -> QResult:
    unsupported = q["type"] == "unsupported"
    rel_ranks = [i + 1 for i, c in enumerate(retrieved) if is_relevant(c, q)]
    first = rel_ranks[0] if rel_ranks else None
    expected = set(q.get("expected_papers", []))
    papers_hit = len(expected & {c.paper_id for c in retrieved}) / len(expected) if expected else 0.0

    cp = cs = fa = None
    if not ans.abstained and ans.sentences:
        cited = [by_id[c] for c in ans.citations if c in by_id]
        if cited:
            cp = sum(c.paper_id in expected for c in cited) / len(cited)
            cs = sum(is_relevant(c, q) for c in cited) / len(cited)
        fa = sum(faithful(s, [by_id[c] for c in cs_ if c in by_id]) for s, cs_ in ans.sentences) / len(ans.sentences)

    # Error taxonomy used in the error-analysis table
    if unsupported:
        error = "" if ans.abstained else "answered_unsupported"
    elif ans.abstained:
        error = "false_abstain" if first else "retrieval_miss+abstain"
    elif first is None:
        error = "retrieval_miss"
    elif cp is not None and cp < 1.0:
        error = "wrong_paper_cited"
    elif fa is not None and fa < 1.0:
        error = "unfaithful_sentence"
    elif papers_hit < 1.0:
        error = "comparison_incomplete"
    else:
        error = ""
    return QResult(q["id"], q["type"], [c.chunk_id for c in retrieved], first, papers_hit,
                   ans.text, ans.abstained, cp, cs, fa, error)


def aggregate(results: list[QResult], k: int) -> dict:
    ans = [r for r in results if r.qtype != "unsupported"]
    uns = [r for r in results if r.qtype == "unsupported"]

    def mean(xs):
        xs = [x for x in xs if x is not None]
        return round(sum(xs) / len(xs), 3) if xs else None

    return {
        f"recall@{k}": mean([r.first_relevant_rank is not None for r in ans]),
        "mrr": mean([1 / r.first_relevant_rank if r.first_relevant_rank else 0 for r in ans]),
        f"paper_recall@{k}": mean([r.papers_hit for r in ans]),
        "citation_precision": mean([r.citation_precision for r in ans]),
        "citation_support": mean([r.citation_support for r in ans]),
        "faithfulness": mean([r.faithfulness for r in ans]),
        "abstain_correct": mean([r.abstained for r in uns]),
        "false_abstain": mean([r.abstained for r in ans]),
        "n_answerable": len(ans),
        "n_unsupported": len(uns),
    }
