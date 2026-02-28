#!/usr/bin/env python3
import json, os

# load spa data
spa_data=json.load(open('spa_triality_summary.json'))
spa=spa_data['spa']
# load tomotope generators
bundle='TOE_block_twist_v02/TOE_tomotope_axis_block_twist_v02_20260228'
tr=json.load(open(os.path.join(bundle,'tomotope_r_generators_in_axis_coords.json')))
r0=tr['r0']; r1=tr['r1']; r2=tr['r2']; r3=tr['r3']
# build t and t4
n=192

def compose(p,q): return tuple(p[q[i]] for i in range(n))
t = compose(r1,r2)
powers=[tuple(range(n))]
for k in range(1,5):
    powers.append(compose(t,powers[-1]))
t4=powers[4]

# map block->block under generator
blocks=json.load(open(os.path.join(bundle,'blocks48_r0r3.json')))['orbits']
flag2block={fid:bi for bi,blk in enumerate(blocks) for fid in blk}
def block_image(gen,bi):
    # apply gen to representative flag
    f=blocks[bi][0]
    return flag2block[gen[f]]

def block_image_t4(bi):
    f=blocks[bi][0]
    return flag2block[t4[f]]

# generate subgroups on all 48 blocks using t4 together with each r-generator
all_blocks=list(range(48))
gen_t4_all={b:block_image_t4(b) for b in all_blocks}
for name, gen in [('r0', r0), ('r1', r1), ('r2', r2), ('r3', r3)]:
    gen_map={b:block_image(gen,b) for b in all_blocks}
    # closure
    grp=[gen_t4_all, gen_map]
    changed=True
    while changed:
        changed=False
        for p in list(grp):
            for q in list(grp):
                comp={b:p[q[b]] for b in all_blocks}
                if comp not in grp:
                    grp.append(comp); changed=True
    print(f'generated subgroup size on 48 blocks (t4,{name})', len(grp))

# now restrict to spa-defined blocks for analysis
spa_blocks=[i for i,v in enumerate(spa) if v is not None]
print('spa blocks',spa_blocks)

# examine direct actions of r0 and r3 on spa blocks
r0_map={b:block_image(r0,b) for b in spa_blocks}
r1_map={b:block_image(r1,b) for b in spa_blocks}
r2_map={b:block_image(r2,b) for b in spa_blocks}
r3_map={b:block_image(r3,b) for b in spa_blocks}
print('r0 mapping on spa blocks', r0_map)
print('r1 mapping on spa blocks', r1_map)
print('r2 mapping on spa blocks', r2_map)
print('r3 mapping on spa blocks', r3_map)
print('r0 spa values', {spa[b]:spa[r0_map[b]] for b in spa_blocks})
print('r1 spa values', {spa[b]:spa[r1_map[b]] for b in spa_blocks})
print('r2 spa values', {spa[b]:spa[r2_map[b]] for b in spa_blocks})
print('r3 spa values', {spa[b]:spa[r3_map[b]] for b in spa_blocks})

# compute orders of restrictions
import math
orders=set()
for p in grp:
    visited=set(); o=1
    for b in spa_blocks:
        if b in visited: continue
        cur=b; cnt=0
        while cur not in visited:
            visited.add(cur); cur=p[cur]; cnt+=1
        if cnt>0:
            o=o*cnt//math.gcd(o,cnt)
    orders.add(o)
print('orders of perms on spa blocks', orders)

# action on spa values
for p in grp:
    mapping={spa[b]:spa[p[b]] for b in spa_blocks}
    print('spa mapping',mapping)
