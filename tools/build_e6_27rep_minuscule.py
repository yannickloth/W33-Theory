#!/usr/bin/env python3
"""
Build the 27-dimensional minuscule representation of E6 (Chevalley generators),
then align it to the repo's *canonical 27-line labeling* using the signed W(E6)
simple-reflection matrices exported by `tools/export_we6_signed_action_on_27.py`.

Why:
  - Recent "More New Work" bundles exported a 78-dim algebra in 27×27 matrices via
    "D6 + coset closure" which actually yields Dynkin type B6 (so(13)), not E6.
  - This tool constructs an *actual* E6 action on 27 with integer matrices and
    pins its basis to the same 27-indexing used by our cubic/firewall artifacts.

Construction:
  1) Use the canonical E6 Cartan matrix (same as `tools/build_e6_chevalley_commutator_table.py`)
  2) Take a minuscule highest weight ω0 (or ω5) and compute its Weyl orbit (size 27)
  3) Build Chevalley generators on the weight basis:
       h_i acts diagonally by Dynkin label μ_i ∈ {-1,0,1}
       f_i lowers when μ_i=+1, with coefficient 1 (minuscule string length = 1)
       e_i is the transpose raising operator
  4) Form Weyl group elements n_i = exp(e_i) exp(-f_i) exp(e_i) (finite polynomials)
     which are signed permutation matrices on the 27 weights
  5) Solve for a signed permutation change-of-basis S that conjugates our n_i to the
     canonical signed action in `artifacts/we6_signed_action_on_27.json`
  6) Conjugate {e_i,f_i,h_i} into canonical 27-line basis and verify:
       - Serre relations
       - n_i match canonical signed permutations
       - generators preserve the canonical cubic triads/signs in
         `artifacts/canonical_su3_gauge_and_cubic.json`

Writes:
  - artifacts/e6_27rep_minuscule.json
  - artifacts/e6_27rep_minuscule.md
  - artifacts/e6_27rep_minuscule_generators.npy    (dict with e,f,h arrays)
"""

from __future__ import annotations

import argparse
import sys
from collections import defaultdict, deque
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from utils.json_safe import dump_json  # noqa: E402

E6_CARTAN: np.ndarray = np.array(
    [
        [2, -1, 0, 0, 0, 0],
        [-1, 2, -1, 0, 0, 0],
        [0, -1, 2, -1, -1, 0],
        [0, 0, -1, 2, 0, 0],
        [0, 0, -1, 0, 2, -1],
        [0, 0, 0, 0, -1, 2],
    ],
    dtype=int,
)


def comm(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    return a @ b - b @ a


def frob(m: np.ndarray) -> float:
    return float(np.linalg.norm(m))


def weyl_reflect_dynkin(
    mu: Tuple[int, ...], i: int, cartan: np.ndarray
) -> Tuple[int, ...]:
    """
    Weyl reflection on a weight expressed in Dynkin labels:
      mu_j = <μ, α_j^∨>

    s_i(μ) = μ - mu_i * α_i
    so mu'_j = mu_j - mu_i * <α_i, α_j^∨> = mu_j - mu_i * A_{j,i}.
    """
    mi = mu[i]
    return tuple(int(mu[j] - mi * int(cartan[j, i])) for j in range(cartan.shape[0]))


def weyl_orbit(start: Tuple[int, ...], cartan: np.ndarray) -> List[Tuple[int, ...]]:
    seen = {start}
    q = deque([start])
    while q:
        mu = q.popleft()
        for i in range(cartan.shape[0]):
            nu = weyl_reflect_dynkin(mu, i, cartan)
            if nu not in seen:
                seen.add(nu)
                q.append(nu)
    return sorted(seen)


def pick_minuscule_orbit(
    cartan: np.ndarray, prefer_index: Optional[int]
) -> Tuple[int, List[Tuple[int, ...]]]:
    candidates = [prefer_index] if prefer_index is not None else [0, 5]
    for idx in candidates:
        if idx is None:
            continue
        start = tuple(1 if j == idx else 0 for j in range(cartan.shape[0]))
        orb = weyl_orbit(start, cartan)
        if len(orb) == 27:
            return idx, orb
    # fallback: try all
    for idx in range(cartan.shape[0]):
        start = tuple(1 if j == idx else 0 for j in range(cartan.shape[0]))
        orb = weyl_orbit(start, cartan)
        if len(orb) == 27:
            return idx, orb
    raise RuntimeError("No minuscule orbit of size 27 found")


@dataclass(frozen=True)
class SignedPerm:
    perm: List[int]  # image of basis index j
    signs: List[int]  # sign multiplier on basis vector j

    def to_matrix(self) -> np.ndarray:
        n = len(self.perm)
        m = np.zeros((n, n), dtype=int)
        for j, (i, s) in enumerate(zip(self.perm, self.signs, strict=True)):
            m[i, j] = int(s)
        return m


def signed_perm_from_matrix(m: np.ndarray) -> SignedPerm:
    if m.shape[0] != m.shape[1]:
        raise ValueError("Expected square matrix")
    n = m.shape[0]
    perm = [-1] * n
    signs = [0] * n
    for j in range(n):
        nz = np.nonzero(m[:, j])[0]
        if nz.size != 1:
            raise RuntimeError("Not a signed permutation (column nz != 1)")
        i = int(nz[0])
        s = int(m[i, j])
        if s not in (-1, 1):
            raise RuntimeError("Not a signed permutation (entry not ±1)")
        perm[j] = i
        signs[j] = s
    # row check
    for i in range(n):
        nz = np.nonzero(m[i, :])[0]
        if nz.size != 1:
            raise RuntimeError("Not a signed permutation (row nz != 1)")
    return SignedPerm(perm=perm, signs=signs)


def build_chevalley_on_minuscule_weights(
    orbit: Sequence[Tuple[int, ...]], cartan: np.ndarray
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, Dict[str, object]]:
    """
    Returns (E,F,H) where:
      E: (6,27,27) int
      F: (6,27,27) int
      H: (6,27,27) int diagonal
    """
    weights = list(orbit)
    n = len(weights)
    if n != 27:
        raise ValueError("Expected 27 weights")
    w_to_idx = {w: i for i, w in enumerate(weights)}

    e = np.zeros((6, n, n), dtype=int)
    f = np.zeros((6, n, n), dtype=int)
    h = np.zeros((6, n, n), dtype=int)

    for a, mu in enumerate(weights):
        for i in range(6):
            h[i, a, a] = int(mu[i])
            if mu[i] == 1:
                # lower by α_i: mu' = mu - A[:,i]
                nu = tuple(int(mu[j] - int(cartan[j, i])) for j in range(6))
                b = w_to_idx.get(nu)
                if b is None:
                    raise RuntimeError("Expected minuscule lowering target to exist")
                f[i, b, a] = 1
                e[i, a, b] = 1

    stats: Dict[str, object] = {
        "weights": weights,
        "unique_label_values": sorted({int(x) for mu in weights for x in mu}),
    }
    return e, f, h, stats


def serre_check(
    e: np.ndarray, f: np.ndarray, h: np.ndarray, cartan: np.ndarray, *, tol: float = 0.0
) -> Dict[str, object]:
    failures: List[Dict[str, object]] = []

    def nz(name: str, m: np.ndarray):
        nrm = frob(m)
        if nrm > tol:
            failures.append({"relation": name, "norm": nrm})

    def ad_power(x: np.ndarray, y: np.ndarray, n: int) -> np.ndarray:
        out = y
        for _ in range(n):
            out = comm(x, out)
        return out

    # [h_i, h_j] = 0
    for i in range(6):
        for j in range(i + 1, 6):
            nz(f"[h{i},h{j}]=0", comm(h[i], h[j]))

    # [h_i, e_j] = A_ij e_j and [h_i, f_j] = -A_ij f_j
    for i in range(6):
        for j in range(6):
            nz(f"[h{i},e{j}]=A e", comm(h[i], e[j]) - int(cartan[i, j]) * e[j])
            nz(f"[h{i},f{j}]=-A f", comm(h[i], f[j]) + int(cartan[i, j]) * f[j])

    # [e_i, f_j] = δ_ij h_i
    for i in range(6):
        for j in range(6):
            target = h[i] if i == j else np.zeros_like(h[0])
            nz(f"[e{i},f{j}]=delta h", comm(e[i], f[j]) - target)

    # Serre relations: ad(e_i)^(1-A_ij)(e_j)=0 for i!=j
    for i in range(6):
        for j in range(6):
            if i == j:
                continue
            aij = int(cartan[i, j])
            if aij > 0:
                failures.append(
                    {
                        "relation": "unexpected_cartan_entry_positive",
                        "i": i,
                        "j": j,
                        "aij": aij,
                    }
                )
                continue
            m = 1 - aij
            nz(f"ad(e{i})^{m}(e{j})=0", ad_power(e[i], e[j], m))
            nz(f"ad(f{i})^{m}(f{j})=0", ad_power(f[i], f[j], m))

    return {
        "ok": len(failures) == 0,
        "n_failures": len(failures),
        "failures": failures,
        "tol": tol,
    }


def compute_weyl_n_matrices(e: np.ndarray, f: np.ndarray) -> List[np.ndarray]:
    """
    n_i = exp(e_i) exp(-f_i) exp(e_i) in a finite-dimensional representation.
    In this minuscule rep, e_i^2=f_i^2=0 so exp(e)=I+e and exp(-f)=I-f.
    """
    n = e.shape[1]
    out = []
    I = np.eye(n, dtype=int)
    for i in range(6):
        ei = e[i]
        fi = f[i]
        ni = (I + ei) @ (I - fi) @ (I + ei)
        out.append(ni)
    return out


def load_canonical_signed_generators() -> List[SignedPerm]:
    path = ROOT / "artifacts" / "we6_signed_action_on_27.json"
    if not path.exists():
        raise FileNotFoundError(
            "Missing artifacts/we6_signed_action_on_27.json; run tools/export_we6_signed_action_on_27.py"
        )
    data = __import__("json").loads(path.read_text(encoding="utf-8"))
    if data.get("status") != "ok":
        raise RuntimeError("Canonical signed action JSON not ok")
    gens = []
    for g in data["generators"]:
        gens.append(
            SignedPerm(
                perm=[int(x) for x in g["permutation"]],
                signs=[int(x) for x in g["signs"]],
            )
        )
    if len(gens) != 6:
        raise RuntimeError("Expected 6 generators")
    return gens


def solve_conjugacy_line_to_weight(
    p_gens: List[SignedPerm], q_gens: List[SignedPerm]
) -> Tuple[List[int], List[int]]:
    """
    Find a signed permutation S mapping canonical line basis -> weight basis such that:
      for all i:  q_i  =  S^{-1} p_i S   (as signed permutation matrices)

    Returns:
      - g: list length 27 mapping line_index -> weight_index
      - d: list length 27 with d[line] in {±1} (diagonal sign for S columns)
    """
    n = 27
    # First solve for the underlying permutation conjugacy on indices.
    p_perm = [pg.perm for pg in p_gens]
    q_perm = [qg.perm for qg in q_gens]
    p_sign = [pg.signs for pg in p_gens]
    q_sign = [qg.signs for qg in q_gens]

    def try_seed(w0: int) -> Optional[List[int]]:
        g = [-1] * n
        g[0] = w0
        dq = deque([0])
        while dq:
            l = dq.popleft()
            w = g[l]
            for i in range(6):
                l2 = q_perm[i][l]
                w2 = p_perm[i][w]
                if g[l2] == -1:
                    g[l2] = w2
                    dq.append(l2)
                elif g[l2] != w2:
                    return None
        if any(x == -1 for x in g):
            return None
        if len(set(g)) != n:
            return None
        return g

    g_map: Optional[List[int]] = None
    for w0 in range(n):
        g_try = try_seed(w0)
        if g_try is not None:
            g_map = g_try
            break
    if g_map is None:
        raise RuntimeError("Failed to find index conjugacy between Weyl generators")

    # Now solve diagonal sign gauge d[line] so that signs match.
    def try_d0(d0: int) -> Optional[List[int]]:
        d = [0] * n
        d[0] = d0
        dq = deque([0])
        while dq:
            l = dq.popleft()
            w = g_map[l]
            dl = d[l]
            for i in range(6):
                l2 = q_perm[i][l]
                s = int(p_sign[i][w])
                t = int(q_sign[i][l])
                req = int(dl * s * t)
                if d[l2] == 0:
                    d[l2] = req
                    dq.append(l2)
                elif d[l2] != req:
                    return None
        if any(x == 0 for x in d):
            return None
        return d

    d_map = try_d0(1) or try_d0(-1)
    if d_map is None:
        raise RuntimeError("Failed to solve diagonal sign gauge")

    return g_map, d_map


def build_signed_perm_matrix_from_maps(
    g_line_to_weight: List[int], d_line: List[int]
) -> np.ndarray:
    """
    Columns indexed by line; rows indexed by weight. Column l is d[l] * e_{g[l]}.
    """
    n = len(g_line_to_weight)
    s = np.zeros((n, n), dtype=int)
    for l, (w, dl) in enumerate(zip(g_line_to_weight, d_line, strict=True)):
        s[int(w), int(l)] = int(dl)
    return s


def cubic_derivative_coeffs(
    triads: Sequence[Tuple[int, int, int, int]], x: np.ndarray
) -> Dict[Tuple[int, int, int], complex]:
    """
    Return coefficients of d/dt cubic(exp(tX)·v) at t=0 as a dict on sorted monomials.
    The cubic is defined by signed triads: d * x_i x_j x_k with {i,j,k} distinct.
    """
    out: Dict[Tuple[int, int, int], complex] = defaultdict(complex)
    for i, j, k, d in triads:
        di = int(d)
        row_i = x[i, :]
        row_j = x[j, :]
        row_k = x[k, :]
        for p in range(27):
            out[tuple(sorted((p, j, k)))] += di * complex(row_i[p])
            out[tuple(sorted((i, p, k)))] += di * complex(row_j[p])
            out[tuple(sorted((i, j, p)))] += di * complex(row_k[p])
    out = {k: v for k, v in out.items() if v != 0}
    return out


def load_canonical_cubic_triads() -> List[Tuple[int, int, int, int]]:
    path = ROOT / "artifacts" / "canonical_su3_gauge_and_cubic.json"
    data = __import__("json").loads(path.read_text(encoding="utf-8"))
    triads = data["triads"]
    d_triples = data["solution"]["d_triples"]
    out = []
    for t, obj in zip(triads, d_triples, strict=True):
        i, j, k = (int(t[0]), int(t[1]), int(t[2]))
        s = int(obj["sign"])
        out.append((i, j, k, s))
    if len(out) != 45:
        raise RuntimeError("Expected 45 cubic triads")
    return out


def _vecC(m: np.ndarray) -> np.ndarray:
    return np.concatenate([m.real.ravel(), m.imag.ravel()]).astype(np.float64)


def close_to_basis(
    seed: Sequence[np.ndarray],
    *,
    target_dim: int,
    tol: float = 1e-12,
    max_passes: int = 32,
) -> List[np.ndarray]:
    """
    Deterministic commutator-closure to a linearly independent basis using
    real Gram-Schmidt on flattened (Re,Im) vectors.
    """
    Q: List[np.ndarray] = []
    basis: List[np.ndarray] = []

    def gram_add(M: np.ndarray) -> bool:
        v = _vecC(M)
        nv = float(np.linalg.norm(v))
        if nv < 1e-14:
            return False
        w = v.copy()
        for q in Q:
            w -= float(np.dot(q, w)) * q
        nw = float(np.linalg.norm(w))
        if nw < tol * nv:
            return False
        Q.append(w / nw)
        basis.append(M)
        return True

    for M in seed:
        gram_add(M)

    for _pass in range(max_passes):
        added = 0
        L = len(basis)
        for i in range(L):
            for j in range(i + 1, L):
                C = basis[i] @ basis[j] - basis[j] @ basis[i]
                if float(np.linalg.norm(C)) < 1e-14:
                    continue
                if gram_add(C):
                    added += 1
                    if len(basis) >= target_dim:
                        return basis[:target_dim]
        if added == 0:
            break

    if len(basis) < target_dim:
        raise RuntimeError(
            f"Closure reached dim {len(basis)} < target_dim {target_dim}"
        )
    return basis[:target_dim]


def _write_md(path: Path, data: dict) -> None:
    lines = []
    lines.append("# E6 27-rep (minuscule) aligned to canonical 27\n")
    lines.append(f"- status: `{data.get('status')}`")
    lines.append(f"- minuscule_index: `{data.get('minuscule_index')}`")
    lines.append(f"- serre_ok: `{data.get('serre', {}).get('ok')}`")
    lines.append(f"- n_match_ok: `{data.get('weyl', {}).get('match_ok')}`")
    lines.append(f"- cubic_invariance_ok: `{data.get('cubic', {}).get('ok')}`")
    lines.append("")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv: Optional[Sequence[str]] = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--minuscule-index",
        type=int,
        default=-1,
        help="0 or 5 (minuscule). Use -1 for auto.",
    )
    parser.add_argument(
        "--skip-cubic", action="store_true", help="Skip cubic invariance verification."
    )
    parser.add_argument(
        "--export-basis78",
        action="store_true",
        help="Also close the Lie algebra under commutators and write artifacts/e6_27rep_basis_export/E6_basis_78.npy.",
    )
    args = parser.parse_args(list(argv) if argv is not None else [])

    prefer = None if args.minuscule_index == -1 else int(args.minuscule_index)
    idx, orb = pick_minuscule_orbit(E6_CARTAN, prefer)

    e_w, f_w, h_w, w_stats = build_chevalley_on_minuscule_weights(orb, E6_CARTAN)
    serre = serre_check(e_w, f_w, h_w, E6_CARTAN, tol=0.0)
    if not bool(serre["ok"]):
        raise RuntimeError("Serre relations failed in weight basis (unexpected)")

    n_w_mats = compute_weyl_n_matrices(e_w, f_w)
    n_w = [signed_perm_from_matrix(m) for m in n_w_mats]

    canon = load_canonical_signed_generators()
    g_line_to_weight, d_line = solve_conjugacy_line_to_weight(n_w, canon)
    S = build_signed_perm_matrix_from_maps(g_line_to_weight, d_line)

    # Conjugate generators into canonical line basis.
    e = np.array([S.T @ e_w[i] @ S for i in range(6)], dtype=int)
    f = np.array([S.T @ f_w[i] @ S for i in range(6)], dtype=int)
    h = np.array([S.T @ h_w[i] @ S for i in range(6)], dtype=int)

    # Verify Weyl generators match canonical (exactly).
    n_line = [signed_perm_from_matrix(m) for m in compute_weyl_n_matrices(e, f)]
    match_ok = True
    for i in range(6):
        if n_line[i].perm != canon[i].perm or n_line[i].signs != canon[i].signs:
            match_ok = False
            break
    if not match_ok:
        raise RuntimeError(
            "Failed to match canonical signed Weyl generators after conjugation"
        )

    # Verify Serre again in canonical basis.
    serre2 = serre_check(e, f, h, E6_CARTAN, tol=0.0)
    if not bool(serre2["ok"]):
        raise RuntimeError("Serre relations failed after conjugation (unexpected)")

    cubic = {"ok": None}
    if not bool(args.skip_cubic):
        triads = load_canonical_cubic_triads()
        max_coeff = 0.0
        worst = None
        for name, mats in [("e", e), ("f", f), ("h", h)]:
            for i in range(6):
                coeffs = cubic_derivative_coeffs(triads, mats[i].astype(np.complex128))
                if coeffs:
                    k, v = max(coeffs.items(), key=lambda kv: abs(kv[1]))
                    nrm = float(abs(v))
                    if nrm > max_coeff:
                        max_coeff = nrm
                        worst = {
                            "gen_type": name,
                            "i": i,
                            "monomial": list(k),
                            "coeff": [float(np.real(v)), float(np.imag(v))],
                        }
        cubic = {"ok": max_coeff < 1e-9, "max_abs_coeff": max_coeff, "worst": worst}
        if not cubic["ok"]:
            raise RuntimeError("Cubic invariance failed (mapping/gauge mismatch)")

    out_json = ROOT / "artifacts" / "e6_27rep_minuscule.json"
    out_md = ROOT / "artifacts" / "e6_27rep_minuscule.md"
    out_npy = ROOT / "artifacts" / "e6_27rep_minuscule_generators.npy"

    data = {
        "status": "ok",
        "minuscule_index": int(idx),
        "weights": {"count": 27, "stats": w_stats},
        "serre": serre2,
        "weyl": {
            "match_ok": True,
            "line_to_weight": g_line_to_weight,
            "line_signs": d_line,
        },
        "cubic": cubic,
    }
    dump_json(data, out_json, indent=2, sort_keys=True)
    _write_md(out_md, data)
    np.save(out_npy, {"e": e, "f": f, "h": h})

    if bool(args.export_basis78):
        out_dir = ROOT / "artifacts" / "e6_27rep_basis_export"
        out_dir.mkdir(parents=True, exist_ok=True)
        seed = (
            [e[i].astype(np.complex128) for i in range(6)]
            + [f[i].astype(np.complex128) for i in range(6)]
            + [h[i].astype(np.complex128) for i in range(6)]
        )
        basis78 = close_to_basis(seed, target_dim=78, tol=1e-12, max_passes=32)
        np.save(out_dir / "E6_basis_78.npy", np.stack(basis78, axis=0))
        print(f"Wrote {out_dir / 'E6_basis_78.npy'}")

    print(f"Wrote {out_json}")
    print(f"Wrote {out_md}")
    print(f"Wrote {out_npy}")


if __name__ == "__main__":
    main(sys.argv[1:])
