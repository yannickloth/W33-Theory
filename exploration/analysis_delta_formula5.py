# recompute ΔE and ΔC0 polynomial formulas based on chosen B matrices
import numpy as np
from scripts.ce2_global_cocycle import (
    _derive_simple_family_tables,
    _derive_naive_tables,
    all_symplectic_matrices,
    apply_matrix,
    matinv,
    _eval_f3_poly_sw,
    _fit_f3_poly_sw,
)

# helper to get transport matrix B for direction d

def matrix_for_dir(d):
    for M in all_symplectic_matrices():
        if apply_matrix(M, d) == (1, 0):
            return np.array(matinv(M), dtype=int)
    raise RuntimeError

# gather samples (p,q,r,s,t, delta_e_poly, delta_c0_poly)
samples = []
actual_e, actual_c0, _ = _derive_simple_family_tables()
naive_e, naive_c0, _ = _derive_naive_tables()
for d1 in range(3):
    for d2 in range(3):
        if (d1,d2) == (0,0): continue
        d = (d1,d2)
        B = matrix_for_dir(d)
        p,q = int(B[0,0]), int(B[0,1])
        r,s = int(B[1,0]), int(B[1,1])
        # compute delta_c0 polynomial (same for t=1/2 so just use t=1)
        vals_c0 = {}
        for s0 in range(3):
            for w0 in range(3):
                act = _eval_f3_poly_sw(s0, w0, actual_c0[1][d])
                nai = _eval_f3_poly_sw(s0, w0, naive_c0[1][d])
                vals_c0[(s0,w0)] = (act - nai) % 3
        poly_c0 = _fit_f3_poly_sw(vals_c0)
        # compute delta_e for t=1 and t=2
        for t in (1,2):
            vals_e = {}
            for s0 in range(3):
                for w0 in range(3):
                    act = _eval_f3_poly_sw(s0, w0, actual_e[t][d])
                    nai = _eval_f3_poly_sw(s0, w0, naive_e[t][d])
                    vals_e[(s0,w0)] = (act - nai) % 3
            poly_e = _fit_f3_poly_sw(vals_e)
            samples.append((p,q,r,s,t, poly_e, poly_c0))

# fit ΔE coefficients as polynomials in p,q,r,s,t
monomials=[]
for i in range(3):
    for j in range(3):
        for k in range(3):
            for l in range(3):
                for m in range(2):
                    if i+j+k+l <= 2:
                        monomials.append((i,j,k,l,m))

coeffs_E = {}
for a in range(3):
    for b in range(3):
        A=[]; bvec=[]
        for p,q,r,s,t,poly_e,poly_c0 in samples:
            row=[(p**i)*(q**j)*(r**k)*(s**l)*(t**m)%3 for (i,j,k,l,m) in monomials]
            A.append(row)
            bvec.append(poly_e[a][b])
        # solve mod3
        def solve(A,b):
            A=[row[:] for row in A]; b=b[:]
            n=len(A); m=len(A[0])
            rank=0; sol=[0]*m
            for col in range(m):
                pivot=None
                for r in range(rank,n):
                    if A[r][col]%3!=0:
                        pivot=r; break
                if pivot is None: continue
                A[rank],A[pivot]=A[pivot],A[rank]
                b[rank],b[pivot]=b[pivot],b[rank]
                inv={1:1,2:2}[A[rank][col]%3]
                A[rank]=[(inv*x)%3 for x in A[rank]]
                b[rank]=(inv*b[rank])%3
                for r in range(n):
                    if r!=rank and A[r][col]!=0:
                        factor=A[r][col]
                        A[r]=[(A[r][c]-factor*A[rank][c])%3 for c in range(m)]
                        b[r]=(b[r]-factor*b[rank])%3
                rank+=1
            for r in range(rank):
                for c in range(m):
                    if A[r][c]!=0:
                        sol[c]=b[r]; break
            return sol
        coeffs_E[(a,b)] = solve(A,bvec)

# fit ΔC0 coefficients (alpha0, alpha1, alpha2) as polynomials in p,q,r,s
deltaC0_vals = []
for p,q,r,s,t,poly_e,poly_c0 in samples:
    alpha0,alpha1,alpha2 = poly_c0[0]
    deltaC0_vals.append((p,q,r,s,alpha0,alpha1,alpha2))

monomials_c0 = [(i,j,k,l) for i in range(3) for j in range(3) for k in range(3) for l in range(3) if i+j+k+l<=2]
coeffs_C0 = {}
for idx,name in enumerate(['alpha0','alpha1','alpha2']):
    A=[]; b=[]
    for p,q,r,s,a0,a1,a2 in deltaC0_vals:
        row=[(p**i)*(q**j)*(r**k)*(s**l)%3 for (i,j,k,l) in monomials_c0]
        A.append(row)
        b.append([a0,a1,a2][idx])
    coeffs_C0[name] = solve(A,b)

print('NEW_DELTA_E_TERMS = {')
for (a,b), sol in coeffs_E.items():
    terms=[f'({coeff},{i},{j},{k},{l},{m})' for coeff,(i,j,k,l,m) in zip(sol,monomials) if coeff!=0]
    print(f'    ({a},{b}): [{", ".join(terms)}],')
print('}')

print('NEW_DELTA_C0_COEFFS = {')
for name, sol in coeffs_C0.items():
    terms=[f'({coeff},{i},{j},{k})' for coeff,(i,j,k,l) in zip(sol,monomials_c0) if coeff!=0]
    print(f'    "{name}": [{", ".join(terms)}],')
print('}')
