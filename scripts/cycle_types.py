#!/usr/bin/env python3
import json
from collections import Counter

def cycle_type(p):
    n=len(p)
    seen=[False]*n
    sizes=[]
    for i in range(n):
        if not seen[i]:
            j=i; l=0
            while not seen[j]:
                seen[j]=True
                j=p[j]; l+=1
            sizes.append(l)
    return Counter(sizes)

axis_adj=json.load(open('TOE_tomotope_flag_model_conjugacy_v01_20260228_bundle/TOE_tomotope_flag_model_conjugacy_v01_20260228/flag_adjacency_r0_r3_permutations.json'))
axis_r=[tuple(axis_adj[f'r{i}']) for i in range(4)]
trans=json.load(open('transported_r_generators.json'))
trans_r=[tuple(trans[f'r{i}']) for i in range(4)]

print('axis cycle types:')
for i,r in enumerate(axis_r):
    print(i,cycle_type(r))
print('trans cycle types:')
for i,r in enumerate(trans_r):
    print(i,cycle_type(r))
