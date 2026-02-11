#!/usr/bin/env python3
"""Analyze overlaps among minimal conflict edge sets to find hotspots."""
from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from e8_embedding_group_theoretic import build_w33

# Pick the latest merged quick analysis file
candidates = sorted(
    Path("checks").glob("PART_CVII_infeasible_block_analysis_quick_merged_*.json")
)
if not candidates:
    raise SystemExit("No merged quick analysis file found in checks/")
merged_path = candidates[-1]
merged = json.loads(merged_path.read_text(encoding="utf-8"))
entries = merged.get("checked", [])

edge_counts = Counter()
edge_to_blocks = defaultdict(list)
for e in entries:
    file = e.get("file")
    sv = e.get("start_vertex")
    m = e.get("minimal_conflict") or []
    for idx in m:
        edge_counts[idx] += 1
        edge_to_blocks[idx].append({"file": file, "start_vertex": sv})

# Map indices back to actual edges
n, vertices, adj, edges = build_w33()

hotspots = []
for idx, cnt in edge_counts.most_common(20):
    uv = edges[idx] if idx < len(edges) else ("?", "?")
    hotspots.append(
        {"edge_index": idx, "edge": uv, "count": cnt, "blocks": edge_to_blocks[idx]}
    )

out = {
    "merged_source": str(merged_path),
    "total_blocks_analyzed": len(entries),
    "hotspots_top20": hotspots,
}

outp = (
    Path("checks")
    / f'PART_CVII_conflict_hotspots_{int(__import__("time").time())}.json'
)
outp.write_text(json.dumps(out, indent=2), encoding="utf-8")
print("Wrote", outp)
print("Top hotspots:")
for h in hotspots[:10]:
    print(h["edge_index"], h["edge"], "count=", h["count"])
