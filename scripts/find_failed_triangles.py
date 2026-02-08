#!/usr/bin/env python3
"""Enumerate failing triangles for a given bijection and produce hotspot edges.
Writes checks/PART_CVII_failed_triangles_<stamp>.json and a copy to committed_artifacts/.
"""
from __future__ import annotations
import json
import time
from pathlib import Path
from collections import Counter
import sys
sys.path.insert(0, str(Path(__file__).parent))
from e8_embedding_group_theoretic import build_w33, generate_e8_roots
from scripts.w33_e8_bijection import vec_add, vec_neg, vec_sub

inpath = Path('committed_artifacts') / 'PART_CVII_e8_bijection_campaign_result_1770513416.json'
if not inpath.exists():
    raise SystemExit(f'bijection file not found: {inpath}')
obj = json.loads(inpath.read_text(encoding='utf-8'))
bij = {int(k): int(v) for k, v in obj['bijection'].items()}

n, vertices, adj, edges = build_w33()
# enumerate all triangles
triangles = []
edge_index = {edges[i]: i for i in range(len(edges))}
edge_index.update({(v, u): i for (u, v), i in edge_index.items()})
for a in range(n):
    for b in adj[a]:
        if b <= a:
            continue
        for c in adj[b]:
            if c <= b:
                continue
            if a in adj[c]:
                tri = tuple(sorted((a, b, c)))
                if tri not in triangles:
                    triangles.append(tri)

roots = generate_e8_roots()
failed_tris = []
ok = 0
partial = 0
for tri in triangles:
    a, b, c = tri
    e_ab = edge_index.get((a, b))
    e_bc = edge_index.get((b, c))
    e_ac = edge_index.get((a, c))
    if e_ab is None or e_bc is None or e_ac is None:
        continue
    r_ab_idx = bij.get(e_ab)
    r_bc_idx = bij.get(e_bc)
    r_ac_idx = bij.get(e_ac)
    if r_ab_idx is None or r_bc_idx is None or r_ac_idx is None:
        continue
    r_ab = roots[r_ab_idx]
    r_bc = roots[r_bc_idx]
    r_ac = roots[r_ac_idx]
    sums = [tuple(vec_add(r_ab, r_bc)), tuple(vec_sub(r_ab, r_bc)), tuple(vec_add(r_ab, vec_neg(r_bc))), tuple(vec_sub(vec_neg(r_ab), r_bc))]
    targets = {tuple(r_ac), tuple(vec_neg(r_ac))}
    if any(s in targets for s in sums):
        ok += 1
    elif any(s in roots or s == tuple(vec_neg(list(s))) for s in sums):
        partial += 1
    else:
        failed_tris.append({'tri': tri, 'edges': [e_ab, e_bc, e_ac], 'roots': [r_ab_idx, r_bc_idx, r_ac_idx]})

edge_counter = Counter()
for f in failed_tris:
    for e in f['edges']:
        edge_counter[e] += 1

out = {
    'timestamp': time.time(),
    'total_triangles': len(triangles),
    'ok': ok,
    'partial': partial,
    'no_match': len(failed_tris),
    'failed_tris': failed_tris,
    'edge_hotspots': edge_counter.most_common(50),
}

stamp = int(time.time())
checks_dir = Path('checks')
checks_dir.mkdir(parents=True, exist_ok=True)
outpath = checks_dir / f'PART_CVII_failed_triangles_{stamp}.json'
outpath.write_text(json.dumps(out, indent=2), encoding='utf-8')
# mirror to committed_artifacts for committing
comm_dir = Path('committed_artifacts')
comm_dir.mkdir(parents=True, exist_ok=True)
comm_path = comm_dir / outpath.name
comm_path.write_text(outpath.read_text(encoding='utf-8'), encoding='utf-8')
print('Wrote', outpath)
print('Summary:', out['total_triangles'], 'triangles => ok', out['ok'], 'partial', out['partial'], 'no_match', out['no_match'])
print('Top hotspots (edge_index,count):', out['edge_hotspots'][:20])
