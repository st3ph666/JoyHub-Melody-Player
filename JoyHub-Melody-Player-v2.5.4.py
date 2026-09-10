#!/usr/bin/env python3
"""Compatibility launcher for JoyHub Melody Player v2.5.4."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from joyhub_melody.main import main

if __name__ == "__main__":
    raise SystemExit(main())
