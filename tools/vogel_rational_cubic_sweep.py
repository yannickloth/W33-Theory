#!/usr/bin/env python3
"""Sweep Vogel rational cubic roots across a dimension range and write JSON/MD summary."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.vogel_rational_cubic_search import find_rational_m_for_dim


def sweep_dims(start: int, end: int, step: int, denom_cap: int) -> Dict[str, Dict]:
    results: Dict[str, Dict] = {}
    for dim in range(start, end + 1, step):
        res = find_rational_m_for_dim(dim, denom_cap=denom_cap)
        results[str(dim)] = res
    return results


def hit_dims(results: Dict[str, Dict]) -> List[int]:
    return sorted(int(dim) for dim, rec in results.items() if rec.get("hits"))


def render_md(results: Dict[str, Dict]) -> str:
    lines: List[str] = ["# Vogel rational cubic sweep", ""]
    hits = hit_dims(results)
    lines.append(f"- Dimensions scanned: `{len(results)}`")
    lines.append(f"- Dimensions with non-degenerate rational hits: `{len(hits)}`")
    lines.append(f"- Hit dimensions: `{hits}`")
    lines.append("")
    lines.append("Dimension | Hits (m values)")
    lines.append("--- | ---")
    for dim in sorted(results.keys(), key=lambda x: int(x)):
        hits_for_dim = results[dim]["hits"]
        lines.append(f"{dim} | {', '.join(hits_for_dim) if hits_for_dim else '-'}")
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
