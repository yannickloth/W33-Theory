"""Align the two 2.M12 backends via order-3 Jordan signatures in the 6D action.

This repo contains two *independent* constructions of a 2-cover of Mathieu M12:

  1) Monster 3B backend (Heisenberg cofactor):  2.Suz ⊂ Sp(12,3)
     with an ATLAS-word maximal subgroup witness M12:2 < Suz.

  2) Monster 11A backend (Golay code): monomial sign lifts on the ternary Golay
     code give 2.M12, and we embed it into Sp(12,3) via the Golay Lagrangian
     gauge (scripts/w33_2m12_sp12_embedding.py).

New rigid bridge (regression-testable):
  Both embeddings induce a faithful 6D representation of 2.M12 over F3
  (the Lagrangian block in a polarization basis), and the order-3 elements split
  into two Jordan types with *exact* class-size counts:

    Counter({(4,2): 2640, (3,1): 1760, (0,0): 1})

These are the two order-3 conjugacy class sizes in M12 (lifted inside 2.M12),
where the signature is computed from N = g - I in characteristic 3:
  signature(g) := (rank(N), rank(N^2)) over F3.

Run:
  & .venv\\Scripts\\python.exe -X utf8 scripts\\w33_2m12_order3_signature_alignment.py
"""

from __future__ import annotations

import sys
import time
from collections import Counter
from pathlib import Path
from typing import Any, Iterable

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = ROOT / "scripts"
for p in (ROOT, SCRIPTS_DIR):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))


def _mat_mod_p(A: np.ndarray, p: int) -> np.ndarray:
    return (np.asarray(A, dtype=np.int64) % int(p)).astype(np.int64)


def _group_elements_bytes(
    gens: Iterable[np.ndarray], *, p: int = 3, limit: int | None = None
) -> list[bytes]:
    """Enumerate group elements by BFS closure under right-multiplication."""
    gens = [(_mat_mod_p(g, p)).astype(np.int16) for g in gens]
    if not gens:
        return [np.eye(1, dtype=np.uint8).tobytes()]
    n = int(gens[0].shape[0])
    I = (np.eye(n, dtype=np.int64) % p).astype(np.uint8)
    id_b = I.tobytes()
    elems: list[bytes] = [id_b]
    seen: set[bytes] = {id_b}

    idx = 0
    while idx < len(elems):
        g_b = elems[idx]
        idx += 1
        g = (
            np.frombuffer(g_b, dtype=np.uint8)
            .astype(np.int16, copy=False)
            .reshape((n, n))
        )
        for gen in gens:
            h = (g @ gen) % p
            h_b = h.astype(np.uint8, copy=False).tobytes()
            if h_b in seen:
                continue
            seen.add(h_b)
            elems.append(h_b)
            if limit is not None and len(seen) > int(limit):
                raise RuntimeError(f"group enumeration exceeded limit={limit}")
    return elems


def _rank_mod_p(M: np.ndarray, p: int) -> int:
    """Rank over F_p via row reduction (small dense matrices)."""
    from scripts.w33_2suz_m12_2_subgroup import _row_reduce_mod_p

    r, _rref, _piv = _row_reduce_mod_p(_mat_mod_p(M, p), p)
    return int(r)


def _order3_signature_counts(elems: list[bytes], *, p: int = 3) -> Counter[tuple[int, int]]:
    """Count signatures for all g with g^3=I (includes identity)."""
    if not elems:
        return Counter()
    n2 = int(len(elems[0]))
    n = int(round(n2**0.5))
    if n * n != n2:
        raise ValueError("unexpected element byte length for square matrix")

    I = np.eye(n, dtype=np.int64) % p
    counts: Counter[tuple[int, int]] = Counter()
    for b in elems:
        M = np.frombuffer(b, dtype=np.uint8).astype(np.int64, copy=False).reshape((n, n)) % p
        if not np.array_equal((M @ M @ M) % p, I):
            continue
        N = (M - I) % p
        sig = (_rank_mod_p(N, p), _rank_mod_p((N @ N) % p, p))
        counts[sig] += 1
    return counts


def _suz_gblock_generators() -> tuple[np.ndarray, np.ndarray]:
    """Return (Gy, Gyx) as 6×6 generators for the derived 2.M12 action."""
    from scripts.w33_2suz_sp12_embedding import analyze as analyze_2suz
    from scripts.w33_2suz_m12_2_subgroup import (
        _basis_matrix,
        _commutant_basis,
        _find_involutive_commutant_element,
        _nullspace_basis_mod_p,
        _solve_in_basis,
        _standard_symplectic_form,
        _symplectic_inverse,
        build_m12_2_generators_from_suz,
    )

    rep = analyze_2suz()
    std = rep["standardized_generators"]
    A = np.array(std["A_std_mod3"], dtype=np.int64) % 3
    B = np.array(std["B_std_mod3"], dtype=np.int64) % 3

    J0 = _standard_symplectic_form(6, p=3)
    I12 = np.eye(12, dtype=np.int64) % 3

    gens = build_m12_2_generators_from_suz(A, B, p=3)
    x = gens["x"]
    y = gens["y"]
    x_inv = _symplectic_inverse(x, J0, p=3)
    y_conj = (x_inv @ y @ x) % 3

    comm = _commutant_basis([y, y_conj], p=3)
    inv = _find_involutive_commutant_element(comm, p=3)
    if inv is None:
        raise RuntimeError("failed to find commutant involution for Suz-derived 2.M12")

    U_plus = _basis_matrix(_nullspace_basis_mod_p((inv - I12) % 3, 3), p=3)
    if U_plus.shape != (12, 6):
        raise RuntimeError(f"unexpected +1 eigenspace basis shape: {U_plus.shape}")

    Gy = _solve_in_basis(U_plus, (y @ U_plus) % 3, p=3)
    Gyx = _solve_in_basis(U_plus, (y_conj @ U_plus) % 3, p=3)
    return Gy % 3, Gyx % 3


def _golay_gblock_generators() -> tuple[np.ndarray, np.ndarray]:
    """Return (g11, g21) as 6×6 generators from Golay monomial lifts (p-axis gauge)."""
    from tools.s12_universal_algebra import ternary_golay_generator_matrix
    from scripts.w33_monster_11a_m12_golay_bridge import analyze as analyze_11a_bridge

    p = 3
    gen = ternary_golay_generator_matrix()
    G = _mat_mod_p(np.array(gen, dtype=np.int64), p)
    if G.shape != (6, 12):
        raise RuntimeError(f"unexpected Golay generator shape: {G.shape}")
    I6 = np.eye(6, dtype=np.int64) % p
    if not np.array_equal(G[:, :6], I6):
        raise RuntimeError("expected systematic Golay generator [I|A]")
    A = _mat_mod_p(G[:, 6:], p)

    Z6 = np.zeros((6, 6), dtype=np.int64)
    S = np.block([[I6, Z6], [(-A) % p, I6]]) % p
    S_inv = np.block([[I6, Z6], [A % p, I6]]) % p

    bridge = analyze_11a_bridge(compute_monomial_order=False)
    if bridge.get("available") is not True:
        raise RuntimeError(f"11A bridge unavailable: {bridge.get('reason')}")
    golay = bridge["golay"]
    gens = golay["m12_generators_in_code_coords"]
    lifts = golay["monomial_lift_signs"]

    b11_perm = tuple(int(x) for x in gens["b11_code_perm"])
    b21_perm = tuple(int(x) for x in gens["b21_code_perm"])
    s11 = tuple(int(x) % p for x in lifts["b11_code"])
    s21 = tuple(int(x) % p for x in lifts["b21_code"])

    def _monomial_matrix(perm: tuple[int, ...], signs: tuple[int, ...]) -> np.ndarray:
        n = len(perm)
        M = np.zeros((n, n), dtype=np.int64)
        for i, j in enumerate(perm):
            M[int(j), int(i)] = int(signs[int(j)]) % p
        return M % p

    M11 = _monomial_matrix(b11_perm, s11)
    M21 = _monomial_matrix(b21_perm, s21)

    M11p = (S @ M11 @ S_inv) % p
    M21p = (S @ M21 @ S_inv) % p
    g11 = M11p[:6, :6] % p
    g21 = M21p[:6, :6] % p
    return g11 % p, g21 % p


def analyze() -> dict[str, Any]:
    p = 3
    expected = Counter({(4, 2): 2640, (3, 1): 1760, (0, 0): 1})

    Gy, Gyx = _suz_gblock_generators()
    suz_elems = _group_elements_bytes([Gy, Gyx], p=p, limit=250_000)
    suz_counts = _order3_signature_counts(suz_elems, p=p)

    g11, g21 = _golay_gblock_generators()
    golay_elems = _group_elements_bytes([g11, g21], p=p, limit=250_000)
    golay_counts = _order3_signature_counts(golay_elems, p=p)

    return {
        "available": True,
        "field_p": int(p),
        "expected_order3_signature_counts": dict(expected),
        "suz": {
            "group_order": int(len(suz_elems)),
            "order3_signature_counts": dict(suz_counts),
        },
        "golay": {
            "group_order": int(len(golay_elems)),
            "order3_signature_counts": dict(golay_counts),
        },
        "alignment": {
            "counts_match": bool(suz_counts == golay_counts),
            "counts_match_expected": bool(suz_counts == expected and golay_counts == expected),
        },
    }


def main() -> None:
    t0 = time.time()
    rep = analyze()
    if rep.get("available") is not True:
        raise SystemExit(f"Unavailable: {rep}")

    print("=" * 78)
    print("2.M12 ALIGNMENT: SUZ (3B backend) vs GOLAY (11A backend) via order-3 signatures")
    print("=" * 78)
    print()

    expected = Counter(rep["expected_order3_signature_counts"])
    print("Expected order-3 Jordan signature counts (incl. identity):")
    print(f"  {expected}")

    suz = rep["suz"]
    golay = rep["golay"]
    print()
    print("§1. Suz-derived 6D action (polarization block)")
    print("-" * 58)
    print(f"  |G| = {int(suz['group_order'])} (expect 190080)")
    print(f"  order-3 signature counts: {Counter(suz['order3_signature_counts'])}")

    print()
    print("§2. Golay-derived 6D action (p-axis gauge)")
    print("-" * 58)
    print(f"  |G| = {int(golay['group_order'])} (expect 190080)")
    print(f"  order-3 signature counts: {Counter(golay['order3_signature_counts'])}")

    print()
    print("§3. Alignment checks")
    print("-" * 58)
    print(f"  suz == golay counts: {bool(rep['alignment']['counts_match'])}")
    print(f"  both match expected: {bool(rep['alignment']['counts_match_expected'])}")

    assert int(suz["group_order"]) == 190_080
    assert int(golay["group_order"]) == 190_080
    assert Counter(suz["order3_signature_counts"]) == expected
    assert Counter(golay["order3_signature_counts"]) == expected

    print()
    print("ALL CHECKS PASSED ✓")
    print(f"Elapsed: {time.time() - t0:.2f}s")


if __name__ == "__main__":
    main()

