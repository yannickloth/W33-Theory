"""Compute E8 coordinate matrices corresponding to Sp(4,3) generators.

This script selects a couple of simple symplectic matrices acting on GF(3)^4,
computes their induced permutation of W33 edges, transfers the permutation to
E8 roots via the established bijection, and then solves for the 8x8 real
orthogonal matrix in W(E8) that realizes the same action on the root vectors.
"""

import json
from itertools import product
import numpy as np

# rebuild data (vertices, edges, mapping, E8 roots)

def build_W33():
    def omega(v,w):
        return (v[0]*w[1]-v[1]*w[0]+v[2]*w[3]-v[3]*w[2])%3
    def normalize(v):
        for i,x in enumerate(v):
            if x!=0:
                inv=pow(x,-1,3)
                return tuple((inv*c)%3 for c in v)
        return v
    points=[p for p in product(range(3), repeat=4) if p!=(0,0,0,0)]
    vertices=list({normalize(p) for p in points})
    edges=[]
    for i,v in enumerate(vertices):
        for j,w in enumerate(vertices):
            if i<j and omega(v,w)==0:
                edges.append((i,j))
    return vertices, edges

vertices, edges = build_W33()
map_json=json.load(open('data/w33_e8_mapping.json'))
map_arr=[map_json[str(i)] for i in range(len(edges))]

# build E8 roots list (float)
roots=[]
for i in range(8):
    for j in range(i+1,8):
        for si in [1,-1]:
            for sj in [1,-1]:
                r=[0.0]*8; r[i]=si; r[j]=sj; roots.append(np.array(r))
from itertools import product
for signs in product([0.5,-0.5], repeat=8):
    if sum(1 for s in signs if s<0)%2==0:
        roots.append(np.array(signs))
roots=np.array(roots)  # shape (240,8)

# helper to apply symplectic matrix to GF(3)^4 vector and normalize

def apply_mat(mat, v):
    w = [(sum(mat[i][j]*v[j] for j in range(4)) % 3) for i in range(4)]
    # normalize so that first nonzero entry is 1
    for idx,x in enumerate(w):
        if x!=0:
            inv = pow(x,-1,3)
            w = [(inv*c)%3 for c in w]
            break
    return tuple(w)

# chosen generators in GL(4,3) preserving standard symplectic form
# simple transvections
G1 = [[1,1,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]]  # add first coord to second
G2 = [[1,0,0,0],[0,1,1,0],[0,0,1,0],[0,0,0,1]]  # add second to third
# actually need symplectic condition: but these may not preserve omega; check

def is_symplectic(mat):
    # check omega(mat v, mat w) == omega(v,w) for all basis
    def omega(v,w):
        return (v[0]*w[1]-v[1]*w[0]+v[2]*w[3]-v[3]*w[2]) % 3
    basis = [(1 if i==j else 0) for i in range(4) for j in range(4)]
    vs = [tuple([int(x) for x in v]) for v in product(range(3), repeat=4)]
    for v in vs:
        for w in vs:
            if omega(v,w) != omega([sum(mat[i][k]*v[k] for k in range(4))%3 for i in range(4)],
                                    [sum(mat[i][k]*w[k] for k in range(4))%3 for i in range(4)]):
                return False
    return True

print('G1 symplectic?', is_symplectic(G1))
print('G2 symplectic?', is_symplectic(G2))

# define list of generators (choose safe symplectics manually)
# we can programmatically search small matrices for those preserving omega

generators = []
for mat in [G1, G2]:
    if is_symplectic(mat):
        generators.append(mat)

print('using',len(generators),'generators')

# compute induced root permutations and attempt to solve linear maps

def find_matrix_for_perm(perm):
    # want M s.t. M @ root_i = root_perm[i] for all i
    # solve least squares: M = X @ pinv(R) with rows
    R = roots.T  # 8x240
    Rp = np.stack([roots[perm[i]] for i in range(240)]).T
    # solve M R = Rp -> M = Rp R^+ (use pseudo-inverse)
    # use numpy pinv for now
    M = Rp @ np.linalg.pinv(R)
    # check closeness transf
    err = np.max(np.abs(M @ R - Rp))
    return M, err

for gi, mat in enumerate(generators):
    # compute permutation on edges
    perm_edges = []
    for e,(i,j) in enumerate(edges):
        vi = apply_mat(mat, vertices[i])
        vj = apply_mat(mat, vertices[j])
        # find their indices in the vertex list
        try:
            new_i = vertices.index(vi)
            new_j = vertices.index(vj)
        except ValueError:
            print('transformed vertex not in list', vi, vj)
            raise
        if new_i > new_j:
            new_i, new_j = new_j, new_i
        # find the corresponding edge index
        perm_edges.append(edges.index((new_i, new_j)))
    # compute corresponding root perm
    perm_roots = [None]*240
    for e,pe in enumerate(perm_edges):
        perm_roots[e] = map_arr[pe]
    # convert to a permutation of root indices
    root_perm = [0]*240
    for e,r in enumerate(map_arr):
        root_perm[e] = perm_roots[e]
    M,err = find_matrix_for_perm(root_perm)
    print(f'generator {gi}: linear error {err}')
    print('matrix approximation:')
    print(np.round(M,3))

print('Done')
