#!/usr/bin/env python3
import itertools
from pathlib import Path
import json

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
# load bundle
bundle = Path("H27_OUTER_TWIST_ACTION_BUNDLE_v01")
perm40 = json.loads((bundle / "perm40_and_H27_pg_ids.json").read_text())["perm40_points_from_phi_n"]
print("perm40 matches a permutation?", sorted(perm40)==list(range(40)))
# compute mapping
mapping = [perm40[i] for i in range(40)]
print("mapping (canonical -> phi_n):\n", mapping)
# check how canonical points correspond
print("canonical first13", pts2[:13])
print("canonical next27", pts2[13:])

# build outer twist matrix N4 from the user formula
N4 = [
    [1,0,0,0],
    [0,1,2,0],
    [2,2,0,0],
    [2,2,1,2],
]
# compute permutation of canonical points induced by N4
perm_from_N4 = []
for p in pts2:
    # multiply N4 * p^T mod 3
    v = [sum(N4[i][j]*p[j] for j in range(4)) % 3 for i in range(4)]
    # normalize to canonical rep
    if all(x==0 for x in v):
        raise ValueError("zero vector")
    for x in v:
        if x!=0:
            inv = 1 if x==1 else 2
            v = tuple((inv*y)%3 for y in v)
            break
    perm_from_N4.append(pts2.index(v))
print("perm from N4 equals perm40?", perm_from_N4 == mapping)

# symplectic form J (antisymmetric)
J = [[0,0,0,1],[0,0,1,0],[0,2,0,0],[2,0,0,0]]
# check properties
# adjacency by v^T J w == 0
def mod3(x): return x%3
adj = [[0]*40 for _ in range(40)]
for i,p in enumerate(pts2):
    for j,q in enumerate(pts2):
        if i==j: continue
        val = 0
        for a in range(4):
            for b in range(4):
                val += p[a]*J[a][b]*q[b]
        if mod3(val)==0:
            adj[i][j]=1
# degrees
deg = [sum(row) for row in adj]
print("degree stats", min(deg), max(deg), sum(deg)/40)
# expect degree 12
print(deg)
# test similitude condition
# compute N4^T J N4
NT = [[N4[j][i] for j in range(4)] for i in range(4)]
prod = [[sum(NT[i][k]*J[k][l]*N4[l][j] for k in range(4) for l in range(4))%3 for j in range(4)] for i in range(4)]
print("N4^T J N4", prod)

# compute infinity neighbor sets for affine points
infinity = list(range(13))
affine = list(range(13,40))
neighbor_map = {}
for i in affine:
    neigh = [j for j in infinity if adj[i][j]]
    neighbor_map[i] = neigh
    assert len(neigh)==4, f"expected 4 infinity neighbors for {i}, got {len(neigh)}"
print("All affine points have 4 infinity neighbors")
# orbit decomposition of those 27 sets under outer twist
orbits = []
unvisited = set(affine)
while unvisited:
    start = unvisited.pop()
    orbit = [start]
    cur = start
    while True:
        nxt = perm_from_N4[cur]
        if nxt==start:
            break
        orbit.append(nxt)
        unvisited.discard(nxt)
        cur=nxt
    orbits.append(orbit)
print("outer twist orbits on affine points", orbits)
# also orbit decomposition of neighbor sets
neighbor_orbits = []
unvisited = set(range(13,40))
while unvisited:
    start = unvisited.pop()
    orbit = [start]
    cur = start
    while True:
        nxt = perm_from_N4[cur]
        if nxt==start:
            break
        orbit.append(nxt)
        unvisited.discard(nxt)
        cur=nxt
    neighbor_orbits.append(sorted(orbit))
print("neighbor orbits under outer twist", neighbor_orbits)
# serialize neighbor map for bundle
import json
out = {"neighbor_map": neighbor_map, "outer_orbits": orbits}
with open("PG33_infinity_neighbors.json","w",encoding="utf-8") as f:
    json.dump(out,f,indent=2)
print("wrote PG33_infinity_neighbors.json")
