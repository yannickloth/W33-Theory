#!/usr/bin/env python3
"""Find best intermediate and patched bijection artifacts.

Usage: py -3 scripts/find_best_artifacts.py
"""
from __future__ import annotations

import glob
import importlib.util
import json

# load modules
spec_e8 = importlib.util.spec_from_file_location('e8','scripts/e8_embedding_group_theoretic.py')
e8 = importlib.util.module_from_spec(spec_e8)
spec_e8.loader.exec_module(e8)

spec_opt = importlib.util.spec_from_file_location('opt','scripts/optimize_bijection_cocycle.py')
opt = importlib.util.module_from_spec(spec_opt)
spec_opt.loader.exec_module(opt)

n, vertices, adj, edges = e8.build_w33()
tri_list = opt.build_triangles(n, adj)
roots = e8.generate_e8_roots()

best_inter = (None, -1)
for f in sorted(glob.glob('checks/PART_CVII_e8_bijection_intermediate_*.json')):
    try:
        bij_map = {int(k):int(v) for k,v in json.load(open(f,encoding='utf-8'))['bijection'].items()}
    except Exception:
        continue
    exact = sum(1 for t in tri_list if opt.triangle_exact(roots, bij_map, edges, t))
    if exact > best_inter[1]: best_inter = (f, exact)

best_patched = (None, -1)
for f in sorted(glob.glob('checks/PART_CVII_e8_bijection_patched_*.json')):
    try:
        j = json.load(open(f,encoding='utf-8'))
    except Exception:
        continue
    ae = j.get('after_exact')
    if ae is None:
        continue
    if ae > best_patched[1]: best_patched = (f, ae)

print('Best intermediate:', best_inter)
print('Best patched:', best_patched)
