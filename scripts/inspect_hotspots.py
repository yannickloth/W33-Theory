#!/usr/bin/env python3
"""Inspect hotspot edges and their assigned E8 roots/sectors to help diagnosis."""
from __future__ import annotations
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent))
from e8_embedding_group_theoretic import build_w33, generate_e8_roots
from w33_e8_bijection import classify_roots_z3_grading

# locate latest hotspots and latest bijection
hotspots = sorted(Path('checks').glob('PART_CVII_conflict_hotspots_*.json'))
if not hotspots:
    raise SystemExit('No hotspots file found in checks/')
hot = json.loads(hotspots[-1].read_text(encoding='utf-8'))

bfiles = sorted(Path('committed_artifacts').glob('PART_CVII_e8_bijection_intermediate_*.json'))
if not bfiles:
    raise SystemExit('No committed bijection found')
bij = json.loads(bfiles[-1].read_text(encoding='utf-8'))
bij_map = {int(k): int(v) for k, v in bij.get('bijection', {}).items()}

n, vertices, adj, edges = build_w33()
roots = generate_e8_roots()
z3 = classify_roots_z3_grading(roots)

print('Hotspots source:', hotspots[-1])
for h in hot['hotspots_top20'][:20]:
    idx = h['edge_index']
    uv = h['edge']
    cnt = h['count']
    root_idx = bij_map.get(idx)
    root_vec = roots[root_idx] if root_idx is not None else None
    sector = None
    if root_idx is not None:
        if root_idx in z3['g0']:
            sector = 'g0'
        elif root_idx in z3['g1']:
            sector = 'g1'
        elif root_idx in z3['g2']:
            sector = 'g2'
    print(f"edge_idx={idx} edge={uv} count={cnt} -> root_idx={root_idx} sector={sector} vec={root_vec}")
