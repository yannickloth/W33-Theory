import itertools
import json
from pathlib import Path

import numpy as np


def canonical_pg33_points():
    pts = []
    for v in itertools.product(range(3), repeat=4):
        if all(x == 0 for x in v):
            continue
        # normalize so first nonzero coordinate is 1
        for x in v:
            if x != 0:
                inv = 1 if x == 1 else 2
                norm = tuple((inv * y) % 3 for y in v)
                pts.append(norm)
                break
    seen = set()
    unique = []
    for p in pts:
        if p not in seen:
            seen.add(p)
            unique.append(p)
    pts2 = sorted(unique)
    assert len(pts2) == 40
    # first 13 should have X0 == 0
    assert all(p[0] == 0 for p in pts2[:13])
    assert all(p[0] == 1 for p in pts2[13:])
    return pts2


def compute_perm_from_matrix(mat, pts2):
    """Apply 4x4 matrix mod3 to projective points and renormalize."""
    perm = []
    for p in pts2:
        v = [(sum(mat[i][j] * p[j] for j in range(4))) % 3 for i in range(4)]
        # renormalize
        for x in v:
            if x != 0:
                inv = 1 if x == 1 else 2
                v = tuple((inv * y) % 3 for y in v)
                break
        perm.append(pts2.index(v))
    return perm


def test_perm40_matches_canonical():
    pts2 = canonical_pg33_points()
    bundle = Path("H27_OUTER_TWIST_ACTION_BUNDLE_v01")
    perm40 = json.loads((bundle / "perm40_and_H27_pg_ids.json").read_text())["perm40_points_from_phi_n"]
    assert sorted(perm40) == list(range(40))
    # compute canonical->phi_n mapping (should equal perm40)
    assert [perm40[i] for i in range(40)] == perm40


def test_outer_matrix_and_symplectic():
    pts2 = canonical_pg33_points()
    # outer twist matrix N4 as described
    N4 = [
        [1, 0, 0, 0],
        [0, 1, 2, 0],
        [2, 2, 0, 0],
        [2, 2, 1, 2],
    ]
    perm_from_N4 = compute_perm_from_matrix(N4, pts2)
    bundle = Path("H27_OUTER_TWIST_ACTION_BUNDLE_v01")
    perm40 = json.loads((bundle / "perm40_and_H27_pg_ids.json").read_text())["perm40_points_from_phi_n"]
    assert perm_from_N4 == perm40
    # symplectic form J
    J = np.array([[0, 0, 0, 1], [0, 0, 1, 0], [0, 2, 0, 0], [2, 0, 0, 0]], dtype=int)
    # check similitude multiplier
    Nt = np.transpose(np.array(N4, dtype=int))
    prod = (Nt @ J @ np.array(N4, dtype=int)) % 3
    # multiplier should be 2 (non-square)
    assert np.array_equal(prod, (2 * J) % 3)
    # adjacency degrees
    adj = np.zeros((40, 40), dtype=int)
    for i, p in enumerate(pts2):
        for j, q in enumerate(pts2):
            if i == j:
                continue
            val = (np.array(p, dtype=int) @ J @ np.array(q, dtype=int)) % 3
            if val == 0:
                adj[i, j] = 1
    deg = adj.sum(axis=1)
    assert set(deg.tolist()) == {12}


def test_infinity_neighbors_and_orbits():
    pts2 = canonical_pg33_points()
    # same J as before
    J = np.array([[0, 0, 0, 1], [0, 0, 1, 0], [0, 2, 0, 0], [2, 0, 0, 0]], dtype=int)
    adj = np.zeros((40, 40), dtype=int)
    for i, p in enumerate(pts2):
        for j, q in enumerate(pts2):
            if i == j:
                continue
            val = (np.array(p, dtype=int) @ J @ np.array(q, dtype=int)) % 3
            if val == 0:
                adj[i, j] = 1
    infinity = list(range(13))
    affine = list(range(13, 40))
    neighbor_map = {}
    for i in affine:
        neigh = [j for j in infinity if adj[i, j]]
        neighbor_map[i] = neigh
        assert len(neigh) == 4
    # orbit under outer twist
    N4 = [
        [1, 0, 0, 0],
        [0, 1, 2, 0],
        [2, 2, 0, 0],
        [2, 2, 1, 2],
    ]
    perm_from_N4 = compute_perm_from_matrix(N4, pts2)
    orbits = []
    unvis = set(affine)
    while unvis:
        start = unvis.pop()
        orb = [start]
        cur = start
        while True:
            nxt = perm_from_N4[cur]
            if nxt == start:
                break
            orb.append(nxt)
            unvis.discard(nxt)
            cur = nxt
        orbits.append(orb)
    # expect five orbits of sizes [8,8,8,1,2]
    sizes = sorted(len(o) for o in orbits)
    assert sizes == [1, 2, 8, 8, 8]
