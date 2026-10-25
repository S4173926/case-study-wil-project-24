"""Connect retrieved context to an answer, with per-sentence citations and abstention.

Two generators share one output shape (Answer):
  ExtractiveGenerator - offline, deterministic: selects the best-supported sentences from the
                        retrieved chunks. Faithful by construction, so it isolates *retrieval* and
                        *abstention* quality from LLM behaviour.
  ClaudeGenerator     - Claude writes the answer from the same passages and must cite a chunk id
                        per claim or reply INSUFFICIENT_EVIDENCE.

Abstention gate (both generators): if the retrieved chunks do not cover enough of the question's
informative (IDF-weighted) terms, answer "insufficient evidence" instead of guessing.
"""
from __future__ import annotations

import math
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


def is_prose(sentence: str) -> bool:
    """Reject text that is not a usable answer sentence: author/affiliation blocks, emails,
    figure and table captions, and runs of numbers from tables or plots."""
    words = sentence.split()
    if not 6 <= len(words) <= 70:
        return False
    if "@" in sentence or re.match(r"^(Figure|Fig\.|Table)\s*\d", sentence):
        return False
    if re.search(r"\b(Figure|Table)\s+\d+\s*:", sentence):
        return False
    numeric = sum(bool(re.fullmatch(r"[\d.,%()±×\-]+", w)) for w in words)
    if numeric / len(words) > 0.2:
        return False
    capitalised = sum(w[:1].isupper() for w in words)
    if capitalised / len(words) > 0.6:  # name lists such as "Gautier Izacard, Mathilde Caron, ..."
        return False
    return True


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
            for s in filter(is_prose, split_sentences(c.text)):
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


class ClaudeGenerator:
    name = "claude"

    def __init__(self, idf: Idf, tau: float = 0.6, model: str = "claude-opus-5-5"):
        import anthropic  # optional dependency

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


LOCAL_MODEL = "Qwen/Qwen2.5-0.5B-Instruct"  # small enough for CPU and Streamlit Community Cloud
LOCAL_PROMPT = """Answer the question using ONLY the passages below. Each passage starts with its id in square brackets.
Write at most 3 short sentences. End each sentence with the id of the passage it comes from, for example [dpr:12].
Keep each paper's details separate. If the passages do not answer the question, reply exactly: INSUFFICIENT_EVIDENCE"""


def attribute(sentence: str, retrieved: list[Chunk], min_overlap: float = 0.5) -> list[str]:
    """Post-hoc citation: the retrieved chunk sharing the most content words with the sentence.
    Returns [] when no chunk covers at least `min_overlap` of the sentence's words (left uncited)."""
    words = set(tokenize(sentence))
    if not words:
        return []
    best = max(retrieved, key=lambda c: len(words & set(tokenize(c.text))))
    return [best.chunk_id] if len(words & set(tokenize(best.text))) / len(words) >= min_overlap else []


def load_local_model(model: str | None = None):
    """(tokenizer, model, name) for a Hugging Face instruction model. Environment overrides:
    RRA_LOCAL_MODEL (e.g. Qwen/Qwen2.5-1.5B-Instruct for better answers with more memory) and
    RRA_LOCAL_DTYPE (float32 or bfloat16)."""
    import os

    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    name = model or os.environ.get("RRA_LOCAL_MODEL", LOCAL_MODEL)
    # RRA_LOCAL_DTYPE=bfloat16 halves memory (about 1 GB for the 0.5B model) at some CPU speed cost
    dtype = getattr(torch, os.environ.get("RRA_LOCAL_DTYPE", "float32"))
    tok = AutoTokenizer.from_pretrained(name)
    m = AutoModelForCausalLM.from_pretrained(name, dtype=dtype)
    m.eval()
    return tok, m, name


class LocalLLMGenerator:
    """Open-source instruction model run locally with Hugging Face transformers (no API key).
    Same abstention gate and output shape as the other generators. Citations the model writes are
    kept if they point at a retrieved chunk; sentences it leaves uncited are attributed afterwards."""

    def __init__(self, idf: Idf, tau: float = 0.6, model: str | None = None, max_words: int = 180, backend=None):
        self.tok, self.model, name = backend or load_local_model(model)
        self.name = "local:" + name.split("/")[-1]
        self.idf, self.tau, self.max_words = idf, tau, max_words
        self.attributed = 0  # sentences that needed post-hoc citation, for reporting

    def generate(self, question: str, retrieved: list[Chunk], max_new_tokens: int = 160) -> str:
        import torch

        passages = "\n\n".join(f"[{c.chunk_id}] {self.focus(question, c.text)}" for c in retrieved)
        msgs = [{"role": "system", "content": LOCAL_PROMPT},
                {"role": "user", "content": f"Passages:\n{passages}\n\nQuestion: {question}"}]
        enc = self.tok.apply_chat_template(msgs, add_generation_prompt=True, return_tensors="pt", return_dict=True)
        with torch.no_grad():
            out = self.model.generate(**enc, max_new_tokens=max_new_tokens, do_sample=False)
        return self.tok.decode(out[0][enc["input_ids"].shape[1]:], skip_special_tokens=True).strip()

    def focus(self, question: str, text: str) -> str:
        """Shorten a chunk to about max_words for the small model by keeping the sentences that share the
        most (IDF-weighted) words with the question, in their original order. Taking only the first words
        of a long chunk would often cut off the evidence."""
        sents = re.split(r"(?<=[.!?])\s+", text)
        if len(text.split()) <= self.max_words:
            return text
        q = set(tokenize(question)) - QUESTION_WORDS
        ranked = sorted(range(len(sents)), key=lambda i: -sum(self.idf(t) for t in q & set(tokenize(sents[i]))))
        keep, n = set(), 0
        for i in ranked:
            w = len(sents[i].split())
            if n + w > self.max_words and keep:
                continue
            keep.add(i)
            n += w
        return " ".join(sents[i] for i in sorted(keep))

    def answer(self, question: str, retrieved: list[Chunk]) -> Answer:
        cov = coverage(question, retrieved, self.idf)
        if cov < self.tau:
            return Answer(ABSTAIN, True, [], cov)
        text = self.generate(question, retrieved)
        if ABSTAIN in text or not text:
            return Answer(ABSTAIN, True, [], cov)
        valid = {c.chunk_id for c in retrieved}
        sentences = []
        for s in re.split(r"(?<=[.!?\]])\s+", text):
            if len(s.split()) < 3:
                continue
            cites = [c for c in CITE_RE.findall(s) if c in valid]
            if not cites:
                cites = attribute(s, retrieved)
                self.attributed += 1
            clean = CITE_RE.sub("", s).strip()
            sentences.append((clean, cites))
        if not sentences:
            return Answer(ABSTAIN, True, [], cov)
        shown = " ".join(f"{s} [{', '.join(c)}]" if c else f"{s} [uncited]" for s, c in sentences)
        return Answer(shown, False, sentences, cov)
