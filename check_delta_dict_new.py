from scripts.ce2_global_cocycle import (
    _derive_simple_family_tables, _derive_naive_tables,
    all_symplectic_matrices, apply_matrix, matinv,
    _eval_f3_poly_sw, _fit_f3_poly_sw
)
import numpy as np

# higher degree terms from analysis_delta_formula6 output
HIGHER_DEG_DELTA_E_TERMS = {
    (0,0): [(1,0,0,0,0,1), (1,0,0,0,1,0), (1,0,0,0,1,1), (2,0,0,0,2,0), (1,1,0,0,0,0),
              (1,1,0,0,0,1), (1,1,0,1,0,0), (2,2,0,0,0,0), (2,2,0,1,0,0), (2,2,0,1,0,1)],
    (0,1): [(2,0,0,0,0,0), (1,0,0,0,1,0), (1,0,0,0,1,1), (1,0,0,0,2,0), (2,0,0,1,0,0),
              (2,1,0,0,0,1), (2,1,0,1,0,0), (2,2,0,0,0,0), (1,2,0,1,0,0), (1,2,0,1,0,1)],
    (0,2): [(2,0,0,0,0,1), (2,0,0,0,1,0), (2,0,0,0,1,1), (2,0,0,0,2,0), (2,0,0,0,2,1),
              (1,0,0,1,0,0), (1,0,0,1,0,1), (1,1,0,0,0,0), (2,1,0,0,0,1), (2,1,0,1,0,0),
              (2,1,0,1,0,1), (1,2,0,0,0,0), (1,2,0,0,0,1), (1,2,0,1,0,0)],
    (1,0): [(2,0,0,0,0,0), (1,0,0,0,2,0), (1,1,0,0,0,1), (2,1,0,1,0,0), (2,2,0,0,0,1),
              (2,2,0,1,0,1)],
    (1,1): [(2,0,0,0,1,0), (1,0,0,1,0,0), (1,0,0,1,0,1), (1,1,0,0,0,0), (2,1,0,0,0,1),
              (1,1,0,1,0,0), (1,2,0,0,0,1), (1,2,0,1,0,0)],
    (1,2): [(1,0,0,0,0,0), (2,0,0,0,0,1), (2,0,0,0,1,1), (1,0,0,0,2,1), (2,0,0,1,0,1),
              (1,1,0,0,0,1), (2,1,0,1,0,0), (2,1,0,1,0,1), (2,2,0,0,0,0), (2,2,0,1,0,0),
              (2,2,0,1,0,1)],
    (2,0): [(1,0,0,0,0,1), (2,0,0,0,2,0), (2,1,0,1,0,1), (1,2,0,0,0,0), (2,2,0,0,0,1)],
    (2,1): [(1,0,0,0,0,0), (2,0,0,0,0,1), (1,0,0,0,1,1), (1,0,0,0,2,0), (2,0,0,0,2,1),
              (1,0,0,1,0,1), (2,1,0,0,0,0), (2,1,0,1,0,1), (2,2,0,0,0,0), (1,2,0,0,0,1),
              (2,2,0,1,0,1)],
    (2,2): [(1,0,0,0,0,0), (1,0,0,0,1,0), (2,0,0,0,1,1), (2,0,0,0,2,0), (1,0,0,0,2,1),
              (1,1,0,1,0,1), (2,2,0,0,0,0), (1,2,0,1,0,1)],
}

# evaluation function using new dictionary

def eval_new(p,q,r,s,t):
    mat=[[0,0,0] for _ in range(3)]
    for (a,b), terms in HIGHER_DEG_DELTA_E_TERMS.items():
        acc=0
        for coef,pp,qq,rr,ss,tt in terms:
            acc=(acc+coef*(p**pp)*(q**qq)*(r**rr)*(s**ss)*(t**tt))%3
        mat[a][b]=acc
    return tuple(tuple(row) for row in mat)

# compute and compare
actual_e,_,_= _derive_simple_family_tables()
naive_e,_,_= _derive_naive_tables()

errors=[]
def matrix_for_dir(d):
    for M in all_symplectic_matrices():
        if apply_matrix(M, d) == (1, 0):
            return np.array(matinv(M), dtype=int)
    raise RuntimeError

for d1 in range(3):
    for d2 in range(3):
        if (d1,d2)==(0,0): continue
        d=(d1,d2)
        B=matrix_for_dir(d)
        p,q=B[0,0],B[0,1]
        r,s=B[1,0],B[1,1]
        for t in (1,2):
            vals={}
            for s0 in range(3):
                for w0 in range(3):
                    act=_eval_f3_poly_sw(s0,w0,actual_e[t][d])
                    nai=_eval_f3_poly_sw(s0,w0,naive_e[t][d])
                    vals[(s0,w0)]=(act-nai)%3
            poly=_fit_f3_poly_sw(vals)
            dict_mat=eval_new(p,q,r,s,t)
            if tuple(tuple(int(x) for x in row) for row in poly)!=dict_mat:
                errors.append((d,t,poly,dict_mat))

print('errors count',len(errors))
for err in errors:
    print(err)
