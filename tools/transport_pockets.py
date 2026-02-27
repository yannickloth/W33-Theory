#!/usr/bin/env python3
"""Attempt to lift 7-pocket skeleton into 480 octonion/g2 representations.

We treat the 540 pockets as nodes and connect twins (same active-6 set).
Each orientation of the octonion multiplication (one of 480) defines a mapping
from pocket vertices to imaginary units.  We propagate a chosen orientation
across the twin graph by requiring that adjacent pockets send their common
active set to the same six octonion units.  If propagation succeeds for every
pocket, the orientation extends globally.

A failure would indicate an obstruction; in practice every orientation should
extend and we therefore recover exactly 480 global lifts.

Usage:
    python tools/transport_pockets.py --pocket_json pocket_geometry.json

Outputs:
    transport_report.json  (counts + propagation stats)
"""
from __future__ import annotations
import argparse, json, os
from itertools import permutations, product
from typing import List, Tuple

# octonion helpers (copied from bundle's src/octonion.py)

# oriented Fano triples matching Cayley–Dickson basis
FANO_TRIPLES = [
    (1,2,3),
    (1,5,4),
    (1,7,6),
    (2,5,7),
    (2,6,4),
    (3,6,5),
    (3,7,4),
]

def build_imag_prod(triples=FANO_TRIPLES):
    d = {}
    for a,b,c in triples:
        d[(a,b)] = (1,c)
        d[(b,c)] = (1,a)
        d[(c,a)] = (1,b)
        d[(b,a)] = (-1,c)
        d[(c,b)] = (-1,a)
        d[(a,c)] = (-1,b)
    return d

def build_table(triples=FANO_TRIPLES):
    ip = build_imag_prod(triples)
    tab = [[(0,0) for _ in range(8)] for __ in range(8)]
    for i in range(8):
        for j in range(8):
            if i==0: tab[i][j]=(1,j); continue
            if j==0: tab[i][j]=(1,i); continue
            if i==j: tab[i][j]=(-1,0); continue
            s,k = ip[(i,j)]
            tab[i][j]=(s,k)
    return tab

def encode(sign: int, idx: int):
    return sign*(idx+1)

def decode(code: int):
    sign = 1 if code>0 else -1
    idx = abs(code)-1
    return sign, idx

def build_code_table(triples=FANO_TRIPLES):
    tab = build_table(triples)
    return [[encode(s,k) for (s,k) in row] for row in tab]

TAB = build_code_table()

def transform_table(tab, perm_arr, sign_arr):
    # apply signed permutation to multiplication table
    n = 8
    new = [[0]*n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            code = tab[i][j]
            s,k = decode(code)
            # map inputs
            if i==0:
                i2 = 0; si = 1
            else:
                i2 = perm_arr[i]; si = sign_arr[i]
            if j==0:
                j2 = 0; sj = 1
            else:
                j2 = perm_arr[j]; sj = sign_arr[j]
            if k==0:
                k2 = 0; sk = 1
            else:
                k2 = perm_arr[k]; sk = sign_arr[k]
            new_code = encode(si*sj*s*sk, k2)
            new[i2][j2] = new_code
    return new


def generate_orientations():
    perms = list(permutations(range(1,8)))
    orients: List[Tuple[List[int],List[int]]] = []
    seen = set()
    for perm in perms:
        perm_arr = [0]*8; perm_arr[0]=0
        for i,p in enumerate(perm, start=1):
            perm_arr[i]=p
        for bits in range(1<<7):
            sign_arr = [1]*8
            for i in range(1,8):
                sign_arr[i] = -1 if ((bits>>(i-1))&1) else 1
            new_tab = transform_table(TAB, perm_arr, sign_arr)
            key = tuple(tuple(row) for row in new_tab)
            if key not in seen:
                seen.add(key)
                orients.append((perm_arr.copy(), sign_arr.copy()))
    return orients


def orient_assignment(orient, pocket):
    perm, sign = orient
    # canonical ordering of pocket vertices
    sorted_vs = sorted(pocket)
    idx = {v: i for i, v in enumerate(sorted_vs, start=1)}
    return {v: perm[idx[v]] for v in pocket}


def active_agreement(orient1, orient2, active_vertices, pocket1, pocket2):
    asg1 = orient_assignment(orient1, pocket1)
    asg2 = orient_assignment(orient2, pocket2)
    vals1 = {asg1[v] for v in active_vertices}
    vals2 = {asg2[v] for v in active_vertices}
    return vals1 == vals2


def propagate_orientation(orients, pockets, twin_edges, start_idx, orient_idx):
    # BFS propagate chosen orientation to all pockets; return True/False
    assigned = {start_idx: orients[orient_idx]}
    queue = [start_idx]
    while queue:
        p = queue.pop()
        orient_p = assigned[p]
        for q in twin_edges.get(p, []):
            if q in assigned:
                continue
            # only consider vertices active in both pockets (should coincide for twins)
            shared = list(set(pockets[p]["active"]) & set(pockets[q]["active"]))
            possible = []
            for oi, o in enumerate(orients):
                if active_agreement(orient_p, o,
                                     shared,
                                     pockets[p]["pocket"],
                                     pockets[q]["pocket"]):
                    possible.append((oi, o))
            if not possible:
                return False
            assigned[q] = possible[0][1]
            queue.append(q)
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pocket_json", required=True)
    args = ap.parse_args()
    data = json.loads(open(args.pocket_json).read())
    pockets_list = data.get("pockets") or []
    pockets = []
    # try to compute silent info from provided map if exists
    silent_map = {}
    if "silent_of_pocket" in data:
        for k,v in data["silent_of_pocket"].items():
            key = tuple(json.loads(k))
            silent_map[key] = v
    for p in pockets_list:
        pocket = sorted(p)
        silent = silent_map.get(tuple(pocket))
        act = [v for v in pocket if v != silent] if silent is not None else pocket
        pockets.append({"pocket": pocket, "silent": silent, "active": act})
    # build twin edges from explicit twin_pairs list if available
    twin_edges = {}
    if "twin_pairs" in data:
        for pair in data["twin_pairs"]:
            if len(pair) == 2:
                p,q = pair
                # find indices of these pockets
                try:
                    i = pockets_list.index(p)
                    j = pockets_list.index(q)
                except ValueError:
                    continue
                twin_edges.setdefault(i, []).append(j)
                twin_edges.setdefault(j, []).append(i)
    else:
        # fallback: recompute from active sets
        by_active = {}
        for idx,p in enumerate(pockets):
            key = tuple(sorted(p["active"]))
            by_active.setdefault(key, []).append(idx)
        for key, lst in by_active.items():
            if len(lst) == 2:
                a,b = lst
                twin_edges.setdefault(a, []).append(b)
                twin_edges.setdefault(b, []).append(a)
    print(f"built {len(pockets)} pockets, {len(twin_edges)//2} twin pairs")
    orients = generate_orientations()
    print(f"generated {len(orients)} distinct orientations")
    successes = 0
    for oi in range(len(orients)):
        if propagate_orientation(orients, pockets, twin_edges, 0, oi):
            successes += 1
    print("success count", successes)
    os.makedirs("out", exist_ok=True)
    with open("out/transport_report.json","w") as f:
        json.dump({"pockets": len(pockets),
                   "twin_pairs": len(twin_edges)//2,
                   "orientations": len(orients),
                   "successful_extensions": successes}, f, indent=2)

if __name__=='__main__':
    main()
