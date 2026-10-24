"""Verify immutable delivery files. Results produced by users are not release files."""
import hashlib,json,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1];p=root/'RELEASE_SHA256.json'
if not p.exists():raise SystemExit('Release manifest is missing.')
manifest=json.loads(p.read_text(encoding="utf-8"));errors=[]
for name,expected in manifest['files'].items():
 file=root/name
 if not file.is_file() or hashlib.sha256(file.read_bytes()).hexdigest()!=expected:errors.append(name)
print(json.dumps({'checked':len(manifest['files']),'mismatches':errors,'passed':not errors},indent=2))
sys.exit(1 if errors else 0)
