#!/usr/bin/env python3

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
DOCX_BUILD_SCRIPT = ROOT / "build_docx.py"


def main() -> int:
    subprocess.run([sys.executable, str(DOCX_BUILD_SCRIPT)], check=True, cwd=ROOT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
