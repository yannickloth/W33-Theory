\
"""
Compute the canonical 7-pockets from the 36-vertex E6-antipode SRG triangle decomposition.

Input:
  data/triangle_decomposition_120_blocks.json

Rule:
  each triangle {a,b,c} defines a closure rule: any pair among (a,b,c) generates the third.
  Start from all 4-subsets; close under this rule; keep those that close to size 7.

Outputs:
  - number of distinct 7-pockets (expected 540)
  - silent element distribution (expected 15 per vertex)
  - pockets list

This is the 'signless' pocket skeleton. Adding the Z2/Z3 transport from the 240→120 cover
is what upgrades these pockets toward a signed/noncommutative pocket algebra.
"""

from __future__ import annotations
import json, os
from itertools import combinations
from collections import defaultdict

def closure(S, pair_to_third):
    S=set(S)
    changed=True
    while changed:
        changed=False
        lst=sorted(S)
        for i in range(len(lst)):
            for j in range(i+1,len(lst)):
                a,b=lst[i],lst[j]
                k=pair_to_third.get((a,b))
                if k is not None and k not in S:
                    S.add(k); changed=True
    return frozenset(S)

def pocket_activity(pocket, pair_to_third):
    pocket=set(pocket)
    active=set()
    for a,b in combinations(pocket,2):
        k=pair_to_third.get((min(a,b),max(a,b)))
        if k is not None and k in pocket:
            active.add(a); active.add(b); active.add(k)
    return active

def main():
    os.makedirs("out", exist_ok=True)
    with open("data/triangle_decomposition_120_blocks.json","r") as f:
        d=json.load(f)
    blocks=d["blocks"]
    n=36
    pair_to_third={}
    for a,b,c in blocks:
        for i,j,k in [(a,b,c),(b,c,a),(c,a,b)]:
            pair_to_third[(min(i,j),max(i,j))]=k

    pockets=set()
    for comb in combinations(range(n),4):
        cl=closure(comb, pair_to_third)
        if len(cl)==7:
            pockets.add(cl)

    silent_per_vertex=[0]*n
    pocket_list=[]
    for P in pockets:
        active=pocket_activity(P, pair_to_third)
        silent=list(set(P)-active)[0]
        silent_per_vertex[silent]+=1
        pocket_list.append({"pocket":sorted(P),"silent":silent,"active":sorted(active)})

    out={
        "num_pockets":len(pockets),
        "silent_per_vertex":silent_per_vertex,
        "silent_counts_set":sorted(set(silent_per_vertex)),
        "expected_pattern":"36 vertices, each silent in 15 pockets => 540 pockets total",
    }
    with open("out/pocket_summary.json","w") as f:
        json.dump(out,f,indent=2)
    with open("out/pockets_540.json","w") as f:
        json.dump(pocket_list,f)
    print("pockets:",len(pockets))
    print("silent distribution set:",sorted(set(silent_per_vertex)))

if __name__=="__main__":
    main()
