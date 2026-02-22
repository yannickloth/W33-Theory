#!/usr/bin/env python3
"""Print a concise summary of the per-A2 combined det=1 cocycle results."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict

ROOT = Path("analysis/minimal_commutator_cycles")


def summarize(path: Path) -> Dict:
    j = json.loads(path.read_text(encoding="utf-8"))
    rows = j.get("rows", [])
    total = len(rows)
    missing = sum(1 for r in rows if r.get("reason") == "missing_edge_root")
    divisible = sum(1 for r in rows if r.get("divisible"))
    k_total = sum(1 for r in rows if r.get("k") is not None)
    div_with_k = sum(1 for r in rows if r.get("divisible") and r.get("k") is not None)
    match_div = sum(
        1
        for r in rows
        if r.get("divisible")
        and r.get("k") is not None
        and r.get("s_mod3") == r.get("k")
    )
    s_counts = {}
    for r in rows:
        if r.get("divisible"):
            s_counts[r.get("s_mod3")] = s_counts.get(r.get("s_mod3"), 0) + 1
    return {
        "total": total,
        "missing_edge_root": missing,
        "divisible": divisible,
        "k_total": k_total,
        "divisible_with_k": div_with_k,
        "k_match_divisible": match_div,
        "match_rate_divisible": (match_div / div_with_k) if div_with_k else None,
        "s_counts": s_counts,
    }


if __name__ == "__main__":
    for i in range(4):
        p = ROOT / f"e8_det1_combined_a2_{i}" / "e8_rootword_cocycle.json"
        if not p.exists():
            continue
        j = json.loads(p.read_text(encoding="utf-8"))
        stats = summarize(p)
        print(f"A2 idx {i}: ai={j.get('ai_idx')} bi={j.get('bi_idx')} -> {stats}")
