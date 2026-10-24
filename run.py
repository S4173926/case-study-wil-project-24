"""Start the unchanged portable Research Workbench from this repository."""
from pathlib import Path
import subprocess
import sys

def main() -> int:
    if sys.version_info < (3, 10):
        print("Python 3.10 or newer is required.", file=sys.stderr)
        return 2
    archive = Path(__file__).resolve().parent / "downloads" / "Research_Workbench.pyz"
    if not archive.is_file():
        print("The portable assistant is missing. Complete all three upload batches or download the complete repository ZIP.", file=sys.stderr)
        return 2
    try:
        return subprocess.call([sys.executable, str(archive), *sys.argv[1:]])
    except KeyboardInterrupt:
        return 130
    except OSError as exc:
        print(f"Could not start Python: {exc}", file=sys.stderr)
        return 2

if __name__ == "__main__":
    raise SystemExit(main())
