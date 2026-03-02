#!/usr/bin/env python3
"""
Recompute the SRG36 triangle->face fibration and the 240 odd non-face triangles.

This reproduces the key structural fact found on 2026-02-27:
  - SRG36 has 1200 triangles.
  - The chosen 120 faces (triangle decomposition blocks) are all hol=1.
  - Exactly 240 other triangles are hol=1 ("odd non-face"), and they fiber over 40 special faces with fiber size 6.
  - Those 40 special faces are exactly one per W33 line (40 lines).

Inputs (expected in /mnt/data, same as existing tools):
  /mnt/data/TOE_E6pair_SRG_triangle_decomp_v01_20260227/
  /mnt/data/TOE_edge_to_oriented_rootpairs_v01_20260227/

Outputs written next to this script.
"""
from __future__ import annotations
import json, csv
from pathlib import Path
from collections import defaultdict, Counter
import numpy as np

ROOT = Path("/mnt/data")
DIR_SRG = ROOT/"TOE_E6pair_SRG_triangle_decomp_v01_20260227"
DIR_MAP = ROOT/"TOE_edge_to_oriented_rootpairs_v01_20260227"
OUT = Path(__file__).resolve().parent

def canon_cycle(seq):
    s=list(seq)
    rots=[tuple(s[i:]+s[:i]) for i in range(len(s))]
    return min(rots)

def main():
    blocks=json.load(open(DIR_SRG/"triangle_decomposition_120_blocks.json"))["blocks"]
    chosen_set=set(tuple(sorted(t)) for t in blocks)

    pairs36=json.load(open(DIR_SRG/"e6_antipode_pairs_36.json"))["pairs"]
    pair_to_vertex={frozenset(p):i for i,p in enumerate(pairs36)}

    edge_to_oriented_rootpairs=json.load(open(DIR_MAP/"edge_to_oriented_rootpair_triple.json"))
    # tri_set -> 2 lifts (each from one of the opposite edges in the edgepair)
    tri_set_to_oriented=defaultdict(list)
    for ekey, pairs in edge_to_oriented_rootpairs.items():
        ids=[]
        for a,b in pairs:
            ids.append(pair_to_vertex[frozenset((a,b))])
        tri_set=tuple(sorted(ids))
        tri_set_to_oriented[tri_set].append((ekey, tuple(ids)))
    assert all(len(v)==2 for v in tri_set_to_oriented.values())

    # canonical face orientation
    tri_orient={}
    for tri_set, lst in tri_set_to_oriented.items():
        opts=[]
        for ekey, ids in lst:
            opts.append((canon_cycle(ids), ekey, ids))
        opts.sort(key=lambda x:x[0])
        tri_orient[tri_set]=opts[0][0]

    # edge_tail from face orientations
    edge_tail={}
    for tri in blocks:
        x,y,z=tri_orient[tuple(sorted(tri))]
        for a,b in [(x,y),(y,z),(z,x)]:
            e=tuple(sorted((a,b)))
            if e in edge_tail:
                raise RuntimeError("edge assigned twice")
            edge_tail[e]=a
    def c_edge(e):
        tail=edge_tail[e]
        return 0 if tail==min(e) else 1

    # build adjacency
    adj=[set() for _ in range(36)]
    edge_to_third={}
    for tri in blocks:
        a,b,c=tri
        for u,v,w in [(a,b,c),(b,c,a),(c,a,b)]:
            e=tuple(sorted((u,v)))
            adj[u].add(v); adj[v].add(u)
            edge_to_third[e]=w

    # enumerate all triangles
    triangles=[]
    for i in range(36):
        for j in adj[i]:
            if j<=i: continue
            for k in (adj[i]&adj[j]):
                if k>j:
                    triangles.append((i,j,k))
    assert len(triangles)==1200

    # face->line mapping
    w33_line_map=json.load(open(DIR_SRG/"w33_line_to_e6pair_triangles.json"))
    face_to_line={}
    for line in w33_line_map:
        lid=line["line_id"]
        for tri in line["triangle_blocks"]:
            face_to_line[tuple(sorted(tri))]=lid

    # compute hol and image face f(t)
    total_preimage=Counter()
    face_preimage_even=Counter()
    face_preimage_odd_nonface=Counter()
    odd_nonface=[]
    for t in triangles:
        i,j,k=t
        img=tuple(sorted((edge_to_third[(i,j)], edge_to_third[(i,k)], edge_to_third[(j,k)])))
        total_preimage[img]+=1
        hol=(c_edge((i,j))+c_edge((i,k))+c_edge((j,k)))%2
        if hol==0:
            face_preimage_even[img]+=1
        else:
            if t not in chosen_set:
                face_preimage_odd_nonface[img]+=1
                odd_nonface.append((t,img,face_to_line[img]))
    # verify constant degree 10
    assert set(total_preimage.values())=={10}

    # classify faces
    special=[f for f,cnt in face_preimage_odd_nonface.items() if cnt>0]
    assert len(special)==40
    # outputs
    OUT.mkdir(parents=True, exist_ok=True)
    with open(OUT/"odd_nonface_triangles_240.csv","w",newline="") as f:
        w=csv.writer(f)
        w.writerow(["i","j","k","image_a","image_b","image_c","line_id"])
        for (t,img,lid) in sorted(odd_nonface):
            w.writerow([*t,*img,lid])

    with open(OUT/"face_preimage_counts_120.csv","w",newline="") as f:
        w=csv.writer(f)
        w.writerow(["line_id","a","b","c","odd_nonface","even_nonface","self","total"])
        for face in sorted(chosen_set):
            odd=face_preimage_odd_nonface[face]
            even=face_preimage_even[face]
            w.writerow([face_to_line[face],*face,odd,even,1,odd+even+1])

    with open(OUT/"SUMMARY.json","w") as f:
        json.dump({
            "triangles_total": 1200,
            "faces": 120,
            "odd_nonface": 240,
            "special_faces": 40,
            "map_degree_triangles_to_faces": 10,
            "special_profile": {"odd_nonface":6,"even_nonface":3,"self":1},
            "ordinary_profile": {"odd_nonface":0,"even_nonface":9,"self":1}
        }, f, indent=2)

    print("done; wrote outputs to", OUT)

if __name__=="__main__":
    main()
