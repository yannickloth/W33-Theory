#!/usr/bin/env python3
import json
from collections import defaultdict

# helpers

def compose(p,q): return tuple(p[i] for i in q)
def invert(p):
    n=len(p); inv=[0]*n
    for i,a in enumerate(p): inv[a]=i
    return tuple(inv)

# load axis generators
axis_adj=json.load(open('TOE_tomotope_flag_model_conjugacy_v01_20260228_bundle/TOE_tomotope_flag_model_conjugacy_v01_20260228/flag_adjacency_r0_r3_permutations.json'))
axis_r=[tuple(axis_adj[f'r{i}']) for i in range(4)]

# generate group closure
G=[tuple(range(192))]
seen={G[0]}
idx=0
while idx < len(G):
    g=G[idx]
    for r in axis_r:
        comp=compose(r,g)
        if comp not in seen:
            seen.add(comp); G.append(comp)
    idx+=1
print('H size', len(G))

# conjugacy closure function
def conj_class(rep):
    cl=set()
    rep_inv=invert(rep)
    for g in G:
        gr=compose(g, compose(rep, rep_inv))
        cl.add(gr)
    return cl

classes = {}
for i,r in enumerate(axis_r):
    classes[i]=conj_class(r)
    print('class size for r',i,len(classes[i]))

# compute where transported generators land
trans=json.load(open('transported_r_generators.json'))
trans_r=[tuple(trans[f'r{i}']) for i in range(4)]

for i, tr in enumerate(trans_r):
    for j,cl in classes.items():
        if tr in cl:
            print(f'transported r{i} lies in class of axis r{j}')
            break

# check pi permutation of classes via its effect on conjugacy classes
pi=tuple(json.load(open('pi_mapping.json')))
# pi acts on generators by conjugation mapping axis_r->transported
# which we already compared

