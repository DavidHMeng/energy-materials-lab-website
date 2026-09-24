#!/usr/bin/env python3
"""Compare checked-in and freshly generated citation data semantically."""

from __future__ import annotations

import argparse
from pathlib import Path

import yaml


parser = argparse.ArgumentParser()
parser.add_argument("checked_in", type=Path)
parser.add_argument("generated", type=Path)
args = parser.parse_args()

checked_in = yaml.safe_load(args.checked_in.read_text(encoding="utf-8"))
generated = yaml.safe_load(args.generated.read_text(encoding="utf-8"))

if checked_in != generated:
    raise SystemExit(
        "checked-in citations are stale: run the citation refresh workflow and commit its output"
    )

print(f"Citation freshness passed for {len(generated or [])} citation(s).")
