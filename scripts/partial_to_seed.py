#!/usr/bin/env python3
import json

IN = 'checks/PART_CVII_e8_embedding_backtrack_partial.json'
OUT = 'checks/PART_CVII_e8_backtrack_seed.json'

d = json.load(open(IN))
edge_map = d.get('edge_to_root', {})
seed_edges = [{'edge_index': int(k), 'root_index': int(v)} for k, v in edge_map.items()]
with open(OUT, 'w') as f:
    json.dump({'seed_edges': seed_edges}, f, indent=2)
print('Wrote', OUT, 'entries=', len(seed_edges))
