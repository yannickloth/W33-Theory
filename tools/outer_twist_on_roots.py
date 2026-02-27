#!/usr/bin/env python3
"""Compute explicit permutation on E8 roots induced by outer twist.

This version uses the direct PG→internal vertex mapping (27 affine points from
H27 bundle plus computed 13 infinity mapping) to convert the outer-twist
permutation from the PG label to the internal label, and then pushes that
permutation through the existing edge->root bijection.

Output is written to artifacts/outer_twist_root_action_certificate.json with
cycle structure and explicit mapping.
"""
import json, zipfile, ast
from pathlib import Path
from collections import Counter

import pandas as pd

ROOT = Path(".").resolve()
OUTER_BUNDLE = Path("H27_OUTER_TWIST_ACTION_BUNDLE_v01")
# locate conjugacy directory (may have " (1)" suffix due to attachment name)
CONJ_DIR = Path("WE6_EVEN_to_PSp43_CONJUGACY_BUNDLE_v01")
if not CONJ_DIR.exists():
    alt = Path("WE6_EVEN_to_PSp43_CONJUGACY_BUNDLE_v01 (1)")
    if alt.exists():
        CONJ_DIR = alt
    else:
        raise FileNotFoundError("conjugacy bundle directory not found")

# helper to load JSON from either a zip or dir

def load_from(bundle, name):
    if bundle.is_dir():
        return json.loads((bundle / name).read_text())
    else:
        with zipfile.ZipFile(bundle) as z:
            return json.loads(z.read(name))

# 1) outer twist p_coset from PG labeling
perm40 = load_from(OUTER_BUNDLE, "perm40_and_H27_pg_ids.json")
p_coset = perm40["perm40_points_from_phi_n"]

# 1a) compute psi: PG -> edge-labeling mapping
psi_path = Path('pg_to_edge_labeling.json')
if not psi_path.exists():
    raise FileNotFoundError("psi mapping file pg_to_edge_labeling.json missing")
psi = {int(k): int(v) for k, v in json.loads(psi_path.read_text()).items()}
psi_inv = {v: k for k, v in psi.items()}

# 1b) permutation in label space
p_label = [None] * 40
for i in range(40):
    pg = psi_inv[i]
    p_label[i] = psi[p_coset[pg]]

# optional: load sigma conjugator if available and compute p_line for reference
sigma_path = CONJ_DIR / "sigma_we6coset_to_w33line.json"
p_line = None
if sigma_path.exists():
    sigma = json.loads(sigma_path.read_text())
    if isinstance(sigma, dict):
        # expect key 'sigma_we6coset_to_w33line'
        if "sigma_we6coset_to_w33line" in sigma:
            s = sigma["sigma_we6coset_to_w33line"]
        else:
            # try to interpret as mapping str->int
            s = [sigma[str(i)] for i in range(40)]
    else:
        s = sigma
    s_inv = [0]*40
    for i,v in enumerate(s):
        s_inv[v]=i
    def conj(p):
        return [s[p[s_inv[i]]] for i in range(40)]
    p_line = conj(p_coset)
    print("computed p_line via sigma from conjugacy bundle")

# 2) build PG->internal bijection
pg_to_internal = {}
# affine points from H27 fusion bridge
df = pd.read_csv("H27_CE2_FUSION_BRIDGE_BUNDLE_v01/pg_point_to_h27_vertex_coords.csv")
for r in df.itertuples(index=False):
    pg_to_internal[int(r.pg_id)] = int(r.vertex_id)
# infinity mapping computed earlier
inf_map = json.loads(Path("pg_to_internal_inf.json").read_text())
for pg, vid in inf_map.items():
    pg_to_internal[int(pg)] = int(vid)
assert len(pg_to_internal) == 40
internal_to_pg = {v: k for k, v in pg_to_internal.items()}

# derive permutation on internal vertices (useful for cross-checks)
p_internal = [None] * 40
for internal in range(40):
    pg = internal_to_pg[internal]
    pg2 = p_coset[pg]
    p_internal[internal] = pg_to_internal[pg2]

# try to load mapping from internal to edge-label (phi)
p_edge = None
phi_path = Path("internal_to_edge_labeling.json")
if phi_path.exists():
    phi = {int(k): int(v) for k, v in json.loads(phi_path.read_text()).items()}
    inv_phi = {v: k for k, v in phi.items()}
    p_edge = [None] * 40
    for i in range(40):
        j = inv_phi[i]
        k = p_internal[j]
        p_edge[i] = phi[k]
    print("computed p_edge permutation using phi mapping")

# require some permutation for root computation
if p_edge is None and p_line is None:
    raise RuntimeError("no suitable permutation (p_edge or p_line) for root action")

# 3) push through edge->root bijection
edge_to_root = json.loads((ROOT / "artifacts" / "edge_to_e8_root.json").read_text())
edge_to_root = {tuple(ast.literal_eval(k)): tuple(v) for k, v in edge_to_root.items()}
edge_to_root = {tuple(sorted(e)): r for e, r in edge_to_root.items()}

# use p_label to act on edges
root_perm = {}
perm_used = p_label
print("using p_label (PG->label) for root action")
for (i, j), r in edge_to_root.items():
    ni, nj = perm_used[i], perm_used[j]
    e2 = tuple(sorted((ni, nj)))
    root_perm[r] = edge_to_root[e2]

# cycle analysis
seen = set(); cycle_lens = []
for r in root_perm:
    if r in seen: continue
    cur = r; length = 0
    while cur not in seen:
        seen.add(cur); length += 1
        cur = root_perm[cur]
    cycle_lens.append(length)

print("Root cycle structure:", Counter(cycle_lens))

# write certificate
out = {
    "p_coset": p_coset,
    "p_internal": p_internal,
    "root_cycle_structure": dict(Counter(cycle_lens)),
    "root_perm": {str(k): list(v) for k, v in root_perm.items()},
}
(ROOT / "artifacts" / "outer_twist_root_action_certificate.json").write_text(
    json.dumps(out, indent=2, sort_keys=True)
)
print("Wrote artifacts/outer_twist_root_action_certificate.json")
