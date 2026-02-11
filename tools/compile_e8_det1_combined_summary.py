#!/usr/bin/env python3
"""Compile summary stats from e8_det1_combined_a2_* outputs."""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

ROOT = Path("analysis/minimal_commutator_cycles")
OUT = ROOT / "e8_det1_combined_summary.json"

summary = []
for i in range(4):
    p = ROOT / f"e8_det1_combined_a2_{i}" / "e8_rootword_cocycle.json"
    if not p.exists():
        continue
    j = json.loads(p.read_text(encoding="utf-8"))
    rows = j.get("rows", [])
    stats = Counter()
    s_counts = Counter()
    divisible_with_k = 0
    k_match_divisible = 0
    for r in rows:
        stats[f"reason_{r.get('reason')}"] += 1 if r.get("reason") else 0
        if r.get("divisible"):
            stats["divisible"] += 1
            s_counts[r.get("s_mod3")] += 1
        if r.get("k") is not None:
            stats["k_total"] += 1
            if r.get("divisible"):
                divisible_with_k += 1
                if r.get("s_mod3") == r.get("k"):
                    k_match_divisible += 1
    stats.update(s_counts)
    stats["divisible_with_k"] = divisible_with_k
    stats["k_match_divisible"] = k_match_divisible
    stats["match_rate_divisible"] = (
        (k_match_divisible / divisible_with_k) if divisible_with_k else None
    )
    summary.append(
        {
            "a2_index": i,
            "ai_idx": j.get("ai_idx"),
            "bi_idx": j.get("bi_idx"),
            "stats": dict(stats),
        }
    )

OUT.write_text(json.dumps(summary, indent=2), encoding="utf-8")
print("Wrote", OUT)
