#!/usr/bin/env python3
"""
Recompute edgepair-level D6 transport and holonomy stats from the two bundles:

- TOE_edge_to_oriented_rootpairs_v01_20260227_bundle.zip
- TOE_E6pair_SRG_triangle_decomp_v01_20260227_bundle.zip

Outputs the same CSV/JSON artifacts as shipped in this folder.
"""
import zipfile, json, math, collections
import numpy as np
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parent

EDGEPAIR_BUNDLE = ROOT / "TOE_edge_to_oriented_rootpairs_v01_20260227_bundle.zip"
SRG_BUNDLE = ROOT / "TOE_E6pair_SRG_triangle_decomp_v01_20260227_bundle.zip"

def perm_order(p):
    n=len(p)
    seen=[False]*n
    lcm=1
    for i in range(n):
        if seen[i]: 
            continue
        j=i; c=0
        while not seen[j]:
            seen[j]=True
            j=p[j]
            c+=1
        lcm=lcm*c//math.gcd(lcm,c)
    return lcm

def cyclic_rots(tri):
    a,b,c=tri
    return [(a,b,c),(b,c,a),(c,a,b)]

def reverse_tri(tri):
    a,b,c=tri
    return (a,c,b)

def match_orientation(src, tgt):
    for k,t in enumerate(cyclic_rots(tgt)):
        if src==t:
            return 0,k
    rt=reverse_tri(tgt)
    for k,t in enumerate(cyclic_rots(rt)):
        if src==t:
            return 1,k
    return None

def main():
    # Load edge->oriented triple
    with zipfile.ZipFile(EDGEPAIR_BUNDLE) as zf:
        df = pd.read_csv(zf.open("TOE_edge_to_oriented_rootpairs_v01_20260227/edge_to_oriented_rootpair_triple.csv"))
        gens_edges = json.loads(zf.read("TOE_edge_to_oriented_rootpairs_v01_20260227/sp43_generators_on_edges_240.json"))

    with zipfile.ZipFile(SRG_BUNDLE) as zf:
        e6pairs = json.loads(zf.read("TOE_E6pair_SRG_triangle_decomp_v01_20260227/e6_antipode_pairs_36.json"))["pairs"]

    root_to_e6={}
    for i,(a,b) in enumerate(e6pairs):
        root_to_e6[a]=i; root_to_e6[b]=i

    # edge endpoints + triples (as 36-ids)
    edge_endpoints=[]
    edge_triples=[]
    for _,r in df.sort_values("edge_id").iterrows():
        edge_endpoints.append((int(r.point_a), int(r.point_b)))
        tri=[]
        for k in [1,2,3]:
            tri.append(root_to_e6[int(r[f"pair{k}_a"])])
        edge_triples.append(tuple(tri))

    # point adjacency
    adj=[set() for _ in range(40)]
    pair_to_e={}
    for eid,(a,b) in enumerate(edge_endpoints):
        adj[a].add(b); adj[b].add(a)
        pair_to_e[tuple(sorted((a,b)))] = eid

    # lines + opposite mapping
    edge_to_line={}
    for eid,(a,b) in enumerate(edge_endpoints):
        common=list(adj[a].intersection(adj[b]))
        assert len(common)==2
        c,d=common
        line=tuple(sorted((a,b,c,d)))
        edge_to_line[eid]=line

    edge_to_opp={}
    for eid,(a,b) in enumerate(edge_endpoints):
        line=edge_to_line[eid]
        c,d=[x for x in line if x not in (a,b)]
        edge_to_opp[eid]=pair_to_e[tuple(sorted((c,d)))]

    # edgepairs
    edgepair_id={}
    edgepairs=[]
    edge_to_pair={}
    for e in range(240):
        o=edge_to_opp[e]
        key=tuple(sorted((e,o)))
        if key not in edgepair_id:
            edgepair_id[key]=len(edgepairs)
            edgepairs.append(key)
        edge_to_pair[e]=edgepair_id[key]

    reps=[min(a,b) for (a,b) in edgepairs]

    gens=np.array(gens_edges,dtype=int)

    # pair transport
    pair_perm=np.zeros((10,120),dtype=int)
    pair_flip=np.zeros((120,10),dtype=int)
    pair_rot=np.zeros((120,10),dtype=int)
    for pid,rep in enumerate(reps):
        for g in range(10):
            e_img=int(gens[g,rep])
            pid_img=edge_to_pair[e_img]
            pair_perm[g,pid]=pid_img
            rep_img=reps[pid_img]
            res=match_orientation(edge_triples[e_img], edge_triples[rep_img])
            assert res is not None
            fl,rt=res
            pair_flip[pid,g]=fl
            pair_rot[pid,g]=rt%3

    # outputs
    out=[]
    for pid in range(120):
        for g in range(10):
            out.append({"edgepair_id":pid,"gen":g,"edgepair_image":int(pair_perm[g,pid]),
                        "flip_Z2":int(pair_flip[pid,g]),"rot_Z3":int(pair_rot[pid,g])})
    pd.DataFrame(out).to_csv(ROOT/"edgepair_transport_D6.csv", index=False)

    # cycle holonomy for generators
    def pair_cycles(g):
        p=pair_perm[g]
        n=120
        seen=[False]*n
        hol=[]
        for s in range(n):
            if seen[s]: continue
            cyc=[]
            j=s
            while not seen[j]:
                seen[j]=True; cyc.append(j); j=int(p[j])
            # product (r^k s^f) along cycle; use semidirect law
            f=0; k=0
            for pid in cyc:
                fl=int(pair_flip[pid,g]); rt=int(pair_rot[pid,g])%3
                k = (k + (rt if f==0 else (-rt)%3)) %3
                f ^= fl
            hol.append((len(cyc),f,k))
        return hol

    rows=[]
    for g in range(10):
        for (L,f,k) in pair_cycles(g):
            rows.append({"gen":g,"cycle_len":L,"hol_flip_Z2":f,"hol_rot_Z3":k})
    pd.DataFrame(rows).to_csv(ROOT/"holonomy_cycles_edgepairs_by_generator.csv", index=False)

    print("Wrote edgepair transport + holonomy CSVs.")
    print("Generator orders on edgepairs:", [perm_order(pair_perm[g].tolist()) for g in range(10)])
    print("rot_Z3 unique values:", sorted(set(pair_rot.flatten().tolist())))
    print("flip_Z2 count:", int(pair_flip.sum()))

if __name__=="__main__":
    main()
