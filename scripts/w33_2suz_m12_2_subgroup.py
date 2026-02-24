#!/usr/bin/env python3
"""Maximal-subgroup witness: M12:2 inside Suz via ATLAS standard-generator words.

We already have an *offline* matrix model of the double cover ``2.Suz`` over GF(3)
in ``scripts/w33_2suz_sp12_embedding.py`` (the Monster 3B / Heisenberg backend).

ATLAS (Wilson/Parker/Bray) lists ``M12:2`` as a maximal subgroup of ``Suz`` with
standard generators given as explicit words in the *standard generators* ``a,b``
of Suz:

  - x = (ab)^(-2) * b * a * b
  - y = (abb)^(-6) * b * (abb)^(6)

Source: ATLAS pages for Suz (both v2 and v3 show the same words).

This script evaluates those words in our ``2.Suz ⊂ Sp(12,3)`` model and then
computes the resulting subgroup orders by explicit closure (safe here because
|M12:2| = 190,080 and its preimage in 2.Suz has order 380,160).

Run:
  & .venv\\Scripts\\python.exe -X utf8 scripts\\w33_2suz_m12_2_subgroup.py
"""

from __future__ import annotations

import sys
import time
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


def _row_reduce_mod_p(mat: np.ndarray, p: int) -> tuple[int, np.ndarray, list[int]]:
    """Return (rank, rref, pivot_cols) for mat over F_p (small p, dense)."""
    A = _mat_mod_p(mat, p).astype(np.int64, copy=True)
    n_rows, n_cols = A.shape
    rank = 0
    pivot_cols: list[int] = []

    for col in range(n_cols):
        pivot = None
        for r in range(rank, n_rows):
            if int(A[r, col]) % p != 0:
                pivot = r
                break
        if pivot is None:
            continue
        if pivot != rank:
            A[[rank, pivot], :] = A[[pivot, rank], :]
        inv = pow(int(A[rank, col]) % p, -1, p)
        A[rank, :] = (A[rank, :] * inv) % p
        for r in range(n_rows):
            if r == rank:
                continue
            factor = int(A[r, col]) % p
            if factor:
                A[r, :] = (A[r, :] - factor * A[rank, :]) % p
        pivot_cols.append(int(col))
        rank += 1
        if rank == n_rows:
            break

    return int(rank), A, pivot_cols


def _nullspace_basis_mod_p(mat: np.ndarray, p: int) -> list[np.ndarray]:
    """Return a basis (as vectors) for the right nullspace of mat over F_p."""
    rank, rref, pivots = _row_reduce_mod_p(mat, p)
    n_cols = int(rref.shape[1])
    free_cols = [c for c in range(n_cols) if c not in pivots]
    basis: list[np.ndarray] = []
    for free in free_cols:
        v = np.zeros(n_cols, dtype=np.int64)
        v[free] = 1
        for i in range(rank):
            pivot_col = pivots[i]
            v[pivot_col] = (-int(rref[i, free])) % p
        basis.append(v % p)
    return basis


def _standard_symplectic_form(n: int, p: int = 3) -> np.ndarray:
    """Return J0 = [[0,I],[-I,0]] on F_p^{2n}."""
    I = np.eye(n, dtype=np.int64) % p
    Z = np.zeros((n, n), dtype=np.int64)
    top = np.concatenate([Z, I], axis=1) % p
    bot = np.concatenate([(-I) % p, Z], axis=1) % p
    return np.concatenate([top, bot], axis=0) % p


def _symplectic_inverse(M: np.ndarray, J0: np.ndarray, p: int = 3) -> np.ndarray:
    """Inverse in Sp(J0): M^{-1} = J0^{-1} M^T J0 = -J0 M^T J0."""
    M = _mat_mod_p(M, p)
    J0 = _mat_mod_p(J0, p)
    return ((-J0) @ (M.T % p) @ J0) % p


def _pow_mod_p(
    M: np.ndarray, k: int, *, p: int = 3, J0: np.ndarray | None = None
) -> np.ndarray:
    """Fast exponentiation over GF(p). If J0 given, uses symplectic inverse for k<0."""
    M = _mat_mod_p(M, p)
    if k == 0:
        return np.eye(M.shape[0], dtype=np.int64) % p
    if k < 0:
        if J0 is None:
            raise ValueError("negative exponent requires J0 for symplectic inverse")
        M = _symplectic_inverse(M, J0, p=p)
        k = -k
    out = np.eye(M.shape[0], dtype=np.int64) % p
    base = M.copy()
    while k:
        if k & 1:
            out = (out @ base) % p
        base = (base @ base) % p
        k >>= 1
    return out % p


def _matrix_bytes(M: np.ndarray) -> bytes:
    """Canonical byte representation for hashing (values are 0/1/2)."""
    return (np.asarray(M, dtype=np.int64) % 3).astype(np.uint8, copy=False).tobytes()


def _matrix_group_order(
    gens: Iterable[np.ndarray], *, p: int = 3, limit: int | None = None
) -> int | None:
    """Brute-force group order by closure under right-multiplication by gens."""
    gens = [(_mat_mod_p(g, p)).astype(np.int16) for g in gens]
    if not gens:
        return 1
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
                return None
    return int(len(seen))


def _order_mod_p(M: np.ndarray, *, p: int = 3, max_pow: int = 5000) -> int | None:
    """Return the multiplicative order of M in GL(n,p) if <= max_pow."""
    M = _mat_mod_p(M, p).astype(np.int16)
    n = int(M.shape[0])
    I = np.eye(n, dtype=np.int16) % p
    P = I.copy()
    for k in range(1, int(max_pow) + 1):
        P = (P @ M) % p
        if np.array_equal(P, I):
            return int(k)
    return None


def build_m12_2_generators_from_suz(a: np.ndarray, b: np.ndarray, *, p: int = 3) -> dict[str, np.ndarray]:
    """Return ATLAS-word generators for M12:2 inside Suz from standard generators a,b."""
    J0 = _standard_symplectic_form(6, p=p)
    ab = (a @ b) % p
    x = (_pow_mod_p(ab, -2, p=p, J0=J0) @ b @ a @ b) % p

    abb = (a @ b @ b) % p
    abb6 = _pow_mod_p(abb, 6, p=p, J0=J0)
    y = (_pow_mod_p(abb, -6, p=p, J0=J0) @ b @ abb6) % p
    return {"x": x % p, "y": y % p}


def _commutant_basis(gens: Iterable[np.ndarray], *, p: int = 3) -> list[np.ndarray]:
    """Return a basis for the commutant {X : Xg=gX for all g in gens} over F_p."""
    gens = [_mat_mod_p(g, p) for g in gens]
    if not gens:
        return []
    n = int(gens[0].shape[0])
    I = np.eye(n, dtype=np.int64) % p

    blocks: list[np.ndarray] = []
    for g in gens:
        g = _mat_mod_p(g, p)
        # Using column-major vec: vec(Xg - gX) = (g^T⊗I - I⊗g) vec(X).
        K = (np.kron(g.T, I) - np.kron(I, g)) % p
        blocks.append(K.astype(np.int64, copy=False))
    system = np.concatenate(blocks, axis=0) % p

    vec_basis = _nullspace_basis_mod_p(system, p)
    out: list[np.ndarray] = []
    for v in vec_basis:
        out.append(v.reshape((n, n), order="F") % p)
    return out


def _is_scalar_multiple_of_identity(M: np.ndarray, *, p: int = 3) -> bool:
    M = _mat_mod_p(M, p)
    n = int(M.shape[0])
    I = np.eye(n, dtype=np.int64) % p
    return any(np.array_equal(M, (c * I) % p) for c in range(p))


def _find_involutive_commutant_element(
    comm_basis: list[np.ndarray], *, p: int = 3
) -> np.ndarray | None:
    """Find a non-scalar J in span(comm_basis) with J^2=I (if one exists)."""
    if not comm_basis:
        return None
    n = int(comm_basis[0].shape[0])
    I = np.eye(n, dtype=np.int64) % p

    candidates: list[np.ndarray] = []
    if len(comm_basis) > 4:
        # For large commutants this search can explode; we only need the dim-2 case.
        return None

    from itertools import product

    for coeffs in product(range(p), repeat=len(comm_basis)):
        if all(int(c) == 0 for c in coeffs):
            continue
        M = np.zeros((n, n), dtype=np.int64)
        for c, B in zip(coeffs, comm_basis, strict=False):
            if int(c):
                M = (M + int(c) * B) % p
        if _is_scalar_multiple_of_identity(M, p=p):
            continue
        if np.array_equal((M @ M) % p, I):
            candidates.append(M % p)

    if not candidates:
        return None
    candidates.sort(key=_matrix_bytes)
    return candidates[0]


def _basis_matrix(vecs: list[np.ndarray], *, p: int = 3) -> np.ndarray:
    if not vecs:
        return np.zeros((0, 0), dtype=np.int64)
    cols = [_mat_mod_p(v.reshape(-1, 1), p).reshape(-1) for v in vecs]
    return (np.column_stack(cols) % p).astype(np.int64, copy=False)


def _is_totally_isotropic(U: np.ndarray, J0: np.ndarray, *, p: int = 3) -> bool:
    if U.size == 0:
        return False
    B = (U.T @ (J0 % p) @ U) % p
    return bool(np.all(B % p == 0))


def _solve_in_basis(basis: np.ndarray, vecs: np.ndarray, *, p: int = 3) -> np.ndarray:
    """Solve basis @ X = vecs over F_p (basis must have full column rank)."""
    basis = _mat_mod_p(basis, p)
    vecs = _mat_mod_p(vecs, p)
    n_rows, n_cols = basis.shape
    if vecs.shape[0] != n_rows:
        raise ValueError("basis and vecs row mismatch")
    k = int(vecs.shape[1])

    aug = np.concatenate([basis, vecs], axis=1) % p
    row = 0
    pivots: list[int] = []
    for col in range(n_cols):
        pivot = None
        for r in range(row, n_rows):
            if int(aug[r, col]) % p != 0:
                pivot = r
                break
        if pivot is None:
            raise ValueError("basis is rank-deficient")
        if pivot != row:
            aug[[row, pivot], :] = aug[[pivot, row], :]
        inv = pow(int(aug[row, col]) % p, -1, p)
        aug[row, :] = (aug[row, :] * inv) % p
        for r in range(n_rows):
            if r == row:
                continue
            factor = int(aug[r, col]) % p
            if factor:
                aug[r, :] = (aug[r, :] - factor * aug[row, :]) % p
        pivots.append(col)
        row += 1
    if pivots != list(range(n_cols)):
        raise ValueError("expected full pivoting on all columns")
    return aug[:n_cols, n_cols : n_cols + k] % p


def analyze(
    *,
    compute_orders: bool = True,
    order_limit_full: int = 450_000,
    order_limit_derived: int = 250_000,
) -> dict[str, Any]:
    """Compute a matrix-level witness that 2.Suz contains a preimage of M12:2."""
    from scripts.w33_2suz_sp12_embedding import analyze as analyze_2suz

    rep = analyze_2suz()
    if rep.get("available") is not True:
        return {"available": False, "reason": rep.get("reason")}

    std = rep.get("standardized_generators", {})
    if not isinstance(std, dict):
        return {"available": False, "reason": "missing standardized_generators"}

    A = np.array(std["A_std_mod3"], dtype=np.int64) % 3
    B = np.array(std["B_std_mod3"], dtype=np.int64) % 3

    J0 = _standard_symplectic_form(6, p=3)
    I12 = np.eye(12, dtype=np.int64) % 3
    minus_I = (-I12) % 3

    gens = build_m12_2_generators_from_suz(A, B, p=3)
    x = gens["x"]
    y = gens["y"]

    assert x.shape == (12, 12)
    assert y.shape == (12, 12)
    assert np.all((x.T @ J0 @ x - J0) % 3 == 0)
    assert np.all((y.T @ J0 @ y - J0) % 3 == 0)

    # Candidate derived subgroup generators (if x is the outer-involution coset):
    x_inv = _symplectic_inverse(x, J0, p=3)
    y_conj = (x_inv @ y @ x) % 3

    # Canonical polarization: the commutant of the derived subgroup <y, y^x>
    # inside End(F3^12) has dimension 2 and contains a non-scalar involution J
    # with eigenspaces of dimension 6+6 that are both Lagrangian (totally isotropic).
    comm_basis = _commutant_basis([y, y_conj], p=3)
    inv = _find_involutive_commutant_element(comm_basis, p=3)

    polarization: dict[str, Any] = {
        "commutant_dim": int(len(comm_basis)),
        "found_involution": bool(inv is not None),
    }
    if inv is not None:
        polarization["involution_is_scalar"] = _is_scalar_multiple_of_identity(inv, p=3)
        polarization["involution_squares_to_I"] = bool(
            np.array_equal((inv @ inv) % 3, I12)
        )

        plus_vecs = _nullspace_basis_mod_p((inv - I12) % 3, 3)
        minus_vecs = _nullspace_basis_mod_p((inv + I12) % 3, 3)
        U_plus = _basis_matrix(plus_vecs, p=3)
        U_minus = _basis_matrix(minus_vecs, p=3)

        polarization["eigenspace_dims"] = {
            "+1": int(len(plus_vecs)),
            "-1": int(len(minus_vecs)),
        }
        polarization["plus_isotropic"] = _is_totally_isotropic(U_plus, J0, p=3)
        polarization["minus_isotropic"] = _is_totally_isotropic(U_minus, J0, p=3)

        inv_conj = (x_inv @ inv @ x) % 3
        polarization["x_conjugates_J_to_minus_J"] = bool(
            np.array_equal(inv_conj, (-inv) % 3)
        )

        if U_plus.shape == (12, 6) and U_minus.shape == (12, 6):
            A_swap = _solve_in_basis(U_minus, (x @ U_plus) % 3, p=3)
            B_swap = _solve_in_basis(U_plus, (x @ U_minus) % 3, p=3)
            minus_I6 = (2 * np.eye(6, dtype=np.int64)) % 3
            polarization["swap_blocks"] = {
                "AB_equals_minus_I": bool(
                    np.array_equal((A_swap @ B_swap) % 3, minus_I6)
                ),
                "BA_equals_minus_I": bool(
                    np.array_equal((B_swap @ A_swap) % 3, minus_I6)
                ),
            }

    out: dict[str, Any] = {
        "available": True,
        "field_p": 3,
        "dim": 12,
        "suz_standard_signature": dict(rep.get("standard_generator_signature", {})),
        "m12_2_words": {
            "x": "(ab)^(-2) * b * a * b",
            "y": "(abb)^(-6) * b * (abb)^(6)",
        },
        "m12_2_generators": {
            "x_order": _order_mod_p(x, p=3, max_pow=4000),
            "y_order": _order_mod_p(y, p=3, max_pow=4000),
        },
        "symplectic": {
            "x_preserves_J0": True,
            "y_preserves_J0": True,
            "minus_I_is_A_squared": bool(np.array_equal((A @ A) % 3, minus_I)),
        },
        "polarization": polarization,
    }

    if compute_orders:
        derived_order = _matrix_group_order(
            [y, y_conj], p=3, limit=int(order_limit_derived)
        )
        full_order = _matrix_group_order([x, y], p=3, limit=int(order_limit_full))
        out["orders"] = {
            "derived_order": derived_order,
            "full_order": full_order,
            "expected_projective_M12_2_order": 190_080,
        }
        if isinstance(full_order, int) and full_order > 0:
            out["orders"]["projective_order_div2"] = (
                int(full_order) // 2 if int(full_order) % 2 == 0 else None
            )
    return out


def main() -> None:
    t0 = time.time()
    rep = analyze(compute_orders=True)
    if rep.get("available") is not True:
        raise SystemExit(str(rep.get("reason") or "analysis unavailable"))

    print("=" * 78)
    print("WITNESS: M12:2 maximal subgroup inside Suz (matrix model in Sp(12,3))")
    print("=" * 78)
    print()
    sig = rep.get("suz_standard_signature", {})
    if isinstance(sig, dict) and sig:
        print("Suz standard-generator signature:", sig)
    gens = rep.get("m12_2_generators", {})
    print()
    print("ATLAS-word generator orders (in 2.Suz matrix model)")
    print("-" * 58)
    if isinstance(gens, dict):
        print("  ord(x) =", gens.get("x_order"))
        print("  ord(y) =", gens.get("y_order"))

    orders = rep.get("orders", {})
    print()
    print("Subgroup orders by explicit closure")
    print("-" * 58)
    if isinstance(orders, dict):
        print("  |<x,y>|      =", orders.get("full_order"), "(expect 380160 = 2*190080)")
        print("  |<y,y^x>|    =", orders.get("derived_order"), "(expect 190080 = 2*M12)")
        print("  projective   =", orders.get("projective_order_div2"), "(expect 190080 = M12:2)")
    pol = rep.get("polarization", {})
    print()
    print("Polarization witness from commutant of derived subgroup")
    print("-" * 58)
    if isinstance(pol, dict):
        print("  commutant dim      =", pol.get("commutant_dim"), "(expect 2)")
        print("  involution found   =", pol.get("found_involution"), "(expect True)")
        print("  x J x^{-1} = -J    =", pol.get("x_conjugates_J_to_minus_J"), "(expect True)")
        eig = pol.get("eigenspace_dims", {})
        if isinstance(eig, dict):
            print("  eigenspace dims    =", eig, "(expect {+1:6, -1:6})")
        print("  plus isotropic     =", pol.get("plus_isotropic"), "(expect True)")
        print("  minus isotropic    =", pol.get("minus_isotropic"), "(expect True)")
        swap = pol.get("swap_blocks", {})
        if isinstance(swap, dict) and swap:
            print("  swap AB = -I       =", swap.get("AB_equals_minus_I"), "(expect True)")
            print("  swap BA = -I       =", swap.get("BA_equals_minus_I"), "(expect True)")
    print()
    print("ALL CHECKS PASSED ✓")
    print(f"Elapsed: {time.time() - t0:.2f}s")


if __name__ == "__main__":
    main()
