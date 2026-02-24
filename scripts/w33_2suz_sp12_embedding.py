#!/usr/bin/env python3
"""ATLAS 2.Suz (GF(3), dim 12) -> Sp(12,3) embedding check.

This is the concrete algebraic backend behind the Monster 3B centralizer

  C_M(3B) = 3^{1+12} · 2.Suz

The extraspecial group 3^{1+12} has an underlying 12-dim symplectic phase space
V ≅ F3^{12}, and the outer automorphisms preserving its commutator are Sp(12,3).

So, to connect Monster → Heisenberg/Clifford → information-theoretic language
(qutrit stabilizers / Pauli group), we want an explicit *offline* verification
that the ATLAS 12-dim GF(3) generators for 2.Suz preserve a nondegenerate
alternating form (unique up to scalar), hence lie in Sp(12,3) after a change of
basis.

Data source (vendored):
  data/atlas/2SuzG1-f3r12B0.m1
  data/atlas/2SuzG1-f3r12B0.m2
See data/atlas/README.md for the originating ATLAS URLs.

Run:
  & .venv\\Scripts\\python.exe -X utf8 scripts\\w33_2suz_sp12_embedding.py
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
    return (A.astype(np.int64) % int(p)).astype(np.int64)


def _rank_mod_p(H: np.ndarray, p: int) -> int:
    """Row-rank over GF(p) by Gaussian elimination."""
    A = _mat_mod_p(H, p).copy()
    m, n = A.shape
    r = 0
    c = 0
    while r < m and c < n:
        pivot = None
        for i in range(r, m):
            if int(A[i, c]) % p != 0:
                pivot = i
                break
        if pivot is None:
            c += 1
            continue
        if pivot != r:
            A[[r, pivot]] = A[[pivot, r]]

        inv = pow(int(A[r, c] % p), -1, p)
        A[r, :] = (A[r, :] * inv) % p

        for i in range(m):
            if i == r:
                continue
            factor = int(A[i, c] % p)
            if factor:
                A[i, :] = (A[i, :] - factor * A[r, :]) % p

        r += 1
        c += 1
    return int(r)


def _rref_mod_p(H: np.ndarray, p: int) -> tuple[np.ndarray, list[int]]:
    """Reduced row echelon form over GF(p). Returns (RREF, pivot_columns)."""
    A = _mat_mod_p(H, p).copy()
    m, n = A.shape
    r = 0
    pivots: list[int] = []
    for c in range(n):
        if r >= m:
            break
        pivot = None
        for i in range(r, m):
            if int(A[i, c]) % p != 0:
                pivot = i
                break
        if pivot is None:
            continue
        if pivot != r:
            A[[r, pivot]] = A[[pivot, r]]

        inv = pow(int(A[r, c] % p), -1, p)
        A[r, :] = (A[r, :] * inv) % p

        for i in range(m):
            if i == r:
                continue
            factor = int(A[i, c] % p)
            if factor:
                A[i, :] = (A[i, :] - factor * A[r, :]) % p

        pivots.append(int(c))
        r += 1
    return A, pivots


def _nullspace_basis_mod_p(H: np.ndarray, p: int) -> np.ndarray:
    """Return a k×n matrix whose rows form a basis of {x : Hx = 0} over GF(p)."""
    R, pivots = _rref_mod_p(H, p)
    n = int(H.shape[1])
    pivot_set = set(pivots)
    free_cols = [c for c in range(n) if c not in pivot_set]
    pivot_row_for_col = {c: i for i, c in enumerate(pivots)}

    basis = []
    for f in free_cols:
        x = np.zeros((n,), dtype=np.int64)
        x[int(f)] = 1
        for c in pivots:
            i = pivot_row_for_col[c]
            x[int(c)] = (-int(R[i, int(f)])) % p
        basis.append(x)
    if not basis:
        return np.zeros((0, n), dtype=np.int64)
    return np.stack(basis, axis=0)


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


def parse_meataxe_text_matrix(path: Path) -> np.ndarray:
    """Parse a single-line MeatAxe text matrix: `1 p r c <row1> ... <rowr>`."""
    toks = path.read_text(encoding="utf-8").split()
    if len(toks) < 5:
        raise ValueError(f"invalid MeatAxe text matrix (too short): {path}")
    if toks[0] != "1":
        raise ValueError(f"expected leading '1' record marker, got {toks[0]!r}: {path}")
    p = int(toks[1])
    r = int(toks[2])
    c = int(toks[3])
    rows = toks[4:]
    if len(rows) != r:
        raise ValueError(f"expected {r} rows, got {len(rows)}: {path}")
    M = np.zeros((r, c), dtype=np.int64)
    for i, row in enumerate(rows):
        if len(row) != c:
            raise ValueError(f"row {i} has len {len(row)} != {c}: {path}")
        M[i, :] = [int(ch) % p for ch in row]
    return M % p


def _upper_pairs(n: int) -> list[tuple[int, int]]:
    return [(i, j) for i in range(n) for j in range(i + 1, n)]


def _invariant_alternating_form_linear_system(
    gens: Iterable[np.ndarray], p: int
) -> tuple[np.ndarray, list[tuple[int, int]]]:
    """Build Hx=0 over GF(p) for g^T J g = J on alternating J (vars are i<j entries)."""
    gens = [(_mat_mod_p(G, p)) for G in gens]
    n = int(gens[0].shape[0])
    pairs = _upper_pairs(n)
    var_index = {pair: k for k, pair in enumerate(pairs)}

    rows = []
    for G in gens:
        if G.shape != (n, n):
            raise ValueError("all generators must have same square size")
        for a in range(n):
            for b in range(a + 1, n):
                row = np.zeros((len(pairs),), dtype=np.int64)
                for (i, j), k in var_index.items():
                    row[k] = (int(G[i, a]) * int(G[j, b]) - int(G[j, a]) * int(G[i, b])) % p
                row[var_index[(a, b)]] = (row[var_index[(a, b)]] - 1) % p
                rows.append(row)
    H = np.stack(rows, axis=0) % p
    return H, pairs


def solve_unique_invariant_alternating_form(
    gens: Iterable[np.ndarray], p: int = 3, max_combo_dim: int = 10
) -> dict[str, Any]:
    """Solve for a full-rank alternating form preserved by gens (unique up to scalar)."""
    gens = [np.asarray(G, dtype=np.int64) for G in gens]
    if not gens:
        raise ValueError("empty generator list")

    H, pairs = _invariant_alternating_form_linear_system(gens, p)
    basis = _nullspace_basis_mod_p(H, p)

    n = int(gens[0].shape[0])
    if basis.shape[0] == 0:
        raise ValueError("no invariant alternating form found (nullspace is trivial)")

    # Search for a nondegenerate solution in the nullspace.
    best_vec = None
    best_J = None
    dim = int(basis.shape[0])

    def vec_to_J(x: np.ndarray) -> np.ndarray:
        J = np.zeros((n, n), dtype=np.int64)
        for k, (i, j) in enumerate(pairs):
            v = int(x[k]) % p
            J[i, j] = v
            J[j, i] = (-v) % p
        return J % p

    if dim <= max_combo_dim:
        from itertools import product

        for coeffs in product(range(p), repeat=dim):
            if all(c == 0 for c in coeffs):
                continue
            x = np.zeros((basis.shape[1],), dtype=np.int64)
            for c, b in zip(coeffs, basis):
                if c:
                    x = (x + int(c) * b) % p
            J = vec_to_J(x)
            if _rank_mod_p(J, p) == n:
                best_vec = x
                best_J = J
                break
    else:
        rng = np.random.default_rng(0)
        for _ in range(5000):
            coeffs = rng.integers(0, p, size=(dim,), dtype=np.int64)
            if not np.any(coeffs):
                continue
            x = (coeffs.reshape((-1, 1)) * basis).sum(axis=0) % p
            J = vec_to_J(x)
            if _rank_mod_p(J, p) == n:
                best_vec = x
                best_J = J
                break

    if best_J is None or best_vec is None:
        raise ValueError("invariant alternating form exists but none found was nondegenerate")

    # Verify invariance.
    for G in gens:
        if not np.all((_mat_mod_p(G.T @ best_J @ G, p) - best_J) % p == 0):
            raise ValueError("constructed form is not invariant (unexpected)")

    return {
        "p": int(p),
        "n": int(n),
        "linear_system_shape": tuple(int(x) for x in H.shape),
        "nullspace_dim": int(dim),
        "form": best_J.astype(int),
        "form_vector_upper": best_vec.astype(int),
    }


def _symp_pairing(J: np.ndarray, x: np.ndarray, y: np.ndarray, p: int) -> int:
    return int((x.reshape(1, -1) @ (J @ y.reshape(-1, 1)))[0, 0] % p)


def _independent_row_basis(vectors: list[np.ndarray], p: int) -> list[np.ndarray]:
    if not vectors:
        return []
    M = np.stack([_mat_mod_p(v, p) for v in vectors], axis=0)
    R, _piv = _rref_mod_p(M, p)
    out = []
    for row in R:
        row = _mat_mod_p(row, p)
        if np.any(row):
            out.append(row)
    return out


def symplectic_change_of_basis_to_standard(J: np.ndarray, p: int = 3) -> np.ndarray:
    """Return P with P^T J P = J0, where J0 = [[0,I],[-I,0]]."""
    J = _mat_mod_p(J, p)
    n = int(J.shape[0])
    if n % 2 != 0:
        raise ValueError("symplectic form requires even dimension")
    if _rank_mod_p(J, p) != n:
        raise ValueError("form is degenerate; cannot build symplectic basis")

    # Start with the standard basis as a row-basis of the space.
    remaining = [np.eye(n, dtype=np.int64)[i, :].copy() for i in range(n)]
    remaining = _independent_row_basis(remaining, p)

    e_list: list[np.ndarray] = []
    f_list: list[np.ndarray] = []

    while len(e_list) < n // 2:
        remaining = _independent_row_basis(remaining, p)
        if not remaining:
            raise ValueError("ran out of vectors while building symplectic basis")

        # pick v
        v = remaining.pop(0)

        # find w with <v,w> != 0
        w = None
        s = 0
        w_idx = None
        for idx, cand in enumerate(remaining):
            val = _symp_pairing(J, v, cand, p)
            if val % p != 0:
                w = cand
                s = int(val) % p
                w_idx = idx
                break
        if w is None or w_idx is None:
            raise ValueError("nondegenerate form but no partner vector found (unexpected)")
        remaining.pop(w_idx)

        # scale w so that <v,w> = 1
        inv = pow(int(s), -1, p)
        w = (w * inv) % p
        assert _symp_pairing(J, v, w, p) == 1

        # orthogonalize remaining vectors against v,w
        new_remaining: list[np.ndarray] = []
        for u in remaining:
            a = _symp_pairing(J, w, u, p)  # <w,u>
            b = _symp_pairing(J, v, u, p)  # <v,u>
            u2 = (u + a * v - b * w) % p
            new_remaining.append(u2)
        remaining = new_remaining

        e_list.append(_mat_mod_p(v, p))
        f_list.append(_mat_mod_p(w, p))

    # Assemble P with columns [e1..em f1..fm] (column basis for new coordinates).
    P = np.stack(e_list + f_list, axis=1) % p

    # Verify P^T J P is the standard symplectic form.
    m = n // 2
    Z = np.zeros((m, m), dtype=np.int64)
    I = np.eye(m, dtype=np.int64)
    J0 = np.block([[Z, I], [-I, Z]]) % p
    if not np.array_equal((P.T @ J @ P) % p, J0):
        raise ValueError("constructed basis does not yield standard symplectic form (unexpected)")
    return P % p


def load_2suz_generators() -> tuple[np.ndarray, np.ndarray]:
    p1 = ROOT / "data" / "atlas" / "2SuzG1-f3r12B0.m1"
    p2 = ROOT / "data" / "atlas" / "2SuzG1-f3r12B0.m2"
    if not p1.exists() or not p2.exists():
        raise FileNotFoundError("missing vendored ATLAS generator files under data/atlas/")
    A = parse_meataxe_text_matrix(p1)
    B = parse_meataxe_text_matrix(p2)
    return A, B


def analyze() -> dict[str, Any]:
    A, B = load_2suz_generators()
    p = 3

    assert A.shape == (12, 12) and B.shape == (12, 12)
    assert _rank_mod_p(A, p) == 12
    assert _rank_mod_p(B, p) == 12

    form = solve_unique_invariant_alternating_form([A, B], p=p)
    J = form["form"]
    assert _rank_mod_p(J, p) == 12

    P = symplectic_change_of_basis_to_standard(J, p=p)
    Pinv = _inv_mod_p(P, p)

    A_std = (Pinv @ A @ P) % p
    B_std = (Pinv @ B @ P) % p

    m = 6
    Z = np.zeros((m, m), dtype=np.int64)
    I = np.eye(m, dtype=np.int64)
    J0 = np.block([[Z, I], [-I, Z]]) % p

    assert np.all((A_std.T @ J0 @ A_std - J0) % p == 0)
    assert np.all((B_std.T @ J0 @ B_std - J0) % p == 0)

    return {
        "available": True,
        "field_p": int(p),
        "dim": 12,
        "generators": {
            "A_rank": int(_rank_mod_p(A, p)),
            "B_rank": int(_rank_mod_p(B, p)),
        },
        "invariant_form": {
            "linear_system_shape": tuple(int(x) for x in form["linear_system_shape"]),
            "nullspace_dim": int(form["nullspace_dim"]),
            "rank": int(_rank_mod_p(J, p)),
            "J_mod3": J.astype(int).tolist(),
        },
        "symplectic_basis": {
            "P_rank": int(_rank_mod_p(P, p)),
            "P_mod3": P.astype(int).tolist(),
        },
        "standardized_generators": {
            "A_std_preserves_J0": True,
            "B_std_preserves_J0": True,
            "A_std_mod3": A_std.astype(int).tolist(),
            "B_std_mod3": B_std.astype(int).tolist(),
        },
        "interpretation": {
            "phase_space_dim": 12,
            "qutrits_n": 6,
            "heisenberg_irrep_dim": int(3**6),
            "note": "2.Suz embeds (after basis change) into Sp(12,3), i.e. into the qutrit Clifford backbone for the 3^{1+12} Heisenberg/Pauli group.",
        },
    }


def main() -> None:
    t0 = time.time()
    rep = analyze()
    if rep.get("available") is not True:
        raise SystemExit(f"Unavailable: {rep}")

    print("=" * 78)
    print("PILLAR/BRIDGE: 2.Suz (GF(3), dim 12) embeds into Sp(12,3)")
    print("=" * 78)

    print()
    print("§1. Load ATLAS generators (vendored MeatAxe text)")
    print("-" * 58)
    print(f"  dim = {rep['dim']}, p = {rep['field_p']}")
    print(f"  rank(A) = {rep['generators']['A_rank']}")
    print(f"  rank(B) = {rep['generators']['B_rank']}")

    inv = rep["invariant_form"]
    print()
    print("§2. Solve invariant alternating form g^T J g = J")
    print("-" * 58)
    print(f"  linear system shape = {tuple(inv['linear_system_shape'])}  (eqns × vars)")
    print(f"  nullspace dim = {inv['nullspace_dim']}  (expect 1 up to scalar)")
    print(f"  rank(J) = {inv['rank']}  (nondegenerate)")

    print()
    print("§3. Change basis to standard symplectic form J0")
    print("-" * 58)
    print(f"  rank(P) = {rep['symplectic_basis']['P_rank']}")
    print("  standardized generators preserve J0: True")

    interp = rep["interpretation"]
    print()
    print("§4. Information-theory interpretation (qutrit Clifford backbone)")
    print("-" * 58)
    print(f"  phase space V = F3^{interp['phase_space_dim']} ≅ (qutrit Pauli) / center")
    print(f"  qutrits n = {interp['qutrits_n']}")
    print(f"  Heisenberg irrep dim = 3^{interp['qutrits_n']} = {interp['heisenberg_irrep_dim']}")

    print()
    print("ALL CHECKS PASSED ✓")
    print(f"Elapsed: {time.time() - t0:.2f}s")


if __name__ == "__main__":
    main()
