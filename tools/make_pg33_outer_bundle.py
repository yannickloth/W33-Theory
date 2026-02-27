#!/usr/bin/env python3
"""Build a small certificate bundle for the PG(3,3) outer twist geometry.

Output structure:
  PG33_points.json        - canonical point list as 4-tuples
  outer_matrix.json       - N4 matrix mod3
  symplectic_form.json    - J matrix mod3
  perm40_from_canonical.json - canonical->phi_n permutation
  infinity_neighbors.json - map affine->list of 4 infinity neighbors
  outer_orbits.json       - orbits of affine points under outer twist

and then zip everything to PG33_OUTER_TWIST_GEOMETRY_BUNDLE_v01.zip.
"""
import itertools
import json
from pathlib import Path

bundle_dir = Path("_tmp_pg33_bundle")
bundle_dir.mkdir(exist_ok=True)

# canonical PG(3,3)
pts=[]
for v in itertools.product(range(3), repeat=4):
    if all(x==0 for x in v): continue
    for x in v:
        if x!=0:
            inv = 1 if x==1 else 2
            norm = tuple((inv*y)%3 for y in v)
            pts.append(norm)
            break
seen=set(); unique=[]
for p in pts:
    if p not in seen:
        seen.add(p); unique.append(p)
pts2=sorted(unique)
assert len(pts2)==40

# outer twist matrix
N4 = [
    [1,0,0,0],
    [0,1,2,0],
    [2,2,0,0],
    [2,2,1,2],
]

# canonical->phi_n permutation (should match existing bundle if present)
bundle_existing = Path("H27_OUTER_TWIST_ACTION_BUNDLE_v01")
if bundle_existing.exists():
    perm40 = json.loads((bundle_existing / "perm40_and_H27_pg_ids.json").read_text())["perm40_points_from_phi_n"]
else:
    perm40 = list(range(40))

# symplectic form J
J = [[0,0,0,1],[0,0,1,0],[0,2,0,0],[2,0,0,0]]

# compute neighbor sets and orbits as in check script
adj = [[0]*40 for _ in range(40)]
for i,p in enumerate(pts2):
    for j,q in enumerate(pts2):
        if i==j: continue
        val = sum(p[a]*J[a][b]*q[b] for a in range(4) for b in range(4))%3
        if val==0:
            adj[i][j]=1
infinity=list(range(13)); affine=list(range(13,40))
neighbor_map={}
for i in affine:
    neigh=[j for j in infinity if adj[i][j]]
    neighbor_map[i]=neigh
orbits=[]
unvisited=set(affine)
while unvisited:
    start=unvisited.pop()
    orbit=[start]
    cur=start
    while True:
        nxt = perm40[cur]
        if nxt==start: break
        orbit.append(nxt)
        unvisited.discard(nxt)
        cur=nxt
    orbits.append(orbit)

# write files
(bundle_dir / "PG33_points.json").write_text(json.dumps(pts2))
(bundle_dir / "outer_matrix.json").write_text(json.dumps(N4))
(bundle_dir / "symplectic_form.json").write_text(json.dumps(J))
(bundle_dir / "perm40_from_canonical.json").write_text(json.dumps(perm40))
(bundle_dir / "infinity_neighbors.json").write_text(json.dumps(neighbor_map))
(bundle_dir / "outer_orbits.json").write_text(json.dumps(orbits))

# compute edge list and orbits under outer twist
edges = []
for i in range(40):
    for j in range(i+1, 40):
        if adj[i][j]:
            edges.append([i, j])
assert len(edges) == 240, f"expected 240 edges, got {len(edges)}"
# map each edge to its index for orbit computation
edge_index = {tuple(e): idx for idx, e in enumerate(edges)}
edge_orbits = []
unseen = set(range(len(edges)))
while unseen:
    start = unseen.pop()
    orb = [start]
    idx = start
    while True:
        i, j = edges[idx]
        ni = perm40[i]
        nj = perm40[j]
        if ni > nj:
            ni, nj = nj, ni
        nxt = edge_index[(ni, nj)]
        if nxt == start:
            break
        orb.append(nxt)
        unseen.discard(nxt)
        idx = nxt
    edge_orbits.append(orb)
(bundle_dir / "edge_orbits.json").write_text(json.dumps(edge_orbits))

# create zip
import zipfile
zip_path = Path("PG33_OUTER_TWIST_GEOMETRY_BUNDLE_v01.zip")
with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as z:
    for file in bundle_dir.iterdir():
        z.write(file, arcname=file.name)
print("wrote", zip_path)
# also update a directory copy for easier access
out_dir = Path("PG33_OUTER_TWIST_GEOMETRY_BUNDLE_v01")
if out_dir.exists():
    for f in out_dir.iterdir():
        f.unlink()
else:
    out_dir.mkdir()
for file in bundle_dir.iterdir():
    dest = out_dir / file.name
    dest.write_bytes(file.read_bytes())
print("updated directory", out_dir)
