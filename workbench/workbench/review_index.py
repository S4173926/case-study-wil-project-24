"""Read-only record discovery for the review UI, separate from answer selection."""
from __future__ import annotations
import json
from collections import defaultdict
from pathlib import Path
from .core import normalize


def run_index(root: Path, engine) -> list[dict]:
    """Return all valid saved runs with explicit version and question identities.

    Corrupt entries are listed as unavailable instead of hiding every other run.
    Original records are never edited. Question IDs are display-only metadata.
    """
    root = Path(root)
    compatibility_path = root / 'config/release_compatibility.json'
    compatible = json.loads(compatibility_path.read_text(encoding="utf-8")).get('compatible_answer_sets', []) if compatibility_path.exists() else []
    qpath = root / 'config/review_question_ids.json'
    qids = {normalize(r['question']).casefold(): r['id'] for r in json.loads(qpath.read_text(encoding="utf-8"))} if qpath.exists() else {}
    reviewed = defaultdict(set)
    for path in (root / 'results/reviews').glob('*.json'):
        try:
            row = json.loads(path.read_text(encoding="utf-8"))
            reviewed[row['run_id']].add(row['reviewer_id'])
        except (ValueError, KeyError, TypeError, OSError):
            continue
    current = {'corpus': engine.corpus_hash, 'knowledge': engine.claim_hash, 'code': engine.code_hash}
    rows = []
    for path in (root / 'results/runs').glob('*.json'):
        try:
            r = json.loads(path.read_text(encoding="utf-8"))
            rid, question = r['run_id'], r['question']
            if not isinstance(rid, str) or not isinstance(question, str) or path.stem != rid:
                raise ValueError('Record identity does not match filename')
            hashes = r.get('hashes', {})
            now = all(hashes.get(k) == v for k, v in current.items())
            match = next((c for c in compatible if all(hashes.get(k) == c.get(k) for k in current)), None)
            paper_ids = r.get('plan', {}).get('named_papers', [])
            if not isinstance(paper_ids, list): paper_ids = []
            rows.append({
                'run_id': rid, 'question': question, 'status': r['status'],
                'mode': r.get('mode', 'explain'), 'created_utc': r.get('created_utc', ''), 'elapsed_seconds': r.get('elapsed_seconds', 0),
                'question_id': r.get('evaluation_question_id') or qids.get(normalize(question).casefold(), ''),
                'paper_ids': paper_ids,
                'paper_titles': [engine.papers[p]['title'] for p in paper_ids if p in engine.papers],
                'hashes': hashes, 'current_answer_set': now or match is not None,
                'version_label': 'Current release' if now else (match['label'] if match else 'Earlier / unverified version'),
                'reviewed_by': sorted(reviewed[rid]), 'available': True,
            })
        except (ValueError, KeyError, TypeError, OSError) as exc:
            rows.append({'run_id': path.stem, 'question': 'Unreadable saved record', 'question_id': '',
                         'status': 'unavailable', 'created_utc': '', 'elapsed_seconds': 0,
                         'paper_ids': [], 'paper_titles': [], 'hashes': {}, 'current_answer_set': False,
                         'version_label': 'Unavailable', 'reviewed_by': [], 'available': False,
                         'error': type(exc).__name__})
    return sorted(rows, key=lambda r: (r.get('created_utc', ''), r['run_id']), reverse=True)
