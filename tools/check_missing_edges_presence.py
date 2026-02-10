#!/usr/bin/env python3
"""Check whether edges listed in missing edges JSON are still absent in combined mapping"""
from __future__ import annotations

import json
from pathlib import Path

miss_path = Path('analysis/minimal_commutator_cycles/w33_uv_parser_det1_missing_edges.json')
combined_path = Path('artifacts/edge_to_e8_root_combined.json')
if not miss_path.exists():
    print('Missing edges file not found:', miss_path)
    raise SystemExit(1)
if not combined_path.exists():
    print('Combined mapping not found:', combined_path)
    raise SystemExit(1)

miss = json.loads(miss_path.read_text(encoding='utf-8')).get('missing_edges', [])
combined = json.loads(combined_path.read_text(encoding='utf-8'))

present = []
absent = []
for ent in miss:
    e = ent.get('edge')
    if not e:
        continue
    a_s, b_s = e.split(',')
    key = f"({int(a_s)}, {int(b_s)})"
    if key in combined:
        present.append(e)
    else:
        absent.append(e)

print('Edges present (from missing list):', len(present))
for e in present:
    print(' P', e)
print('\nEdges absent (still missing):', len(absent))
for e in absent:
    print(' M', e)
