#!/usr/bin/env python3
import json, os

# load pocket->twin mapping
mapfile='TOE_K27_HEISENBERG_S3/TOE_K27_HEISENBERG_S3_v01_20260228/K54_to_K27_twin_map.csv'
import csv
pocket2qid={}
with open(mapfile) as f:
    rdr=csv.DictReader(f)
    for row in rdr:
        pocket2qid[int(row['pocket_id'])]=int(row['qid'])

# load tomotope generators
bundle='TOE_block_twist_v02/TOE_tomotope_axis_block_twist_v02_20260228'
tr=json.load(open(os.path.join(bundle,'tomotope_r_generators_in_axis_coords.json')))
r1=tr['r1']; r2=tr['r2']; r0=tr['r0']; r3=tr['r3']

# build t = r1 r2
n=192

def compose(p,q): return tuple(p[q[i]] for i in range(n))

t = compose(r1,r2)

# compute t^4
p4=tuple(range(n))
for _ in range(4):
    p4=compose(t,p4)

# compute action on pockets (0..53)
# need mapping from flag->pocket index; we might not have this directly
# earlier block_pocket_correlation computed block->pockets for blocks; but pocket=some index related to flag
# easiest: load that mapping again
block2p=json.load(open('block_to_pockets.json'))
# build flag->pocket by reversing: each block flags, but each block had list of pockets of size maybe many
flag2pocket={}
for bi,blk in enumerate(json.load(open(os.path.join(bundle,'blocks48_r0r3.json')))['orbits']):
    pockets=block2p.get(str(bi),[])
    for fid in blk:
        # assign all pockets to this flag: but which to pick? using first
        if pockets:
            flag2pocket[fid]=pockets[0]
        else:
            flag2pocket[fid]=None

# compute twin id per pocket
pocket2twin={p: pocket2qid.get(p) for p in range(54)}

# compute twin action under t^4 on pockets
twin_after={}
for p in range(54):
    # find a flag with this pocket
    f=[fid for fid,poc in flag2pocket.items() if poc==p]
    if not f: continue
    f=f[0]
    f2=p4[f]
    p2=flag2pocket.get(f2)
    if p2 is None: continue
    twin_after[p]=pocket2twin.get(p2)

print('twin_after sample', list(twin_after.items())[:10])

# build twin permutation
twin_perm={}
for p,t in pocket2twin.items():
    if t is None: continue
    t2=twin_after.get(p)
    twin_perm.setdefault(t, set()).add(t2)
print('twin_perm', twin_perm)

# next, generate subgroup of tomotope acting on twin ids by t4 and r0
# we need permutation of twin ids induced by r0 and r3 as well
# compute mapping of twin id under r0/r3
twin_map0={}
twin_map3={}
# will fill in below

# now attempt to generate the subgroup on twin ids using explicit multiplication rules
# represent permutations of {0..26}
import itertools
all_twins=set(pocket2twin.values())

# convert mapping sets to singletons if possible
perm_t4={t:next(iter(v)) for t,v in twin_perm.items() if len(v)==1}
perm_r0={t:next(iter(v)) for t,v in twin_map0.items() if len(v)==1}
perm_r3={t:next(iter(v)) for t,v in twin_map3.items() if len(v)==1}
print('perm_t4',perm_t4)
print('perm_r0',perm_r0)
print('perm_r3',perm_r3)

# generate group by these permutations
def apply(perm,x): return perm.get(x,x)
G=set()
front=[tuple(sorted(all_twins))] # encode as tuple for simplicity
# actually build as list of dicts
perms=[perm_t4, perm_r0, perm_r3]
# brute force generate closure of permutations on twin ids
import copy
perm_list=[]
# start identity
eidp={t:t for t in all_twins}
perm_list.append(idp)
changed=True
while changed:
    changed=False
    for p in list(perm_list):
        for q in perms:
            new={t: q.get(p.get(t,t), p.get(t,t)) for t in all_twins}
            if new not in perm_list:
                perm_list.append(new); changed=True
print('generated twin group size', len(perm_list))

