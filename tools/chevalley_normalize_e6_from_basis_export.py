#!/usr/bin/env python3
"""
Chevalley-normalize a rank-6, 78-dim Lie algebra from a 27×27 matrix-basis export.

This tool is intended to consume the "v3p38" style export found in:
  artifacts/more_new_work_extracted/**/e6_basis_export/

In particular it expects:
  - E6_basis_78.npy      shape (78, 27, 27) complex128
  - (optionally) Cartan_mats.npy / Cartan_indices.npy

Important: Some exports contain a *commuting* 6-tuple that is not a semisimple Cartan
subalgebra (often mostly nilpotent). Weight clustering with those matrices collapses.

Instead, we deterministically recover a true Cartan subalgebra by:
  - Choosing a regular element X in the 78-dim algebra (seeded random combo)
  - Computing its centralizer in the 78-dim span via an SVD nullspace
  - Using the resulting 6-dim centralizer as Cartan (it is abelian for regular X)

Then we:
  - Build the adjoint action matrices ad(H_k) in the 78-basis coordinates
  - Diagonalize a generic Cartan element to obtain 72 one-dimensional root spaces
  - Choose a positive system and identify 6 simple roots
  - Normalize (e_i,f_i,h_i) so that α_i(h_i)=2 (Chevalley scaling)
  - Classify the Dynkin type (E6/B6/C6) from the recovered Cartan matrix (up to permutation)
  - Verify all Serre relations in the 27-rep

Writes:
  - artifacts/e6_basis_export_chevalley.json
  - artifacts/e6_basis_export_chevalley.md
  - artifacts/e6_basis_export_chevalley_generators.npy  (optional matrices)
"""

from __future__ import annotations

import argparse
import math
import sys
from dataclasses import dataclass
from itertools import permutations
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from utils.json_safe import dump_json  # noqa: E402

E6_CANONICAL_CARTAN: List[List[int]] = [
    [2, -1, 0, 0, 0, 0],
    [-1, 2, -1, 0, 0, 0],
    [0, -1, 2, -1, -1, 0],
    [0, 0, -1, 2, 0, 0],
    [0, 0, -1, 0, 2, -1],
    [0, 0, 0, 0, -1, 2],
]

# Canonical rank-6 Cartan matrices in the standard Serre convention:
#   [h_i, e_j] = a_{ij} e_j
# i.e. rows are coroot indices and columns are simple-root indices.
B6_CANONICAL_CARTAN: List[List[int]] = [
    [2, -1, 0, 0, 0, 0],
    [-1, 2, -1, 0, 0, 0],
    [0, -1, 2, -1, 0, 0],
    [0, 0, -1, 2, -1, 0],
    [0, 0, 0, -1, 2, -1],
    [0, 0, 0, 0, -2, 2],
]

C6_CANONICAL_CARTAN: List[List[int]] = [
    [2, -1, 0, 0, 0, 0],
    [-1, 2, -1, 0, 0, 0],
    [0, -1, 2, -1, 0, 0],
    [0, 0, -1, 2, -1, 0],
    [0, 0, 0, -1, 2, -2],
    [0, 0, 0, 0, -1, 2],
]


def comm(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    return a @ b - b @ a


def vec(m: np.ndarray) -> np.ndarray:
    return m.reshape(-1)


def frob_norm(m: np.ndarray) -> float:
    return float(np.linalg.norm(m))


def _sorted_paths(paths: Iterable[Path]) -> List[Path]:
    return sorted(paths, key=lambda p: str(p).lower())


def find_latest_basis_export_dir() -> Path:
    """
    Locate an extracted 'e6_basis_export' folder by searching for E6_basis_78.npy.
    Prefers lexicographically-latest path (works well with v3pNN naming).
    """
    search_root = ROOT / "artifacts" / "more_new_work_extracted"
    hits = _sorted_paths(search_root.rglob("E6_basis_78.npy"))
    if not hits:
        raise FileNotFoundError(
            "Could not find E6_basis_78.npy under artifacts/more_new_work_extracted. "
            "Run: python3 tools/ingest_more_new_work.py"
        )
    return hits[-1].parent


def load_basis_export(export_dir: Path) -> np.ndarray:
    basis_path = export_dir / "E6_basis_78.npy"
    if not basis_path.exists():
        raise FileNotFoundError(f"Missing {basis_path}")
    mats = np.load(basis_path)
    if mats.shape != (78, 27, 27):
        raise ValueError(f"Unexpected basis shape {mats.shape}; expected (78,27,27)")
    if mats.dtype != np.complex128:
        mats = mats.astype(np.complex128)
    return mats


def build_projection(basis: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """
    Returns (V, P) where:
      V is 729×78 with columns vec(B_i)
      P is 78×729 pseudoinverse so that coords(M) = P @ vec(M)
    """
    v = np.vstack([vec(b) for b in basis]).T  # 729×78
    if v.shape != (27 * 27, 78):
        raise RuntimeError("Unexpected flatten shape")
    p = np.linalg.pinv(v)
    if p.shape != (78, 27 * 27):
        raise RuntimeError("Unexpected pinv shape")
    return v, p


def nullspace_via_svd(a: np.ndarray, rcond: float) -> np.ndarray:
    """
    Nullspace basis columns (n×k) for A (m×n) using SVD with relative threshold rcond.
    """
    u, s, vh = np.linalg.svd(a, full_matrices=False)
    if s.size == 0:
        raise ValueError("Empty singular values")
    thresh = float(rcond) * float(s[0])
    rank = int(np.sum(s > thresh))
    return vh[rank:].conj().T


def find_cartan_via_regular_centralizer(
    basis: np.ndarray,
    *,
    seed: int = 0,
    max_tries: int = 32,
    rcond: float = 1e-10,
    require_commute_tol: float = 1e-8,
) -> Tuple[np.ndarray, np.ndarray, Dict[str, float | int]]:
    """
    Returns (H_mats, H_coeffs, stats) where:
      - H_mats is (6,27,27) Cartan basis matrices (commuting)
      - H_coeffs is (78,6) coefficients in the given 78-basis (columns)
    """
    rng = np.random.default_rng(seed)
    n = basis.shape[0]
    if n != 78:
        raise ValueError("Expected 78 basis matrices")

    best: Optional[Tuple[np.ndarray, np.ndarray, Dict[str, float | int]]] = None
    for attempt in range(max_tries):
        coeff = rng.normal(size=n)
        x = np.tensordot(coeff, basis, axes=([0], [0]))
        cmat = np.vstack([vec(comm(x, bj)) for bj in basis]).T  # 729×78
        ns = nullspace_via_svd(cmat, rcond=rcond)
        null_dim = ns.shape[1]

        stats = {
            "attempt": attempt,
            "null_dim": int(null_dim),
        }
        if null_dim < 6:
            # Too-regular but keep best (closest to 6) as diagnostic.
            best = best or (np.zeros((0, 27, 27)), np.zeros((78, 0)), stats)
            continue
        if null_dim > 6:
            continue

        # Orthonormalize for numerical stability.
        q, _ = np.linalg.qr(ns)
        if q.shape != (78, 6):
            raise RuntimeError("Unexpected QR shape")
        h_mats = np.tensordot(q.T, basis, axes=([1], [0]))  # (6,27,27)

        # Verify commuting.
        comm_max = 0.0
        for i in range(6):
            for j in range(i + 1, 6):
                comm_max = max(comm_max, frob_norm(comm(h_mats[i], h_mats[j])))
        stats["cartan_comm_max_frob"] = float(comm_max)
        if comm_max > require_commute_tol:
            continue

        return h_mats, q, stats

    if best is not None:
        raise RuntimeError(
            "Failed to find a regular element with 6-dim centralizer. "
            f"Best null_dim seen: {best[2].get('null_dim')}"
        )
    raise RuntimeError("Failed to find Cartan (no attempts made)")


def ad_matrix_in_basis(
    h: np.ndarray, basis: np.ndarray, proj: np.ndarray
) -> np.ndarray:
    n = basis.shape[0]
    out = np.zeros((n, n), dtype=np.complex128)
    for j in range(n):
        coords = proj @ vec(comm(h, basis[j]))
        out[:, j] = coords
    return out


@dataclass(frozen=True)
class RootSpace:
    weight: np.ndarray  # (6,) complex weights: α(H_k)
    key: Tuple[int, ...]  # rounded key for lookup (Re,Im)
    eigvec: np.ndarray  # (78,) complex coordinates in the 78-basis


def choose_key_scale(weights_embed: np.ndarray) -> float:
    """
    Pick a rounding scale based on the minimum separation between distinct weights.
    Returns a power-of-10 scale in [1e6, 1e12].
    """
    if weights_embed.ndim != 2 or weights_embed.shape[1] != 12:
        raise ValueError("Expected embedded weights shape (N,12)")
    n = weights_embed.shape[0]
    if n < 2:
        return 1e9
    sep = float("inf")
    for i in range(n):
        wi = weights_embed[i]
        for j in range(i + 1, n):
            wj = weights_embed[j]
            d = float(np.max(np.abs(wi - wj)))
            if d == 0.0:
                continue
            sep = min(sep, d)
    if not math.isfinite(sep):
        return 1e9
    tol = max(sep / 1000.0, 1e-14)
    raw_scale = 1.0 / tol
    pow10 = 10.0 ** int(math.floor(math.log10(raw_scale)))
    return float(min(max(pow10, 1e6), 1e12))


def embed_weight(weight: np.ndarray) -> np.ndarray:
    if weight.shape != (6,):
        raise ValueError("Expected (6,) weight")
    return np.concatenate([np.real(weight), np.imag(weight)], axis=0).astype(np.float64)


def weight_key(weight: np.ndarray, *, scale: float) -> Tuple[int, ...]:
    emb = embed_weight(weight)
    return tuple(int(round(float(x) * scale)) for x in emb.tolist())


def diagonalize_generic_cartan(
    ad_cartan: Sequence[np.ndarray],
    *,
    seed: int = 0,
    zero_eig_tol: float = 1e-10,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Diagonalize a generic Cartan element A = Σ t_k ad(H_k).
    Returns (eigvals, eigvecs, t) with eigenvectors as columns.
    """
    rng = np.random.default_rng(seed)
    t = rng.normal(size=len(ad_cartan))
    a = np.zeros_like(ad_cartan[0])
    for ck, ak in zip(t.tolist(), ad_cartan, strict=True):
        a = a + float(ck) * ak

    eigvals, eigvecs = np.linalg.eig(a)
    # Deterministic ordering.
    order = np.lexsort((np.round(np.imag(eigvals), 12), np.round(np.real(eigvals), 12)))
    eigvals = eigvals[order]
    eigvecs = eigvecs[:, order]

    # Quick sanity: expect 6 near-zero eigenvalues for Cartan directions.
    scale = float(np.max(np.abs(eigvals))) if eigvals.size else 1.0
    tol = max(zero_eig_tol * scale, 1e-14)
    n_zero = int(np.sum(np.abs(eigvals) < tol))
    if n_zero != 6:
        # Still usable, but we want determinism and correctness; treat as hard error.
        raise RuntimeError(f"Unexpected zero-eigen multiplicity: {n_zero} (expected 6)")
    return eigvals, eigvecs, t


def extract_roots_from_eigendecomposition(
    eigvals: np.ndarray,
    eigvecs: np.ndarray,
    ad_cartan: Sequence[np.ndarray],
    *,
    key_scale: float,
    zero_eig_tol: float = 1e-10,
) -> Tuple[List[RootSpace], Dict[str, float | int]]:
    """
    Convert eigenvectors into 72 root spaces (skipping the 6-dim Cartan eigenspace).
    """
    scale = float(np.max(np.abs(eigvals))) if eigvals.size else 1.0
    tol = max(zero_eig_tol * scale, 1e-14)

    roots: List[RootSpace] = []
    residuals: List[float] = []
    imag_max = 0.0

    for idx, lam in enumerate(eigvals.tolist()):
        if abs(lam) < tol:
            continue
        v = eigvecs[:, idx]
        nv = float(np.linalg.norm(v))
        if nv == 0.0:
            continue
        v = v / nv

        w = []
        res = []
        for ak in ad_cartan:
            lk = np.vdot(v, ak @ v) / np.vdot(v, v)
            w.append(lk)
            res.append(float(np.linalg.norm(ak @ v - lk * v) / np.linalg.norm(v)))
        wv = np.array(w, dtype=np.complex128)
        imag_max = max(imag_max, float(np.max(np.abs(np.imag(wv)))))
        residuals.append(max(res) if res else 0.0)

        roots.append(
            RootSpace(weight=wv, key=weight_key(wv, scale=key_scale), eigvec=v)
        )

    # Cluster sanity: expect 72 roots.
    if len(roots) != 72:
        raise RuntimeError(f"Unexpected number of roots: {len(roots)} (expected 72)")

    stats: Dict[str, float | int] = {
        "root_count": int(len(roots)),
        "root_weight_imag_max": float(imag_max),
        "root_eigvec_residual_max": float(max(residuals) if residuals else 0.0),
        "root_eigvec_residual_median": float(
            np.median(residuals) if residuals else 0.0
        ),
        "key_scale": float(key_scale),
    }
    return roots, stats


def choose_positive_roots(roots: Sequence[RootSpace]) -> List[RootSpace]:
    """
    Deterministically choose a positive half of the roots using a fixed linear functional.
    """
    # Root weights live in a complex 6-dim space. Choose positivity by embedding into R^12
    # via (Re,Im) and applying a fixed real linear functional.
    f = np.array(
        [1.0, 2.0, 3.0, 5.0, 7.0, 11.0, -13.0, 17.0, -19.0, 23.0, -29.0, 31.0],
        dtype=np.float64,
    )
    pos = []
    for r in roots:
        score = float(np.dot(f, embed_weight(r.weight)))
        if score > 0:
            pos.append(r)
    if len(pos) != 36:
        # Fallback: choose a different functional if degenerate.
        f2 = np.array(
            [1.0, 1.0, -2.0, 3.0, -5.0, 8.0, 21.0, -34.0, 55.0, -89.0, 144.0, -233.0],
            dtype=np.float64,
        )
        pos = [r for r in roots if float(np.dot(f2, embed_weight(r.weight))) > 0]
    if len(pos) != 36:
        raise RuntimeError(
            f"Positive root split failed: got {len(pos)} positives (expected 36)"
        )
    return pos


def find_simple_roots(pos_roots: Sequence[RootSpace]) -> List[RootSpace]:
    """
    Simple roots are positive roots not expressible as sum of two positive roots.
    Root addition is tested in weight space with a small tolerance.
    """
    # These weights are numerically extremely stable, but do not live on an obvious
    # integer lattice in these coordinates. Using rounded integer keys for arithmetic
    # can break additivity (round(a)+round(b) != round(a+b)). So we do approximate
    # matching directly in weight space.
    weights = [r.weight for r in pos_roots]
    w_arr = np.array([embed_weight(w) for w in weights], dtype=np.float64)
    # Tolerance as a small fraction of the minimum separation in this chamber.
    sep = float("inf")
    for i in range(w_arr.shape[0]):
        for j in range(i + 1, w_arr.shape[0]):
            d = float(np.max(np.abs(w_arr[i] - w_arr[j])))
            if d == 0.0:
                continue
            sep = min(sep, d)
    tol = max(sep / 1000.0, 1e-12)

    def has_positive_root(target: np.ndarray) -> bool:
        t = embed_weight(target)
        return any(float(np.max(np.abs(embed_weight(w) - t))) < tol for w in weights)

    simple = []
    for a in pos_roots:
        is_simple = True
        for b in pos_roots:
            if b.key == a.key:
                continue
            if has_positive_root(a.weight - b.weight):
                is_simple = False
                break
        if is_simple:
            simple.append(a)
    if len(simple) != 6:
        raise RuntimeError(f"Unexpected simple root count: {len(simple)} (expected 6)")
    # Deterministic ordering.
    simple = sorted(simple, key=lambda r: r.key)
    return simple


def solve_cartan_coords(
    h: np.ndarray, cartan_mats: np.ndarray
) -> Tuple[np.ndarray, float]:
    """
    Least-squares solve for coefficients c (6,) such that h ≈ Σ c_k H_k.
    Returns (c, rel_residual) where residual is ||h-h_proj||/||h||.
    """
    ch = np.vstack([vec(x) for x in cartan_mats]).T  # 729×6
    c, *_ = np.linalg.lstsq(ch, vec(h), rcond=None)
    hproj = ch @ c
    resid = float(np.linalg.norm(vec(h) - hproj))
    denom = float(np.linalg.norm(vec(h)))
    rel = resid / denom if denom != 0.0 else resid
    return c.astype(np.complex128), rel


def chevalley_normalize_simple_generators(
    basis: np.ndarray,
    cartan_mats: np.ndarray,
    simple_roots: Sequence[RootSpace],
    root_by_key: Dict[Tuple[int, ...], RootSpace],
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, Dict[str, float]]:
    """
    Build (e_i,f_i,h_i) matrices in 27-rep for each simple root and normalize so α_i(h_i)=2.
    Returns (E, F, H, stats) where each has shape (6,27,27).
    """
    e_mats = np.zeros((6, 27, 27), dtype=np.complex128)
    f_mats = np.zeros((6, 27, 27), dtype=np.complex128)
    h_mats = np.zeros((6, 27, 27), dtype=np.complex128)

    cartan_proj_relmax = 0.0
    alpha_hi_diag_dev = 0.0

    for i, sr in enumerate(simple_roots):
        neg_key = tuple(-x for x in sr.key)
        if neg_key not in root_by_key:
            raise RuntimeError(
                "Missing negative root for a simple root (pairing failed)"
            )
        sp = sr
        sn = root_by_key[neg_key]

        e0 = np.tensordot(sp.eigvec, basis, axes=([0], [0]))
        f0 = np.tensordot(sn.eigvec, basis, axes=([0], [0]))
        h0 = comm(e0, f0)

        c, rel = solve_cartan_coords(h0, cartan_mats)
        cartan_proj_relmax = max(cartan_proj_relmax, rel)
        alpha_h = np.dot(c, sr.weight)  # α(h0_proj)

        if abs(alpha_h) == 0.0:
            raise RuntimeError("Degenerate α(h) for a simple root")

        # Fix phase so α(h) becomes real-positive.
        phase = np.conj(alpha_h) / abs(alpha_h)
        f1 = phase * f0
        h1 = comm(e0, f1)
        c1, rel1 = solve_cartan_coords(h1, cartan_mats)
        cartan_proj_relmax = max(cartan_proj_relmax, rel1)
        alpha_h1 = np.dot(c1, sr.weight)
        alpha_hi_diag_dev = max(
            alpha_hi_diag_dev, float(abs(np.real(alpha_h1) - abs(alpha_h)))
        )

        scale = 2.0 / float(abs(alpha_h1))
        t = math.sqrt(scale)
        e = t * e0
        f = t * f1
        h = comm(e, f)

        e_mats[i] = e
        f_mats[i] = f
        h_mats[i] = h

    stats = {
        "cartan_projection_rel_resid_max": float(cartan_proj_relmax),
        "alpha_hi_diag_phase_fix_dev": float(alpha_hi_diag_dev),
    }
    return e_mats, f_mats, h_mats, stats


def cartan_matrix_from_h(
    simple_roots: Sequence[RootSpace], h_mats: np.ndarray, cartan_mats: np.ndarray
) -> Tuple[List[List[int]], Dict[str, float]]:
    """
    Compute a_ij = α_j(h_i) in the standard Serre convention:
      [h_i, e_j] = a_ij e_j
    using projection of h_i to Cartan span and rounding to ℤ.
    """
    c_list = []
    rel_list = []
    for i in range(6):
        c, rel = solve_cartan_coords(h_mats[i], cartan_mats)
        c_list.append(c)
        rel_list.append(rel)

    a = [[0 for _ in range(6)] for _ in range(6)]
    max_round_dev = 0.0
    max_imag = 0.0
    # rows: h_i coefficients; cols: root weights α_j
    for i, ci in enumerate(c_list):
        for j, sj in enumerate(simple_roots):
            val_c = np.dot(ci, sj.weight)
            max_imag = max(max_imag, float(abs(np.imag(val_c))))
            val = float(np.real(val_c))
            rounded = int(round(val))
            max_round_dev = max(max_round_dev, abs(val - rounded))
            a[i][j] = rounded

    stats = {
        "cartan_proj_rel_resid_max": float(max(rel_list) if rel_list else 0.0),
        "cartan_entry_round_dev_max": float(max_round_dev),
        "cartan_entry_imag_max": float(max_imag),
    }
    return a, stats


def find_perm_to_target(
    a: List[List[int]], target: List[List[int]]
) -> Optional[List[int]]:
    for perm in permutations(range(6)):
        ok = True
        for i in range(6):
            for j in range(6):
                if target[i][j] != a[perm[i]][perm[j]]:
                    ok = False
                    break
            if not ok:
                break
        if ok:
            return list(perm)
    return None


def classify_rank6_cartan(a: List[List[int]]) -> Tuple[str, Optional[List[int]]]:
    """
    Identify the Dynkin type among the common rank-6 dimension-78 candidates.
    Returns (type, perm_to_canonical_order).
    """
    perm = find_perm_to_target(a, E6_CANONICAL_CARTAN)
    if perm is not None:
        return "E6", perm
    perm = find_perm_to_target(a, B6_CANONICAL_CARTAN)
    if perm is not None:
        return "B6", perm
    perm = find_perm_to_target(a, C6_CANONICAL_CARTAN)
    if perm is not None:
        return "C6", perm
    return "unknown", None


def serre_check(
    e: np.ndarray,
    f: np.ndarray,
    h: np.ndarray,
    cartan: List[List[int]],
    *,
    tol: float = 1e-7,
) -> Dict[str, object]:
    failures = []

    def nz(name: str, m: np.ndarray):
        if frob_norm(m) > tol:
            failures.append({"relation": name, "norm": frob_norm(m)})

    def ad_power(x: np.ndarray, y: np.ndarray, n: int) -> np.ndarray:
        out = y
        for _ in range(n):
            out = comm(x, out)
        return out

    # [h_i, h_j] = 0
    for i in range(6):
        for j in range(i + 1, 6):
            nz(f"[h{i},h{j}]=0", comm(h[i], h[j]))

    # [h_i, e_j] = A_{j,i} e_j  (note index convention)
    for i in range(6):
        for j in range(6):
            nz(f"[h{i},e{j}]=A e", comm(h[i], e[j]) - cartan[i][j] * e[j])
            nz(f"[h{i},f{j}]=-A f", comm(h[i], f[j]) + cartan[i][j] * f[j])

    # [e_i, f_j] = δ_{ij} h_i
    for i in range(6):
        for j in range(6):
            target = h[i] if i == j else np.zeros_like(h[0])
            nz(f"[e{i},f{j}]=delta h", comm(e[i], f[j]) - target)

    # Serre: for i!=j, ad(e_i)^(1-A_ij)(e_j)=0 and same for f.
    for i in range(6):
        for j in range(6):
            if i == j:
                continue
            aij = cartan[i][j]
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
            m = 1 - int(aij)
            nz(f"ad(e{i})^{m}(e{j})=0", ad_power(e[i], e[j], m))
            nz(f"ad(f{i})^{m}(f{j})=0", ad_power(f[i], f[j], m))

    return {
        "ok": len(failures) == 0,
        "n_failures": len(failures),
        "failures": failures,
        "tol": tol,
    }


def _write_md(path: Path, data: dict) -> None:
    perm = data.get("cartan", {}).get("perm_to_canonical")
    dynkin = data.get("cartan", {}).get("dynkin_type")
    cartan = data.get("cartan", {}).get("cartan_matrix")
    serre = data.get("serre", {})
    lines = []
    lines.append("# Chevalley normalization from basis export\n")
    lines.append(f"- Source export: `{data.get('source', {}).get('export_dir')}`")
    if dynkin is not None:
        lines.append(f"- Detected Dynkin type: `{dynkin}`")
    lines.append(f"- Root spaces found: `{data.get('dims', {}).get('roots')}`")
    lines.append(f"- Cartan dim found: `{data.get('dims', {}).get('cartan')}`")
    lines.append(
        f"- Serre: `{serre.get('ok')}` (failures={serre.get('n_failures')}, tol={serre.get('tol')})"
    )
    lines.append("")
    if cartan is not None:
        lines.append("## Cartan matrix (computed order)\n")
        for row in cartan:
            lines.append(f"- `{row}`")
        lines.append("")
    if perm is not None:
        target = str(dynkin) if dynkin is not None else "rank-6"
        lines.append(f"## Permutation to canonical {target}\n")
        lines.append(f"- `perm_to_canonical = {perm}`")
        lines.append("")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv: Optional[Sequence[str]] = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--export-dir",
        type=str,
        default="",
        help="Path to e6_basis_export directory (containing E6_basis_78.npy). "
        "If omitted, uses the latest extracted export under artifacts/more_new_work_extracted.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=0,
        help="Deterministic seed for Cartan recovery and eigen choices.",
    )
    parser.add_argument(
        "--out-stem",
        type=str,
        default="e6_basis_export_chevalley",
        help="Artifact basename under artifacts/. Writes <stem>.json, <stem>.md, <stem>_generators.npy.",
    )
    # When imported and called from tests, we must not consume the parent's CLI flags (e.g. pytest's `-q`).
    args = parser.parse_args(list(argv) if argv is not None else [])

    export_dir = (
        Path(args.export_dir).expanduser().resolve()
        if args.export_dir
        else find_latest_basis_export_dir()
    )
    basis = load_basis_export(export_dir)
    _v, proj = build_projection(basis)

    cartan_mats, cartan_coeffs, cartan_stats = find_cartan_via_regular_centralizer(
        basis,
        seed=int(args.seed),
        max_tries=64,
        rcond=1e-10,
        require_commute_tol=1e-8,
    )

    ad_cartan = [ad_matrix_in_basis(hk, basis, proj) for hk in cartan_mats]
    eigvals, eigvecs, t = diagonalize_generic_cartan(ad_cartan, seed=int(args.seed))

    # Extract weights for all root eigenvectors to decide a robust rounding scale.
    tmp_weights_embed = []
    scale0 = float(np.max(np.abs(eigvals))) if eigvals.size else 1.0
    tol0 = max(1e-10 * scale0, 1e-14)
    for idx, lam in enumerate(eigvals.tolist()):
        if abs(lam) < tol0:
            continue
        v = eigvecs[:, idx]
        nv = float(np.linalg.norm(v))
        if nv == 0.0:
            continue
        v = v / nv
        w = []
        for ak in ad_cartan:
            lk = np.vdot(v, ak @ v) / np.vdot(v, v)
            w.append(lk)
        tmp_weights_embed.append(embed_weight(np.array(w, dtype=np.complex128)))
    tmp_weights_arr = np.array(tmp_weights_embed, dtype=np.float64)
    key_scale = choose_key_scale(tmp_weights_arr)

    roots, root_stats = extract_roots_from_eigendecomposition(
        eigvals, eigvecs, ad_cartan, key_scale=key_scale
    )
    root_by_key = {r.key: r for r in roots}

    # Cluster sanity: 72 distinct root keys and 1 zero key (Cartan) should hold.
    if len(root_by_key) != 72:
        raise RuntimeError("Root keys are not unique (rounding scale too coarse?)")

    pos = choose_positive_roots(roots)
    simple = find_simple_roots(pos)

    e, f, h, gen_stats = chevalley_normalize_simple_generators(
        basis, cartan_mats, simple, root_by_key
    )
    cartan, cartan_stats2 = cartan_matrix_from_h(simple, h, cartan_mats)
    dynkin_type, perm = classify_rank6_cartan(cartan)
    if perm is None:
        raise RuntimeError(
            "Unrecognized rank-6 Cartan matrix (not E6/B6/C6 under permutation)"
        )

    # Serre check in 27×27 matrices.
    norm_scale = max(frob_norm(x) for x in list(e) + list(f) + list(h))
    serre_tol = max(1e-7 * norm_scale, 1e-10)
    serre = serre_check(e, f, h, cartan, tol=serre_tol)
    if not bool(serre.get("ok")):
        raise RuntimeError("Serre relations failed (see artifacts for details)")

    out_json = ROOT / "artifacts" / f"{args.out_stem}.json"
    out_md = ROOT / "artifacts" / f"{args.out_stem}.md"
    out_npy = ROOT / "artifacts" / f"{args.out_stem}_generators.npy"

    data = {
        "status": "ok",
        "source": {
            "export_dir": str(export_dir),
            "basis_file": str(export_dir / "E6_basis_78.npy"),
        },
        "dims": {"cartan": 6, "roots": 72, "total": 78},
        "cartan_recovery": cartan_stats,
        "root_decomposition": {
            "generic_cartan_coeffs_t": t.tolist(),
            **root_stats,
        },
        "simple_roots": [
            {"key": list(sr.key), "weight": sr.weight.tolist()} for sr in simple
        ],
        "cartan": {
            "dynkin_type": dynkin_type,
            "cartan_matrix": cartan,
            "canonical_matrices": {
                "E6": E6_CANONICAL_CARTAN,
                "B6": B6_CANONICAL_CARTAN,
                "C6": C6_CANONICAL_CARTAN,
            },
            "perm_to_canonical": perm,
            **cartan_stats2,
        },
        "generators": gen_stats,
        "serre": serre,
    }
    dump_json(data, out_json, indent=2, sort_keys=True)
    _write_md(out_md, data)

    # Save generators for downstream exact work (optional).
    np.save(
        out_npy,
        {
            "e": e,
            "f": f,
            "h": h,
            "cartan_mats": cartan_mats,
            "cartan_coeffs": cartan_coeffs,
        },
    )

    print(f"Wrote {out_json}")
    print(f"Wrote {out_md}")
    print(f"Wrote {out_npy}")


if __name__ == "__main__":
    main(sys.argv[1:])
