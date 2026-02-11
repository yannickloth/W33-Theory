#!/usr/bin/env python3
"""Sweep Vogel rational cubic roots across a dimension range and write JSON/MD summary."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, List

from tools.vogel_rational_cubic_search import find_rational_m_for_dim


def sweep_dims(start: int, end: int, step: int, denom_cap: int) -> Dict[str, Dict]:
    results: Dict[str, Dict] = {}
    for D in range(start, end + 1, step):
        res = find_rational_m_for_dim(D, denom_cap=denom_cap)
        results[str(D)] = res
    return results


def render_md(results: Dict[str, Dict]) -> str:
    lines: List[str] = ["# Vogel rational cubic sweep", ""]
    lines.append("Dimension | Hits (m values)")
    lines.append("--- | ---")
    for D in sorted(results.keys(), key=lambda x: int(x)):
        hits = results[D]["hits"]
        lines.append(f"{D} | {', '.join(hits) if hits else '—'}")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", type=int, default=200)
    parser.add_argument("--end", type=int, default=1000)
    parser.add_argument("--step", type=int, default=1)
    parser.add_argument("--denom-cap", type=int, default=500)
    parser.add_argument(
        "--out-json", type=Path, default=Path("artifacts/vogel_rational_sweep.json")
    )
    parser.add_argument(
        "--out-md", type=Path, default=Path("artifacts/vogel_rational_sweep.md")
    )
    args = parser.parse_args()

    results = sweep_dims(
        int(args.start), int(args.end), int(args.step), int(args.denom_cap)
    )
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(results, indent=2), encoding="utf-8")
    args.out_md.parent.mkdir(parents=True, exist_ok=True)
    args.out_md.write_text(render_md(results), encoding="utf-8")
    print(f"Wrote {args.out_json} and {args.out_md}")


if __name__ == "__main__":
    main()
