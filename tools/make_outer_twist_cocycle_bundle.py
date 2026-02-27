#!/usr/bin/env python3
"""Package the outer-twist root cocycle results into a reproducible bundle.

Creates OUTER_TWIST_INDUCES_ROOTWORD_COCYCLE_BUNDLE_v01.zip containing:
 - edge_defect.json
 - edge_defect.csv
 - orbits_under_WE6.json
 - pg_to_edge_labeling.json
 - pg_to_internal_inf.json
 - A4_matrix.json
 - N4_matrix.json
 - summary.json (cycle structure, stats, orders)
"""
from pathlib import Path
import json, zipfile
import csv

# matrices from earlier discovery
A4 = [[0,1,0,1],[1,0,1,0],[0,2,0,0],[2,0,0,0]]
N4 = [[1,0,0,0],[0,1,2,0],[2,2,0,0],[2,2,1,2]]

# load psi and infinity maps
psi = json.loads(Path('pg_to_edge_labeling.json').read_text())
inf_map = json.loads(Path('pg_to_internal_inf.json').read_text())

# load cycle stats from previous script output
cdir = Path('analysis/outer_twist_cocycle')
edge_defect = json.loads((cdir/'edge_defect.json').read_text())
stats = edge_defect.get('stats',{})
# possibly compute cycle structure of p_label here
# p_label computed previously by outer_twist_on_roots script; replicate lightly
perm40 = json.loads((Path('H27_OUTER_TWIST_ACTION_BUNDLE_v01')/'perm40_and_H27_pg_ids.json').read_text())
p_coset = perm40['perm40_points_from_phi_n']
# compute p_label as in other scripts
psi_int = {int(k):int(v) for k,v in psi.items()}
psi_inv = {v:k for k,v in psi_int.items()}
p_label = [None]*40
for i in range(40):
    pg = psi_inv[i]
    p_label[i] = psi_int[p_coset[pg]]
# cycle structure
from collections import Counter
seen=set(); cycle_lens=[]
for i in range(40):
    if i in seen: continue
    cur=i; length=0
    while cur not in seen:
        seen.add(cur); length+=1; cur=p_label[cur]
    cycle_lens.append(length)
cycle_stats = dict(Counter(cycle_lens))

# write summary
summary = {
    'A4_matrix': A4,
    'N4_matrix': N4,
    'p_label_cycle_structure': cycle_stats,
    'defect_stats': stats,
}

# create bundle
zipname = Path('OUTER_TWIST_INDUCES_ROOTWORD_COCYCLE_BUNDLE_v01.zip')
with zipfile.ZipFile(zipname,'w',compression=zipfile.ZIP_DEFLATED) as z:
    for fname in ['edge_defect.json','edge_defect.csv','orbits_under_WE6.json']:
        z.write(cdir/fname, arcname=fname)
    for fname in ['pg_to_edge_labeling.json','pg_to_internal_inf.json']:
        z.write(Path(fname), arcname=fname)
    with open('A4_matrix.json','w') as f:
        json.dump(A4,f)
    with open('N4_matrix.json','w') as f:
        json.dump(N4,f)
    z.write('A4_matrix.json','A4_matrix.json')
    z.write('N4_matrix.json','N4_matrix.json')
    with open('summary.json','w') as f:
        json.dump(summary,f,indent=2)
    z.write('summary.json','summary.json')
print('wrote',zipname)
