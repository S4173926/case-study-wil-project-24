#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")"
python3 -m unittest discover -s tests -v
python3 -m workbench.cli doctor
python3 tools/verify_release.py
