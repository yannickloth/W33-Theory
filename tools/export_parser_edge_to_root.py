#!/usr/bin/env python3
"""Export the parser's consolidated edge->root mapping to artifacts file.

Writes: artifacts/edge_to_e8_root_combined.json as dict "(a, b)" -> [root coords]
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tools.w33_rootword_uv_parser import W33RootwordParser


def main():
    p = W33RootwordParser()
    out = {}
    for (a, b), coords in p.edge_to_root.items():
        out[f"({a}, {b})"] = list(coords)
    Path("artifacts").mkdir(exist_ok=True)
    Path("artifacts/edge_to_e8_root_combined.json").write_text(
        json.dumps(out, indent=2), encoding="utf-8"
    )
    print("Wrote artifacts/edge_to_e8_root_combined.json")


if __name__ == "__main__":
    main()
