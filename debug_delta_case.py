import numpy as np
from scripts.ce2_global_cocycle import (
    _derive_simple_family_tables,_derive_naive_tables,
    all_symplectic_matrices, apply_matrix, matinv,
    _eval_f3_poly_sw, _fit_f3_poly_sw, _evaluate_delta_e
)

def matrix_for_dir(d):
    for M in all_symplectic_matrices():
        if apply_matrix(M, d) == (1, 0):
            return np.array(matinv(M), dtype=int)
    raise RuntimeError

actual_e, _, _ = _derive_simple_family_tables()
naive_e, _, _ = _derive_naive_tables()
d=(2,2)
t=1
B=matrix_for_dir(d)
p,q=B[0,0],B[0,1]
r,s=B[1,0],B[1,1]
print('B',B)
print('actual_e[t][d]',actual_e[t][d])
print('naive_e[t][d]',naive_e[t][d])
# compute delta polynomial explicitly
vals={}
for s0 in range(3):
    for w0 in range(3):
        act=_eval_f3_poly_sw(s0,w0,actual_e[t][d])
        nai=_eval_f3_poly_sw(s0,w0,naive_e[t][d])
        vals[(s0,w0)]=(act-nai)%3
poly=_fit_f3_poly_sw(vals)
print('delta poly',poly)
print('_evaluate_delta_e for this B,t',_evaluate_delta_e(p,q,r,s,t))
print('delta poly evals:')
for s0 in range(3):
    for w0 in range(3):
        print(s0,w0,_eval_f3_poly_sw(s0,w0,poly))
print('direct comparison of poly and _evaluate_delta_e:')
print('poly matrix',poly)
print('eval matrix',_evaluate_delta_e(p,q,r,s,t))
