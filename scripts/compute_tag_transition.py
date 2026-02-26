import sys
import os
# ensure workspace root on path
sys.path.append(os.getcwd())
import numpy as np
from collections import defaultdict

from scripts.ce2_global_cocycle import (
    _simple_family_sign_map,
    _heisenberg_vec_maps,
    _f3_dot,
    _f3_omega,
    all_symplectic_matrices,
    apply_matrix,
    compute_phase,
)

# define the two axis-swap matrices explicitly
A1 = np.array([[0, 2], [1, 0]], dtype=int)  # sends (1,0)->(0,1)
A2 = np.array([[0, 1], [2, 0]], dtype=int)  # sends (1,0)->(0,2)

heis, _ = _heisenberg_vec_maps()

def invariants(u_c, zc, u_m, zm, u_o, zo):
    t = 1 if u_m == u_o else 2
    d1 = (u_m[0] - u_c[0]) % 3
    d2 = (u_m[1] - u_c[1]) % 3
    d = (d1, d2)
    w = _f3_omega(u_c, d)
    s = _f3_dot(u_c, d)
    zsum = (zm + zo) % 3
    return t, d, int(w), int(s), int(zsum)


def lift(A, u, z, mu):
    u_p = apply_matrix(A, u)
    z_p = (z + mu.get(u, 0)) % 3
    return u_p, z_p


for name, A in [('A1', A1), ('A2', A2)]:
    mu = compute_phase(A)
    tag_map = defaultdict(set)
    for key in _simple_family_sign_map().keys():
        c_i, m_i, o_i = key
        uc = tuple(heis[int(c_i)][:2])
        zc = int(heis[int(c_i)][2])
        um = tuple(heis[int(m_i)][:2])
        zm = int(heis[int(m_i)][2])
        uo = tuple(heis[int(o_i)][:2])
        zo = int(heis[int(o_i)][2])
        # original tag
        t0, d0, w0, s0, z0 = invariants(uc, zc, um, zm, uo, zo)
        tag0 = (t0, w0, z0)
        # apply symplectic
        uc2, zc2 = lift(A, uc, zc, mu)
        um2, zm2 = lift(A, um, zm, mu)
        uo2, zo2 = lift(A, uo, zo, mu)
        t1, d1, w1, s1, z1 = invariants(uc2, zc2, um2, zm2, uo2, zo2)
        tag1 = (t1, w1, z1)
        tag_map[tag0].add(tag1)
    print(f"{name} tag transitions:")
    for k, v in sorted(tag_map.items()):
        print(k, '->', v)
    print()
