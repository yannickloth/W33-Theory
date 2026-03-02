\
"""
Octonion multiplication from an oriented Fano plane, in a Cayley–Dickson basis.

Basis: e0=1, e1..e7 imaginary.
Oriented triples (a,b,c) mean:
  e_a e_b = + e_c
  e_b e_c = + e_a
  e_c e_a = + e_b
and anti-commutation gives the reverse products.

These oriented triples are chosen to match the standard Cayley–Dickson basis:
  e1=(i,0), e2=(j,0), e3=(k,0), e4=(0,1), e5=(0,i), e6=(0,j), e7=(0,k).
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Tuple

# Oriented Fano cycles matching Cayley–Dickson basis
FANO_TRIPLES: List[Tuple[int,int,int]] = [
    (1,2,3),
    (1,5,4),
    (1,7,6),
    (2,5,7),
    (2,6,4),
    (3,6,5),
    (3,7,4),
]

def build_imag_prod(triples=FANO_TRIPLES) -> Dict[Tuple[int,int], Tuple[int,int]]:
    """
    Return dict mapping (i,j) for i!=j in {1..7} to (sign, k) such that e_i*e_j = sign*e_k.
    """
    d: Dict[Tuple[int,int], Tuple[int,int]] = {}
    for a,b,c in triples:
        # cyclic
        d[(a,b)] = (1,c)
        d[(b,c)] = (1,a)
        d[(c,a)] = (1,b)
        # reverse
        d[(b,a)] = (-1,c)
        d[(c,b)] = (-1,a)
        d[(a,c)] = (-1,b)
    return d

def build_table(triples=FANO_TRIPLES) -> List[List[Tuple[int,int]]]:
    """
    Multiplication table for basis indices 0..7.
    Returns tab[i][j] = (sign, k) meaning e_i*e_j = sign*e_k, k in 0..7.
    """
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

def encode(sign: int, idx: int) -> int:
    """Signed basis code: sign*(idx+1), idx=0..7, sign in {+1,-1}."""
    return sign*(idx+1)

def decode(code: int) -> Tuple[int,int]:
    sign = 1 if code>0 else -1
    idx = abs(code)-1
    return sign, idx

def build_code_table(triples=FANO_TRIPLES) -> List[List[int]]:
    tab = build_table(triples)
    return [[encode(s,k) for (s,k) in row] for row in tab]

def vec_mul(u: List[int], v: List[int], tab_code: List[List[int]] | None=None) -> List[int]:
    if tab_code is None:
        tab_code = build_code_table()
    out = [0]*8
    for i,ui in enumerate(u):
        if ui==0: continue
        for j,vj in enumerate(v):
            if vj==0: continue
            code = tab_code[i][j]
            s,k = decode(code)
            out[k] += ui*vj*s
    return out

def conj(u: List[int]) -> List[int]:
    return [u[0]] + [-x for x in u[1:]]
