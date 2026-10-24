"""Connect retrieved context to an answer, with per-sentence citations and abstention.

Two generators share one output shape (Answer):
  ExtractiveGenerator - offline, deterministic: selects the best-supported sentences from the
                        retrieved chunks. Faithful by construction, so it isolates *retrieval* and
                        *abstention* quality from LLM behaviour.
  RemoteGenerator     - A configured remote model answers from the same passages and must cite a chunk id
                        per claim or reply INSUFFICIENT_EVIDENCE.

Abstention gate (both generators): if the retrieved chunks do not cover enough of the question's
informative (IDF-weighted) terms, answer "insufficient evidence" instead of guessing.
"""
from __future__ import annotations

import math
import os
import re
from collections import Counter
from dataclasses import dataclass, field

from .chunking import Chunk
from .retrieval import tokenize

CITE_RE = re.compile(r"\[([a-z0-9_\-]+:\d+)\]")
ABSTAIN = "INSUFFICIENT_EVIDENCE"
# Words that carry no evidence in a question ("which paper uses ...") and would dilute coverage.
QUESTION_WORDS = {"doe", "do", "did", "use", "us", "paper", "work", "according", "approach", "describe", "differ",
                  "difference", "compare", "compar", "collection", "kind", "way"}


@dataclass
class Answer:
    text: str
    abstained: bool
    sentences: list[tuple[str, list[str]]] = field(default_factory=list)  # (sentence, cited chunk ids)
    coverage: float = 0.0

    @property
    def citations(self) -> list[str]:
        return sorted({c for _, cs in self.sentences for c in cs})


class Idf:
    def __init__(self, chunks: list[Chunk]):
        df = Counter(t for c in chunks for t in set(tokenize(c.text)))
        n = len(chunks)
        self.idf = {t: math.log((n + 1) / (d + 0.5)) for t, d in df.items()}
        self.unknown = math.log(n + 1) * 1.5  # a term absent from the corpus is highly informative

    def __call__(self, t: str) -> float:
        return self.idf.get(t, self.unknown)


def coverage(question: str, chunks: list[Chunk], idf: Idf) -> float:
    """IDF-weighted share of question terms that appear in the retrieved chunks."""
    q = set(tokenize(question)) - QUESTION_WORDS
    if not q:
        return 0.0
    ctx = set(t for c in chunks for t in tokenize(c.text))
    return sum(idf(t) for t in q & ctx) / sum(idf(t) for t in q)


def split_sentences(text: str) -> list[str]:
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if len(s.split()) >= 4]


class ExtractiveGenerator:
    name = "extractive"

    def __init__(self, idf: Idf, tau: float = 0.6, max_sentences: int = 3):
        self.idf, self.tau, self.max_sentences = idf, tau, max_sentences

    def answer(self, question: str, retrieved: list[Chunk]) -> Answer:
        cov = coverage(question, retrieved, self.idf)
        if cov < self.tau:
            return Answer(ABSTAIN, True, [], cov)
        q = set(tokenize(question))
        cands = []
        for rank, c in enumerate(retrieved):
            for s in split_sentences(c.text):
                overlap = sum(self.idf(t) for t in q & set(tokenize(s)))
                cands.append((overlap / (1 + 0.1 * rank), s, c))
        cands.sort(key=lambda x: -x[0])
        picked, papers_used, seen = [], Counter(), set()
        for score, s, c in cands:
            if score <= 0 or len(picked) >= self.max_sentences:
                break
            # skip repeats (chunk overlap) and leave room for other papers in comparison questions
            if s in seen or papers_used[c.paper_id] >= 2:
                continue
            seen.add(s)
            picked.append((s, [c.chunk_id]))
            papers_used[c.paper_id] += 1
        if not picked:
            return Answer(ABSTAIN, True, [], cov)
        text = " ".join(f"{s} [{cid[0]}]" for s, cid in picked)
        return Answer(text, False, picked, cov)


SYSTEM_PROMPT = """You are a research assistant answering questions about a fixed collection of academic papers.
Use ONLY the numbered passages provided in the user message. Each passage is labelled with a chunk id such as [dpr:12] and the paper it comes from.

Rules:
- End every sentence of your answer with the chunk id(s) that support it, e.g. "... in-batch negatives [dpr:12]."
- Attribute each method, number or formula to the paper whose passage states it. Never merge details from two papers into one claim.
- For comparison questions, state each paper's approach separately with its own citation.
- If the passages do not contain the information needed, reply with exactly: INSUFFICIENT_EVIDENCE
- Be concise: at most 4 sentences."""


class RemoteGenerator:
    name = "remote"

    def __init__(self, idf: Idf, tau: float = 0.6, model: str | None = None):
        model = (model if model is not None else os.environ.get("RRA_REMOTE_MODEL", "")).strip()
        if not model:
            raise ValueError(
                "Set RRA_REMOTE_MODEL to a supported model identifier before using "
                "--generator remote, or use the default extractive generator."
            )
        try:
            import anthropic  # optional dependency used only by the remote backend
        except ImportError as exc:
            raise RuntimeError(
                "The remote backend requires the optional anthropic package. "
                "Install it or use the default extractive generator."
            ) from exc

        self.client = anthropic.Anthropic()
        self.idf, self.tau, self.model = idf, tau, model

    def answer(self, question: str, retrieved: list[Chunk]) -> Answer:
        cov = coverage(question, retrieved, self.idf)
        if cov < self.tau:
            return Answer(ABSTAIN, True, [], cov)
        passages = "\n\n".join(
            f"[{c.chunk_id}] (paper: {c.paper_id}, section: {c.section}, page {c.page})\n{c.text}" for c in retrieved
        )
        response = self.client.beta.messages.create(
            model=self.model,
            max_tokens=16000,
            output_config={"effort": "medium"},
            betas=["server-side-fallback-2026-07-01"],
            fallbacks="default",
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": f"<passages>\n{passages}\n</passages>\n\nQuestion: {question}"}],
        )
        if response.stop_reason == "refusal":
            return Answer(ABSTAIN, True, [], cov)
        text = "".join(b.text for b in response.content if b.type == "text").strip()
        if ABSTAIN in text:
            return Answer(ABSTAIN, True, [], cov)
        valid = {c.chunk_id for c in retrieved}
        sentences = [(s, [c for c in CITE_RE.findall(s) if c in valid]) for s in re.split(r"(?<=[.!?\]])\s+", text) if s]
        return Answer(text, False, sentences, cov)
