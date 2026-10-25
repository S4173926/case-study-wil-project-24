"""Start the portable Research Workbench included in this repository."""
from pathlib import Path
import subprocess
import sys

def main() -> int:
    if sys.version_info < (3, 10):
        print("Python 3.10 or newer is required.", file=sys.stderr)
        return 2
    archive = Path(__file__).resolve().parent / "downloads" / "Research_Workbench.pyz"
    if not archive.is_file():
        print("The portable application is missing. The repository must include downloads/Research_Workbench.pyz.", file=sys.stderr)
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
