#!/usr/bin/env python3
"""Reproduce this report's mechanical checks without changing saved research data.

Usage:
    python3 reproduce_core_audit.py --repository /path/to/case-study-wil-project-24
All new files go to --output, never into the supplied application's saved records.
"""
from __future__ import annotations
import argparse
from collections import Counter
import json
from pathlib import Path
import subprocess
import sys
import zipfile


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False), encoding='utf-8')


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repository', type=Path, required=True)
    parser.add_argument('--output', type=Path, default=Path('report_audit_rerun'))
    args = parser.parse_args()
    repo = args.repository.expanduser().resolve()
    root = repo / 'workbench'
    output = args.output.expanduser().resolve()
    required = [root / 'workbench/core.py', root / 'eval/all52_development.jsonl',
                root / 'eval/regression67_selection_repair.jsonl',
                repo / 'evaluation/repaired67_original.zip']
    for path in required:
        if not path.is_file():
            parser.error(f'Missing required file: {path}')
    if output == root or root in output.parents:
        parser.error('--output must be outside the application folder.')
    output.mkdir(parents=True, exist_ok=True)
    sys.path.insert(0, str(root))
    from workbench.core import Workbench  # type: ignore
    from workbench.cli import doctor, ablation  # type: ignore

    completed = subprocess.run([sys.executable, '-m', 'unittest', 'discover',
                                '-s', 'tests', '-v'], cwd=root, text=True,
                               stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    (output / 'software_tests.txt').write_text(completed.stdout, encoding='utf-8')
    if completed.returncode:
        print('Software tests failed. Inspect software_tests.txt; no results are claimed.', file=sys.stderr)
        return completed.returncode
    write_json(output / 'integrity.json', doctor(root))
    ablation(root / 'eval/all52_development.jsonl', output / 'matched_ablation_52.json', root)
    bench = Workbench(root)
    questions = [json.loads(line) for line in (root / 'eval/regression67_selection_repair.jsonl').read_text(encoding='utf-8').splitlines() if line.strip()]
    fields = ['question', 'mode', 'blocks', 'comparison', 'citations', 'status',
              'missing', 'first_stage', 'retrieved', 'plan']
    rows = []
    with zipfile.ZipFile(repo / 'evaluation/repaired67_original.zip') as archive:
        for q in questions:
            old = json.loads(archive.read(q['id'] + '.json'))
            new = bench.answer(q['question'], persist=False)
            mismatched = [key for key in fields if old.get(key) != new.get(key)]
            rows.append({'id': q['id'], 'status': new['status'],
                         'matches_saved_factual_fields': not mismatched,
                         'mismatched_fields': mismatched})
    write_json(output / 'regression_equivalence.json', {
        'n': len(rows), 'matched': sum(r['matches_saved_factual_fields'] for r in rows),
        'status_counts': dict(Counter(r['status'] for r in rows)), 'rows': rows})
    protocol_path = Path(__file__).resolve().parent / 'supplementary_probes/protocol.json'
    if protocol_path.exists():
        protocol = json.loads(protocol_path.read_text(encoding='utf-8'))
        probe_dir = output / 'supplementary_probes'
        probe_dir.mkdir(exist_ok=True)
        write_json(probe_dir / 'protocol.json', protocol)
        for question in protocol['questions']:
            write_json(probe_dir / f"{question['id']}.json", bench.answer(question['question'], persist=False))
    print(f'Completed. New diagnostic records: {output}')
    print('These are mechanical/development checks, not independently measured accuracy.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
