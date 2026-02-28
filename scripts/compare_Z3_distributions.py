#!/usr/bin/env python3
import json

# load necessary data
bundle_dir='TOE_block_twist_v02/TOE_tomotope_axis_block_twist_v02_20260228'
blocks=json.load(open(bundle_dir+'/blocks48_r0r3.json'))['orbits']
flag2block={fid:bi for bi,blk in enumerate(blocks) for fid in blk}
tr=json.load(open(bundle_dir+'/tomotope_r_generators_in_axis_coords.json'))
r1=tr['r1']; r2=tr['r2']

# spa from earlier script
spa = json.load(open('spa_triality_summary.json'))['spa']

# k distribution along edges
counts={'r1':{},'r2':{}}
for name,gen in (('r1',r1),('r2',r2)):
    for bi in range(48):
        label=spa[bi] if spa[bi] is not None else 0
        counts[name][label]=counts[name].get(label,0)+1
print('Z3 label counts on edges',counts)

# load K cocycle sanity
kdata=json.load(open(bundle_dir.replace('block_twist_v02','matched_pair_push_v01_20260228')+'/K_Z3_cocycle_sanity.json'))
print('K generator distribution',kdata['per_generator_exp_distribution'])
