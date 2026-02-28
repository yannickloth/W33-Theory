#!/usr/bin/env python3
"""Within the axis-192 torsor group, search for an element whose
conjugation permutes r0,r1,r2 among themselves (a nontrivial S3 action)
while leaving r3 fixed.  This would be an internal triality automorphism.
"""

import json
from collections import deque

# helpers

def compose(p,q): return tuple(p[i] for i in q)
def inv(p):
    n=len(p); out=[0]*n
    for i,a in enumerate(p): out[a]=i
    return tuple(out)

# load axis generators
axis_adj=json.load(open('TOE_tomotope_flag_model_conjugacy_v01_20260228_bundle/TOE_tomotope_flag_model_conjugacy_v01_20260228/flag_adjacency_r0_r3_permutations.json'))
rs=[tuple(axis_adj[f'r{i}']) for i in range(4)]

# generate full group closure
G=[tuple(range(192))]
seen={G[0]}
idx=0
while idx < len(G):
    g=G[idx]
    for r in rs:
        comp=compose(r,g)
        if comp not in seen:
            seen.add(comp); G.append(comp)
    idx+=1
print("group size",len(G))

# test each element
perms=[(0,1,2),(0,2,1),(1,0,2),(1,2,0),(2,0,1),(2,1,0)]
found=[]

for g in G:
    gi=inv(g)
    # conjugate each generator
    conj=[compose(g, compose(r, gi)) for r in rs]
    # check r3 fixed
    if conj[3] != rs[3]:
        continue
    # find mapping of r0,r1,r2
    mapping=[]
    for i in range(3):
        for j in range(3):
            if conj[i] == rs[j]:
                mapping.append(j)
                break
    if len(mapping)==3 and tuple(mapping) in perms and tuple(mapping)!=(0,1,2):
        found.append((g,tuple(mapping)))
        print("found element mapping",mapping)
        break

print("done, found count",len(found))
if found:
    # save first element
    g, mapping = found[0]
    json.dump(g, open("triality_element.json","w"))
    print("triality element saved to triality_element.json with mapping",mapping)
