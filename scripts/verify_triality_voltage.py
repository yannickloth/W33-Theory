#!/usr/bin/env python3
import json, os

bundle='TOE_block_twist_v02/TOE_tomotope_axis_block_twist_v02_20260228'
blocks=json.load(open(os.path.join(bundle,'blocks48_r0r3.json')))['orbits']
flag2block={fid:bi for bi,blk in enumerate(blocks) for fid in blk}
# load silent-to-pocket mapping earlier
block2p=json.load(open('block_to_pockets.json'))
pockets=json.load(open('pocket_geometry.json'))['pockets']
so=json.load(open('pocket_geometry.json'))['silent_of_pocket']
# determine silent pair index
silent_map={}
def sp_index(bi):
    ps=block2p[str(bi)]
    sil = tuple(sorted(so.get(str(pockets[p])) for p in ps))
    # map three specific pairs to 0,1,2
    if sil==(27,28): return 0
    if sil==(27,29): return 1
    if sil==(27,30): return 2
    return None

spa=[sp_index(b) for b in range(48)]
# load generators
tr=json.load(open(os.path.join(bundle,'tomotope_r_generators_in_axis_coords.json')))
r1=tr['r1']; r2=tr['r2']

def compose(p,q): return tuple(p[q[i]] for i in range(192))
t = compose(r1,r2)
# compute t^4 on each flag
n=192
powers=[None]*5
powers[0]=tuple(range(n))
p=tuple(range(n))
for k in range(1,5):
    p=compose(t,p)
    powers[k]=p

# how spa moves under t^4 on blocks
spa_after=[None]*48
for bi in range(48):
    f=blocks[bi][0]
    f4=powers[4][f]
    spa_after[bi]=spa[ flag2block[f4] ]
print('spa after t^4 distribution', spa_after)
# check if spa_after is cyclic shift of spa
mapping = {}
for i in range(48):
    if spa[i] is not None and spa_after[i] is not None:
        mapping.setdefault(spa[i],set()).add(spa_after[i])
print('mapping of spa under t4',mapping)

# also check a couple edges whether they change spa
block_map = {}
for name,gen in (('r1',r1),('r2',r2)):
    for bi in range(48):
        block_map.setdefault(name, {})[bi] = flag2block[gen[blocks[bi][0]]]
print('spa at block 0',spa[0], 'dest r1', spa[block_map['r1'][0]], 'dest r2', spa[block_map['r2'][0]])

# summary
json.dump({'spa':spa,'spa_after_t4':spa_after,'spa_mapping':{k:list(v) for k,v in mapping.items()},
           'block_map':block_map}, open('spa_triality_summary.json','w'), indent=2)
print('wrote spa_triality_summary.json')
