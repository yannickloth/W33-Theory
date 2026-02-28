#!/usr/bin/env python3
import json
from collections import Counter

def compose(p,q): return tuple(p[i] for i in q)
def inv(p):
    out=[0]*len(p)
    for i,v in enumerate(p): out[v]=i
    return tuple(out)

def cycle_type(p):
    n=len(p)
    seen=[False]*n
    cycles=[]
    for i in range(n):
        if not seen[i]:
            c=[]; j=i
            while not seen[j]:
                seen[j]=True; c.append(j); j=p[j]
            cycles.append(len(c))
    return Counter(cycles)

axis_adj=json.load(open('TOE_tomotope_flag_model_conjugacy_v01_20260228_bundle/TOE_tomotope_flag_model_conjugacy_v01_20260228/flag_adjacency_r0_r3_permutations.json'))
axis_r=[tuple(axis_adj[f'r{i}']) for i in range(4)]
trans=json.load(open('transported_r_generators.json'))
trans_r=[tuple(trans[f'r{i}']) for i in range(4)]

for i in [1,2]:
    d = compose(trans_r[i], inv(axis_r[i]))
    print(f"difference for r{i} cycle type", cycle_type(d))

# try to factor d into involutions maybe

