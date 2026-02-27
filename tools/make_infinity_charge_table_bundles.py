#!/usr/bin/env python3
"""Generate the infinity neighbor charge table and direction decomposition bundles.

Produces two zip archives:

1. INFINITY_NEIGHBOR_CHARGE_TABLE_BUNDLE_v01.zip
   - u_to_4_infinity_neighbors_compressed9.csv
   - affine_point_to_4_infinity_neighbors_full27.csv
   - pg33_point_coordinates.csv
   - symplectic_form_and_outer_matrix.json
   - W33_collinearity_edges_240.csv
   - neighbor_map.json
   - orbits_outer.json
   - orbits_P.json
   - orbits_NP.json

2. W33_DIRECTION_DECOMPOSITION_BUNDLE_v01.zip
   - edges_with_direction_and_triangle_class.csv
   - lines_40_with_direction_and_affine_triples.csv
   - direction_inf_id_to_3_affine_lines.csv

"""
from pathlib import Path
import json
import csv
import zipfile
import sys
# ensure the `scripts` package is importable when running from workspace root
top = Path(__file__).resolve().parents[1]
for p in (top, top / "scripts"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

# helper to compute orbits of a set under group given as list of perms

def compute_orbits(pts, group):
    pts = list(pts)
    unvis = set(pts)
    orbs = []
    while unvis:
        start = unvis.pop()
        orb = {start}
        changed = True
        while changed:
            changed = False
            for g in group:
                new = {g[p] for p in orb}
                if not new.issubset(orb):
                    orb |= new
                    changed = True
        orbs.append(sorted(orb))
        unvis -= orb
    return orbs

# load PG33 coords
bundle = Path("PG33_OUTER_TWIST_GEOMETRY_BUNDLE_v01")
pts = json.loads((bundle / "PG33_points.json").read_text())
# pts is list of 40 quadruples
# load neighbor_map and orbits produced earlier by compute_neighbor_orbit_classification
# JSON keys are strings so convert back to ints for convenience
raw_neighbor = json.loads((Path("neighbor_map.json")).read_text())
neighbor_map = {int(k): [int(x) for x in v] for k, v in raw_neighbor.items()}
outer_orbits = json.loads((Path("orbits_outer.json")).read_text())
P_orbits = json.loads((Path("orbits_P.json")).read_text())
NP_orbits = json.loads((Path("orbits_NP.json")).read_text())
# load PG coordinate csv mapping PG id to x,y,t
coord = {}
with open("H27_CE2_FUSION_BRIDGE_BUNDLE_v01/pg_point_to_h27_vertex_coords.csv","r",encoding="utf-8") as f:
    rdr = csv.DictReader(f)
    for r in rdr:
        coord[int(r["pg_id"])] = (int(r["x"]), int(r["y"]), int(r["t"]))

# compute compressed 9 map -- only affine points have coords
compressed = {}
for pgid, neigh in neighbor_map.items():
    if pgid not in coord:
        # skip the 13 infinity points
        continue
    u = coord[pgid][:2]
    compressed.setdefault(tuple(u), neigh)
assert len(compressed) == 9, "expected 9 distinct affine directions"

# write first bundle files to temporary directory
cdir = Path("_tmp_infinity_bundle")
cdir.mkdir(exist_ok=True)
# u_to_4 ...
with open(cdir / "u_to_4_infinity_neighbors_compressed9.csv","w",encoding="utf-8",newline="") as f:
    w = csv.writer(f)
    w.writerow(["x","y","inf1","inf2","inf3","inf4"])
    for (x,y), neigh in sorted(compressed.items()):
        w.writerow([x,y] + neigh)
# full affine map
with open(cdir / "affine_point_to_4_infinity_neighbors_full27.csv","w",encoding="utf-8",newline="") as f:
    w = csv.writer(f)
    w.writerow(["pg_id","x","y","t","inf1","inf2","inf3","inf4"])
    for pgid in sorted(neighbor_map.keys()):
        # infinity points don't appear in coord mapping; skip them or fill blanks
        if pgid in coord:
            x,y,t = coord[pgid]
        else:
            x,y,t = (None,None,None)
        w.writerow([pgid,x,y,t] + neighbor_map[pgid])
# PG33 point coordinates
with open(cdir / "pg33_point_coordinates.csv","w",encoding="utf-8",newline="") as f:
    w = csv.writer(f)
    w.writerow(["pg_id","X0","X1","X2","X3"])
    for i, pt in enumerate(pts):
        w.writerow([i] + list(pt))
# symplectic form and outer matrix
J = [[0,0,0,1],[0,0,1,0],[0,2,0,0],[2,0,0,0]]
N4 = [[1,0,0,0],[0,1,2,0],[2,2,0,0],[2,2,1,2]]
with open(cdir / "symplectic_form_and_outer_matrix.json","w",encoding="utf-8") as f:
    json.dump({"J":J,"N4":N4,"multiplier":2},f,indent=2)
# W33 edges from adjacency
from scripts.w33_homology import build_w33
n, verts, adj, edges = build_w33()
with open(cdir / "W33_collinearity_edges_240.csv","w",encoding="utf-8",newline="") as f:
    w = csv.writer(f)
    w.writerow(["v1","v2"])
    for i,j in edges:
        w.writerow([i,j])
# also copy neighbor_map and orbits for transparency
with open(cdir / "neighbor_map.json","w",encoding="utf-8") as f:
    json.dump(neighbor_map,f,indent=2)
with open(cdir / "orbits_outer.json","w",encoding="utf-8") as f:
    json.dump(outer_orbits,f,indent=2)
with open(cdir / "orbits_P.json","w",encoding="utf-8") as f:
    json.dump(P_orbits,f,indent=2)
with open(cdir / "orbits_NP.json","w",encoding="utf-8") as f:
    json.dump(NP_orbits,f,indent=2)

# create first zip
zip1 = Path("INFINITY_NEIGHBOR_CHARGE_TABLE_BUNDLE_v01.zip")
with zipfile.ZipFile(zip1,"w",compression=zipfile.ZIP_DEFLATED) as z:
    for file in cdir.iterdir():
        z.write(file,arcname=file.name)
print("wrote",zip1)

# now second bundle: direction decomposition
# compute direction label for each edge and triangle
triangle_sets = [{1,2,3},{4,5,6},{7,8,9},{10,11,12}]

def triangle_class(d):
    for idx,s in enumerate(triangle_sets):
        if d in s:
            return idx
    return None

edges_with_labels = []
for i,j in edges:
    if i<13 and j<13:
        d = i  # choose first endpoint
    elif i<13 or j<13:
        d = i if i<13 else j
    else:
        # both affine
        inter = set(neighbor_map[i]).intersection(neighbor_map[j])
        d = next(iter(inter)) if inter else None
    tri = triangle_class(d) if d is not None else None
    edges_with_labels.append((i,j,d,tri))

with open(cdir / "edges_with_direction_and_triangle_class.csv","w",encoding="utf-8",newline="") as f:
    w=csv.writer(f)
    w.writerow(["v1","v2","direction","triangle_class"])
    for row in edges_with_labels:
        w.writerow(list(row))

# compute 40 lines (4-cliques)
lines=[]
for i in range(40):
    for j in range(i+1,40):
        if j not in adj[i]: continue
        for k in range(j+1,40):
            if k not in adj[i] or k not in adj[j]: continue
            for l in range(k+1,40):
                if l not in adj[i] or l not in adj[j] or l not in adj[k]: continue
                lines.append((i,j,k,l))
# remove duplicates
lines = sorted(lines)
with open(cdir / "lines_40_with_direction_and_affine_triples.csv","w",encoding="utf-8",newline="") as f:
    w=csv.writer(f)
    w.writerow(["line_vertices","direction","affine_points"])
    for line in lines:
        aff = [v for v in line if v>=13]
        # determine direction from aff if any
        if aff:
            # choose neighbor intersection of first two aff
            a=aff[0]; b=aff[1] if len(aff)>1 else aff[0]
            inter=set(neighbor_map[a]).intersection(neighbor_map[b])
            d = next(iter(inter)) if inter else None
        else:
            d = None
        w.writerow([list(line),d,aff])

# direction to 3 affine lines: group by direction and list affines
dir_to_aff = {}
for pgid,neigh in neighbor_map.items():
    # determine direction id as frozenset of neighbours
    for dir_id, neighs in compressed.items():
        if neigh == neighs:
            did = dir_id
            break
    else:
        did = None
    dir_to_aff.setdefault(did, []).append(pgid)
# each list should be length3
with open(cdir / "direction_inf_id_to_3_affine_lines.csv","w",encoding="utf-8",newline="") as f:
    w=csv.writer(f)
    w.writerow(["direction","affine_points"])
    for did, affs in dir_to_aff.items():
        w.writerow([did, affs])

# create second zip
zip2 = Path("W33_DIRECTION_DECOMPOSITION_BUNDLE_v01.zip")
with zipfile.ZipFile(zip2,"w",compression=zipfile.ZIP_DEFLATED) as z:
    for file in cdir.iterdir():
        if file.name.startswith("u_to_") or file.name.startswith("affine_") or file.name.startswith("pg33_") or file.name.endswith('.csv') or file.suffix=='.json':
            z.write(file,arcname=file.name)
print("wrote",zip2)
