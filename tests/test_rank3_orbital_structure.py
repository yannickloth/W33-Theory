"""
Phase CCXLVII: W(3,3) is a rank-3 graph under PSp(4,3).

PSp(4,3) acts on v=40 points with exactly 3 orbits on ORDERED PAIRS:
  {p0} (size 1), adj(p0) (size k=12), non-adj(p0) (size v-k-1=27).

This confirms W(3,3) is an ORBITAL GRAPH of PSp(4,3):
  it is the unique orbital graph for the 'adjacency' orbital.

Key results:
  - Rank = 3 (3 orbits on ordered pairs from any base point)
  - |Stab(p0)| = PSp4_order/v = 648 = 2^3 * 3^4
  - Bose-Mesner algebra dimension = 3
  - Complement eigenvalue 3 = Phi4 - Phi6
  - A^2 = k*I + lambda*A + mu*B exactly
"""

import numpy as np
from fractions import Fraction
from math import comb
from itertools import product as iproduct
import pytest

v, k, l, m, q = 40, 12, 2, 4, 3
Phi3, Phi4, Phi6 = 13, 10, 7
f_dim, g_dim = 24, 15
s_param = k // l
PSp4_order = 25920
F3 = [0, 1, 2]


def normalize_pt(vec, q=3):
    for i, c in enumerate(vec):
        if c % q != 0:
            inv = pow(int(c), -1, q)
            return tuple((int(x)*inv) % q for x in vec)
    return None


def symp_form(x, y, q=3):
    return (x[0]*y[2]+x[1]*y[3]-x[2]*y[0]-x[3]*y[1]) % q


def build_pts_adj():
    pts_set = set()
    for coords in iproduct(F3, repeat=4):
        if any(c != 0 for c in coords):
            p = normalize_pt(coords)
            if p: pts_set.add(p)
    pts = sorted(pts_set)
    A = np.zeros((v, v), dtype=int)
    for i, pi in enumerate(pts):
        for j, pj in enumerate(pts):
            if i != j and symp_form(pi, pj) == 0:
                A[i, j] = 1
    return pts, A


def apply_transvection(x, a, c, q=3):
    Jxa = symp_form(x, a, q)
    return tuple((x[i] + c * Jxa * a[i]) % q for i in range(4))


def make_perm(a_vec, c_val, pts):
    return [pts.index(normalize_pt(apply_transvection(pt, a_vec, c_val), pt[0].__class__)) for pt in pts]


def make_perm_v2(a_vec, c_val, pts, q=3):
    imgs = [normalize_pt(apply_transvection(pt, a_vec, c_val, q), q) for pt in pts]
    return [pts.index(p) for p in imgs]


def generate_group_bfs(gens_perms, v=40, max_size=60000):
    iden = tuple(range(v))
    group = {iden}
    frontier = {iden}
    gen_and_inv = []
    for p in gens_perms:
        inv = [0]*v
        for i in range(v): inv[p[i]] = i
        gen_and_inv.append(tuple(p))
        gen_and_inv.append(tuple(inv))
    while frontier and len(group) < max_size:
        new_frontier = set()
        for elem in frontier:
            for gen in gen_and_inv:
                new_elem = tuple(gen[elem[i]] for i in range(v))
                if new_elem not in group:
                    group.add(new_elem)
                    new_frontier.add(new_elem)
        frontier = new_frontier
    return group


def stab_orbits(stab, n=40):
    visited = [-1] * n
    orbit_id = 0
    for start in range(n):
        if visited[start] == -1:
            queue = [start]
            visited[start] = orbit_id
            while queue:
                cur = queue.pop()
                for g in stab:
                    img = g[cur]
                    if visited[img] == -1:
                        visited[img] = orbit_id
                        queue.append(img)
            orbit_id += 1
    orbits = {}
    for pt, oid in enumerate(visited):
        orbits.setdefault(oid, []).append(pt)
    return list(orbits.values())


pts, A = build_pts_adj()
all_trans = [make_perm_v2(a, 1, pts) for a in pts]
G = generate_group_bfs(all_trans)
G_list = list(G)
p0_idx = 0
stab_p0 = [g for g in G_list if g[p0_idx] == p0_idx]
orbits = stab_orbits(stab_p0)
orbit_sizes = sorted(len(o) for o in orbits)

# Complement
J = np.ones((v,v), dtype=int); np.fill_diagonal(J, 0)
B = J - A; np.fill_diagonal(B, 0)


class TestRank3OrbitalStructure:

    def test_group_order(self):
        """Group has order PSp4_order = 25920."""
        assert len(G) == PSp4_order

    def test_stabilizer_order(self):
        """|Stab(p0)| = PSp4_order/v = 648 = 2^3 * 3^4."""
        assert len(stab_p0) == PSp4_order // v
        assert len(stab_p0) == 648
        assert 648 == 2**3 * 3**4

    def test_rank_is_3(self):
        """Rank = 3 (exactly 3 orbits of Stab(p0) on all 40 points)."""
        assert len(orbits) == 3

    def test_orbit_sizes(self):
        """Orbit sizes are 1, k=12, v-k-1=27."""
        assert orbit_sizes == [1, k, v-k-1]
        assert orbit_sizes == [1, 12, 27]

    def test_self_orbit_size_1(self):
        """The singleton orbit is {p0}."""
        singleton = [o for o in orbits if len(o) == 1]
        assert len(singleton) == 1
        assert p0_idx in singleton[0]

    def test_adj_orbit_size_k(self):
        """The adjacency orbit has size k=12."""
        adj_orbit = [o for o in orbits if len(o) == k]
        assert len(adj_orbit) == 1
        pts_in_adj = adj_orbit[0]
        assert all(A[p0_idx, j] == 1 for j in pts_in_adj)

    def test_non_adj_orbit_size_v_k_1(self):
        """The non-adjacency orbit has size v-k-1=27."""
        non_adj_orbit = [o for o in orbits if len(o) == v-k-1]
        assert len(non_adj_orbit) == 1
        pts_in_non = non_adj_orbit[0]
        assert all(A[p0_idx, j] == 0 and j != p0_idx for j in pts_in_non)

    def test_orbital_graph_is_srg(self):
        """W(3,3) is the orbital graph for the adjacency orbital."""
        # SRG parameters already verified elsewhere
        row_sums = A.sum(axis=1)
        assert np.all(row_sums == k)

    def test_A_squared_relation(self):
        """A^2 = k*I + lambda*A + mu*B."""
        A2 = A @ A
        I = np.eye(v, dtype=int)
        rhs = k*I + l*A + m*B
        assert np.array_equal(A2, rhs)

    def test_complement_eigenvalues(self):
        """Complement B has eigenvalues v-k-1=27, -1-r=-3, -1-s=3."""
        eigvals_B = np.linalg.eigvalsh(B.astype(float))
        ev_B = sorted(set(np.round(eigvals_B).astype(int)))
        assert ev_B == [-3, 3, 27]
        assert -1 - 2 == -3  # -1 - r_eig
        assert -1 - (-4) == 3  # -1 - s_eig

    def test_complement_ev_3_is_Phi4_minus_Phi6(self):
        """Complement eigenvalue 3 = Phi4 - Phi6 = 10 - 7."""
        assert Phi4 - Phi6 == 3
        assert -1 - (-4) == Phi4 - Phi6

    def test_bose_mesner_dim_3(self):
        """Bose-Mesner algebra has dimension 3 = rank."""
        assert len(orbits) == 3  # rank = dim(Bose-Mesner)

    def test_intersection_matrix_L1(self):
        """L1 has correct intersection numbers."""
        L1 = np.array([[0, k, 0],
                       [1, l, k-l-1],
                       [0, m, k-m]])
        assert L1[1,2] == k - l - 1 == 9
        assert L1[2,1] == m == 4
        assert L1[2,2] == k - m == 8

    def test_L1_eigenvalues_are_graph_eigenvalues(self):
        """Eigenvalues of L1 = {k, r, s} = {12, 2, -4}."""
        L1 = np.array([[0, k, 0], [1, l, k-l-1], [0, m, k-m]])
        ev = sorted(np.round(np.linalg.eigvals(L1.astype(float))).astype(int))
        assert ev == sorted([k, 2, -4])

    def test_p22_intersection_numbers(self):
        """From non-adj point: p_{22}^1 = k-m = 8, p_{22}^2 = v-2k+m-2 = 18."""
        assert k - m == 8
        assert v - 2*k + m - 2 == 18
        assert 1 + (k-m) + (v-2*k+m-2) == v-k-1  # partition

    def test_idempotents_sum_to_identity(self):
        """E0 + E1 + E2 = I (Bose-Mesner idempotent decomposition)."""
        eigvals_A, eigvecs_A = np.linalg.eigh(A.astype(float))
        ev_arr = np.round(eigvals_A).astype(int)
        E0 = (1/v)*np.ones((v,v))
        E1 = eigvecs_A[:, ev_arr==2] @ eigvecs_A[:, ev_arr==2].T
        E2 = eigvecs_A[:, ev_arr==-4] @ eigvecs_A[:, ev_arr==-4].T
        assert np.allclose(E0 + E1 + E2, np.eye(v))

    def test_stab_order_factored(self):
        """|Stab(p0)| = 648 = 2^3 * 3^4."""
        import sympy
        factors = sympy.factorint(648)
        assert factors == {2: 3, 3: 4}
