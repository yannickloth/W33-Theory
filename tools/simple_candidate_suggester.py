#!/usr/bin/env python3
"""Simpler candidate suggester (fallback) that picks direct and nearest neighbor candidates for top problem edges."""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.suggest_missing_edge_candidates import (
    build_all_mapped_vectors,
    build_inverse_vec_map,
    dist2,
)
from tools.w33_rootword_uv_parser import W33RootwordParser

TOP = Path("analysis/minimal_commutator_cycles/problem_cycle_edge_tally.json")
OUT = Path(
    "analysis/minimal_commutator_cycles/w33_uv_parser_det1_simple_candidates.json"
)

p = W33RootwordParser()
edge_candidates_map = build_inverse_vec_map(p)
all_mapped = build_all_mapped_vectors(p)

j = json.loads(TOP.read_text(encoding="utf-8"))
top = j.get("top_edges", [])[:20]

out = {"edges": []}

for e in top:
    a = e["edge_a"]
    b = e["edge_b"]
    direct = edge_candidates_map.get((a, b), [])
    candlist = []
    for vec, tag in direct:
        candlist.append({"vector": list(vec), "source": "direct", "tag": tag})
    # centroid neighbor: find centroid of incident mapped vectors
    incident = []
    for (aa, bb), vec in p.edge_to_root.items():
        if aa == a or bb == a or aa == b or bb == b:
            incident.append(tuple(int(x) for x in vec))
    if incident:
        n = len(incident)
        mean = [sum(v[i] for v in incident) / n for i in range(len(incident[0]))]
        # find nearest neighbors among all_mapped
        nn = sorted(
            all_mapped, key=lambda t: dist2(t[0], tuple(int(round(x)) for x in mean))
        )[:6]
        for vec, edge_pair, tag in nn:
            candlist.append({"vector": list(vec), "source": f"centroid_nn", "tag": tag})
    # fallback: global NN to zero
    nn_global = sorted(
        all_mapped, key=lambda t: dist2(t[0], (0,) * len(all_mapped[0][0]))
    )[:6]
    for vec, edge_pair, tag in nn_global:
        candlist.append({"vector": list(vec), "source": "global_nn", "tag": tag})

    # dedup preserve order
    seen = set()
    final = []
    for c in candlist:
        vt = tuple(int(x) for x in c["vector"])
        if vt in seen:
            continue
        seen.add(vt)
        final.append(c)

    out["edges"].append(
        {"edge": f"{a},{b}", "count": e.get("count", 1), "candidates": final[:10]}
    )

OUT.write_text(json.dumps(out, indent=2), encoding="utf-8")
print("Wrote", OUT)
