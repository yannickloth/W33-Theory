
from __future__ import annotations
import json
from itertools import product
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).resolve().parents[1]))

EDGE_MAP_DIR = Path("/mnt/data/TOE_edge_to_oriented_rootpairs_v01_20260227")
CENTRAL_DIR  = Path("/mnt/data/TOE_push_central_extension_edges_v02_20260227")  # extracted folder

def main():
    with open(EDGE_MAP_DIR/"edge_to_oriented_rootpair_triple.json","r") as f:
        edge_map = json.load(f)

    # Build 36 antipode-pairs (vertices)
    pairs=set()
    for tri in edge_map.values():
        for a,b in tri:
            pairs.add(tuple(sorted((a,b))))
    pairs_list=sorted(pairs)
    pair_to_vid={p:i for i,p in enumerate(pairs_list)}

    # Rebuild 240 W33 isotropic edges to get deterministic edge ids
    from itertools import product as cartprod
    def build_projective_points_F3_4():
        F3=[0,1,2]
        pts=[]
        seen=set()
        for v in cartprod(F3, repeat=4):
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

    pts=build_projective_points_F3_4()
    edges240=build_isotropic_edges(pts)
    edgeid_to_key=[f"{i}-{j}" for i,j in edges240]

    # Load edgepairs, and choose a deterministic orientation for each SRG face:
    # pick the smaller edge-id in each edgepair as the "orientation source"
    with open(CENTRAL_DIR/"artifacts"/"edge_pairs_120.json","r") as f:
        edgepairs=json.load(f)

    # For each edge id, get oriented triple of vids as cyclic order
    def tri_vid_cyclic(edge_id: int):
        tri = edge_map[edgeid_to_key[edge_id]]
        vids=[pair_to_vid[tuple(sorted(p))] for p in tri]
        return tuple(vids)  # already cyclic order from the mapping

    face_oriented = {}  # unordered face -> oriented cyclic triple (a,b,c)
    for rec in edgepairs:
        ea, eb = rec["edge_a"], rec["edge_b"]
        src = min(ea, eb)
        cyc = tri_vid_cyclic(src)
        face = tuple(sorted(cyc))
        # store (a,b,c) where a*b=c, b*c=a, c*a=b
        face_oriented[face] = cyc

    # Build adjacency and "third" map from unordered edge -> third vertex
    third = {}
    for face, cyc in face_oriented.items():
        a,b,c = cyc
        # Since cyc is cyclic, set directed products:
        third[(a,b)] = (c, +1)
        third[(b,c)] = (a, +1)
        third[(c,a)] = (b, +1)
        # and anti-commutative opposites:
        third[(b,a)] = (c, -1)
        third[(c,b)] = (a, -1)
        third[(a,c)] = (b, -1)

    n=36

    # Product function on basis: returns (idx, sign) or None (meaning 0)
    def mul(i,j):
        return third.get((i,j), None)

    # Associator (i,j,k) = (i*j)*k - i*(j*k)
    # Returns 0 or ±e_m.
    assoc_hist = {"0":0}
    total=0
    for i in range(n):
        for j in range(n):
            for k in range(n):
                ij = mul(i,j)
                jk = mul(j,k)
                # left = (i*j)*k
                left=None
                if ij is not None:
                    m,s = ij
                    mk = mul(m,k)
                    if mk is not None:
                        m2,s2 = mk
                        left = (m2, s*s2)
                # right = i*(j*k)
                right=None
                if jk is not None:
                    m,s = jk
                    im = mul(i,m)
                    if im is not None:
                        m2,s2 = im
                        right = (m2, s*s2)
                # compute difference
                if left is None and right is None:
                    assoc_hist["0"] += 1
                elif left is None and right is not None:
                    m,s = right
                    assoc_hist[f"{-s:+d}e{m}"] = assoc_hist.get(f"{-s:+d}e{m}",0)+1
                elif left is not None and right is None:
                    m,s = left
                    assoc_hist[f"{s:+d}e{m}"] = assoc_hist.get(f"{s:+d}e{m}",0)+1
                else:
                    (m1,s1) = left
                    (m2,s2) = right
                    if m1==m2:
                        # same basis element: +/- may cancel or double; over Z this can be -2,0,2
                        val = s1 - s2
                        if val==0:
                            assoc_hist["0"] += 1
                        else:
                            assoc_hist[f"{val:+d}e{m1}"] = assoc_hist.get(f"{val:+d}e{m1}",0)+1
                    else:
                        # two different basis elements appear
                        key = f"{s1:+d}e{m1}{s2:+d}e{m2}"
                        assoc_hist[key] = assoc_hist.get(key,0)+1
                total += 1

    # Report headline stats
    nonzero = total - assoc_hist["0"]
    print("Triangle-presentation algebra on 36 basis elements")
    print(f"Defined directed products: {len(third)} (max possible {n*n})")
    print(f"Associator nonzero rate: {nonzero}/{total} = {nonzero/total:.6f}")

    # Print top 12 nonzero associators by frequency
    items = [(k,v) for k,v in assoc_hist.items() if k!="0"]
    items.sort(key=lambda kv: kv[1], reverse=True)
    print("\nTop nonzero associator outputs:")
    for k,v in items[:12]:
        print(f"  {k:>10s} : {v}")

if __name__ == "__main__":
    main()
