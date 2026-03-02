import numpy as np
from scripts.ce2_global_cocycle import (
    _derive_simple_family_tables,
    _derive_naive_tables,
    all_symplectic_matrices,
    apply_matrix,
    matinv,
    _evaluate_delta_e,
    _eval_f3_poly_sw,
)

# check the failing case
for t in (1,2):
    for d in [(0,1)]:
        print('checking t,d',t,d)
        # compute B
        def matrix_for_dir(d):
            for M in all_symplectic_matrices():
                if apply_matrix(M, d) == (1, 0):
                    return np.array(matinv(M), dtype=int)
            raise RuntimeError
        B = matrix_for_dir(d)
        p, q = int(B[0, 0]), int(B[0, 1])
        r, s = int(B[1, 0]), int(B[1, 1])
        print('B',B,'p,q,r,s',p,q,r,s)
        actual_e, actual_c0, _ = _derive_simple_family_tables()
        naive_e, naive_c0, _ = _derive_naive_tables()
        delta = _evaluate_delta_e(p, q, r, s, t)
        print('formula delta matrix', delta)
        print('table delta values by (s,w):')
        for s0 in range(3):
            for w0 in range(3):
                act = _eval_f3_poly_sw(s0, w0, actual_e[t][d])
                nai = _eval_f3_poly_sw(s0, w0, naive_e[t][d])
                diff = (act - nai) % 3
                form = _eval_f3_poly_sw(s0, w0, delta)
                if diff != form:
                    print('mismatch at', s0, w0, 'old', diff, 'form', form)
                    
