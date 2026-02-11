#!/usr/bin/env python3
"""Quick helper: print det=2 involutions in GL(2,3) with sample conjugators."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.analyze_gl2_f3_involution_conjugacy import build_report


def main() -> None:
    payload = build_report()
    rows = payload.get("candidates", [])
    print(f"Found {len(rows)} candidate involutions with det=2, order=2.")
    print("Sample conjugators to diag(-1,1):")
    for row in rows:
        print(
            f"  M={tuple(row['matrix'][:4])} -> U={tuple(row['conjugator_example'][:4])}"
        )


if __name__ == "__main__":
    main()
