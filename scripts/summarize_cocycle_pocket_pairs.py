import json, csv

block2p=json.load(open('block_to_pockets.json'))
pockets=json.load(open('pocket_geometry.json'))['pockets']
so=json.load(open('pocket_geometry.json'))['silent_of_pocket']

blocks_special=[]
for bi,ps in block2p.items():
    if len(ps)==2:
        bi=int(bi)
        sil=[so.get(str(pockets[p])) for p in ps]
        blocks_special.append((bi,ps,sil))

print('special blocks with pocket pairs and their silents')
for bi,ps,sil in blocks_special:
    print(bi,ps,sil)

# also count by silent pair
from collections import defaultdict
by_silent=defaultdict(list)
for bi,ps,sil in blocks_special:
    by_silent[tuple(sorted(sil))].append(bi)
print('blocks grouped by silent pairs:')
for sil,blks in by_silent.items():
    print(sil,blks)
