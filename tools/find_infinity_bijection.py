#!/usr/bin/env python3
"""Attempt to match PG infinity IDs 0..12 with internal vertex IDs.

Uses adjacency to the 27 affine points (known mapping from PG to internal) to
solve for a bijection satisfying the neighbor_map patterns computed from
PG geometry.

Writes out a JSON file `pg_to_internal_inf.json` if successful.
"""
from pathlib import Path
import json
from itertools import permutations

# load H27 mapping for affines
import pandas as pd

df = pd.read_csv("H27_CE2_FUSION_BRIDGE_BUNDLE_v01/pg_point_to_h27_vertex_coords.csv")
pg_to_vid = {int(r.pg_id): int(r.vertex_id) for r in df.itertuples(index=False)}
affine_pg = [i for i in range(13,40)]
affine_vid = [pg_to_vid[i] for i in affine_pg]

# build W33 graph adjacency
import sys
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from scripts.w33_homology import build_w33
n, verts, adj, edges = build_w33()

# neighbor_map as computed earlier (PG IDs -> list of infPG)
# replicate computation from test or script
import numpy as np
pts = json.loads((Path("PG33_OUTER_TWIST_GEOMETRY_BUNDLE_v01") / "PG33_points.json").read_text())
J = np.array([[0,0,0,1],[0,0,1,0],[0,2,0,0],[2,0,0,0]], dtype=int)

pg_adj_inf = {i: [] for i in range(13)}
for i in affine_pg:
    neigh = []
    for j in range(13):
        # compute index mapping to canonical pts order? we assume PG IDs correspond to pts list indices
        val = (np.array(pts[i]) @ J @ np.array(pts[j])) % 3
        if val == 0:
            neigh.append(j)
    # neighbor_map, but we only need invert mapping
    for inf in neigh:
        pg_adj_inf[inf].append(i)

# determine internal infinity candidate IDs (complement of affine_vid in 0..39)
all_vid=set(range(40))
inf_vids=sorted(all_vid - set(affine_vid))
print("candidate inf vids", inf_vids)

# compute for each inf_vid which affines it's adjacent to
int_adj_inf = {}
for v in inf_vids:
    neigh = [a for a in affine_vid if v in adj[a]]
    int_adj_inf[v] = neigh

# convert these lists to sets of pg indices using reverse of pg_to_vid
vid_to_pg = {v:k for k,v in pg_to_vid.items()}

pg_sets = {inf: set(pg_adj_inf[inf]) for inf in pg_adj_inf}
int_sets = {v: {vid_to_pg[a] for a in neigh} for v,neigh in int_adj_inf.items()}

# we need to match pg_sets to int_sets
# brute force search using backtracking with pruning
solutions=[]

pg_keys = list(pg_sets.keys())
int_keys = list(int_sets.keys())

# use simple recursion
used = set()
mapping = {}


def backtrack(i=0):
    if i==len(pg_keys):
        solutions.append(mapping.copy())
        return True
    pgk = pg_keys[i]
    target_set = pg_sets[pgk]
    for intk in int_keys:
        if intk in used: continue
        if int_sets[intk]==target_set:
            used.add(intk)
            mapping[pgk]=intk
            backtrack(i+1)
            used.remove(intk)
            mapping.pop(pgk)
    return False

backtrack()
print("found", len(solutions), "solutions")
if solutions:
    Path("pg_to_internal_inf.json").write_text(json.dumps(solutions[0], indent=2))
    print("wrote pg_to_internal_inf.json")
