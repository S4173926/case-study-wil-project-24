#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")"
OUT="results/development_$(date -u +%Y%m%dT%H%M%S)_${RANDOM}"
python3 -m workbench.cli evaluate --questions eval/regression67_selection_repair.jsonl --out "$OUT" --publish-runs
