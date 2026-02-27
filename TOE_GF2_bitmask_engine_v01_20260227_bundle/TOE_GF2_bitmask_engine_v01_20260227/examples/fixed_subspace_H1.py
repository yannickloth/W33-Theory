
from __future__ import annotations
import json
from itertools import product
from pathlib import Path

import sys
sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.gf2lin import GF2Matrix

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
    return pts

def omega_sym(x,y):
    return (x[0]*y[2]-x[2]*y[0] + x[1]*y[3]-x[3]*y[1])%3

def build_isotropic_edges(points):
    edges=[]
    for i in range(40):
        for j in range(i+1,40):
            if omega_sym(points[i], points[j])==0:
                edges.append((i,j))
    return edges

def main():
    # Load generators on roots (240) and antipode involution
    with open(EDGE_MAP_DIR/"sp43_generators_on_roots_240.json","r") as f:
        gen_roots = json.load(f)

    with open(EDGE_MAP_DIR/"edge_to_oriented_rootpair_triple.json","r") as f:
        edge_map = json.load(f)

    # Build 36 antipode-pairs used in the mapping
    pairs=set()
    for tri in edge_map.values():
        for a,b in tri:
            pairs.add(tuple(sorted((a,b))))
    pairs_list=sorted(pairs)
    pair_to_vid={p:i for i,p in enumerate(pairs_list)}

    # Induce generators on 36 antipode-pairs
    gen_pairs=[]
    for g in gen_roots:
        perm=[pair_to_vid[tuple(sorted((g[a],g[b])))] for (a,b) in pairs_list]
        gen_pairs.append(perm)

    # Build faces (120) from edgepairs list
    pts=build_projective_points_F3_4()
    edges240=build_isotropic_edges(pts)
    edgeid_to_key=[f"{i}-{j}" for i,j in edges240]

    with open(CENTRAL_DIR/"artifacts"/"edge_pairs_120.json","r") as f:
        edgepairs=json.load(f)

    def tri_to_tuple(tri):
        return tuple(sorted(pair_to_vid[tuple(sorted(p))] for p in tri))

    faces=set()
    for rec in edgepairs:
        ea=rec["edge_a"]
        faces.add(tuple(sorted(tri_to_tuple(edge_map[edgeid_to_key[ea]]))))
    faces=sorted(faces)

    # SRG edges (360) induced from faces
    edge_set=set()
    for a,b,c in faces:
        for u,v in ((a,b),(a,c),(b,c)):
            if u>v: u,v=v,u
            edge_set.add((u,v))
    edges36=sorted(edge_set)
    edge_to_eid={e:i for i,e in enumerate(edges36)}

    # ∂1 constraints rows (36 equations in 360 vars)
    nE=360
    inc_rows=[0]*36
    for eid,(u,v) in enumerate(edges36):
        inc_rows[u] ^= (1<<eid)
        inc_rows[v] ^= (1<<eid)

    # face -> its 3 edge ids
    face_edges=[]
    for a,b,c in faces:
        e1=edge_to_eid[(a,b)]
        e2=edge_to_eid[tuple(sorted((a,c)))]
        e3=edge_to_eid[tuple(sorted((b,c)))]
        face_edges.append((e1,e2,e3))

    # Induce generators on edges (360)
    gen_edges=[]
    for gp in gen_pairs:
        perm=[]
        for (u,v) in edges36:
            u2,v2=gp[u], gp[v]
            e=tuple(sorted((u2,v2)))
            perm.append(edge_to_eid[e])
        gen_edges.append(perm)

    inv_edges=[]
    for perm in gen_edges:
        inv=[0]*360
        for e,ep in enumerate(perm):
            inv[ep]=e
        inv_edges.append(inv)

    # Constraints for fixed classes in H1:
    # x in ker ∂1 AND for each generator and each face, d(e1)=d(e2)=d(e3) where d(e)=x_e+x_{inv(e)}.
    rows=[]
    rows.extend(inc_rows)
    for inv in inv_edges:
        for e1,e2,e3 in face_edges:
            eq=0
            for e in (e1, inv[e1], e2, inv[e2]):
                eq ^= (1<<e)
            rows.append(eq)
            eq=0
            for e in (e1, inv[e1], e3, inv[e3]):
                eq ^= (1<<e)
            rows.append(eq)

    rank = GF2Matrix.from_rows(nE, rows).rank()
    dimS = nE - rank            # solutions x in C1 satisfying all constraints
    dimB = len(faces)           # im ∂2 has dimension 120 (faces are independent)
    dim_fixed_H1 = dimS - dimB  # quotient by boundaries

    print("Fixed subspace in H1 under all 10 generators (GF(2))")
    print(f"rank(constraints) = {rank}")
    print(f"dim(S) = {dimS}")
    print(f"dim(B) = {dimB}")
    print(f"dim(H1^G) = {dim_fixed_H1}")

if __name__ == "__main__":
    main()
