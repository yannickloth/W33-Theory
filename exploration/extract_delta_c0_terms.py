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

# helper

def matrix_for_dir(d):
    for M in all_symplectic_matrices():
        if apply_matrix(M, d) == (1, 0):
            return np.array(matinv(M), dtype=int)
    raise

# gather samples (p,q,r,s, poly matrix)
samples = []
actual_e, actual_c0, _ = _derive_simple_family_tables()
naive_e, naive_c0, _ = _derive_naive_tables()
for d1 in range(3):
    for d2 in range(3):
        if (d1,d2)==(0,0): continue
        d=(d1,d2)
        B = matrix_for_dir(d)
        p,q = int(B[0,0]), int(B[0,1])
        r,s = int(B[1,0]), int(B[1,1])
        vals={}
        for s0 in range(3):
            for w0 in range(3):
                act = _eval_f3_poly_sw(s0,w0, actual_c0[1][d])
                nai = _eval_f3_poly_sw(s0,w0, naive_c0[1][d])
                vals[(s0,w0)] = (act-nai)%3
        poly = _fit_f3_poly_sw(vals)
        samples.append((p,q,r,s,poly))

# fit each coefficient of the 3x3 polynomial in terms of p,q,r,s
monomials=[]
for i in range(3):
    for j in range(3):
        for k in range(3):
            for l in range(3):
                if i+j+k+l <=2:
                    monomials.append((i,j,k,l))

coeffs={}
for a in range(3):
    for b in range(3):
        A=[]; bvec=[]
        for p,q,r,s,poly in samples:
            row=[(p**i)*(q**j)*(r**k)*(s**l)%3 for (i,j,k,l) in monomials]
            A.append(row)
            bvec.append(poly[a][b])
        # gaussian elimination
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

print('DELTA_C0_TERMS = {')
for (a,b), sol in coeffs.items():
    terms=[f'({coeff},{i},{j},{k},{l})' for coeff,(i,j,k,l) in zip(sol,monomials) if coeff!=0]
    print(f'    ({a},{b}): [{", ".join(terms)}],')
print('}')
