#!/usr/bin/env python3
"""2.M12 orbit decomposition on the ternary Golay code equals the weight enumerator.

The ternary Golay code G_12 has parameters [12,6,6]_3 and exactly 3^6=729 codewords.
Its classical weight distribution is:

  weight 0:   1
  weight 6: 264
  weight 9: 440
  weight 12: 24

From the repo's Monster 11A bridge, M12 acts on G_12 only after a monomial
sign-lift, giving a 2-cover (2.M12). This script computes the induced action of
those generators on the 728 nonzero message vectors p ∈ F3^6 and shows:

  - the action has exactly three nontrivial orbits of sizes 24, 264, 440
  - each orbit has constant Hamming weight in the codeword (p, A p)

So the group-action orbit decomposition recovers the weight enumerator purely
from the 11A↔Golay bridge machinery.

Run:
  & .venv\\Scripts\\python.exe -X utf8 scripts\\w33_2m12_golay_weight_orbits.py
"""

from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = ROOT / "scripts"
for p in (ROOT, SCRIPTS_DIR):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))


def _mat_mod_p(A: np.ndarray, p: int) -> np.ndarray:
    return (np.asarray(A, dtype=np.int64) % int(p)).astype(np.int64)


def _inv_mod_p(A: np.ndarray, p: int) -> np.ndarray:
    A = _mat_mod_p(A, p)
    n = int(A.shape[0])
    aug = np.concatenate([A.copy(), np.eye(n, dtype=np.int64)], axis=1) % p
    r = 0
    for c in range(n):
        pivot = None
        for i in range(r, n):
            if int(aug[i, c]) % p != 0:
                pivot = i
                break
        if pivot is None:
            continue
        if pivot != r:
            aug[[r, pivot]] = aug[[pivot, r]]
        inv = pow(int(aug[r, c] % p), -1, p)
        aug[r, :] = (aug[r, :] * inv) % p
        for i in range(n):
            if i == r:
                continue
            factor = int(aug[i, c] % p)
            if factor:
                aug[i, :] = (aug[i, :] - factor * aug[r, :]) % p
        r += 1
        if r == n:
            break
    if not np.array_equal(aug[:, :n] % p, np.eye(n, dtype=np.int64) % p):
        raise ValueError("singular matrix over GF(p)")
    return aug[:, n:] % p


def _monomial_matrix(perm: tuple[int, ...], signs: tuple[int, ...], p: int = 3) -> np.ndarray:
    n = len(perm)
    M = np.zeros((n, n), dtype=np.int64)
    for i, j in enumerate(perm):
        M[int(j), int(i)] = int(signs[int(j)]) % p
    return M % p


def _vec_to_int(v: np.ndarray) -> int:
    # little-endian base-3 packing for length-6 vectors
    x = 0
    for i, a in enumerate(v.tolist()):
        x += int(a) * (3**i)
    return int(x)


def _int_to_vec(x: int) -> np.ndarray:
    out = np.zeros((6,), dtype=np.int64)
    y = int(x)
    for i in range(6):
        out[i] = y % 3
        y //= 3
    return out


def _codeword_weight_from_p(p_vec: np.ndarray, A: np.ndarray) -> int:
    p_vec = _mat_mod_p(p_vec.reshape((6, 1)), 3).reshape((6,))
    q = (A @ p_vec) % 3
    cw = np.concatenate([p_vec, q], axis=0) % 3
    return int(np.sum(cw != 0))


def analyze() -> dict[str, Any]:
    from tools.s12_universal_algebra import ternary_golay_generator_matrix
    from scripts.w33_monster_11a_m12_golay_bridge import analyze as analyze_11a_bridge

    p = 3

    gen = ternary_golay_generator_matrix()
    G = _mat_mod_p(np.array(gen, dtype=np.int64), p)
    if G.shape != (6, 12):
        raise AssertionError(f"unexpected Golay generator shape: {G.shape}")
    if not np.array_equal(G[:, :6], np.eye(6, dtype=np.int64) % p):
        raise AssertionError("expected systematic Golay generator [I|A]")
    A = _mat_mod_p(G[:, 6:], p)
    if not np.array_equal(A, A.T):
        raise AssertionError("expected symmetric A in systematic Golay generator [I|A]")

    # Symplectic shear S(p,q)=(p, q-Ap) to extract the induced action on p.
    I6 = np.eye(6, dtype=np.int64) % p
    Z6 = np.zeros((6, 6), dtype=np.int64)
    S = np.block([[I6, Z6], [(-A) % p, I6]]) % p
    S_inv = np.block([[I6, Z6], [A % p, I6]]) % p

    bridge = analyze_11a_bridge()
    if bridge.get("available") is not True:
        return {"available": False, "reason": bridge.get("reason")}
    golay = bridge.get("golay", {})
    gens = golay.get("m12_generators_in_code_coords", {})
    lifts = golay.get("monomial_lift_signs", {})
    if not (isinstance(gens, dict) and isinstance(lifts, dict)):
        return {"available": False, "reason": "missing generators/lifts in bridge payload"}

    b11_perm = tuple(int(x) for x in gens["b11_code_perm"])
    b21_perm = tuple(int(x) for x in gens["b21_code_perm"])
    s11 = tuple(int(x) % p for x in lifts["b11_code"])
    s21 = tuple(int(x) % p for x in lifts["b21_code"])

    M11 = _monomial_matrix(b11_perm, s11, p=p)
    M21 = _monomial_matrix(b21_perm, s21, p=p)
    M11p = (S @ M11 @ S_inv) % p
    M21p = (S @ M21 @ S_inv) % p
    assert np.all((M11p[6:, :6] % p) == 0)
    assert np.all((M21p[6:, :6] % p) == 0)
    g11 = _mat_mod_p(M11p[:6, :6], p)
    g21 = _mat_mod_p(M21p[:6, :6], p)
    g11_inv = _inv_mod_p(g11, p)
    g21_inv = _inv_mod_p(g21, p)
    gens6 = [g11, g21, g11_inv, g21_inv]

    unseen = set(range(1, 3**6))
    orbit_sizes: list[int] = []
    orbit_weights: list[int] = []
    weight_to_orbit_size: dict[int, int] = {}

    while unseen:
        start = unseen.pop()
        q = [start]
        orb = {start}
        while q:
            a = q.pop()
            v = _int_to_vec(a)
            for M in gens6:
                w = (M @ v) % p
                b = _vec_to_int(w)
                if b == 0:
                    continue
                if b not in orb:
                    orb.add(b)
                    q.append(b)
        unseen -= orb

        # weight must be constant on the orbit: verify on all points
        w0 = _codeword_weight_from_p(_int_to_vec(next(iter(orb))), A)
        for a in orb:
            if _codeword_weight_from_p(_int_to_vec(a), A) != w0:
                raise AssertionError("orbit is not weight-homogeneous")

        orbit_sizes.append(len(orb))
        orbit_weights.append(int(w0))
        weight_to_orbit_size[int(w0)] = len(orb)

    hist = dict(sorted(Counter(orbit_sizes).items()))
    by_weight = dict(sorted(weight_to_orbit_size.items()))
    return {
        "available": True,
        "field_p": 3,
        "orbit_size_hist": hist,
        "orbits_by_weight": by_weight,
        "orbit_sizes_sorted": sorted(orbit_sizes),
        "weights_sorted": sorted(set(orbit_weights)),
    }


def main() -> None:
    rep = analyze()
    if rep.get("available") is not True:
        raise SystemExit(f"Unavailable: {rep}")

    print("=" * 78)
    print("2.M12 ORBITS ON NONZERO TERNARY GOLAY CODEWORDS (via message-space action)")
    print("=" * 78)
    print()
    print("orbit size histogram:", rep["orbit_size_hist"])
    print("orbits by weight:", rep["orbits_by_weight"])
    print()

    # canonical weight enumerator for ternary Golay code:
    #   1 + 264 y^6 + 440 y^9 + 24 y^12
    assert rep["orbits_by_weight"] == {6: 264, 9: 440, 12: 24}
    assert rep["orbit_sizes_sorted"] == [24, 264, 440]
    assert rep["weights_sorted"] == [6, 9, 12]
    print("ALL CHECKS PASSED ✓")


if __name__ == "__main__":
    main()

