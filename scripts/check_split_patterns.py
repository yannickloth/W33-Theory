#!/usr/bin/env python3
import json, os
bundle='TOE_block_twist_v02/TOE_tomotope_axis_block_twist_v02_20260228'
blocks=json.load(open(os.path.join(bundle,'blocks48_r0r3.json')))['orbits']
flag2block={fid:bi for bi,blk in enumerate(blocks) for fid in blk}
tr=json.load(open(os.path.join(bundle,'tomotope_r_generators_in_axis_coords.json')))
r1=tr['r1']; r2=tr['r2']
split_stats={'r1':{},'r2':{}}
for name,gen in (('r1',r1),('r2',r2)):
    for bi,blk in enumerate(blocks):
        dests=[flag2block[gen[f]] for f in blk]
        counts={}
        for d in dests: counts[d]=counts.get(d,0)+1
        split_stats[name][bi]=tuple(sorted(counts.values()))
print('unique patterns r1', set(split_stats['r1'].values()))
print('unique patterns r2', set(split_stats['r2'].values()))
