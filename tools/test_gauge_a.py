#!/usr/bin/env python3
import json
from pathlib import Path
import numpy as np
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.compute_phi_lift_subgroup import build_w33
from tools.compute_phi_sign_gauge import load_root_list, compute_sign_gauge

ROOT = Path(__file__).resolve().parents[1]
# load canonical mapping
edges_sorted, roots = load_root_list(ROOT / 'artifacts' / 'edge_to_e8_root.json')
# load permutation under a
import csv
perm_map = {}
csvpath = ROOT / 'OUTER_TWIST_ON_E8_ROOTS_CERTIFICATE_BUNDLE_v01' / 'root_perm_under_a.csv'
with open(csvpath, newline='') as f:
    reader = csv.reader(f)
    next(reader)
    for row in reader:
        if not row: continue
        r = tuple(int(x) for x in row[0].strip('"').strip('()').split(','))
        ri = tuple(int(x) for x in row[1].strip('"').strip('()').split(','))
        perm_map[r] = ri
# map roots to indices in canonical list
index = {tuple(v):i for i,v in enumerate(roots)}
perm_idx = [index[tuple(perm_map[tuple(v)])] for v in roots]

# compute how many ip=-1 pairs
from tools.compute_phi_lift_subgroup import dot
ipcount=0
violate=0
Gram = np.zeros((240,240),dtype=int)
for a in range(240):
    for b in range(240):
        Gram[a,b]=dot(roots[a],roots[b])
for a in range(240):
    for b in range(240):
        if Gram[a,b]==-Gram[perm_idx[a],perm_idx[b]]:
            ipcount+=1
        elif Gram[a,b]!=Gram[perm_idx[a],perm_idx[b]]:
            violate+=1
print('ip=-1 pairs', ipcount, 'violated', violate)
# try gauge using root list
signvec, signed_roots, gauged = compute_sign_gauge(roots)
print('gauge lift size (full group, not just a)', gauged)
