import json
from pathlib import Path
import pandas as pd
import sys
# ensure scripts package is available
ROOT = Path(__file__).resolve().parents[1]
for p in (ROOT, ROOT / "scripts"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

# load p_coset
bundle = Path('H27_OUTER_TWIST_ACTION_BUNDLE_v01')
perm40 = json.loads((bundle / 'perm40_and_H27_pg_ids.json').read_text())
p_coset = perm40['perm40_points_from_phi_n']
# compute p_line via sigma if available
sigma_path = Path('WE6_EVEN_to_PSp43_CONJUGACY_BUNDLE_v01 (1)') / 'sigma_we6coset_to_w33line.json'
p_line = None
if sigma_path.exists():
    sigma = json.loads(sigma_path.read_text())
    if isinstance(sigma, dict) and 'sigma_we6coset_to_w33line' in sigma:
        s = sigma['sigma_we6coset_to_w33line']
    elif isinstance(sigma, dict):
        s = [sigma[str(i)] for i in range(40)]
    else:
        s = sigma
    s_inv = [0]*40
    for i,v in enumerate(s): s_inv[v] = i
    def conj(p): return [s[p[s_inv[i]]] for i in range(40)]
    p_line = conj(p_coset)
    print('computed p_line')

# pg->internal
pg_to_internal = {}
df = pd.read_csv('H27_CE2_FUSION_BRIDGE_BUNDLE_v01/pg_point_to_h27_vertex_coords.csv')
for r in df.itertuples(index=False):
    pg_to_internal[int(r.pg_id)] = int(r.vertex_id)
inf_map = json.loads(Path('pg_to_internal_inf.json').read_text())
for pg, vid in inf_map.items():
    pg_to_internal[int(pg)] = int(vid)
internal_to_pg = {v: k for k, v in pg_to_internal.items()}

p_internal = [None] * 40
for internal in range(40):
    pg = internal_to_pg[internal]
    p_internal[internal] = pg_to_internal[p_coset[pg]]
print('p_internal', p_internal)

# compute p_edge via phi mapping if available
p_edge = None
phi_path = Path('internal_to_edge_labeling.json')
if phi_path.exists():
    phi = {int(k): int(v) for k,v in json.loads(phi_path.read_text()).items()}
    inv_phi = {v:k for k,v in phi.items()}
    p_edge = [None]*40
    for i in range(40):
        j = inv_phi[i]
        k = p_internal[j]
        p_edge[i] = phi[k]
    print('debug_mapping computed p_edge')

from scripts.w33_homology import build_w33
n, verts, adj, edges = build_w33()
edge_set_internal = {tuple(sorted(e)) for e in edges}
# adjacency in edge_to_root labeling
edge_to_root = json.loads((Path('artifacts')/'edge_to_e8_root.json').read_text())
edge_set_label = {tuple(sorted(eval(k))) for k in edge_to_root.keys()}

# check p_internal against internal set
bad = []
for e in edge_set_internal:
    i,j = e
    ni, nj = p_internal[i], p_internal[j]
    e2 = tuple(sorted((ni,nj)))
    if e2 not in edge_set_internal:
        bad.append((e,e2))
print('bad edges count (internal map)', len(bad))
if bad:
    print(bad[:20])
# check p_line against internal set
if p_line is not None:
    bad2 = []
    for e in edge_set_internal:
        i,j = e
        ni, nj = p_line[i], p_line[j]
        e2 = tuple(sorted((ni,nj)))
        if e2 not in edge_set_internal:
            bad2.append((e,e2))
    print('bad edges count (line map vs internal)', len(bad2))
    if bad2:
        print(bad2[:20])
    # also check against label set
    bad2b=[]
    for e in edge_set_label:
        i,j=e
        ni,nj = p_line[i], p_line[j]
        e2=tuple(sorted((ni,nj)))
        if e2 not in edge_set_label:
            bad2b.append((e,e2))
    print('bad edges count (line map vs label)', len(bad2b))
    if bad2b:
        print(bad2b[:20])
# check p_edge against label set
if 'p_edge' in globals() and p_edge is not None:
    bad3 = []
    for e in edge_set_label:
        i,j = e
        ni, nj = p_edge[i], p_edge[j]
        e2 = tuple(sorted((ni,nj)))
        if e2 not in edge_set_label:
            bad3.append((e,e2))
    print('bad edges count (edge map vs label)', len(bad3))
    if bad3:
        print(bad3[:20])
