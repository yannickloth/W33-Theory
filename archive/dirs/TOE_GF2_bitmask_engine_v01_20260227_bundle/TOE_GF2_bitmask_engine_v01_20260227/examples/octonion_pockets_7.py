
from __future__ import annotations
import json
from itertools import combinations, product
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).resolve().parents[1]))

EDGE_MAP_DIR = Path("/mnt/data/TOE_edge_to_oriented_rootpairs_v01_20260227")
CENTRAL_DIR  = Path("/mnt/data/TOE_push_central_extension_edges_v02_20260227")

def build_projective_points_F3_4():
    F3=[0,1,2]
    pts=[]; seen=set()
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
    with open(EDGE_MAP_DIR/"edge_to_oriented_rootpair_triple.json","r") as f:
        edge_map = json.load(f)
    with open(EDGE_MAP_DIR/"sp43_generators_on_roots_240.json","r") as f:
        gen_roots = json.load(f)
    with open(EDGE_MAP_DIR/"summary.json","r") as f:
        summ = json.load(f)
    G_order = int(summ["group_order"])

    # Build 36 antipode-pairs (vertices)
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

    # Rebuild 240 isotropic edges (deterministic ordering) and edgepairs
    pts=build_projective_points_F3_4()
    edges240=build_isotropic_edges(pts)
    edgeid_to_key=[f"{i}-{j}" for i,j in edges240]

    with open(CENTRAL_DIR/"artifacts"/"edge_pairs_120.json","r") as f:
        edgepairs=json.load(f)

    def tri_vid_cyclic(edge_id: int):
        tri = edge_map[edgeid_to_key[edge_id]]
        return tuple(pair_to_vid[tuple(sorted(p))] for p in tri)

    # Choose deterministic orientation per face from smaller edge-id
    face_oriented={}
    for rec in edgepairs:
        ea, eb = rec["edge_a"], rec["edge_b"]
        cyc = tri_vid_cyclic(min(ea,eb))
        face_oriented[tuple(sorted(cyc))] = cyc

    # Build (signless) multiplication table mul(i,j) -> k if defined
    mul=[[None]*36 for _ in range(36)]
    for cyc in face_oriented.values():
        a,b,c=cyc
        mul[a][b]=c; mul[b][c]=a; mul[c][a]=b
        mul[b][a]=c; mul[c][b]=a; mul[a][c]=b

    def closure(seed):
        S=set(seed)
        changed=True
        while changed:
            changed=False
            items=list(S)
            for i in items:
                for j in items:
                    k=mul[i][j]
                    if k is not None and k not in S:
                        S.add(k); changed=True
        return frozenset(S)

    # Enumerate all 4-subset closures; collect 7-pockets
    pockets=set()
    for comb in combinations(range(36),4):
        cl=closure(comb)
        if len(cl)==7:
            pockets.add(cl)

    pockets=sorted([sorted(p) for p in pockets])
    print(f"Found {len(pockets)} distinct closed 7-pockets (from 4-generator closure).")

    # Orbit-check: show pockets form a single orbit under the 10 generators
    def apply_perm(S, perm):
        return frozenset(perm[i] for i in S)

    S0=frozenset(pockets[0])
    orbit=set([S0])
    stack=[S0]
    while stack:
        cur=stack.pop()
        for perm in gen_pairs:
            nxt=apply_perm(cur, perm)
            if nxt not in orbit:
                orbit.add(nxt); stack.append(nxt)
    print(f"Orbit size of first pocket under generators: {len(orbit)}")

    if len(orbit) != len(pockets):
        print("WARNING: pockets split into multiple orbits.")
    else:
        print("OK: all 7-pockets form a single G-orbit.")

    stab_order = G_order // len(orbit)
    print(f"Implied pocket stabilizer size: {stab_order}")

    # Save artifacts
    OUT = Path(__file__).resolve().parents[1] / "artifacts"
    OUT.mkdir(exist_ok=True)
    (OUT/"octonion_pockets_7.json").write_text(json.dumps(pockets, indent=2))
    (OUT/"octonion_pocket_orbit_summary.json").write_text(json.dumps({
        "G_order": G_order,
        "pocket_orbit_size": len(orbit),
        "stabilizer_order": stab_order,
        "num_pockets": len(pockets),
        "note": "These are closed subsets under the signless triangle-product induced by the 120 face decomposition."
    }, indent=2))
    print("Wrote artifacts/octonion_pockets_7.json and artifacts/octonion_pocket_orbit_summary.json")

if __name__ == "__main__":
    main()
