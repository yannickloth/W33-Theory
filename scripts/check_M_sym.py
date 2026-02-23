import sys, numpy as np
sys.path.append('.')
from e8_embedding_group_theoretic import build_w33
from tools.cycle_space_analysis import compute_automorphisms
from sympy import Matrix
from tools.cycle_space_decompose import build_clique_complex, boundary_matrix, permute_cycle, build_cycle_basis

# reimplement helper functions

def construct_H1_basis(n, adj, edges):
    simplices = build_clique_complex(n, adj)
    B2 = boundary_matrix(simplices[2], simplices[1])
    M2 = Matrix(B2.tolist())
    im_basis_sym = M2.columnspace()
    im_basis = [np.array([int(x) for x in v], dtype=int).flatten() for v in im_basis_sym]
    H1_basis = []
    def in_span(v, vecs):
        if not vecs:
            return False
        M = Matrix(np.column_stack(vecs + [v]))
        return M.rank() <= Matrix(np.column_stack(vecs)).rank()
    full_basis = build_cycle_basis(n, adj, edges)
    for v in full_basis:
        if not in_span(v, H1_basis + im_basis):
            H1_basis.append(v.copy())
        if len(H1_basis) == 81:
            break
    return H1_basis


def action_matrix_on_H1(perm, basis, edges):
    dim = len(basis)
    Bmat = np.column_stack(basis)
    pinv = np.linalg.pinv(Bmat)
    M = Matrix.zeros(dim, dim)
    for i, b in enumerate(basis):
        b_perm = permute_cycle(b, perm, edges)
        coeffs = pinv @ b_perm
        coeffs = np.rint(coeffs).astype(int)
        for j, c in enumerate(coeffs):
            M[j, i] = c
    return M

n, verts, adj, edges = build_w33()
autos = compute_automorphisms(n, adj, limit=1411)
perm = autos[1410]
H1_basis = construct_H1_basis(n, adj, edges)
M_sym = action_matrix_on_H1(perm, H1_basis, edges)
mat = np.array(M_sym.tolist(), dtype=int)
print('shape', mat.shape)
print('column nonzeros counts', np.count_nonzero(mat, axis=0))
print('unique entries', set(mat.flatten()))
