#!/usr/bin/env python3
"""2.M12 (Golay monomial lifts) -> Sp(12,3): unify the 11A and 3B backends.

This repo has two Monster-side centralizer facts:
  - C_M(11A) = 11 · M12
  - C_M(3B)  = 3^{1+12} · 2.Suz, where 3^{1+12} is an extraspecial (Heisenberg) 3-group
    with 12-dim symplectic phase space V ≅ F3^{12}, and 2.Suz ⊂ Sp(12,3).

On the algebra side, the ternary Golay code C ⊂ F3^{12} (dim 6) is a Lagrangian
subspace for the standard symplectic form once the generator is in systematic
shape [I|A] with A symmetric (verified in scripts/w33_monster_3b_s12_sl27_bridge.py).

The subtlety behind the 11A ↔ Golay bridge is that M12 does not act on C by
pure coordinate permutations; it needs a monomial sign lift (a 2-cover), giving
2.M12 as the actual symmetry group in F3.

This script makes the Heisenberg/symplectic part explicit:

  1) Let W = {(p, A p)} be the Golay Lagrangian (graph of symmetric A).
  2) The symplectic shear S = [[I,0],[-A,I]] sends W to the p-axis P={(p,0)}.
  3) For any code automorphism M (our monomial lifts), the conjugate
         M' = S M S^{-1}
     preserves P, so its upper-left 6×6 block g is the induced GL(6,3) action
     on the message space.
  4) The block-diagonal extension diag(g, g^{-T}) lies in Sp(12,3) and agrees
     with M on W after conjugating back.

So we get a concrete embedding of the 2.M12 Golay symmetry into Sp(12,3), the
same ambient group that hosts 2.Suz in the Monster 3B centralizer.

Run:
  & .venv\\Scripts\\python.exe -X utf8 scripts\\w33_2m12_sp12_embedding.py
"""

from __future__ import annotations

import sys
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
    """Matrix inverse over GF(p). Raises ValueError if singular."""
    A = _mat_mod_p(A, p)
    n = int(A.shape[0])
    if A.shape != (n, n):
        raise ValueError(f"expected square matrix, got {A.shape}")
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

    left = aug[:, :n] % p
    if not np.array_equal(left, np.eye(n, dtype=np.int64) % p):
        raise ValueError("matrix is singular over GF(p)")
    return aug[:, n:] % p


def _standard_symplectic_form(n: int, p: int = 3) -> np.ndarray:
    """Return J0 = [[0,I],[-I,0]] on F_p^{2n}."""
    I = np.eye(n, dtype=np.int64) % p
    Z = np.zeros((n, n), dtype=np.int64)
    top = np.concatenate([Z, I], axis=1) % p
    bot = np.concatenate([(-I) % p, Z], axis=1) % p
    return np.concatenate([top, bot], axis=0) % p


def _monomial_matrix(perm: tuple[int, ...], signs: tuple[int, ...], p: int = 3) -> np.ndarray:
    """Return the monomial matrix D*P in the repo convention perm[i]=j via out[j]=word[i]."""
    n = len(perm)
    M = np.zeros((n, n), dtype=np.int64)
    for i, j in enumerate(perm):
        M[int(j), int(i)] = int(signs[int(j)]) % p
    return M % p


def _act_matrix(M: np.ndarray, v: tuple[int, ...], p: int = 3) -> tuple[int, ...]:
    w = (np.asarray(M, dtype=np.int64) % p) @ (np.asarray(v, dtype=np.int64) % p)
    w = (w % p).astype(np.int64).reshape((-1,))
    return tuple(int(x) % p for x in w.tolist())


def analyze() -> dict[str, Any]:
    from tools.s12_universal_algebra import (
        enumerate_linear_code_f3,
        ternary_golay_generator_matrix,
    )
    from scripts.w33_monster_11a_m12_golay_bridge import analyze as analyze_11a_bridge

    p = 3

    gen = ternary_golay_generator_matrix()
    G = _mat_mod_p(np.array(gen, dtype=np.int64), p)
    if G.shape != (6, 12):
        raise AssertionError(f"unexpected Golay generator shape: {G.shape}")

    I6 = np.eye(6, dtype=np.int64) % p
    systematic = bool(np.array_equal(G[:, :6], I6))
    if not systematic:
        raise AssertionError("expected systematic Golay generator [I|A]")
    A = _mat_mod_p(G[:, 6:], p)
    A_symmetric = bool(np.array_equal(A, A.T))
    if not A_symmetric:
        raise AssertionError("expected symmetric A in systematic Golay generator [I|A]")

    # Shear S(p,q) = (p, q - A p) sends W={(p,Ap)} to the p-axis P={(p,0)}.
    Z6 = np.zeros((6, 6), dtype=np.int64)
    S = np.block([[I6, Z6], [(-A) % p, I6]]) % p
    S_inv = np.block([[I6, Z6], [A % p, I6]]) % p

    I12 = np.eye(12, dtype=np.int64) % p
    assert np.array_equal((S_inv @ S) % p, I12)

    J0 = _standard_symplectic_form(6, p=p)
    assert np.array_equal((S.T @ J0 @ S) % p, J0)

    bridge = analyze_11a_bridge()
    if bridge.get("available") is not True:
        return {"available": False, "reason": bridge.get("reason")}
    golay = bridge.get("golay", {})
    if not isinstance(golay, dict):
        return {"available": False, "reason": "unexpected 11A bridge payload"}

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

    # Conjugate so the Golay Lagrangian becomes the coordinate p-axis.
    M11p = (S @ M11 @ S_inv) % p
    M21p = (S @ M21 @ S_inv) % p
    bl11 = _mat_mod_p(M11p[6:, :6], p)
    bl21 = _mat_mod_p(M21p[6:, :6], p)
    assert np.all(bl11 == 0), "expected conjugated generator to preserve p-axis"
    assert np.all(bl21 == 0), "expected conjugated generator to preserve p-axis"

    g11 = _mat_mod_p(M11p[:6, :6], p)
    g21 = _mat_mod_p(M21p[:6, :6], p)
    g11_inv = _inv_mod_p(g11, p)
    g21_inv = _inv_mod_p(g21, p)

    # Symplectic extension in the p-axis gauge, then conjugate back.
    E11 = np.block([[g11, Z6], [Z6, g11_inv.T % p]]) % p
    E21 = np.block([[g21, Z6], [Z6, g21_inv.T % p]]) % p
    M11_symp = (S_inv @ E11 @ S) % p
    M21_symp = (S_inv @ E21 @ S) % p

    assert np.array_equal((M11_symp.T @ J0 @ M11_symp) % p, J0)
    assert np.array_equal((M21_symp.T @ J0 @ M21_symp) % p, J0)

    # Verify the symplectic embedding matches the original monomial action on the code.
    code = set(tuple(int(x) % p for x in cw) for cw in enumerate_linear_code_f3(gen))
    for cw in code:
        assert _act_matrix(M11, cw, p=p) == _act_matrix(M11_symp, cw, p=p)
        assert _act_matrix(M21, cw, p=p) == _act_matrix(M21_symp, cw, p=p)

    def _order(M: np.ndarray, max_pow: int = 200) -> int | None:
        I = np.eye(M.shape[0], dtype=np.int64) % p
        P = I.copy()
        for k in range(1, max_pow + 1):
            P = (P @ M) % p
            if np.array_equal(P, I):
                return int(k)
        return None

    return {
        "available": True,
        "field_p": 3,
        "golay": {
            "systematic_generator": bool(systematic),
            "A_symmetric": bool(A_symmetric),
        },
        "symplectic": {
            "J0_rank": int(np.linalg.matrix_rank(J0 % p)),
            "S_preserves_J0": True,
            "gens_preserve_J0": True,
        },
        "2m12": {
            "b11_order": _order(M11_symp),
            "b21_order": _order(M21_symp),
        },
    }


def main() -> None:
    rep = analyze()
    if rep.get("available") is not True:
        raise SystemExit(f"Unavailable: {rep}")

    print("=" * 78)
    print("2.M12 (Golay monomial lifts) -> Sp(12,3) embedding (Lagrangian gauge)")
    print("=" * 78)
    print()
    print("§1. Golay generator in Lagrangian gauge")
    print("-" * 58)
    print(f"  systematic [I|A]: {rep['golay']['systematic_generator']}")
    print(f"  A symmetric mod 3: {rep['golay']['A_symmetric']}")
    print()
    print("§2. Symplectic embedding invariants")
    print("-" * 58)
    print(f"  S preserves J0: {rep['symplectic']['S_preserves_J0']}")
    print(f"  generators preserve J0: {rep['symplectic']['gens_preserve_J0']}")
    print(f"  rank(J0) = {rep['symplectic']['J0_rank']} (expected 12)")
    print()
    print("§3. Generator orders (in Sp(12,3) model)")
    print("-" * 58)
    print(f"  ord(b11) = {rep['2m12']['b11_order']}")
    print(f"  ord(b21) = {rep['2m12']['b21_order']}")
    print()
    print("ALL CHECKS PASSED ✓")


if __name__ == "__main__":
    main()

