"""Read-only verification of the files supplied with this repository edition."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path, PurePosixPath
import sys

ROOT = Path(__file__).resolve().parents[1]

def main() -> int:
    manifest_path = ROOT / "REPOSITORY_SHA256.json"
    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
        files = data["files"]
        if not isinstance(files, dict):
            raise ValueError("Expected a filename-to-hash mapping")
    except (OSError, ValueError, KeyError) as exc:
        print(f"Cannot read repository manifest: {exc}", file=sys.stderr)
        return 2
    missing: list[str] = []
    changed: list[str] = []
    for name, expected in files.items():
        rel = PurePosixPath(name)
        if rel.is_absolute() or ".." in rel.parts or "\\" in name:
            print("Unsafe path in manifest", file=sys.stderr)
            return 2
        path = ROOT.joinpath(*rel.parts)
        if not path.is_file():
            missing.append(name)
        elif hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            changed.append(name)
    print(json.dumps({"checked": len(files), "missing": missing,
                      "changed": changed, "passed": not missing and not changed}, indent=2))
    return 1 if missing or changed else 0

if __name__ == "__main__":
    raise SystemExit(main())
