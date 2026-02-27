#!/usr/bin/env python3
"""Determine derivation space dimensions for the 36-vertex algebra modulo a prime.

This tool constructs the same linear system as compute_full_derivations.py but
computes the rank of the coefficient matrix over GF(p) for one or more primes.
The nullspace dimension (n*n - rank) gives the dimension of the derivation space
modulo p, which for a semisimple algebra should equal 14 for most primes.

Usage:
    python tools/compute_full_derivations_modp.py --tri_zip TRI --edge_zip EDGE \
        --primes 101 103 107

Outputs a report printed on stdout.
"""
from __future__ import annotations
import argparse, json, zipfile
from itertools import combinations
import numpy as np

import sympy as sp


def load_json_from_zip(zip_path: str, inner_path: str):
    with zipfile.ZipFile(zip_path, "r") as z:
        return json.loads(z.read(inner_path).decode("utf-8"))


def build_multiplication(tri_zip: str) -> list:
    tri_obj = load_json_from_zip(tri_zip,
        "TOE_E6pair_SRG_triangle_decomp_v01_20260227/triangle_decomposition_120_blocks.json")
    blocks = tri_obj["blocks"]
    # orientation taken directly from listing
    n = 36
    mult = [[None]*n for _ in range(n)]
    for tri in blocks:
        if len(tri) != 3:
            continue
        a,b,c = tri
        mult[a][b]=(1,c); mult[b][c]=(1,a); mult[c][a]=(1,b)
        mult[b][a]=(-1,c); mult[c][b]=(-1,a); mult[a][c]=(-1,b)
    return mult


def build_equations(mult):
    n = len(mult)
    # setup variable indexing
    idx = {}
    vars_=[]
    for i in range(n):
        for j in range(n):
            sym = sp.Symbol(f'd{i}_{j}')
            idx[(i,j)]=sym
            vars_.append(sym)
    def D_of(k):
        return [idx[(p,k)] for p in range(n)]
    def mult_vec(vec,j,left=True):
        out=[0]*n
        for p,coeff in enumerate(vec):
            if coeff==0: continue
            prod = mult[p][j] if left else mult[j][p]
            if prod is not None:
                sign,k2=prod
                out[k2] += coeff*sign
        return out
    eqs=[]
    for i in range(n):
        for j in range(n):
            prod = mult[i][j]
            left=[0]*n
            if prod is not None:
                sign,k = prod
                Dk = D_of(k)
                for t in range(n):
                    left[t]+=sign*Dk[t]
            Di=D_of(i); Dj=D_of(j)
            right1 = mult_vec(Di,j,left=True)
            right2 = mult_vec(Dj,i,left=False)
            right=[right1[t]+right2[t] for t in range(n)]
            for t in range(n):
                expr = left[t]-right[t]
                if expr!=0: eqs.append(expr)
    return eqs, vars_


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tri_zip", required=True)
    ap.add_argument("--primes", nargs="+", type=int, default=[101])
    args = ap.parse_args()
    mult = build_multiplication(args.tri_zip)
    eqs,vars_ = build_equations(mult)
    A,_=sp.linear_eq_to_matrix(eqs,vars_)
    n2 = 36*36
    print("equations", len(eqs), "variables", len(vars_))
    for p in args.primes:
        Ap = A.copy().applyfunc(lambda x: sp.Mod(x, p))
        rank = Ap.rank()  # computed in GF(p)
        null_dim = n2 - rank
        print(f"prime {p}: rank {rank}, null_dim {null_dim}")

if __name__=='__main__':
    main()
