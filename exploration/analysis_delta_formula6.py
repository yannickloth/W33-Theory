# try fitting ΔE polynomial with higher-degree monomials to resolve mismatch
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

# function to compute B for direction d

def matrix_for_dir(d):
    for M in all_symplectic_matrices():
        if apply_matrix(M, d) == (1, 0):
            return np.array(matinv(M), dtype=int)
    raise RuntimeError

# gather samples
samples = []
actual_e, _, _ = _derive_simple_family_tables()
naive_e, _, _ = _derive_naive_tables()
for d1 in range(3):
    for d2 in range(3):
        if (d1, d2) == (0, 0):
            continue
        d = (d1, d2)
        B = matrix_for_dir(d)
        p, q = int(B[0, 0]), int(B[0, 1])
        r, s = int(B[1, 0]), int(B[1, 1])
        for t in (1, 2):
            vals = {}
            for s0 in range(3):
                for w0 in range(3):
                    act = _eval_f3_poly_sw(s0, w0, actual_e[t][d])
                    nai = _eval_f3_poly_sw(s0, w0, naive_e[t][d])
                    vals[(s0, w0)] = (act - nai) % 3
            poly = _fit_f3_poly_sw(vals)
            samples.append((p, q, r, s, t, poly))

# build monomials up to total degree <=3 and t-exp<=1
monomials = []
for i in range(4):
    for j in range(4):
        for k in range(4):
            for l in range(4):
                for m in range(2):
                    if i + j + k + l <= 3:
                        monomials.append((i, j, k, l, m))

# solve linear system for each entry
coeffs = {}
def solve(A, b):
    A = [row[:] for row in A]
    b = b[:]
    n = len(A); m = len(A[0])
    rank = 0
    sol = [0] * m
    for col in range(m):
        pivot = None
        for r in range(rank, n):
            if A[r][col] % 3 != 0:
                pivot = r; break
        if pivot is None: continue
        A[rank], A[pivot] = A[pivot], A[rank]
        b[rank], b[pivot] = b[pivot], b[rank]
        inv = 1 if A[rank][col] % 3 == 1 else 2
        A[rank] = [(inv * x) % 3 for x in A[rank]]
        b[rank] = (inv * b[rank]) % 3
        for r in range(n):
            if r != rank and A[r][col] != 0:
                factor = A[r][col]
                A[r] = [(A[r][c] - factor * A[rank][c]) % 3 for c in range(m)]
                b[r] = (b[r] - factor * b[rank]) % 3
        rank += 1
        if rank == n: break
    for r in range(rank):
        for c in range(m):
            if A[r][c] != 0:
                sol[c] = b[r]; break
    return sol

for a in range(3):
    for b in range(3):
        A_mat = []
        bvec = []
        for p, q, r, s, t, poly in samples:
            row = [(p**i)*(q**j)*(r**k)*(s**l)*(t**m) % 3 for (i,j,k,l,m) in monomials]
            A_mat.append(row)
            bvec.append(poly[a][b])
        coeffs[(a,b)] = solve(A_mat, bvec)

# convert to dictionary output
print('HIGHER_DEG_DELTA_E_TERMS = {')
for (a,b), sol in coeffs.items():
    terms=[f'({coeff},{i},{j},{k},{l},{m})' for coeff,(i,j,k,l,m) in zip(sol,monomials) if coeff!=0]
    print(f'    ({a},{b}): [{", ".join(terms)}],')
print('}')
