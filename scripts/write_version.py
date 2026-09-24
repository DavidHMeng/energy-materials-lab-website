#!/usr/bin/env python3
"""Write the public, secret-free production build manifest."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


parser = argparse.ArgumentParser()
parser.add_argument("destination", type=Path)
parser.add_argument("--source-commit", required=True)
parser.add_argument("--build-commit", required=True)
args = parser.parse_args()

payload = {
    "source_commit": args.source_commit,
    "build_commit": args.build_commit,
    "built_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    "environment": "production",
}
args.destination.mkdir(parents=True, exist_ok=True)
(args.destination / "version.json").write_text(
    json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
)
