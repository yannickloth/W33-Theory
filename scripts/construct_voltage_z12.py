#!/usr/bin/env python3
"""Build Z12 voltage assignment on the 48-block graph for r1/r2 edges.

Voltage[b][gen] = minimal k>0 such that, starting from representative flag
in block b and applying t=(r1 r2) repeatedly, you first reach a flag in the
block reached by gen.

We then verify that for each block the sequence of k's around the t-cycle
is exactly [1,2,...,12] (i.e. the edge voltages integrate to t).
"""
import json, os

bundle='TOE_block_twist_v02/TOE_tomotope_axis_block_twist_v02_20260228'
blocks=json.load(open(os.path.join(bundle,'blocks48_r0r3.json')))['orbits']
flag2block={fid:bi for bi,blk in enumerate(blocks) for fid in blk}
tr=json.load(open(os.path.join(bundle,'tomotope_r_generators_in_axis_coords.json')))
r1=tr['r1']; r2=tr['r2']

# build t=r1 r2 permutation
n=192
def compose(p,q): return tuple(p[q[i]] for i in range(n))
t = compose(r1,r2)

# choose representative flag for each block
rep_flag=[blk[0] for blk in blocks]

voltage = {b:{} for b in range(48)}
for b in range(48):
    f0 = rep_flag[b]
    # compute block destination for r1 and r2
    for name,gen in (('r1',r1),('r2',r2)):
        dest = flag2block[gen[f0]]
        # iterate t until we hit dest block (avoid infinite loop)
        cur=f0
        for k in range(1,13):
            cur = t[cur]
            if flag2block[cur]==dest:
                voltage[b][name]=k
                break
        else:
            voltage[b][name]=None

# verify cycle consistency: for each block follow t^k and track labels
consistent=True
for b in range(48):
    f=rep_flag[b]
    seq=[]
    cur_block=b
    for step in range(1,13):
        # determine which gen leads to next t-step: the t-step is r1 then r2,
        # but the intermediate generator may not correspond to a single block move.
        # Instead we just compute dest block after applying t once from current flag.
        f = t[f]
        next_block = flag2block[f]
        # find which generator would take current block to next_block
        candidate=None
        for gen,name in ((r1,'r1'),(r2,'r2')):
            if flag2block[gen[rep_flag[cur_block]]]==next_block:
                candidate=name; break
        seq.append(voltage[cur_block].get(candidate))
        cur_block=next_block
    if seq != list(range(1,13)):
        consistent=False
        print('block',b,'sequence',seq)

print('cycle consistency',consistent)

# write voltage table
json.dump(voltage, open('block_voltage_z12.json','w'), indent=2)
print('wrote block_voltage_z12.json')

# examine distribution of voltages
counts={}
for b in range(48):
    for name in ('r1','r2'):
        k=voltage[b][name]
        counts[k]=counts.get(k,0)+1
print('voltage counts',counts)
