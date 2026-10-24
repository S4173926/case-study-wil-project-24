"""Retrievers compared in the experiments. All share one interface: search(query, k) -> [(chunk, score)].

bm25    - lexical baseline (rank_bm25)
tfidf   - cosine over TF-IDF with bigrams
dense   - sentence-transformers embeddings when available, else an offline LSA embedding
          (TF-IDF -> TruncatedSVD). LSA is a stand-in so the pipeline runs anywhere; report which
          one ran (`Retriever.name`) next to every result.
hybrid  - reciprocal-rank fusion of bm25 + dense
"""
from __future__ import annotations

import re

import numpy as np
from rank_bm25 import BM25Okapi
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS, TfidfVectorizer
from sklearn.preprocessing import normalize

from .chunking import Chunk

TOKEN_RE = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")


def _stem(t: str) -> str:
    """Very light suffix stripping so 'uses'/'use' and 'retrieved'/'retrieve' match."""
    if len(t) > 5 and t.endswith("ing"):
        return t[:-3]
    if len(t) > 4 and t.endswith("ed"):
        return t[:-2]
    if len(t) > 3 and t.endswith("s") and not t.endswith(("ss", "us", "is")):
        return t[:-1]
    return t


def tokenize(text: str) -> list[str]:
    return [_stem(t) for t in TOKEN_RE.findall(text.lower()) if t not in ENGLISH_STOP_WORDS]


class Retriever:
    name = "base"

    def __init__(self, chunks: list[Chunk]):
        self.chunks = chunks

    def scores(self, query: str) -> np.ndarray:
        raise NotImplementedError

    def search(self, query: str, k: int = 5) -> list[tuple[Chunk, float]]:
        s = self.scores(query)
        top = np.argsort(-s)[:k]
        return [(self.chunks[i], float(s[i])) for i in top]


class BM25(Retriever):
    name = "bm25"

    def __init__(self, chunks):
        super().__init__(chunks)
        # k1/b as in Walert (Okapi BM25 with pyserini defaults k1=1.2, b=0.75)
        self.bm25 = BM25Okapi([tokenize(c.index_text) for c in chunks], k1=1.2, b=0.75)

    def scores(self, query):
        return np.asarray(self.bm25.get_scores(tokenize(query)))


class TfIdf(Retriever):
    name = "tfidf"

    def __init__(self, chunks):
        super().__init__(chunks)
        self.vec = TfidfVectorizer(tokenizer=tokenize, lowercase=False, ngram_range=(1, 2),
                                   sublinear_tf=True, token_pattern=None)
        self.m = self.vec.fit_transform([c.index_text for c in chunks])

    def scores(self, query):
        return (self.m @ self.vec.transform([query]).T).toarray().ravel()


class Dense(Retriever):
    name = "dense-lsa"

    def __init__(self, chunks, model: str = "sentence-transformers/all-MiniLM-L6-v2", dims: int = 256):
        super().__init__(chunks)
        texts = [c.index_text for c in chunks]
        try:
            from sentence_transformers import SentenceTransformer  # optional dependency
            self.model = SentenceTransformer(model)
            self.emb = self.model.encode(texts, normalize_embeddings=True, show_progress_bar=False)
            self.name = "dense-minilm"
            self._encode = lambda q: self.model.encode([q], normalize_embeddings=True)[0]
        except Exception:
            vec = TfidfVectorizer(tokenizer=tokenize, lowercase=False, sublinear_tf=True, token_pattern=None)
            m = vec.fit_transform(texts)
            svd = TruncatedSVD(n_components=min(dims, m.shape[1] - 1, m.shape[0] - 1), random_state=0)
            self.emb = normalize(svd.fit_transform(m))
            self._encode = lambda q: normalize(svd.transform(vec.transform([q])))[0]

    def scores(self, query):
        return self.emb @ self._encode(query)


class Hybrid(Retriever):
    """Reciprocal-rank fusion: robust to the two retrievers' incomparable score scales."""

    def __init__(self, chunks, parts: list[Retriever], k_rrf: int = 60):
        super().__init__(chunks)
        self.parts, self.k_rrf = parts, k_rrf
        self.name = "hybrid(" + "+".join(p.name for p in parts) + ")"

    def scores(self, query):
        total = np.zeros(len(self.chunks))
        for p in self.parts:
            ranks = np.empty(len(self.chunks))
            ranks[np.argsort(-p.scores(query))] = np.arange(len(self.chunks))
            total += 1.0 / (self.k_rrf + ranks + 1)
        return total


class PaperRouter(Retriever):
    """Added after error analysis: generic terms ("retrieval", "RAG") appear in every paper and outrank the
    paper a question names, so the wrong paper's passages fill the top k. When a question names papers,
    rank only those papers' chunks and share the k slots between them (round-robin)."""

    def __init__(self, chunks, base: Retriever, aliases: dict[str, list[str]]):
        super().__init__(chunks)
        self.base, self.name = base, base.name + "+route"
        self.patterns = {pid: [re.compile(r"(?<![\w-])" + re.escape(a) + r"(?![\w-])", re.I) for a in al]
                         for pid, al in aliases.items()}
        if "rag" in self.patterns:  # "REALM and RAG" names the paper; "its RAG pipeline" does not
            self.patterns["rag"].append(re.compile(r"(?<!its )(?<!the )(?<!a )(?<!their )(?<![\w-])RAG(?![\w-])"))

    def mentioned(self, query: str) -> list[str]:
        return [pid for pid, pats in self.patterns.items() if any(p.search(query) for p in pats)]

    def scores(self, query):
        return self.base.scores(query)

    def search(self, query, k=5):
        papers = self.mentioned(query)
        if not papers:
            return self.base.search(query, k)
        s = self.base.scores(query)
        order = [i for i in np.argsort(-s) if self.chunks[i].paper_id in papers]
        queues = {p: [i for i in order if self.chunks[i].paper_id == p] for p in papers}
        picked = []
        while len(picked) < k and any(queues.values()):
            for p in papers:
                if queues[p] and len(picked) < k:
                    picked.append(queues[p].pop(0))
        return [(self.chunks[i], float(s[i])) for i in picked]


def paper_aliases() -> dict[str, list[str]]:
    import json
    from pathlib import Path

    manifest = json.loads((Path(__file__).resolve().parent.parent / "corpus" / "manifest.json").read_text())
    return {p["id"]: p.get("aliases", [p["id"]]) for p in manifest["papers"]}


def build(name: str, chunks: list[Chunk]) -> Retriever:
    if name.endswith("+route"):
        return PaperRouter(chunks, build(name[: -len("+route")], chunks), paper_aliases())
    if name == "bm25":
        return BM25(chunks)
    if name == "tfidf":
        return TfIdf(chunks)
    if name == "dense":
        return Dense(chunks)
    if name == "hybrid":
        return Hybrid(chunks, [BM25(chunks), Dense(chunks)])
    raise ValueError(name)


RETRIEVERS = ["bm25", "tfidf", "dense", "hybrid", "hybrid+route"]
