import numpy as np
mat = np.load('data/24_basis.npz')['arr_0']
print('shape', mat.shape)
print('nonzero per column', np.count_nonzero(mat, axis=0))
print('nonzero per row stats: min,max', np.min(np.count_nonzero(mat,axis=1)), np.max(np.count_nonzero(mat,axis=1)))
rows_one = np.where(np.count_nonzero(mat,axis=1)==1)[0]
print('rows with single nonzero', rows_one)
for r in rows_one[:10]:
    print('row',r,'pattern',mat[r])

# show columns
for j in range(6):
    print('col',j, 'nonzeros', np.where(mat[:,j]!=0)[0])
