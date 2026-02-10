#!/usr/bin/env python3
"""Check which 'ok' cycles from w33_uv_parser_det1_results.json are missing oriented edges in artifacts/edge_to_e8_root_combined.json"""
from __future__ import annotations

import json
from pathlib import Path

rows = json.loads(Path('analysis/minimal_commutator_cycles/w33_uv_parser_det1_results.json').read_text(encoding='utf-8')).get('rows', [])
edge_data = json.loads(Path('artifacts/edge_to_e8_root_combined.json').read_text(encoding='utf-8'))

edge_map = {}
if isinstance(edge_data, dict):
    for k, coords in edge_data.items():
        if isinstance(k, str) and k.startswith('(') and ',' in k:
            s = k.strip()[1:-1]
            a,b = s.split(',')
            a=int(a.strip()); b=int(b.strip())
            coords_t = tuple(int(x) for x in coords)
            edge_map[(a,b)] = coords_t
            edge_map[(b,a)] = tuple(-x for x in coords_t)
else:
    for ent in edge_data:
        a = int(ent.get('v_i'))
        b = int(ent.get('v_j'))
        coords = tuple(int(x) for x in ent.get('root_coords'))
        edge_map[(a,b)] = coords
        edge_map[(b,a)] = tuple(-x for x in coords)

ok_total=0
ok_missing=0
missing_cycles=[]
for r in rows:
    if r.get('status')!='ok':
        continue
    ok_total+=1
    cyc = r.get('cycle')
    n=len(cyc)
    missing=False
    for i in range(n):
        a=cyc[i]
        b=cyc[(i+1)%n]
        if (a,b) not in edge_map:
            missing=True
            break
    if missing:
        ok_missing+=1
        missing_cycles.append((r.get('idx'),cyc))

print('ok_total', ok_total, 'ok_missing', ok_missing)
print('Example missing cycles (first 10):')
for i, cyc in missing_cycles[:10]:
    print(i, cyc)
