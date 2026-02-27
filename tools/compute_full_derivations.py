#!/usr/bin/env python3
"""Compute derivations of the full 36-vertex triangle algebra.

This script reads the triangle orientation data from the same bundles used by
`derive_7pocket_derivations.py` but works on the full 36-element algebra.  It
builds the multiplication table, sets up the derivation equations over Q, and
solves for the space of derivations; the expectation is to recover a 14-
 dimensional Lie algebra isomorphic to \mathfrak{g}_2 (with a 1-dim center).

Usage:
    python tools/compute_full_derivations.py --tri_zip path/to/triangle_bundle.zip \
        --edge_zip path/to/edgebundle.zip

Outputs:
    full_derivations_basis.json  (list of derivation matrices)
    full_derivations_report.json (invariants)
"""

from __future__ import annotations
import argparse, json, os, zipfile
from itertools import combinations
from pathlib import Path
import numpy as np
import sympy as sp


def load_json_from_zip(zip_path: str, inner_path: str):
    with zipfile.ZipFile(zip_path, "r") as z:
        return json.loads(z.read(inner_path).decode("utf-8"))


def build_multiplication(tri_zip: str, edge_zip: str) -> np.ndarray:
    # replicate code from derive_7pocket_derivations but for 36
    tri_obj = load_json_from_zip(tri_zip,
        "TOE_E6pair_SRG_triangle_decomp_v01_20260227/triangle_decomposition_120_blocks.json")
    blocks = tri_obj["blocks"]
    # orient each triangle directly using listed order
    block_oriented = {}
    for tri in blocks:
        if len(tri) != 3:
            continue
        a,b,c = tri
        block_oriented[frozenset(tri)] = [a,b,c]
    n=36
    mult = [[None]*n for _ in range(n)]
    for ori in block_oriented.values():
        a,b,c = ori
        mult[a][b]=(1,c); mult[b][c]=(1,a); mult[c][a]=(1,b)
        mult[b][a]=(-1,c); mult[c][b]=(-1,a); mult[a][c]=(-1,b)
    return np.array(mult, dtype=object)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tri_zip", required=True)
    ap.add_argument("--edge_zip", required=True)
    ap.add_argument("--quick", action="store_true",
                    help="skip solving the linear system (for tests)")
    args = ap.parse_args()
    mult = build_multiplication(args.tri_zip, args.edge_zip)
    n=36
    if args.quick:
        # generate empty outputs quickly
        outdir=Path('.').resolve()
        with open(outdir/'full_derivations_report.json','w') as f:
            json.dump({'rank':None,'null_dim':None,'note':'quick'},f)
        with open(outdir/'full_derivations_basis.json','w') as f:
            json.dump({'basis': [], 'note': 'quick'},f)
        print('quick mode, done')
        return
    # setup variables d{i}_{j}
    vars_=[]; var_index={}    
    for i in range(n):
        for j in range(n):
            sym=sp.Symbol(f'd{i}_{j}')
            vars_.append(sym); var_index[(i,j)]=sym
    def D_of(q):
        return [var_index[(p,q)] for p in range(n)]
    def mult_vec(vec,j,left=True):
        out=[0]*n
        for p,coeff in enumerate(vec):
            if coeff==0: continue
            prod = mult[p][j] if left else mult[j][p]
            if prod is not None:
                sign,k=prod
                out[k] += coeff*sign
        return out
    eqs=[]
    for i in range(n):
        for j in range(n):
            prod = mult[i][j]
            left=[0]*n
            if prod is not None:
                sign,k = prod
                Dk = D_of(k)
                for t in range(n): left[t]+=sign*Dk[t]
            Di=D_of(i); Dj=D_of(j)
            right1=mult_vec(Di,j,left=True)
            right2=mult_vec(Dj,i,left=False)
            right=[right1[t]+right2[t] for t in range(n)]
            for t in range(n):
                expr=left[t]-right[t]
                if expr!=0: eqs.append(expr)
    A,_=sp.linear_eq_to_matrix(eqs,vars_)
    rankA=A.rank()
    null_dim = n*n - rankA
    nulls=A.nullspace()
    # write results
    outdir=Path('.').resolve()
    with open(outdir/'full_derivations_report.json','w') as f:
        json.dump({'rank':rankA,'null_dim':null_dim},f)
    basis=[]
    for v in nulls:
        # convert sympy vector to ints
        iv=[int(x) for x in v]
        mat = np.array(iv).reshape(n,n).tolist()
        basis.append(mat)
    with open(outdir/'full_derivations_basis.json','w') as f:
        json.dump(basis,f)
    print('done rank',rankA,'null_dim',null_dim)

if __name__=='__main__':
    main()
