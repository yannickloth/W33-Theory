#!/usr/bin/env python3
"""
TOE hammer: complete a W33-derived 7-pocket to a true octonion table (correct G2 3-form),
then compute Der = g2 (dim 14) and split into sl3 (axis-fixing) + 6 axis movers.

This script assumes you have the previously generated bundles extracted under /mnt/data:
  - TOE_E6pair_SRG_triangle_decomp_v01_20260227/...
  - TOE_edge_to_oriented_rootpairs_v01_20260227/...

It reproduces RESULTS.json and REPORT.md in the parent folder.
"""
from __future__ import annotations
import os, json, itertools, math
import numpy as np
import sympy as sp

TRI_DIR = "/mnt/data/TOE_E6pair_SRG_triangle_decomp_v01_20260227/TOE_E6pair_SRG_triangle_decomp_v01_20260227"
EDGE_DIR = "/mnt/data/TOE_edge_to_oriented_rootpairs_v01_20260227"

# --- load data ---
tri_blocks = json.load(open(os.path.join(TRI_DIR,"triangle_decomposition_120_blocks.json")))
w33_line_map = json.load(open(os.path.join(TRI_DIR,"w33_line_to_e6pair_triangles.json")))
pairs36 = json.load(open(os.path.join(TRI_DIR,"e6_antipode_pairs_36.json")))["pairs"]
edge_map = json.load(open(os.path.join(EDGE_DIR,"edge_to_oriented_rootpair_triple.json")))

pair_to_vertex = {frozenset(p): i for i,p in enumerate(pairs36)}

# --- orient 120 blocks via canonical edge on each edgepair (as in derive_7pocket_derivations.py) ---
block_oriented = {}
for line in w33_line_map:
    p0,p1,p2,p3 = line["w33_points"]
    matchings = [((p0,p1),(p2,p3)),((p0,p2),(p1,p3)),((p0,p3),(p1,p2))]
    for m in matchings:
        eA = tuple(sorted(m[0])); eB = tuple(sorted(m[1]))
        edge_key = f"{eA[0]}-{eA[1]}" if eA < eB else f"{eB[0]}-{eB[1]}"
        root_pairs_oriented = edge_map[edge_key]
        verts = [pair_to_vertex[frozenset(rp)] for rp in root_pairs_oriented]
        block_oriented[frozenset(verts)] = verts

n=36
mult = [[None]*n for _ in range(n)]
for ori in block_oriented.values():
    a,b,c = ori
    mult[a][b]=(1,c); mult[b][c]=(1,a); mult[c][a]=(1,b)
    mult[b][a]=(-1,c); mult[c][b]=(-1,a); mult[a][c]=(-1,b)

def closure(seed):
    S=set(seed)
    changed=True
    while changed:
        changed=False
        for i in list(S):
            for j in list(S):
                if i==j: continue
                m=mult[i][j]
                if m is None: continue
                k=m[1]
                if k not in S:
                    S.add(k); changed=True
    return frozenset(S)

# pocket from prior report
pocket_global = [0,1,2,14,15,17,27]
pocket_set=set(pocket_global)

idx={g:i for i,g in enumerate(pocket_global)}
constraints=[]
for a in pocket_global:
    for b in pocket_global:
        if a==b: continue
        m=mult[a][b]
        if m is None: continue
        s,c=m
        if c in pocket_set:
            constraints.append((idx[a], idx[b], s, idx[c]))

# --- standard positive G2 form sign pattern (one common convention) ---
pos_triples=[(1,2,7),(3,4,7),(5,6,7),(1,3,5)]
neg_triples=[(1,4,6),(2,3,6),(2,4,5)]
mul2={}
def add_triple(a,b,c,sgn=1):
    mul2[(a,b)]=(sgn,c); mul2[(b,c)]=(sgn,a); mul2[(c,a)]=(sgn,b)
    mul2[(b,a)]=(-sgn,c); mul2[(c,b)]=(-sgn,a); mul2[(a,c)]=(-sgn,b)
for t in pos_triples: add_triple(*t,sgn=1)
for t in neg_triples: add_triple(*t,sgn=-1)
def oct_mul(i,j):
    if i==0: return (1,j)
    if j==0: return (1,i)
    if i==j: return (-1,0)
    return mul2[(i,j)]

def solve_sign_eqs(eqs, nvars=7):
    rows=[(mask,rhs) for mask,rhs in eqs]
    piv={}
    for col in range(nvars):
        pivrow=None
        for i,(mask,rhs) in enumerate(rows):
            if (mask>>col)&1:
                pivrow=i; break
        if pivrow is None: continue
        pm,pr = rows.pop(pivrow)
        new=[]
        for mask,rhs in rows:
            if (mask>>col)&1:
                mask ^= pm; rhs ^= pr
            new.append((mask,rhs))
        rows=new
        piv[col]=(pm,pr)
    for mask,rhs in rows:
        if mask==0 and rhs==1:
            return None, 0
    rank=len(piv)
    nfree=nvars-rank
    sol=[0]*nvars
    for col in sorted(piv.keys(), reverse=True):
        mask,rhs=piv[col]
        s=rhs
        m=mask & ~(1<<col)
        while m:
            lb=m & -m
            j=(lb.bit_length()-1)
            s ^= sol[j]
            m ^= lb
        sol[col]=s
    return sol, 2**nfree

# find unique induced octonion tables on pocket labels
def canon_table(tab):
    enc=[]
    for i in range(7):
        for j in range(7):
            s,out=tab[i][j]
            enc.append(int(s))
            enc.append(-1 if out is None else int(out))
    return tuple(enc)

unique={}
for phi in itertools.permutations(range(1,8),7):
    eqs=[]
    ok=True
    for x,y,spock,z in constraints:
        so,k=oct_mul(phi[x],phi[y])
        if k==0 or k!=phi[z]:
            ok=False; break
        o=0 if so==1 else 1
        p=0 if spock==1 else 1
        mask=(1<<z)|(1<<x)|(1<<y)
        eqs.append((mask, o^p))
    if not ok: continue
    sol, nsol = solve_sign_eqs(eqs,7)
    if sol is None: continue
    for bits in itertools.product([0,1], repeat=7):
        good=True
        for mask,rhs in eqs:
            s=rhs
            m=mask
            while m:
                lb=m & -m
                j=(lb.bit_length()-1)
                s ^= bits[j]
                m ^= lb
            if s!=0:
                good=False; break
        if not good: continue
        inv={phi[i]: i for i in range(7)}
        signs=[-1 if b else 1 for b in bits]
        tab=[[None]*7 for _ in range(7)]
        for i in range(7):
            for j in range(7):
                if i==j:
                    tab[i][j]=(-1,None); continue
                so,k=oct_mul(phi[i],phi[j])
                out=inv[k]
                tab[i][j]=(signs[i]*signs[j]*so*signs[out], out)
        enc=canon_table(tab)
        if enc not in unique:
            unique[enc]=(phi,bits,tab)

# pick one completion tab
enc0, (phi0, bits0, tab0) = next(iter(unique.items()))

def build_mul8(tab7):
    def mul8(a,b):
        v=[0]*8
        if a==0: v[b]=1; return v
        if b==0: v[a]=1; return v
        if a==b: v[0]=-1; return v
        s,out=tab7[a-1][b-1]
        v[out+1]=int(s)
        return v
    return mul8

mul8 = build_mul8(tab0)

def derivation_basis_sympy(mul8):
    n=8
    vars=[]
    idx={}
    for i in range(n):
        for j in range(n):
            v=sp.Symbol(f"d{i}_{j}")
            idx[(i,j)]=len(vars); vars.append(v)
    eqs=[]
    for a in range(n):
        for b in range(n):
            prod=mul8(a,b)
            left=[0]*n
            for j,coef in enumerate(prod):
                if coef==0: continue
                for t in range(n):
                    left[t]+=coef*vars[idx[(t,j)]]
            right=[0]*n
            for i in range(n):
                coef=vars[idx[(i,a)]]
                vec=mul8(i,b)
                for t,c in enumerate(vec):
                    if c: right[t]+=coef*c
            for j in range(n):
                coef=vars[idx[(j,b)]]
                vec=mul8(a,j)
                for t,c in enumerate(vec):
                    if c: right[t]+=coef*c
            for t in range(n):
                eq=left[t]-right[t]
                if eq!=0: eqs.append(eq)
    for i in range(n):
        eqs.append(vars[idx[(i,0)]])  # D(1)=0
    A,_=sp.linear_eq_to_matrix(eqs, vars)
    null=A.nullspace()
    mats=[]
    for v in null:
        vv=[sp.Rational(x) for x in list(v)]
        den=1
        for x in vv:
            den=sp.ilcm(den, x.q)
        ints=[int(x*den) for x in vv]
        g=0
        for x in ints: g=math.gcd(g, abs(x))
        if g>1: ints=[x//g for x in ints]
        mats.append(np.array(ints,dtype=int).reshape((8,8)))
    return mats

basis14 = derivation_basis_sympy(mul8)
axis = 7  # pocket silent = local idx 6 => imag basis index 7

C = sp.Matrix([[int(basis14[k][r,axis]) for k in range(14)] for r in range(8)])
sl3_coeffs = C.nullspace()

sl3_basis=[]
for vec in sl3_coeffs:
    den=1
    for x in vec: den=sp.ilcm(den, sp.Rational(x).q)
    c=[int(sp.Rational(x)*den) for x in vec]
    g=0
    for x in c: g=math.gcd(g, abs(x))
    if g>1: c=[x//g for x in c]
    M=np.zeros((8,8),dtype=int)
    for k in range(14):
        if c[k]: M += c[k]*basis14[k]
    sl3_basis.append(M)

rrefC, piv = C.rref()
movers=[basis14[i] for i in piv]

out = {
  "base_pocket": {"global_vertices": pocket_global, "silent_global": 27, "silent_local": 6},
  "completion_unique_tables": len(unique),
  "g2_dim": len(basis14),
  "sl3_dim": len(sl3_basis),
  "movers_dim": len(movers),
  "axis_images": [m[:,axis].astype(int).tolist() for m in movers],
  "pos_triples": pos_triples,
  "neg_triples": neg_triples,
}
print(json.dumps(out, indent=2))
