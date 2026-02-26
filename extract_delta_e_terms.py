import numpy as np
from scripts.ce2_global_cocycle import (
    _derive_simple_family_tables,
    _derive_naive_tables,
    _eval_f3_poly_sw,
    _fit_f3_poly_sw,
    all_symplectic_matrices,
    apply_matrix,
    matinv,
)

# helper to obtain B for direction d

def matrix_for_dir(d):
    for M in all_symplectic_matrices():
        if apply_matrix(M, d) == (1, 0):
            return np.array(matinv(M), dtype=int)
    raise RuntimeError

# collect samples (p,q,r,s,t -> delta poly)
samples=[]
actual_e, actual_c0, _ = _derive_simple_family_tables()
naive_e, naive_c0, _ = _derive_naive_tables()
for d1 in range(3):
    for d2 in range(3):
        if (d1,d2)==(0,0): continue
        d=(d1,d2)
        B=matrix_for_dir(d)
        p,q=int(B[0,0]),int(B[0,1])
        r,s=int(B[1,0]),int(B[1,1])
        for t in (1,2):
            vals={}
            for s0 in range(3):
                for w0 in range(3):
                    act=_eval_f3_poly_sw(s0,w0,actual_e[t][d])
                    nai=_eval_f3_poly_sw(s0,w0,naive_e[t][d])
                    vals[(s0,w0)]=(act-nai)%3
            poly=_fit_f3_poly_sw(vals)
            samples.append((p,q,r,s,t,poly))

# fit polynomial for each coefficient entry
# restrict to monomials depending only on p and q (no r or s) since
# empirical observation and theory show ΔE does not involve the bottom row
# of B.  this drastically reduces the search space and eliminates
# underdetermination issues.
monomials=[]
for i in range(3):
    for j in range(3):
        for m in range(2):
            if i+j <= 2:  # total degree in p,q ≤2
                monomials.append((i,j,0,0,m))

coeffs={}
for a in range(3):
    for b in range(3):
        A=[]; bvec=[]
        for p,q,r,s,t,poly in samples:
            row=[(p**i)*(q**j)*(r**k)*(s**l)*(t**m)%3 for (i,j,k,l,m) in monomials]
            A.append(row)
            bvec.append(poly[a][b])
        # solve
        def solve(A,b):
            A=[row[:] for row in A]; b=b[:]
            n=len(A); m=len(A[0])
            rank=0; sol=[0]*m
            for col in range(m):
                pivot=None
                for r_ in range(rank,n):
                    if A[r_][col]%3!=0:
                        pivot=r_; break
                if pivot is None: continue
                A[rank],A[pivot]=A[pivot],A[rank]
                b[rank],b[pivot]=b[pivot],b[rank]
                inv={1:1,2:2}[A[rank][col]%3]
                A[rank]=[(inv*x)%3 for x in A[rank]]
                b[rank]=(inv*b[rank])%3
                for r_ in range(n):
                    if r_!=rank and A[r_][col]!=0:
                        factor=A[r_][col]
                        A[r_]=[(A[r_][c]-factor*A[rank][c])%3 for c in range(m)]
                        b[r_]=(b[r_]-factor*b[rank])%3
                rank+=1
            for r_ in range(rank):
                for c in range(m):
                    if A[r_][c]!=0:
                        sol[c]=b[r_]; break
            return sol
        coeffs[(a,b)] = solve(A,bvec)

# construct readable dictionary
final = {}
for (a,b), sol in coeffs.items():
    termlist=[]
    for coeff,exps in zip(sol, monomials):
        if coeff!=0:
            termlist.append((coeff,)+exps)
    final[(a,b)] = termlist

import pprint
pprint.pprint(final, width=120)
