import numpy as np
from scripts.ce2_global_cocycle import all_symplectic_matrices, apply_matrix, matinv,_f3_chi

# helper functions

def mu_coeffs(p,q,r,s):
    A = (p * r) % 3
    B = (p * s + q * r - 1) % 3
    C = (q * s) % 3
    return A,B,C

def mu_A(u, p,q,r,s):
    x,y = u
    A,B,C=mu_coeffs(p,q,r,s)
    return (2*(A*x*x + B*x*y + C*y*y)) % 3

def compute_u_c(s,w,d):
    # invert frame map: u_c = N^{-1}( s d + w J(d))
    d1,d2=d
    N = (d1*d1 + d2*d2) %3
    invN = {1:1,2:2}[N]
    J = (-d2 %3, d1 %3)
    u_c = ((s*d1 + w*J[0])*invN %3, (s*d2 + w*J[1])*invN %3)
    return u_c

# compute Gauss normalization sign

def gauss_norm(A_entries,d,u_c):
    # A_entries = (a,b,c,d)
    values=[]
    for x in range(3):
        u = ((u_c[0] + x*d[0])%3, (u_c[1] + x*d[1])%3)
        val = mu_A(u,*A_entries)
        values.append(val)
    # Gauss sum = sum_{x} ζ^{val}; sign encoded by χ of ??? maybe val?
    # Actually perform complete sum over F3 with exp(2πi/3) mapping
    import cmath
    zeta = cmath.exp(2j*cmath.pi/3)
    ssum = sum(zeta**v for v in values)
    # find sign ±1 by comparing to sqrt something? We just check argument or real part
    print('values',values,'Gauss sum',ssum)
    # maybe sign = 1 if real part >0 else 2 etc
    if abs(ssum.imag) < 1e-6:
        if ssum.real>0: return 1
        else: return 2
    return None

# quick test for d=(0,1) as earlier
d=(0,1)
B = matrix_for_dir = None
# find B via earlier logic
def matrix_for_dir(d):
    from scripts.ce2_global_cocycle import all_symplectic_matrices, apply_matrix, matinv
    import numpy as np
    for M in all_symplectic_matrices():
        if apply_matrix(M,d)==(1,0):
            return np.array(matinv(M),dtype=int)
    raise

B = matrix_for_dir(d)
p,q=int(B[0,0]),int(B[0,1]); r,s=int(B[1,0]),int(B[1,1])
A = np.array(matinv(tuple(map(tuple,B))),dtype=int)
a,b=A[0,0],A[0,1]; c,d_ = A[1,0],A[1,1]
print('d',d,'B',B,'A',A)

for s_val in range(3):
    for w_val in range(3):
        u_c = compute_u_c(s_val,w_val,d)
        sign = gauss_norm((a,b,c,d_),d,u_c)
        print('s,w',s_val,w_val,'u_c',u_c,'gauss sign',sign)
