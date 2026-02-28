#!/usr/bin/env python3
"""Analyse which pairs of spa blocks satisfy central Heisenberg translation.

We use the six unique qids that appear in T4b.  For each spa block b we have
candidate qids block_qids[b] (size two).  Let b4 = t^4(b).  We check
whether there exists a choice q in block_qids[b], q4 in block_qids[b4] such
that coords[q4]-coords[q] = central=(0,0,1).

Results are printed and written to JSON for later use.
"""
import json, zipfile, csv, os

report = json.load(open('data/w33_triality_bridge.json'))
block_qids = {int(k): set(v) for k, v in report['T4b_block_qids'].items()}
spa = json.load(open('spa_triality_summary.json'))['spa']

# Heis coords
with zipfile.ZipFile('TOE_K27_HEISENBERG_S3_v01_20260228_bundle.zip') as zf:
    coords_csv = zf.read('TOE_K27_HEISENBERG_S3_v01_20260228/K27_heisenberg_coords.csv').decode()
qid2coords = {int(r['qid']):(int(r['x']),int(r['y']),int(r['z'])) for r in csv.DictReader(coords_csv.splitlines())}

# compute t4 mapping on blocks
bundle = 'TOE_block_twist_v02/TOE_tomotope_axis_block_twist_v02_20260228'
blocks = json.load(open(os.path.join(bundle,'blocks48_r0r3.json')))['orbits']
tr = json.load(open(os.path.join(bundle,'tomotope_r_generators_in_axis_coords.json')))
r1,r2 = tr['r1'],tr['r2']
n=192

def compose(p,q): return tuple(p[q[i]] for i in range(n))

p = tuple(range(n))
t = compose(r1,r2)
for _ in range(4): p = compose(t,p)
t4 = p
flag2block = {fid:bi for bi,blk in enumerate(blocks) for fid in blk}
block_t4 = {b: flag2block[t4[blocks[b][0]]] for b in range(len(blocks))}

CENTRAL=(0,0,1)
def diff(a,b): return tuple((a[i]-b[i])%3 for i in range(3))

results={}
for b,qs in block_qids.items():
    b4=block_t4[b]
    if b4 not in block_qids:
        continue
    good_pairs=[]
    for q in qs:
        for q4 in block_qids[b4]:
            if diff(qid2coords[q4], qid2coords[q])==CENTRAL:
                good_pairs.append((q,q4))
    results[b]={'b4':b4,'spa':spa[b],'pairs':good_pairs}

json.dump(results, open('heis6_translation_pairs.json','w'), indent=2)
print('wrote heis6_translation_pairs.json')
for b,r in results.items():
    print(b,'->',r)
