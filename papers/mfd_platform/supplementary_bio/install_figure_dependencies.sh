#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../../.." && pwd)"
PYTHON="${1:-${REPO_ROOT}/.venv/bin/python}"

"${PYTHON}" -m pip install -r "${SCRIPT_DIR}/figure_requirements.txt"

"${PYTHON}" - <<'PY'
import cairosvg
import openpyxl
import pandas
import roifile
import skimage

print("Axotomy figure dependencies are available.")
PY
