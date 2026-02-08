#!/usr/bin/env python3
import json
import sys
from pathlib import Path

if len(sys.argv) < 2:
    print('Usage: make_temp_seed.py edge1 edge2 ... [outpath]')
    sys.exit(2)

*edges, last = sys.argv[1:], None
# If last arg ends with .json treat as outpath
outpath = Path('checks') / '_tmp_seed_dd_manual.json'
try:
    if edges and edges[-1].endswith('.json'):
        outpath = Path(edges[-1])
        edges = edges[:-1]
except Exception:
    pass

bij = json.loads(open('committed_artifacts/PART_CVII_e8_bijection_intermediate_1770491863.json', encoding='utf-8').read())['bijection']
seed_edges = []
for e in edges:
    try:
        ie = int(e)
    except:
        continue
    if str(ie) in bij:
        seed_edges.append({'edge_index': ie, 'root_index': int(bij[str(ie)])})

out = {'seed_edges': seed_edges, 'rotation': None}
outpath.write_text(json.dumps(out, indent=2), encoding='utf-8')
print('Wrote', outpath)
