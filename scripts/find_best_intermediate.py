#!/usr/bin/env python3
"""Scan PART_CVII intermediate bijections and report the one with the most exact triangles.

Usage: python scripts/find_best_intermediate.py
"""
from __future__ import annotations

import glob
import importlib.util
import json
from pathlib import Path

# load e8 module
spec_e8 = importlib.util.spec_from_file_location("e8", "scripts/e8_embedding_group_theoretic.py")
e8 = importlib.util.module_from_spec(spec_e8)
spec_e8.loader.exec_module(e8)

# load optimize module (for triangle checking)
spec_opt = importlib.util.spec_from_file_location("opt", "scripts/optimize_bijection_cocycle.py")
opt = importlib.util.module_from_spec(spec_opt)
spec_opt.loader.exec_module(opt)

files = sorted(glob.glob("checks/PART_CVII_e8_bijection_intermediate_*.json"))
best = (None, -1)
for f in files:
    j = json.load(open(f, encoding="utf-8"))
    bij_map = {int(k): int(v) for k, v in j["bijection"].items()}
    n, vertices, adj, edges = e8.build_w33()
    tri_list = opt.build_triangles(n, adj)
    roots = e8.generate_e8_roots()
    exact = sum(1 for t in tri_list if opt.triangle_exact(roots, bij_map, edges, t))
    print(f"{f}: {exact} exact triangles")
    if exact > best[1]:
        best = (f, exact)

print("\nBest intermediate:", best)
