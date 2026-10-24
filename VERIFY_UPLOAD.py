"""Verify every supplied repository file after all upload batches are combined."""
from pathlib import Path
import hashlib
import json

root = Path(__file__).resolve().parent
manifest = root / "UPLOAD_MANIFEST.json"
if not manifest.is_file():
    raise SystemExit("UPLOAD_MANIFEST.json is missing. Complete all three upload batches.")
data = json.loads(manifest.read_text(encoding="utf-8"))
missing, changed = [], []
for rel, expected in data["files"].items():
    p = root / rel
    if not p.is_file():
        missing.append(rel)
    elif hashlib.sha256(p.read_bytes()).hexdigest() != expected:
        changed.append(rel)
if missing or changed:
    for rel in missing: print("MISSING:", rel)
    for rel in changed: print("CHANGED:", rel)
    raise SystemExit(1)
print(f"All {len(data['files'])} supplied files match. Final application and evidence are present.")
