#!/usr/bin/env python3
"""Solve sign gauge for a single 240-edge permutation.

Given a permutation of the 240 edges (as a list of indices) and the current
root list, determine if there exists a sign assignment to the roots making
the resulting map an isometry.  This is the core of "charge table" upgrade
when applied to the residual inner element 'a'.

Usage: provide a CSV file with two columns root,root_image (as in
root_perm_under_a.csv).  The script outputs sign vector and reports the
lift size after applying the signs to the global map.
"""
from __future__ import annotations

import json, csv
from pathlib import Path
from typing import List, Tuple

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
import sys
sys.path.insert(0, str(ROOT))

from tools.compute_phi_lift_subgroup import dot, edges, edge_index, compute_lift_for_roots
from tools.compute_phi_lift_subgroup import Gperms, build_w33

# load canonical roots
orig = json.loads((ROOT / "artifacts" / "edge_to_e8_root.json").read_text())
edges_sorted = []
root_list: List[Tuple[int,...]] = []
for k,v in orig.items():
    if not k.startswith("("):
        continue
    pair = tuple(int(x.strip()) for x in k.strip()[1:-1].split(","))
    if pair[0]<pair[1]:
        edges_sorted.append(pair)
        root_list.append(tuple(int(x) for x in v))
assert len(root_list)==240

# compute Gram
Gram = np.zeros((240,240),dtype=int)
for a in range(240):
    for b in range(240):
        Gram[a,b]=dot(root_list[a],root_list[b])

# read permutation from csv
import argparse
parser=argparse.ArgumentParser()
parser.add_argument("--perm-csv", help="CSV file with root and root_image columns")
args=parser.parse_args()

perm_map={}
with open(args.perm_csv,newline='') as f:
    rdr=csv.reader(f)
    next(rdr)
    for r,ri in rdr:
        r=tuple(int(x) for x in r.strip('"() ').split(','))
        ri=tuple(int(x) for x in ri.strip('"() ').split(','))
        perm_map[r]=ri

# build index mapping
index={tuple(v):i for i,v in enumerate(root_list)}
perm_idx=[index[perm_map[tuple(v)]] for v in root_list]

# now attempt gauge: linear system mask x = rhs as before
m=240
def solve_for_perm(perm_idx):
    basis={}
    def add(mask,rhs):
        nonlocal basis
        while mask:
            lead=mask.bit_length()-1
            if lead in basis:
                pm,pr=basis[lead]
                mask^=pm
                rhs^=pr
            else:
                basis[lead]=(mask,rhs)
                return True
        return rhs==0

    for a in range(m):
        for b in range(a+1,m):
            A=Gram[a,b]
            B=Gram[perm_idx[a],perm_idx[b]]
            if A==B: continue
            if A==-B:
                mask=(1<<a)^(1<<b)^(1<<perm_idx[a])^(1<<perm_idx[b])
                if not add(mask,1):
                    return None
            else:
                return None
    # back-substitute
    sol=[0]*m
    for lead,(mask,rhs) in sorted(basis.items(),reverse=True):
        s=rhs
        other=mask & ~(1<<lead)
        while other:
            lb=(other & -other).bit_length()-1
            s ^= sol[lb]
            other &= other-1
        sol[lead]=s
    return sol

signs = solve_for_perm(perm_idx)
if signs is None:
    print("no gauge exists for this permutation")
else:
    print("found gauge ({} flips)".format(sum(signs)))
    # apply signs and compute lift
    signed_roots=[tuple(-x if signs[i] else x for x in root_list[i]) for i in range(m)]
    new_lift=compute_lift_for_roots(signed_roots)
    print("lift size after gauge",new_lift)
    (ROOT/"artifacts"/"perm_a_sign_gauge.json").write_text(json.dumps(signs))

