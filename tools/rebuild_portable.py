"""Rebuild the executable from its unchanged, hash-checked source assets."""
from pathlib import Path
import argparse
import hashlib
import json
import zipfile

ROOT = Path(__file__).resolve().parents[1]

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("output", type=Path, help="New output .pyz file; existing files are not replaced")
    args = parser.parse_args()
    out = args.output.expanduser().resolve()
    if out.exists():
        raise SystemExit("Choose a new output file; existing files are not overwritten.")
    metadata = ROOT / "distribution_source"
    manifest = json.loads((metadata / "bundle_manifest.json").read_text(encoding="utf-8"))
    for rel, expected in manifest["files"].items():
        p = ROOT / "workbench" / rel
        if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest() != expected:
            raise SystemExit("An original payload file is missing or changed: " + rel)
    out.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(out, "x") as z:
        for name in ("__main__.py", "launcher.py", "bundle_manifest.json"):
            z.write(metadata / name, name, compress_type=zipfile.ZIP_DEFLATED)
        for rel in manifest["files"]:
            z.write(ROOT / "workbench" / rel, "payload/" + rel, compress_type=zipfile.ZIP_LZMA)
    print("Built:", out)
    print("Bytes:", out.stat().st_size)

if __name__ == "__main__":
    main()
