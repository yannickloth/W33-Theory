#!/usr/bin/env python3
import json, csv, os

bundle='TOE_block_twist_v02/TOE_tomotope_axis_block_twist_v02_20260228'
labels={}
with open(os.path.join(bundle,'blocks48_labeled_by_tomotope_edge_face.csv')) as f:
    reader=csv.DictReader(f)
    for row in reader:
        labels[int(row['block'])] = (int(row['tE']), int(row['tF']))

block2p=json.load(open('block_to_pockets.json'))
pockets=json.load(open('pocket_geometry.json'))['pockets']
so=json.load(open('pocket_geometry.json'))['silent_of_pocket']

groups={}
for bi,ps in block2p.items():
    bi=int(bi)
    if len(ps)==2:
        sil = tuple(sorted(so.get(str(pockets[p])) for p in ps))
        groups.setdefault(sil, []).append(bi)

for sil,blks in groups.items():
    print('silent pair',sil,'blocks',blks)
    print('tE,tF of these blocks', [labels[b] for b in blks])
    print()
