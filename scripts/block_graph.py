#!/usr/bin/env python3
import json
from collections import defaultdict

def compose(p,q): return tuple(p[i] for i in q)

# load axis generators
axis_adj=json.load(open('TOE_tomotope_flag_model_conjugacy_v01_20260228_bundle/TOE_tomotope_flag_model_conjugacy_v01_20260228/flag_adjacency_r0_r3_permutations.json'))
r=[tuple(axis_adj[f'r{i}']) for i in range(4)]
pi=tuple(json.load(open('pi_mapping.json')))

# compute r0-blocks
n=192
seen=[False]*n
blocks=[]
flag2block=[None]*n
for i in range(n):
    if not seen[i]:
        orb=[]; stack=[i]
        while stack:
            x=stack.pop()
            if x in orb: continue
            orb.append(x); seen[x]=True
            for g in (r[0],r[3]):
                y=g[x]
                if y not in orb: stack.append(y)
        bid=len(blocks)
        for x in orb: flag2block[x]=bid
        blocks.append(sorted(orb))

# build block-level permutations induced by r1,r2
block_perm=[None, None]
for i in [1,2]:
    perm=[None]*len(blocks)
    for bidx,blk in enumerate(blocks):
        # pick a representative
        rep=blk[0]
        tgt = r[i][rep]
        perm[bidx]=flag2block[tgt]
    block_perm[i-1]=tuple(perm)

# apply pi to blocks mapping
pi_block=[flag2block[pi[x]] for x in range(n)]
# chosen rep for each block (first element)
pos_map={}  # mapping of old block index to new
for bidx,blk in enumerate(blocks):
    pos_map[bidx]=flag2block[pi[blk[0]]]

print('block count',len(blocks))
print('block perm r1 counts', len(set(block_perm[0])))
print('block perm r2 counts', len(set(block_perm[1])))
print('pi_block sample', pi_block[:10])
print('pos_map sample', {k:pos_map[k] for k in range(10)})

# graph adjacency via r1,r2
adj=defaultdict(set)
for bidx,blk in enumerate(blocks):
    for g in (r[1],r[2]):
        for x in blk:
            adj[bidx].add(flag2block[g[x]])

print('adj neighbors sample', {k:list(adj[k]) for k in range(5)})

# how does pi act on adjacency? check if preserves structure
preserve=True
for b in range(len(blocks)):
    newnbrs=set(pos_map[n] for n in adj[b])
    if newnbrs != adj[pos_map[b]]:
        preserve=False; break
print('pi preserves block adjacency?',preserve)
