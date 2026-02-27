
from __future__ import annotations
import json, os
from itertools import product
from pathlib import Path

import sys
sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.gf2lin import GF2Matrix

ROOT = Path(__file__).resolve().parents[1]

# Inputs (generated earlier in this chat)
EDGE_MAP_DIR = Path("/mnt/data/TOE_edge_to_oriented_rootpairs_v01_20260227")
CENTRAL_DIR  = Path("/mnt/data/TOE_push_central_extension_edges_v02_20260227")  # extracted folder

def build_projective_points_F3_4():
    F3=[0,1,2]
    pts=[]
    seen=set()
    for v in product(F3, repeat=4):
        if all(x==0 for x in v): 
            continue
        v=list(v)
        for i in range(4):
            if v[i]!=0:
                inv=1 if v[i]==1 else 2
                v=tuple((x*inv)%3 for x in v)
                break
        if v not in seen:
            seen.add(v); pts.append(v)
    assert len(pts)==40
    return pts

def omega_sym(x,y):
    return (x[0]*y[2]-x[2]*y[0] + x[1]*y[3]-x[3]*y[1])%3

def build_isotropic_edges(points):
    edges=[]
    for i in range(40):
        for j in range(i+1,40):
            if omega_sym(points[i], points[j])==0:
                edges.append((i,j))
    assert len(edges)==240
    return edges

def main():
    # Load edge->oriented triple of antipode pairs
    with open(EDGE_MAP_DIR/"edge_to_oriented_rootpair_triple.json","r") as f:
        edge_map = json.load(f)

    # Build the 36 antipode-pairs (vertices) and 120 face triangles
    pairs=set()
    for tri in edge_map.values():
        for a,b in tri:
            pairs.add(tuple(sorted((a,b))))
    pairs_list=sorted(pairs)
    pair_to_vid={p:i for i,p in enumerate(pairs_list)}

    def tri_to_tuple(tri):
        idxs=sorted(pair_to_vid[tuple(sorted(p))] for p in tri)
        return tuple(idxs)

    # Rebuild 240 W33 isotropic edges with deterministic ordering used in the bundle
    pts=build_projective_points_F3_4()
    edges=build_isotropic_edges(pts)
    edgeid_to_key=[f"{i}-{j}" for i,j in edges]

    # Load 120 edgepairs (each is a pair of opposite W33 edges)
    with open(CENTRAL_DIR/"artifacts"/"edge_pairs_120.json","r") as f:
        edgepairs=json.load(f)

    # Build faces as unordered triples of the 36 vertices
    faces=set()
    for rec in edgepairs:
        ea=rec["edge_a"]
        tri = tri_to_tuple(edge_map[edgeid_to_key[ea]])
        faces.add(tuple(sorted(tri)))
    faces=sorted(faces)
    assert len(faces)==120

    # SRG edges = union of triangle edges
    edge_set=set()
    for a,b,c in faces:
        for u,v in ((a,b),(a,c),(b,c)):
            if u>v: u,v=v,u
            edge_set.add((u,v))
    edges36=sorted(edge_set)
    assert len(edges36)==360
    edge_to_eid={e:i for i,e in enumerate(edges36)}

    # Build boundary ∂1 rows: C1->C0 (36 x 360)
    nE=360
    inc_rows=[0]*36
    for eid,(u,v) in enumerate(edges36):
        inc_rows[u] ^= (1<<eid)
        inc_rows[v] ^= (1<<eid)

    # Build face boundary rows ∂2^T: C2->C1 (120 x 360)
    face_rows=[]
    for (a,b,c) in faces:
        eab=edge_to_eid[(a,b)]
        eac=edge_to_eid[tuple(sorted((a,c)))]
        ebc=edge_to_eid[tuple(sorted((b,c)))]
        face_rows.append((1<<eab)|(1<<eac)|(1<<ebc))

    r1 = GF2Matrix.from_rows(nE, inc_rows).rank()
    r2 = GF2Matrix.from_rows(nE, face_rows).rank()

    dim_ker_d1 = nE - r1
    dim_H1 = dim_ker_d1 - r2

    print("Triangle complex over GF(2)")
    print(f"V=36, E=360, F=120")
    print(f"rank(d1) = {r1}")
    print(f"rank(d2) = {r2}")
    print(f"dim ker(d1) = {dim_ker_d1}")
    print(f"dim H1 = {dim_H1}")

if __name__ == "__main__":
    main()
