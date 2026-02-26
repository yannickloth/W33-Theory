from scripts.ce2_global_cocycle import all_symplectic_matrices, apply_matrix, matinv, _eval_f3_poly_sw
import numpy as np

# formula for mu for a matrix M=[[p,q],[r,s]]
def mu_coeffs(p,q,r,s):
    # returns coefficients (A,B,C) such that mu(x,y)=2*(A x^2 + B x y + C y^2)
    A = (p * r) % 3
    B = (p * s + q * r - 1) % 3
    C = (q * s) % 3
    return A,B,C

# for direction d compute B and A and then compute alpha(d;A)
def matrix_for_dir(d):
    for M in all_symplectic_matrices():
        if apply_matrix(M, d) == (1, 0):
            return np.array(matinv(M), dtype=int)
    raise

# compute alpha coefficient for given d and A (p,q,r,s entries of A)
def alpha_from_A(p,q,r,s,d):
    # need to compute quadratic coefficient of mu_A(u_c + x d) as function of x
    # choose generic u_c with symbolic variables maybe, but we can compute using invariants s,w via linear relation.
    # But easier: pick basis for u_c that produce invariants (s,w) variable and compute expression for alpha.
    # Derive symbolic formula for alpha maybe later; for now compute numeric pattern for each d and arbitrary u_c? Actually alpha depends only on d and A (not u_c), so we can compute with u_c=0.
    # because coefficient of x^2 in mu_A(x d) = mu_A(d) maybe? We can test.
    Acoeff, Bcoeff, Ccoeff = mu_coeffs(p,q,r,s)
    # mu_A(d) = 2*(A * d1^2 + B * d1*d2 + C * d2^2)
    d1,d2 = d
    return (2 * (Acoeff * d1 * d1 + Bcoeff * d1 * d2 + Ccoeff * d2 * d2)) % 3

# compute alpha for each direction with A = inverse of B used in transport
for d1 in range(3):
    for d2 in range(3):
        if (d1,d2)==(0,0): continue
        d=(d1,d2)
        B = matrix_for_dir(d)
        # A = inv(B)
        A = np.array(matinv(tuple(map(tuple,B))),dtype=int)
        a,b=A[0,0],A[0,1]
        c,d_=A[1,0],A[1,1]
        alpha = alpha_from_A(a,b,c,d_,d)
        print('d',d,'A entries',a,b,c,d_,'alpha',alpha)
