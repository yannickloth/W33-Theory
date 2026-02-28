#!/usr/bin/env python3
"""Investigate how conjugator pi acts on the 4-flag blocks under <r0,r3>."""
import json

def compose(p,q): return tuple(p[i] for i in q)

# load r0,r3 from axis
axis_adj=json.load(open('TOE_tomotope_flag_model_conjugacy_v01_20260228_bundle/TOE_tomotope_flag_model_conjugacy_v01_20260228/flag_adjacency_r0_r3_permutations.json'))
r0=tuple(axis_adj['r0']); r3=tuple(axis_adj['r3'])
# load pi mapping
pi=tuple(json.load(open('pi_mapping.json')))

# compute blocks
n=192
seen=[False]*n
blocks=[]
for i in range(n):
    if not seen[i]:
        # build orbit
        orb=[]; stack=[i]
        while stack:
            x=stack.pop()
            if x in orb: continue
            orb.append(x); seen[x]=True
            for g in (r0,r3):
                y=g[x]
                if y not in orb: stack.append(y)
        if len(orb)!=4:
            print('block size',len(orb))
        blocks.append(sorted(orb))

# check effect of pi on each block
mismatch=0
for blk in blocks:
    mapped=[pi[x] for x in blk]
    if sorted(mapped)!=blk:
        mismatch+=1
print(f"blocks count {len(blocks)}, mismatched {mismatch}")

# if blocks preserved, print mapping on each block
for blk in blocks[:10]:
    print(blk,'->',[pi[x] for x in blk])
