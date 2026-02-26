import numpy as np
from scripts.ce2_global_cocycle import all_symplectic_matrices, apply_matrix, matinv

def matrix_for_dir(d):
    for M in all_symplectic_matrices():
        if apply_matrix(M, d) == (1, 0):
            return np.array(matinv(M), dtype=int)
    raise RuntimeError

pairs={}
for d1 in range(3):
    for d2 in range(3):
        if (d1,d2)==(0,0): continue
        d=(d1,d2)
        B=matrix_for_dir(d)
        p,q=B[0,0],B[0,1]
        pairs.setdefault((p,q),[]).append(d)
for pq, dirs in pairs.items():
    if len(dirs)>1:
        print('first row',pq,'shared by',dirs)
