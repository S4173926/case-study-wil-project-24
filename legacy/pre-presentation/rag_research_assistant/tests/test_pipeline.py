"""Pipeline tests on small synthetic PDFs (made-up text, not real papers).

They check the behaviours the evaluation depends on: two-column reading order, header and
reference removal, hyphen repair, evidence matching, retrieval, citations and abstention.
"""
from __future__ import annotations

import pymupdf
import pytest

from rra import chunking, evaluate, generate, ingest, retrieval

ALPHA_LEFT = ("1 Introduction\nThe alpha retriever encodes every passage into a single vector. "
              "Training uses in-batch negatives drawn from the same mini-batch, which is cheap and effec-\n"
              "tive for large corpora. ")
ALPHA_RIGHT = ("2 Method\nAt query time alpha performs maximum inner product search over the vector index. "
               "The index is refreshed every five hundred steps during training.")
BETA_BODY = ("1 Introduction\nThe beta reader concatenates twenty passages in the decoder and generates an "
             "answer token by token. Beta was evaluated on a trivia benchmark with exact match scoring. "
             "References\n[1] Someone. Alpha retriever encodes things. 2020.")


def _paper(path, title, left, right=""):
    doc = pymupdf.open()
    for _ in range(3):
        page = doc.new_page(width=612, height=792)
        page.insert_textbox(pymupdf.Rect(50, 20, 560, 40), "Running Header Proceedings", fontsize=8)
        page.insert_textbox(pymupdf.Rect(50, 50, 560, 90), title, fontsize=16, fontname="hebo")
        # Right column first in the content stream, to prove re-ordering is by geometry.
        if right:
            page.insert_textbox(pymupdf.Rect(320, 100, 560, 700), right, fontsize=10)
        page.insert_textbox(pymupdf.Rect(50, 100, 290, 700), left, fontsize=10)
        page.insert_textbox(pymupdf.Rect(290, 750, 320, 770), "1", fontsize=8)
    doc.save(path)


@pytest.fixture(scope="module")
def docs(tmp_path_factory):
    d = tmp_path_factory.mktemp("pdfs")
    _paper(d / "alpha.pdf", "Alpha Retrieval", ALPHA_LEFT, ALPHA_RIGHT)
    _paper(d / "beta.pdf", "Beta Reader", BETA_BODY)
    return ingest.ingest_all(d, d / "processed", {"alpha": "Alpha Retrieval", "beta": "Beta Reader"})


def text_of(doc):
    return " ".join(s["text"] for s in doc["sections"])


def test_reading_order_and_cleaning(docs):
    alpha = text_of(docs[0])
    assert alpha.index("single vector") < alpha.index("maximum inner product")  # left column before right
    assert "Running Header" not in alpha
    assert "effective for large corpora" in alpha  # hyphenation repaired
    assert "Someone" not in text_of(docs[1])  # reference list dropped


def test_ground_truth_validation(docs):
    qs = [{"id": "a", "type": "single", "evidence": [{"paper": "alpha", "quote": "in-batch negatives"}]},
          {"id": "b", "type": "single", "evidence": [{"paper": "beta", "quote": "not in the paper"}]}]
    problems = evaluate.validate_ground_truth(qs, docs)
    assert len(problems) == 1 and problems[0].startswith("b:")


@pytest.mark.parametrize("strategy", list(chunking.STRATEGIES))
@pytest.mark.parametrize("retr", retrieval.RETRIEVERS)
def test_retrieval_answer_and_abstention(docs, strategy, retr):
    chunks = chunking.STRATEGIES[strategy](docs)
    by_id = {c.chunk_id: c for c in chunks}
    r = retrieval.build(retr, chunks)
    gen = generate.ExtractiveGenerator(generate.Idf(chunks), tau=0.6)

    q = {"id": "q", "type": "single", "question": "What negatives does the alpha retriever use in training?",
         "expected_papers": ["alpha"], "evidence": [{"paper": "alpha", "quote": "in-batch negatives"}]}
    top = [c for c, _ in r.search(q["question"], 3)]
    ans = gen.answer(q["question"], top)
    res = evaluate.score_question(q, top, ans, by_id)
    assert res.first_relevant_rank is not None
    assert not ans.abstained and ans.citations
    assert res.citation_precision == 1.0 and res.faithfulness == 1.0

    u = {"id": "u", "type": "unsupported", "question": "What sourdough hydration suits rye flour?", "expected_papers": []}
    top = [c for c, _ in r.search(u["question"], 3)]
    assert evaluate.score_question(u, top, gen.answer(u["question"], top), by_id).abstained


def test_paper_router_restricts_to_named_papers(docs):
    chunks = chunking.STRATEGIES["sentence-150"](docs)
    base = retrieval.build("bm25", chunks)
    r = retrieval.PaperRouter(chunks, base, {"alpha": ["alpha"], "beta": ["beta"]})
    assert {c.paper_id for c, _ in r.search("How does beta use passages?", 3)} == {"beta"}
    assert {c.paper_id for c, _ in r.search("How do alpha and beta handle passages?", 4)} == {"alpha", "beta"}
    assert [c.chunk_id for c, _ in r.search("passages", 2)] == [c.chunk_id for c, _ in base.search("passages", 2)]
