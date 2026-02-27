#!/usr/bin/env python3
"""Analyze the Z3 cocycle produced by the outer-twist gauge change.

Reads analysis/outer_twist_cocycle/edge_defect.json and performs:
  * verify cocycle condition on triangles (sum around any triangle == 0 mod3)
  * attempt to solve d(e)=f(j)-f(i) mod3 for vertex labeling f (coboundary test)
  * compute orbit distribution of defect values under the p_label permutation
  * output summary statistics to console and JSON.
"""
from __future__ import annotations

import json
from collections import defaultdict, Counter
from pathlib import Path
from typing import Dict, Tuple, List

import numpy as np


def load_edge_defect(path: Path) -> Dict[Tuple[int,int], int]:
    data = json.loads(path.read_text())
    m = {}
    for ent in data.get("rows", []):
        i,j = ent["edge"]
        d = ent["defect"]
        m[(i,j)] = d
        m[(j,i)] = (-d) % 3
    return m


def triangle_cocycle_check(edges: Dict[Tuple[int,int], int]) -> List[Tuple[int,int,int,int]]:
    # list violations: (i,j,k,sum)
    violations = []
    verts = sorted({v for e in edges for v in e})
    n = len(verts)
    for a in verts:
        for b in verts:
            if b<=a or (a,b) not in edges: continue
            for c in verts:
                if c<=b or (b,c) not in edges or (a,c) not in edges: continue
                s = (edges[(a,b)] + edges[(b,c)] + edges[(c,a)]) % 3
                if s != 0:
                    violations.append((a,b,c,s))
    return violations


def try_solve_coboundary(edges: Dict[Tuple[int,int], int]) -> Tuple[bool, List[int]]:
    # build linear system mod3 for f: for each oriented edge i->j, f[j]-f[i]=d
    verts = sorted({v for e in edges for v in e})
    idx = {v:i for i,v in enumerate(verts)}
    m = len(verts)
    A = []
    b = []
    for (i,j),d in edges.items():
        if i<j:  # only include each undirected edge once
            row = [0]*m
            row[idx[j]] = 1
            row[idx[i]] = -1
            A.append(row)
            b.append(d % 3)
    A = np.array(A, dtype=int) % 3
    b = np.array(b, dtype=int) % 3
    # Solve using Gaussian elimination mod3
    # reshape to augmented matrix
    aug = np.hstack([A, b.reshape(-1,1)])
    aug = aug.copy()
    r,c = aug.shape
    col = 0
    for row in range(m):
        if col>=c-1: break
        # find pivot
        piv = None
        for i in range(row, r):
            if aug[i,col] % 3 != 0:
                piv = i; break
        if piv is None:
            col +=1
            continue
        aug[[row,piv]] = aug[[piv,row]]
        inv = {1:1,2:2}[int(aug[row,col])]  # 2 is its own inverse mod3
        aug[row] = (aug[row]*inv) % 3
        for i in range(r):
            if i!=row and aug[i,col]!=0:
                factor = aug[i,col]
                aug[i] = (aug[i] - factor*aug[row]) % 3
        col +=1
    # check consistency
    for i in range(r):
        if all(aug[i,j]==0 for j in range(c-1)) and aug[i,c-1]!=0:
            return False, []
    # back-substitute for a particular solution (zero free vars)
    sol = [0]*m
    # identify pivot columns
    piv_cols = []
    row = 0
    for col in range(c-1):
        if row<r and aug[row,col]==1:
            piv_cols.append(col)
            sol[col] = int(aug[row,c-1])
            row +=1
    return True, sol


def main():
    path = Path('analysis/outer_twist_cocycle/edge_defect.json')
    if not path.exists():
        raise FileNotFoundError(path)
    edges = load_edge_defect(path)
    # undirected edge map: keep only i<j representatives
    ud_edges = {(i,j):d for (i,j),d in edges.items() if i < j}
    stats = Counter(ud_edges.values())
    print('defect distribution (undirected)', stats)
    # triangle check: iterate triples a<b<c and use oriented values
    def tri_check(ed):
        viol = []
        verts = sorted({v for e in ed for v in e})
        for a in verts:
            for b in verts:
                if b <= a: continue
                for c in verts:
                    if c <= b: continue
                    # only consider a cycle if all three pairs are edges
                    if (a, b) not in edges or (b, c) not in edges or (c, a) not in edges:
                        continue
                    # orientation a->b, b->c, c->a
                    s = (edges[(a, b)] + edges[(b, c)] + edges[(c, a)]) % 3
                    if s != 0:
                        viol.append((a, b, c, s))
        return viol
    viol = tri_check(ud_edges)
    print('triangle violations count', len(viol))
    if viol:
        print('sample violations', viol[:5])
    cob, sol = try_solve_coboundary(edges)
    print('coboundary solvable?', cob)
    if cob:
        print('example f values', sol[:10])
    # compute orbits under p_label (repeat earlier code)
    psi = {int(k):int(v) for k,v in json.loads(Path('pg_to_edge_labeling.json').read_text()).items()}
    psi_inv = {v:k for k,v in psi.items()}
    perm40 = json.loads((Path('H27_OUTER_TWIST_ACTION_BUNDLE_v01')/'perm40_and_H27_pg_ids.json').read_text())
    p_coset = perm40['perm40_points_from_phi_n']
    p_label = [None]*40
    for i in range(40):
        pg = psi_inv[i]
        p_label[i] = psi[p_coset[pg]]
    # classify undirected edges by orbit
    orbits = defaultdict(set)
    seen = set()
    ud_list = list(ud_edges.keys())
    edge_index = {e: idx for idx, e in enumerate(ud_list)}
    unvis = set(range(len(ud_list)))
    orb_sizes = []
    while unvis:
        start = unvis.pop()
        cur_idx = start
        orb = [cur_idx]
        while True:
            i, j = ud_list[cur_idx]
            ni, nj = p_label[i], p_label[j]
            if ni > nj:
                ni, nj = nj, ni
            cur_idx = edge_index[(ni, nj)]
            if cur_idx == start:
                break
            orb.append(cur_idx)
            unvis.discard(cur_idx)
        orb_sizes.append(len(orb))
    orbits = Counter(orb_sizes)
    print('edge orbit lengths under p_label', dict(orbits))
    # write summary
    out = {
        'stats': stats,
        'triangle_violations': len(viol),
        'triangle_violation_samples': viol[:10],
        'coboundary': cob,
        'orbit_lengths': dict(orbits),
    }
    Path('analysis/outer_twist_cocycle/defect_summary.json').write_text(json.dumps(out,indent=2))
    print('wrote summary')

if __name__=='__main__':
    main()
