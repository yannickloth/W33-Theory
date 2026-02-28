#!/usr/bin/env python3
"""Analyze triality and conjugation behaviour in the axis and transported
models.  Compute t=r3 r2 r1 r0 and examine its order and action on the
four generators.  Also compare with transported generators.
"""

import json

# helper

def compose(p,q): return tuple(p[i] for i in q)
def inv(p):
    out=[0]*len(p)
    for i,a in enumerate(p): out[a]=i
    return tuple(out)

# load axis generators
axis_adj=json.load(open('TOE_tomotope_flag_model_conjugacy_v01_20260228_bundle/TOE_tomotope_flag_model_conjugacy_v01_20260228/flag_adjacency_r0_r3_permutations.json'))
axis_r=[tuple(axis_adj[f'r{i}']) for i in range(4)]
# transported tomotope ones
trans=json.load(open('transported_r_generators.json'))
trans_r=[tuple(trans[f'r{i}']) for i in range(4)]

# compute t for a list of 4 perms

def compute_t(rs, order=(3,2,1,0)):
    # order is a tuple indicating indices to multiply in sequence
    t=tuple(range(len(rs[0])))
    for idx in order:
        t=compose(rs[idx], t)
    return t

def perm_order(p):
    idp=tuple(range(len(p)))
    cur=p; k=1
    while cur!=idp:
        cur=compose(p,cur); k+=1
    return k

for order,name_rs in [((3,2,1,0),'axis'),((3,2,1,0),'transported'),((0,1,2,3),'axis'),((0,1,2,3),'transported')]:
    name = name_rs[1]
    rs = axis_r if name=='axis' and order==(3,2,1,0) else (
         trans_r if name=='transported' and order==(3,2,1,0) else (
         axis_r if name=='axis' else trans_r))
    t = compute_t(rs, order)
    print(f"{name} t(order={order}) order",perm_order(t))
    for i,r in enumerate(rs):
        conj=compose(t, compose(r, inv(t)))
        print(f"{name} r{i} ->",'same' if conj==r else 'different')

# test conjugations
print("\nconjugation mapping axis, t= r3 r2 r1 r0:")
def test_conjugation(rs,order):
    t=compute_t(rs,order)
    for i in range(4):
        conj=compose(t, compose(rs[i], inv(t)))
        for j in range(4):
            if conj==rs[j]:
                print(f'r{i} -> r{j}')
                break

print("axis:")
test_conjugation(axis_r,(3,2,1,0))
print("transported:")
test_conjugation(trans_r,(3,2,1,0))
print("axis with r0r1r2r3:")
test_conjugation(axis_r,(0,1,2,3))
print("transported with r0r1r2r3:")
test_conjugation(trans_r,(0,1,2,3))
