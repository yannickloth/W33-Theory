#!/usr/bin/env python3
"""
Recompute: pocket(20) edgepair completion deck lift under PSp(4,3) stabilizer.

Inputs (expected under /mnt/data):
  TOE_E6pair_SRG_triangle_decomp_v01_20260227/sp43_generators_on_e6pairs_36.json
  TOE_WELD_480S_v01_20260227/pocket_geometry.json
  TOE_pocket20_K5_edgepair_cover_v01_20260227/pocket20_edgepair_cover.csv

Outputs (in cwd):
  SUMMARY.json
  edgepair_fiber_pairs_45.csv
  deck_flip_perm_on_90.json
  stab20_generators_and_induced_actions.json
  COMMUTATION_CHECK.txt
  REPORT.md
"""
from __future__ import annotations
import os, json, re, math
from collections import deque
import pandas as pd

N = 36
V0 = 20

def perm_comp(p,q):
    return tuple(p[i] for i in q)

def generate_group(generators, n=N, max_size=100000):
    idperm = tuple(range(n))
    seen = {idperm}
    q = deque([idperm])
    elems = [idperm]
    while q:
        a = q.popleft()
        for g in generators:
            b = perm_comp(g,a)
            if b not in seen:
                seen.add(b)
                q.append(b)
                elems.append(b)
                if len(elems) >= max_size:
                    raise RuntimeError("hit max_size; group larger than expected")
    return elems

def parse_edge(s):
    nums = list(map(int, re.findall(r"-?\d+", str(s))))
    return tuple(sorted(nums))

def to_cycles(perm):
    n=len(perm)
    seen=[False]*n
    cycles=[]
    for i in range(n):
        if not seen[i]:
            cur=i
            cyc=[]
            while not seen[cur]:
                seen[cur]=True
                cyc.append(cur)
                cur=perm[cur]
            if len(cyc)>1:
                cycles.append(cyc)
    cycles.sort(key=len, reverse=True)
    return cycles

def main():
    base="/mnt/data"
    e6root=os.path.join(base,"TOE_E6pair_SRG_triangle_decomp_v01_20260227")
    pg_path=os.path.join(base,"TOE_WELD_480S_v01_20260227","pocket_geometry.json")
    p20_path=os.path.join(base,"TOE_pocket20_K5_edgepair_cover_v01_20260227","pocket20_edgepair_cover.csv")

    gens = [tuple(g) for g in json.load(open(os.path.join(e6root,"sp43_generators_on_e6pairs_36.json")))]
    G = generate_group(gens, n=N)
    stab = [g for g in G if g[V0]==V0]

    pg = json.load(open(pg_path))
    pockets = [tuple(p) for p in pg["pockets"]]
    pocket_map = {frozenset(p): i for i,p in enumerate(pockets)}
    def image_pocket_id(perm, pid):
        img = frozenset(perm[v] for v in pockets[pid])
        return pocket_map[img]

    df = pd.read_csv(p20_path)
    df["e1"]=df["k5_edge1"].apply(parse_edge)
    df["e2"]=df["k5_edge2"].apply(parse_edge)
    def canon_edgepair(r):
        a,b=sorted([r.e1,r.e2])
        return (a,b)
    df["edgepair"]=df.apply(canon_edgepair, axis=1)

    # build fiber pairing
    edgepair_to_pockets={}
    for ep,g in df.groupby("edgepair"):
        d={}
        for row in g.itertuples():
            d[int(row.completion)]=int(row.pocket_id)
        edgepair_to_pockets[ep]=d

    pids=sorted(df["pocket_id"].astype(int).tolist())
    pid_to_epcomp={int(r.pocket_id):(r.edgepair,int(r.completion)) for r in df.itertuples()}

    # deck flip
    flip_pid={}
    for ep,d in edgepair_to_pockets.items():
        flip_pid[d[0]]=d[1]
        flip_pid[d[1]]=d[0]

    # commutation check
    def commute_check(perm):
        for pid in pids:
            left=image_pocket_id(perm, flip_pid[pid])
            right=flip_pid[image_pocket_id(perm,pid)]
            if left!=right:
                return False
        return True
    commute_all = all(commute_check(g) for g in stab)

    # find 2 generators of stabilizer (random search)
    import random
    def subgroup_generated(gens2):
        idperm=tuple(range(N))
        seen={idperm}
        q=deque([idperm])
        while q:
            a=q.popleft()
            for g in gens2:
                b=perm_comp(g,a)
                if b not in seen:
                    seen.add(b)
                    q.append(b)
        return seen
    g1=g2=None
    for _ in range(5000):
        a=random.choice(stab); b=random.choice(stab)
        if a==b: 
            continue
        H=subgroup_generated([a,b])
        if len(H)==len(stab):
            g1,g2=a,b
            break
    if g1 is None:
        raise RuntimeError("could not find 2-generator set for stabilizer")

    # induced action on 90 as position permutations
    pid_pos={pid:i for i,pid in enumerate(pids)}
    def action_perm_on_90(perm):
        img=[pid_pos[image_pocket_id(perm,pid)] for pid in pids]
        return tuple(img)
    g1_90=action_perm_on_90(g1)
    g2_90=action_perm_on_90(g2)
    F_90=tuple(pid_pos[flip_pid[pid]] for pid in pids)

    # group sizes on 90
    def generate_group_on_m(m, generators, max_size=200000):
        idperm=tuple(range(m))
        def comp(p,q): return tuple(p[i] for i in q)
        seen={idperm}
        q=deque([idperm])
        while q:
            a=q.popleft()
            for g in generators:
                b=comp(g,a)
                if b not in seen:
                    seen.add(b)
                    q.append(b)
                    if len(seen)>=max_size:
                        raise RuntimeError("hit max_size")
        return seen
    H1=generate_group_on_m(len(pids), [g1_90,g2_90])
    H2=generate_group_on_m(len(pids), [g1_90,g2_90,F_90])

    summary={
        "PSp43_order_on_36": len(G),
        "stab20_order_PSp": len(stab),
        "pocket20_cover_pockets": len(pids),
        "edgepairs": len(edgepair_to_pockets),
        "deck_flip_commutes_with_stab20": commute_all,
        "stab20_action_on_90_order": len(H1),
        "extended_group_with_deck_order": len(H2),
    }
    with open("SUMMARY.json","w") as f:
        json.dump(summary,f,indent=2)

    # exports
    pairs=[]
    for ep,d in edgepair_to_pockets.items():
        pairs.append({"edgepair": str(ep), "pocket0": d[0], "pocket1": d[1]})
    pd.DataFrame(pairs).to_csv("edgepair_fiber_pairs_45.csv",index=False)

    with open("deck_flip_perm_on_90.json","w") as f:
        json.dump({"pids_order": pids, "perm_pos": list(F_90)}, f, indent=2)

    gens_export=[]
    for name,perm36 in [("g1",g1),("g2",g2)]:
        perm36_list=list(perm36)
        perm90=list(action_perm_on_90(perm36))
        gens_export.append({
            "name": name,
            "perm36": perm36_list,
            "perm36_cycle_lengths": [len(c) for c in to_cycles(perm36_list)],
            "perm90_pos": perm90,
            "perm90_cycle_lengths": [len(c) for c in to_cycles(perm90)],
        })
    with open("stab20_generators_and_induced_actions.json","w") as f:
        json.dump({
            "pids_order": pids,
            "generators": gens_export,
            "deck_flip": {"perm90_pos": list(F_90), "cycle_lengths": [len(c) for c in to_cycles(list(F_90))]},
        }, f, indent=2)

    with open("COMMUTATION_CHECK.txt","w") as f:
        f.write(f"Deck flip commutes with all {len(stab)} stabilizer elements: {commute_all}\n")

    # short report
    with open("REPORT.md","w") as f:
        f.write(f\"\"\"# Pocket(20) completion deck lift under PSp(4,3)\n\n* |PSp(4,3)| in 36-point action: **{len(G)}**\n* |Stab(20)|: **{len(stab)}**\n\nPocket cover:\n* edgepairs = 45, pockets = 90\n\nDeck flip:\n* commutes with all stabilizer elements: **{commute_all}**\n* group on 90 from stabilizer: **{len(H1)}**\n* group on 90 after adjoining deck flip: **{len(H2)} = 2×{len(H1)}**\n\nInterpretation: the 90-pocket cover is a canonical place where the hidden central Z2 becomes visible.\n\"\"\")
    print("done", summary)

if __name__=="__main__":
    main()
