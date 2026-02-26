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

# compute alpha function again
def mu_coeffs(p,q,r,s):
    A = (p * r) % 3
    B = (p * s + q * r - 1) % 3
    C = (q * s) % 3
    return A,B,C

def alpha_from_A(p,q,r,s,d):
    Acoeff,Bcoeff,Ccoeff = mu_coeffs(p,q,r,s)
    d1,d2 = d
    return (2 * (Acoeff * d1 * d1 + Bcoeff * d1 * d2 + Ccoeff * d2 * d2)) % 3

def matrix_for_dir(d):
    for M in all_symplectic_matrices():
        if apply_matrix(M, d) == (1, 0):
            return np.array(matinv(M), dtype=int)
    raise RuntimeError

actual_e, actual_c0, _ = _derive_simple_family_tables()
naive_e, naive_c0, _ = _derive_naive_tables()

for d1 in range(3):
    for d2 in range(3):
        if (d1,d2)==(0,0): continue
        d=(d1,d2)
        B = matrix_for_dir(d)
        # compute A
        A = np.array(matinv(tuple(map(tuple,B))),dtype=int)
        a,b=A[0,0],A[0,1]
        c,d_ = A[1,0],A[1,1]
        alpha = alpha_from_A(a,b,c,d_,d)
        print('direction',d,'alpha',alpha)
        for t in (1,2):
            # fit delta polynomial
            vals={}
            for s in range(3):
                for w in range(3):
                    act=_eval_f3_poly_sw(s,w,actual_e[t][d])
                    nai=_eval_f3_poly_sw(s,w,naive_e[t][d])
                    vals[(s,w)]=(act-nai)%3
            poly=_fit_f3_poly_sw(vals)
            print(' t',t,'delta poly',poly)
        print()
