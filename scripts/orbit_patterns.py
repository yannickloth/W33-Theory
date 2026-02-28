#!/usr/bin/env python3
import json
from collections import deque,Counter

# helpers

def compose(p,q): return tuple(p[i] for i in q)

def orbit(rs, gens_idx):
    n=len(rs[0])
    gens=[rs[i] for i in gens_idx]
    all_sizes=[]
    seen=set()
    for v in range(n):
        if v in seen: continue
        q=deque([v]); orb=set()
        while q:
            x=q.popleft()
            if x in orb: continue
            orb.add(x); seen.add(x)
            for g in gens:
                y=g[x]
                if y not in orb: q.append(y)
        all_sizes.append(len(orb))
    all_sizes.sort()
    return tuple(all_sizes)

axis_adj=json.load(open('TOE_tomotope_flag_model_conjugacy_v01_20260228_bundle/TOE_tomotope_flag_model_conjugacy_v01_20260228/flag_adjacency_r0_r3_permutations.json'))
axis_rs=[tuple(axis_adj[f'r{i}']) for i in range(4)]
trans=json.load(open('transported_r_generators.json'))
trans_rs=[tuple(trans[f'r{i}']) for i in range(4)]

print("axis orbit pattern:")
subs=[]
for mask in range(1,1<<4):
    idxs=[i for i in range(4) if mask&(1<<i)]
    subs.append((idxs,orbit(axis_rs,idxs)))
for idxs,sizes in subs:
    print(idxs, sizes)

print("\ntransported orbit pattern:")
subs=[]
for mask in range(1,1<<4):
    idxs=[i for i in range(4) if mask&(1<<i)]
    subs.append((idxs,orbit(trans_rs,idxs)))
for idxs,sizes in subs:
    print(idxs, sizes)

