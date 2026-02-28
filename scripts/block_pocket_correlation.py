#!/usr/bin/env python3
"""Correlate 48 incidence blocks with octonion pockets via axis vertices.

Each flag has axis coordinates (aV,aE,aF,aC).  We will treat the pair
(aV,aC) as the two vertices from the axis model carried by the flag.
A block contains four flags; we take the set of all aV and aC values from
those flags.  We then look for pockets (from pocket_geometry.json) that
contain that set (or a large subset).

Output mapping block -> list of pocket indices and a summary.
"""
import json,os

bundle='TOE_block_twist_v02/TOE_tomotope_axis_block_twist_v02_20260228'
blocks=json.load(open(os.path.join(bundle,'blocks48_r0r3.json')))['orbits']
# load flag coordinates
tab = {}
with open(os.path.join(bundle,'flag_coordinates_tomotope_vs_axis.csv')) as f:
    hdr=f.readline().strip().split(',')
    for line in f:
        parts=line.strip().split(',')
        flag=int(parts[0])
        coords={k:int(v) for k,v in zip(hdr[1:],parts[1:])}
        tab[flag]=coords
# load pockets
defload='pocket_geometry.json'
pockets = json.load(open(defload))['pockets']

block_to_pockets={}
for bi,blk in enumerate(blocks):
    verts=set()
    for fid in blk:
        c=tab[fid]
        verts.add(c['aV'])
        verts.add(c['aC'])
    # find pockets containing all these verts
    matches=[]
    for pi,p in enumerate(pockets):
        if verts.issubset(set(p)):
            matches.append(pi)
    block_to_pockets[bi]=matches

# summary counts
counts={}
for bi,match in block_to_pockets.items():
    counts[len(match)] = counts.get(len(match),0)+1
print('number of pockets containing each block', counts)
# print blocks with exactly one pocket (likely most)
for bi,match in block_to_pockets.items():
    if len(match)==1:
        print('block',bi,'pocket',match[0])
# save mapping
json.dump(block_to_pockets, open('block_to_pockets.json','w'), indent=2)
print('wrote block_to_pockets.json')
