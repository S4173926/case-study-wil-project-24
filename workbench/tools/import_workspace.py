"""Copy saved research records without modifying a previous workspace."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import re
import tempfile
from pathlib import Path

CATEGORIES = ('runs', 'reviews', 'pilot')


def copy_records(source: Path, destination: Path) -> dict:
    """Preflight all records before adding any files; never overwrite a conflict."""
    source, destination = Path(source), Path(destination)
    if source.is_symlink() or destination.is_symlink():
        raise ValueError('Use real workspace directories, not symbolic links')
    if not source.is_dir():
        return {'status': 'NO_PREVIOUS_WORKSPACE', 'copied': 0, 'identical': 0}
    if source.resolve() == destination.resolve():
        return {'status': 'SAME_WORKSPACE', 'copied': 0, 'identical': 0}
    plans, identical = [], 0
    for category in CATEGORIES:
        folder = source / 'results' / category
        target = destination / 'results' / category
        for parent in (source/'results', folder, destination/'results', target):
            if parent.is_symlink(): raise ValueError('Record directories must not be symbolic links')
        for path in sorted(folder.glob('*.json')):
            if path.is_symlink() or not re.fullmatch(r'[A-Za-z0-9_-]+\.json', path.name):
                raise ValueError('Unsafe record filename: ' + path.name)
            content = path.read_bytes()
            row = json.loads(content)
            if not isinstance(row, dict): raise ValueError('Record must be a JSON object: ' + path.name)
            key = {'runs': 'run_id', 'reviews': 'review_id', 'pilot': 'session_id'}[category]
            if str(row.get(key, '')) != path.stem:
                raise ValueError('Record identity mismatch: ' + path.name)
            dest = target / path.name
            if dest.is_symlink(): raise ValueError('Destination record is a symbolic link')
            if dest.exists():
                if dest.read_bytes() != content:
                    raise ValueError('Conflicting saved record; neither file was overwritten: ' + category + '/' + path.name)
                identical += 1
            else:
                plans.append((dest, content))
    created = []
    try:
        for dest, content in plans:
            dest.parent.mkdir(parents=True, exist_ok=True)
            # Exclusive create prevents a race from overwriting a newly saved record.
            with dest.open('xb') as f:
                created.append(dest)
                f.write(content)
    except Exception:
        for dest in created: dest.unlink(missing_ok=True)
        raise
    return {'status': 'COPIED', 'copied': len(created), 'identical': identical,
            'copied_files': [str(p.relative_to(destination)) for p in created],
            'notice': 'Original records and archived evaluation ZIPs remain in the previous workspace.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--destination', type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    try:
        result = copy_records(args.source, args.destination)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        raise SystemExit('Record import stopped without overwriting originals: ' + str(exc))
    print(json.dumps({k: v for k, v in result.items() if k != 'copied_files'}, indent=2))

if __name__ == '__main__': main()
