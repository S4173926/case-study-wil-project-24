"""Download the corpus PDFs from arXiv and pin them in a versioned lock file.

Every PDF is stored under corpus/pdfs/<id>.pdf and recorded in corpus/corpus.lock.json
with its arXiv version, title and SHA-256. The corpus version is a hash over all
file hashes, so every evaluation run can say exactly which corpus it was scored on.
"""
from __future__ import annotations

import hashlib
import json
import time
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CORPUS = ROOT / "corpus"
ATOM = "{http://www.w3.org/2005/Atom}"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def arxiv_metadata(arxiv_id: str) -> dict:
    url = f"https://export.arxiv.org/api/query?id_list={arxiv_id}"
    with urllib.request.urlopen(url, timeout=30) as r:
        entry = ET.fromstring(r.read()).find(f"{ATOM}entry")
    versioned = entry.find(f"{ATOM}id").text.rsplit("/", 1)[-1]  # e.g. 2005.11401v4
    return {
        "title": " ".join(entry.find(f"{ATOM}title").text.split()),
        "authors": [a.find(f"{ATOM}name").text for a in entry.findall(f"{ATOM}author")],
        "published": entry.find(f"{ATOM}published").text[:10],
        "arxiv_version": versioned,
    }


def fetch(force: bool = False) -> dict:
    manifest = json.loads((CORPUS / "manifest.json").read_text())
    pdf_dir = CORPUS / "pdfs"
    pdf_dir.mkdir(exist_ok=True)
    lock_path = CORPUS / "corpus.lock.json"
    lock = json.loads(lock_path.read_text()) if lock_path.exists() else {"papers": {}}

    for paper in manifest["papers"]:
        pid, aid = paper["id"], paper["arxiv"]
        pdf = pdf_dir / f"{pid}.pdf"
        entry = lock["papers"].get(pid)
        if pdf.exists() and entry and not force:
            # Pinned: refuse to silently use a changed file.
            if sha256(pdf) != entry["sha256"]:
                raise RuntimeError(f"{pdf} does not match corpus.lock.json; re-run with --force to re-pin")
            continue
        meta = arxiv_metadata(aid)
        if paper["title_must_contain"].lower() not in meta["title"].lower():
            raise RuntimeError(f"{aid} title {meta['title']!r} does not match manifest ({paper['title_must_contain']!r})")
        print(f"downloading {meta['arxiv_version']}  {meta['title']}")
        urllib.request.urlretrieve(f"https://arxiv.org/pdf/{meta['arxiv_version']}", pdf)
        lock["papers"][pid] = {**meta, "arxiv": aid, "file": f"pdfs/{pid}.pdf", "sha256": sha256(pdf),
                               "licence_url": f"https://arxiv.org/abs/{meta['arxiv_version']}"}
        time.sleep(3)  # arXiv API etiquette

    digest = hashlib.sha256("".join(lock["papers"][p]["sha256"] for p in sorted(lock["papers"])).encode())
    lock["corpus_version"] = digest.hexdigest()[:12]
    lock_path.write_text(json.dumps(lock, indent=2))
    print(f"corpus_version={lock['corpus_version']}  ({len(lock['papers'])} papers)")
    return lock


def corpus_version() -> str:
    lock_path = CORPUS / "corpus.lock.json"
    if not lock_path.exists():
        return "unpinned"
    return json.loads(lock_path.read_text()).get("corpus_version", "unpinned")


def paper_titles() -> dict[str, str]:
    lock_path = CORPUS / "corpus.lock.json"
    if lock_path.exists():
        return {k: v["title"] for k, v in json.loads(lock_path.read_text())["papers"].items()}
    manifest = json.loads((CORPUS / "manifest.json").read_text())
    return {p["id"]: p["title_must_contain"] for p in manifest["papers"]}

