#!/usr/bin/env python3
"""Diagnostics for the naive "transvection" guess T_x := I + ad(x) (mod 3).

In characteristic 3, if ad(x) is nilpotent with ad(x)^3 = 0, then one sometimes
gets order-3 automorphisms via truncated exponentials / transvections.

For the 24-dimensional GF(3) Golay Lie algebra in this repo, the basis
derivations ad(e_i) are generally *not* nilpotent, and T_{e_i} is therefore not
expected to have order 3 or form an elementary abelian subgroup.

This script checks, for the 24 basis elements:
  - the order of each candidate T_i := I + ad(e_i) (up to a bound)
  - commutation across all pairs (i,j)
  - whether the product T_i T_j lands back inside {T_k}

It is a debugging tool; it does not compute Aut(L) or Inn(L).
"""

import numpy as np
import os, sys

repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, repo_root)
sys.path.insert(0, os.path.join(repo_root, 'scripts'))
from scripts.w33_golay_lie_algebra import build_golay_lie_algebra, _ad_matrices

alg = build_golay_lie_algebra()
ad = _ad_matrices(alg)

size = 24
I = np.eye(size, dtype=int)

def mod3(A):
    return A % 3

# build T_x matrices for basis
T = [mod3(I + A) for A in ad]

# helper to multiply mod 3
def mat_mult(A, B):
    return mod3(A.dot(B))

def mat_pow(A, n):
    R = np.eye(size, dtype=int)
    for _ in range(n):
        R = mat_mult(R, A)
    return R

# check orders up to some bound
orders = []
bound = 243
for i, M in enumerate(T):
    o = None
    P = np.eye(size, dtype=int)
    for k in range(1, bound+1):
        P = mat_mult(P, M)
        if np.array_equal(P, I):
            o = k
            break
    orders.append(o)

print(f'orders of T_x (<= {bound}):', orders)
print('unique orders', set(orders))

# check injectivity: T_x = I ?
zeros = [i for i,M in enumerate(T) if np.array_equal(M, I)]
print('indices with T=I (should be none):', zeros)

# test commutation for all pairs and compute exact product mapping
commuting = True
product_map = {}  # (i,j) -> k if exists such that T_i T_j = T_k
for i in range(size):
    for j in range(size):
        M = T[i]; N = T[j]
        if not np.array_equal(mat_mult(M, N), mat_mult(N, M)):
            commuting = False
        # look for k with T_k == M*N
        found = False
        for k, P in enumerate(T):
            if np.array_equal(mat_mult(M, N), P):
                product_map[(i, j)] = k
                found = True
                break
        if not found:
            product_map[(i, j)] = None

print('commuting all pairs:', commuting)
# report whether product law holds universally
if all(v is not None for v in product_map.values()):
    print('product law holds for all pairs; mapping size', len(product_map))
else:
    bad = [pair for pair, k in product_map.items() if k is None]
    print('product fails for pairs', bad[:10], '... total', len(bad))

# Optionally display structure of product_map for small subset
print('sample products:', list(product_map.items())[:10])

# determine rank of vector space spanned by logs M-I
logs = [mod3(M - I) for M in T]
stack = np.vstack([L.flatten() for L in logs])
# compute rank via earlier routine

def rank_mod3(M):
    M = M.copy() % 3
    rows, cols = M.shape
    r=0
    for c in range(cols):
        pivot=None
        for i in range(r,rows):
            if M[i,c]!=0:
                pivot=i; break
        if pivot is None:
            continue
        M[[r,pivot]]=M[[pivot,r]]
        inv = 1 if M[r,c]==1 else 2
        M[r]=(M[r]*inv)%3
        for i in range(rows):
            if i!=r and M[i,c]!=0:
                M[i]=(M[i]-M[i,c]*M[r])%3
        r+=1
    return r

print('rank of logs:', rank_mod3(stack))
