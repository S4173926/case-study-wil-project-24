"""Chunking strategies compared in the experiments.

fixed    - N-word windows with overlap over the whole paper, ignoring structure (the naive baseline)
sentence - sentences packed up to N words, one-sentence overlap, never crossing a section
section  - like `sentence`, but every chunk is prefixed with its section heading and paper title,
           so a chunk about "the retriever" still says *which* paper's retriever it is
"""
from __future__ import annotations

import re
from dataclasses import dataclass

from .ingest import page_at

SENT_RE = re.compile(r"(?<=[.!?])\s+(?=[A-Z(\[])")


@dataclass
class Chunk:
    chunk_id: str
    paper_id: str
    section: str
    page: int
    text: str          # text shown to the generator and used for evidence matching
    index_text: str    # text the retriever indexes (may carry extra context)


def _sentences(text: str) -> list[tuple[int, str]]:
    out, pos = [], 0
    for s in SENT_RE.split(text):
        start = text.find(s, pos)
        out.append((start, s))
        pos = start + len(s)
    return out


def fixed(docs: list[dict], words: int = 200, overlap: int = 50) -> list[Chunk]:
    chunks = []
    for d in docs:
        toks = []  # (word, section, page)
        for s in d["sections"]:
            for m in re.finditer(r"\S+", s["text"]):
                toks.append((m.group(), s["heading"], page_at(s, m.start())))
        step = max(words - overlap, 1)
        for i, start in enumerate(range(0, max(len(toks) - overlap, 1), step)):
            win = toks[start:start + words]
            text = " ".join(w for w, _, _ in win)
            chunks.append(Chunk(f"{d['paper_id']}:{i}", d["paper_id"], win[0][1], win[0][2], text, text))
    return chunks


def _make(d: dict, s: dict, cur: list[tuple[int, str]], i: int, with_context: bool) -> Chunk:
    text = " ".join(t for _, t in cur)
    ctx = f"{d['title']} | {s['heading']} | {text}" if with_context else text
    return Chunk(f"{d['paper_id']}:{i}", d["paper_id"], s["heading"], page_at(s, cur[0][0]), text, ctx)


def sentence(docs: list[dict], max_words: int = 150, with_context: bool = False) -> list[Chunk]:
    chunks = []
    for d in docs:
        i = 0
        for s in d["sections"]:
            sents = _sentences(s["text"])
            cur: list[tuple[int, str]] = []
            n = unflushed = 0
            for off, sent in sents:
                w = len(sent.split())
                if unflushed and n + w > max_words:
                    chunks.append(_make(d, s, cur, i, with_context))
                    i += 1
                    cur, n, unflushed = cur[-1:], len(cur[-1][1].split()), 0  # one-sentence overlap
                cur.append((off, sent))
                n += w
                unflushed += 1
            if unflushed:
                chunks.append(_make(d, s, cur, i, with_context))
                i += 1
    return chunks


def section(docs: list[dict], max_words: int = 150) -> list[Chunk]:
    return sentence(docs, max_words=max_words, with_context=True)


STRATEGIES = {
    "fixed-200": lambda d: fixed(d, 200, 50),
    "fixed-400": lambda d: fixed(d, 400, 100),
    "sentence-150": lambda d: sentence(d, 150),
    "section-150": lambda d: section(d, 150),
}
