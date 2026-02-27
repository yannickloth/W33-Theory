import json
from pathlib import Path
import networkx as nx
from itertools import product
import numpy as np

# load psi mapping
psi = {int(k):int(v) for k,v in json.loads(Path('pg_to_edge_labeling.json').read_text()).items()}
psi_inv = {v:k for k,v in psi.items()}

# load p_coset
perm40=json.loads((Path('H27_OUTER_TWIST_ACTION_BUNDLE_v01')/'perm40_and_H27_pg_ids.json').read_text())
p_coset=perm40['perm40_points_from_phi_n']

# compute p_label
p_label=[None]*40
for i in range(40):
    pg = psi_inv[i]
    p_label[i] = psi[p_coset[pg]]

# build label adjacency from edge_to_root
edge_to_root=json.loads((Path('artifacts')/'edge_to_e8_root.json').read_text())
label_edges={tuple(sorted(eval(k))) for k in edge_to_root.keys()}

# check preservation
bad=[]
for e in label_edges:
    i,j=e
    ni,nj=p_label[i],p_label[j]
    if tuple(sorted((ni,nj))) not in label_edges:
        bad.append((e,(ni,nj)))
print('bad count',len(bad))
if bad: print(bad[:20])

# output cycle structure
from collections import Counter
seen=set();cycles=[]
for i in range(40):
    if i in seen: continue
    cur=i;length=0
    while cur not in seen:
        seen.add(cur);length+=1
        cur=p_label[cur]
    cycles.append(length)
print('cycle sizes',Counter(cycles))
