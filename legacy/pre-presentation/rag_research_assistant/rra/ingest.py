"""PDF -> clean, structured text with a per-paper extraction-quality report.

Handles the PDF problems called out in the project risks:
  * two-column layouts   -> blocks are re-ordered column by column between full-width blocks
  * running headers/footers, page numbers, the rotated arXiv stamp -> removed
  * hyphenation across line breaks -> repaired
  * the reference list   -> dropped (it matches almost any query and pollutes retrieval)
  * equations / tables   -> not repaired, but *measured*: pages with a high symbol ratio are
                            flagged so the team inspects them before indexing.
"""
from __future__ import annotations

import json
import re
import statistics
from collections import Counter
from pathlib import Path

import pymupdf

HEADING_RE = re.compile(r"^(\d+(\.\d+)*\.?|[A-H](\.\d+)*\.?)\s+[A-Z][\w\-,:;()&’' ]{2,80}$")
UNNUMBERED_HEADINGS = {"abstract", "introduction", "related work", "conclusion", "conclusions",
                       "references", "acknowledgements", "acknowledgments", "appendix", "discussion",
                       "limitations", "background", "method", "methods", "experiments", "results"}
SECNUM_RE = re.compile(r"(\d{1,2}(\.\d{1,2})*|[A-H](\.\d{1,2})*)\.?")
FOOTNOTE_RE = re.compile(r"^\d{1,2}(https?:|www\.|[a-z][\w.-]*\.(org|io|com|edu|net)|[A-Z][a-z])")
MATH_CHARS = set("=∑∏∫√≈≤≥±×÷∈∀∃∂∇αβγδεθλμσφψωΩ∆→←⊕⊗⟨⟩|^_{}")


def _norm(line: str) -> str:
    return re.sub(r"\d+", "#", line.strip().lower())


def _page_lines(page: pymupdf.Page) -> list[dict]:
    """Return text lines in reading order with font size, handling two-column pages."""
    width, height = page.rect.width, page.rect.height
    blocks = []
    for b in page.get_text("dict")["blocks"]:
        if b.get("type") != 0:
            continue
        lines = []
        for ln in b["lines"]:
            if abs(ln["dir"][1]) > 0.1:  # rotated text: arXiv side stamp, rotated table headers
                continue
            text = "".join(s["text"] for s in ln["spans"]).strip()
            if text:
                size = max(s["size"] for s in ln["spans"])
                bold = any("bold" in s["font"].lower() or s["flags"] & 16 for s in ln["spans"])
                lines.append({"text": text, "size": size, "bold": bold, "y": ln["bbox"][1] / height})
        if lines:
            x0, y0, x1, _ = b["bbox"]
            blocks.append({"x0": x0, "x1": x1, "y0": y0, "lines": lines})

    def column(b):
        if b["x1"] <= 0.55 * width:
            return 0
        if b["x0"] >= 0.45 * width:
            return 1
        return None  # spans the middle: full width (title, centred abstract, single-column body)

    ordered, pending = [], []
    for b in sorted(blocks, key=lambda b: b["y0"]):
        if column(b) is None:
            ordered += sorted(pending, key=lambda b: (column(b), b["y0"]))
            pending = []
            ordered.append(b)
        else:
            pending.append(b)
    ordered += sorted(pending, key=lambda b: (column(b), b["y0"]))
    return _merge_numbers([ln for b in ordered for ln in b["lines"]])


def _merge_numbers(lines: list[dict]) -> list[dict]:
    """Many templates set a section number and its title as separate lines ("3" / "Method"): rejoin them."""
    out = []
    for ln in lines:
        prev = out[-1] if out else None
        if (prev and SECNUM_RE.fullmatch(prev["text"]) and (prev["bold"] or prev["size"] > ln["size"] - 0.5)
                and abs(prev["size"] - ln["size"]) < 0.6 and len(ln["text"]) < 80):
            out[-1] = {**ln, "text": f"{prev['text']} {ln['text']}", "bold": prev["bold"] or ln["bold"]}
        else:
            out.append(ln)
    return out


def extract(pdf_path: Path, paper_id: str, title: str = "") -> dict:
    doc = pymupdf.open(pdf_path)
    pages = [_page_lines(p) for p in doc]

    # Lines repeated on many pages at the same position are running headers/footers.
    edge = Counter()
    for lines in pages:
        for ln in lines[:2] + lines[-2:]:
            edge[_norm(ln["text"])] += 1
    boilerplate = {t for t, c in edge.items() if c >= max(3, 0.4 * len(pages))}

    body_size = statistics.median([ln["size"] for lines in pages for ln in lines] or [10])
    sections: list[dict] = [{"heading": "Front matter", "page": 1, "paras": []}]
    page_quality = []
    in_refs = False
    seen_abstract = False
    last_top = 0  # last accepted top-level section number, to reject affiliations like "3 Inria, Paris"
    for pno, lines in enumerate(pages, start=1):
        text_chars = 0
        math_chars = 0
        for ln in lines:
            t = ln["text"]
            if _norm(t) in boilerplate or re.fullmatch(r"\d{1,3}", t):
                continue
            if ln["size"] < 0.7 * body_size:
                continue  # labels inside figures ("MaxSim MaxSim MaxSim")
            if ln["size"] < 0.9 * body_size and FOOTNOTE_RE.match(t):
                continue  # footnotes such as "1lucene.apache.org" that land mid-paragraph
            text_chars += len(t)
            math_chars += sum(ch in MATH_CHARS for ch in t)
            is_heading = (
                len(t) < 90
                and ln["y"] < 0.88  # footers/footnotes (e.g. affiliations like "3 Inria, Paris")
                and (ln["size"] > body_size + 0.5 or ln["bold"])
                and (HEADING_RE.match(t) or t.lower().rstrip(".:") in UNNUMBERED_HEADINGS)
            )
            num = re.match(r"^(\d+)[.\s]", t)
            if is_heading and num and not in_refs:
                n = int(num.group(1))
                if pno == 1 and not seen_abstract:
                    is_heading = False  # numbered affiliations ("1 Facebook AI Research") above the abstract
                elif n not in (last_top, last_top + 1):
                    is_heading = False
                else:
                    last_top = n
            if is_heading:
                heading = t.lower().rstrip(".:")
                seen_abstract = seen_abstract or heading == "abstract"
                if in_refs and not re.match(r"^[A-H](\.\d+)*\.?\s", t) and "appendix" not in heading:
                    continue  # bold author names etc. inside the reference list
                in_refs = heading.endswith("references") or heading.endswith("bibliography")
                sections.append({"heading": t, "page": pno, "paras": []})
                continue
            if in_refs:
                continue
            sections[-1]["paras"].append({"page": pno, "text": t})
        page_quality.append({"page": pno, "chars": text_chars,
                             "symbol_ratio": round(math_chars / max(text_chars, 1), 4)})

    out_sections = []
    for s in sections:
        if s["heading"].lower().rstrip(".:").endswith("references"):
            continue
        text, page_spans = _join_lines(s["paras"])
        if text:
            out_sections.append({"heading": s["heading"], "page": s["page"], "text": text, "page_spans": page_spans})

    flagged = [q["page"] for q in page_quality if q["chars"] < 200 or q["symbol_ratio"] > 0.03]
    return {
        "paper_id": paper_id,
        "title": title,
        "n_pages": len(pages),
        "sections": out_sections,
        "quality": {
            "total_chars": sum(q["chars"] for q in page_quality),
            "n_sections": len(out_sections),
            "section_headings": [s["heading"] for s in out_sections],
            "pages_flagged_for_review": flagged,
            "pages": page_quality,
        },
    }


def _join_lines(paras: list[dict]) -> tuple[str, list[tuple[int, int]]]:
    """Join lines, repairing hyphenation. Returns text and (char_offset, page) spans."""
    text, spans = "", []
    for p in paras:
        t = p["text"]
        if not spans or spans[-1][1] != p["page"]:
            spans.append((len(text), p["page"]))
        if text.endswith("-") and t[:1].islower():
            text = text[:-1] + t
        else:
            text = f"{text} {t}" if text else t
    return re.sub(r"\s+", " ", text).strip(), spans


def page_at(section: dict, offset: int) -> int:
    page = section["page"]
    for start, p in section.get("page_spans", []):
        if start <= offset:
            page = p
    return page


def ingest_all(pdf_dir: Path, out_dir: Path, titles: dict[str, str]) -> list[dict]:
    out_dir.mkdir(parents=True, exist_ok=True)
    docs = []
    for pdf in sorted(pdf_dir.glob("*.pdf")):
        doc = extract(pdf, pdf.stem, titles.get(pdf.stem, pdf.stem))
        (out_dir / f"{pdf.stem}.json").write_text(json.dumps(doc, indent=1))
        q = doc["quality"]
        print(f"{pdf.stem:10s} pages={doc['n_pages']:3d} chars={q['total_chars']:7d} "
              f"sections={q['n_sections']:3d} flagged_pages={q['pages_flagged_for_review']}")
        docs.append(doc)
    return docs


def load_docs(processed_dir: Path) -> list[dict]:
    return [json.loads(p.read_text()) for p in sorted(processed_dir.glob("*.json"))]
