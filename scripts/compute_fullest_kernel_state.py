import sys, os
sys.path.append(os.getcwd())
import numpy as np
from collections import defaultdict

from scripts.ce2_global_cocycle import (
    _simple_family_sign_map,
    _heisenberg_vec_maps,
    _f3_dot,
    _f3_omega,
    apply_matrix,
    compute_phase,
)

A1 = np.array([[0, 2], [1, 0]], dtype=int)
A2 = np.array([[0, 1], [2, 0]], dtype=int)

heis, _ = _heisenberg_vec_maps()

def lift(A, u, z, mu):
    u_p = apply_matrix(A, u)
    z_p = (z + mu.get(u, 0)) % 3
    return u_p, z_p

for name, A in [('A1', A1), ('A2', A2)]:
    mu = compute_phase(A)
    mapping = defaultdict(set)
    for key in _simple_family_sign_map().keys():
        c_i,m_i,o_i = key
        uc = tuple(heis[int(c_i)][:2]); zc = int(heis[int(c_i)][2])
        um = tuple(heis[int(m_i)][:2]); zm = int(heis[int(m_i)][2])
        uo = tuple(heis[int(o_i)][:2]); zo = int(heis[int(o_i)][2])
        t0 = 1 if um==uo else 2
        d1 = (um[0]-uc[0])%3; d2=(um[1]-uc[1])%3
        w0 = int(_f3_omega(uc,(d1,d2)))
        s0 = int(_f3_dot(uc,(d1,d2)))
        state0 = (t0,s0,w0,zm,zo)
        uc2, zc2 = lift(A, uc, zc, mu)
        um2, zm2 = lift(A, um, zm, mu)
        uo2, zo2 = lift(A, uo, zo, mu)
        t1 = 1 if um2==uo2 else 2
        d1 = (um2[0]-uc2[0])%3; d2=(um2[1]-uc2[1])%3
        w1 = int(_f3_omega(uc2,(d1,d2)))
        s1 = int(_f3_dot(uc2,(d1,d2)))
        state1 = (t1,s1,w1,zm2,zo2)
        mapping[state0].add(state1)
    print(name,'transitions (should be singletons):')
    for k,v in sorted(mapping.items())[:20]:
        print(k,'->',v)
    print('... total keys', len(mapping))
    multi = [k for k,v in mapping.items() if len(v)>1]
    print('multi-case count', len(multi))
    print()
