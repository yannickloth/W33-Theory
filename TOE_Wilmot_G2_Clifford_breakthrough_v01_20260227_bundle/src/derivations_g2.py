\
"""
Derivations of the octonions: Der(O) ≅ g2 (dim 14).

We solve the linear system over GF(p):
    D(xy) = D(x) y + x D(y)
with D an 8x8 linear map on the basis {1,e1..e7}.

We report:
  - dim Der(O) over GF(p) (should be 14 for large primes)
  - dim {D in Der(O): D(e7)=0} (should be 8, the sl3 axis-stabilizer)

We also export a basis of derivations mod p.
"""

from __future__ import annotations
from typing import List, Tuple, Dict, Any
import json, os
from src.octonion import build_code_table, decode

TAB = build_code_table()

def build_equations_mod_p(p: int, fix_idx: int | None = None) -> Tuple[List[List[int]], int]:
    """
    Return matrix A over GF(p) for equations A * vec(D) = 0.
    Variables are x_{a,b} for D(e_b)=sum_a x_{a,b} e_a (a,b in 0..7).
    """
    n = 8
    nvars = n*n
    def vid(a,b): return a*n+b
    rows: List[List[int]] = []

    for i in range(n):
        for j in range(n):
            code_prod = TAB[i][j]
            s_prod, idx_prod = decode(code_prod)
            for k in range(n):
                row = [0]*nvars
                # LHS: s_prod * D(e_idx_prod)
                row[vid(k, idx_prod)] = (row[vid(k, idx_prod)] + s_prod) % p
                # RHS: -D(e_i)*e_j
                for a in range(n):
                    s,k2 = decode(TAB[a][j])
                    if k2==k:
                        row[vid(a,i)] = (row[vid(a,i)] - s) % p
                # RHS: -e_i*D(e_j)
                for a in range(n):
                    s,k2 = decode(TAB[i][a])
                    if k2==k:
                        row[vid(a,j)] = (row[vid(a,j)] - s) % p
                if any(c % p for c in row):
                    rows.append(row)

    # Constraints D(e_fix)=0 (all coefficients in that column are 0)
    if fix_idx is not None:
        for a in range(n):
            row = [0]*nvars
            row[vid(a, fix_idx)] = 1
            rows.append(row)

    return rows, nvars

def rref_and_nullspace(rows: List[List[int]], nvars: int, p: int) -> Tuple[int, List[int], List[List[int]]]:
    """
    Return (rank, pivot_cols, nullspace_basis_vectors) over GF(p).
    Basis vectors are length nvars lists.
    """
    A = [r[:] for r in rows]
    m = len(A)
    rank = 0
    pivot_cols: List[int] = []
    where = [-1]*nvars

    for col in range(nvars):
        pivot = None
        for r in range(rank, m):
            if A[r][col] % p:
                pivot = r
                break
        if pivot is None:
            continue
        A[rank], A[pivot] = A[pivot], A[rank]
        pv = A[rank][col] % p
        inv = pow(pv, -1, p)
        if pv != 1:
            A[rank] = [(c*inv) % p for c in A[rank]]

        for r in range(m):
            if r == rank:
                continue
            f = A[r][col] % p
            if f:
                A[r] = [(A[r][c] - f*A[rank][c]) % p for c in range(nvars)]

        where[col] = rank
        pivot_cols.append(col)
        rank += 1
        if rank == m:
            break

    free_cols = [c for c in range(nvars) if where[c] == -1]
    basis: List[List[int]] = []

    for fc in free_cols:
        vec = [0]*nvars
        vec[fc] = 1
        # Solve for pivot vars
        for pc in pivot_cols:
            r = where[pc]
            # pc variable = - sum_{free} A[r][free]*free
            vec[pc] = (-A[r][fc]) % p
        basis.append(vec)

    return rank, pivot_cols, basis

def vec_to_matrix(vec: List[int], n: int=8) -> List[List[int]]:
    M = [[0]*n for _ in range(n)]
    for a in range(n):
        for b in range(n):
            M[a][b] = vec[a*n + b]
    return M

def solve_and_export(p: int=1000003, fix_idx: int | None=None) -> Dict[str, Any]:
    rows, nvars = build_equations_mod_p(p, fix_idx=fix_idx)
    rank, pivots, basis = rref_and_nullspace(rows, nvars, p)
    dim = nvars - rank
    out = {
        "p": p,
        "nvars": nvars,
        "neq": len(rows),
        "rank": rank,
        "derivation_dim": dim,
        "pivot_cols": pivots[:20],  # shorten
        "basis_matrices_mod_p": [vec_to_matrix(v) for v in basis],
    }
    return out

if __name__ == "__main__":
    os.makedirs("out", exist_ok=True)

    out_full = solve_and_export(p=1000003, fix_idx=None)
    out_fix  = solve_and_export(p=1000003, fix_idx=7)
    print("dim Der(O) =", out_full["derivation_dim"])
    print("dim {D: D(e7)=0} =", out_fix["derivation_dim"])
    with open("out/derivations_g2_modp_full.json","w") as f:
        json.dump(out_full, f)
    with open("out/derivations_g2_modp_fix_e7.json","w") as f:
        json.dump(out_fix, f)
