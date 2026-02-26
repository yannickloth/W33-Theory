from scripts.ce2_global_cocycle import all_symplectic_matrices, matinv, apply_matrix
import numpy as np

d=(0,1)
print('matrices mapping d to (1,0):')
for M in all_symplectic_matrices():
    if apply_matrix(M,d)==(1,0):
        B = np.array(matinv(M),dtype=int)
        print(M,'-> B',tuple(map(tuple,B)))
