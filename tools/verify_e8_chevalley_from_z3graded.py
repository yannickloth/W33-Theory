#!/usr/bin/env python3
"""
Build a *Chevalley-Serre certificate* for the E8 algebra realized by the Z3-graded
trinification bracket:

  e8 ≅ (e6 ⊕ sl3) ⊕ (27⊗3) ⊕ (27*⊗3*)

This upgrades the existing closeout from "Jacobi holds + Dynkin recovered" to an
explicit set of generators {e_i,f_i,h_i} (i=1..8) satisfying:
  [h_i,h_j]=0
  [h_i,e_j]=A_ij e_j
  [h_i,f_j]=-A_ij f_j
  [e_i,f_j]=δ_ij h_i
  Serre: (ad e_i)^(1-A_ij)(e_j)=0 for i≠j (and same for f)

Key design choice:
  - We use the repo's natural Cartan basis H = (H_E6[6], H_A2[2]) where:
      H_E6 are the certified diagonal Chevalley h_i in the 27-rep
      H_A2 are the standard sl3 coroots diag(1,-1,0), diag(0,1,-1)
  - The *simple roots* are taken from artifacts/verify_e8_dynkin_from_trinification.json
    (a positivity-chosen E8 simple system in this Cartan coordinate basis).
  - For mixed roots, we pick canonical basis elements in g1/g2.
  - For the two E6-only simple roots that appear in that simple system, we solve for
    explicit e6 root vectors inside the 78-dim e6 span using ad(H_E6) eigen-equations.

Outputs:
  - artifacts/verify_e8_chevalley_from_z3graded.json
  - artifacts/verify_e8_chevalley_from_z3graded.md
"""

from __future__ import annotations

import importlib.util
import json
from dataclasses import dataclass
from itertools import permutations
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

ROOT = Path(__file__).resolve().parents[1]


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load module {name} from {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _write_json(path: Path, obj: Dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_md(path: Path, lines: List[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def _max_abs(m: np.ndarray) -> float:
    if m.size == 0:
        return 0.0
    return float(np.max(np.abs(m)))


@dataclass(frozen=True)
class RelResidual:
    coeff: float
    rel_resid: float


def _elt_to_vec(e, *, complex_ok: bool = True) -> np.ndarray:
    parts = [e.e6.reshape(-1), e.sl3.reshape(-1), e.g1.reshape(-1), e.g2.reshape(-1)]
    v = np.concatenate(parts).astype(np.complex128 if complex_ok else np.float64)
    return v


def _inner(a, b) -> float:
    va = _elt_to_vec(a)
    vb = _elt_to_vec(b)
    return float(np.vdot(va, vb).real)


def _norm(a) -> float:
    return float(np.sqrt(max(_inner(a, a), 0.0)))


def _best_scalar(target, basis) -> float:
    denom = _inner(basis, basis)
    if denom == 0.0:
        return 0.0
    return _inner(basis, target) / denom


def _rel_residual(target, basis, coeff: float) -> float:
    # ||target - coeff*basis|| / (||basis|| + eps)
    diff = target - basis.scale(coeff)
    return _norm(diff) / (_norm(basis) + 1e-30)


def _fit_scalar_multiple(target, basis) -> RelResidual:
    c = _best_scalar(target, basis)
    return RelResidual(coeff=float(c), rel_resid=float(_rel_residual(target, basis, c)))


def _as_int_matrix(m: np.ndarray) -> List[List[int]]:
    return [[int(x) for x in row] for row in m.tolist()]


def _canonical_e8_cartan() -> np.ndarray:
    return np.array(
        [
            [2, -1, 0, 0, 0, 0, 0, 0],
            [-1, 2, -1, 0, 0, 0, 0, 0],
            [0, -1, 2, -1, 0, 0, 0, 0],
            [0, 0, -1, 2, -1, 0, 0, 0],
            [0, 0, 0, -1, 2, -1, 0, -1],
            [0, 0, 0, 0, -1, 2, -1, 0],
            [0, 0, 0, 0, 0, -1, 2, 0],
            [0, 0, 0, 0, -1, 0, 0, 2],
        ],
        dtype=int,
    )


def _perm_match_cartan(C: np.ndarray, target: np.ndarray) -> Optional[List[int]]:
    for perm in permutations(range(8)):
        P = np.array(perm, dtype=int)
        Cp = C[np.ix_(P, P)]
        if np.array_equal(Cp, target):
            return list(perm)
    return None


def _load_e6_cartan_h() -> np.ndarray:
    obj = np.load(
        ROOT / "artifacts" / "e6_27rep_minuscule_generators.npy", allow_pickle=True
    ).item()
    h = np.array(obj["h"], dtype=np.complex128)
    if h.shape != (6, 27, 27):
        raise ValueError(f"Unexpected e6 Cartan shape: {h.shape}")
    # Ensure diagonal entries are integral up to rounding.
    diag = np.stack([np.diag(h[i]).real for i in range(6)], axis=1)
    if float(np.max(np.abs(diag - np.rint(diag)))) > 1e-8:
        raise ValueError("E6 Cartan diagonals are not near-integers; basis mismatch?")
    return h


def _load_e6_basis78() -> np.ndarray:
    p = ROOT / "artifacts" / "e6_27rep_basis_export" / "E6_basis_78.npy"
    mats = np.load(p)
    if mats.shape != (78, 27, 27):
        raise ValueError(f"Unexpected E6_basis_78 shape: {mats.shape}")
    return mats.astype(np.complex128)


def _comm(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    return a @ b - b @ a


def _e6_ad_mats(basis78: np.ndarray, h6: np.ndarray) -> np.ndarray:
    """
    Return Ad_k matrices (6,78,78) in the given 78-basis coordinates:
      Ad_k[:,j] = coords([h_k, basis_j]).
    """
    # Gram_{ab} = Tr(B_a B_b)
    gram = np.einsum("aij,bji->ab", basis78, basis78)
    if int(np.linalg.matrix_rank(gram)) != 78:
        raise RuntimeError("E6 basis Gram not full rank")
    gram_inv = np.linalg.inv(gram)

    # flattened basis for BLAS-backed projections (faster than einsum in loops)
    basis78_flat = basis78.reshape(78, -1)

    def coords(M: np.ndarray) -> np.ndarray:
        M_flat = M.T.ravel()
        b = basis78_flat @ M_flat
        return gram_inv @ b

    ad = np.zeros((6, 78, 78), dtype=np.complex128)
    for k in range(6):
        hk = h6[k]
        for j in range(78):
            ad[k, :, j] = coords(_comm(hk, basis78[j]))
    return ad


def _nullspace(A: np.ndarray, *, rcond: float) -> np.ndarray:
    u, s, vh = np.linalg.svd(A, full_matrices=False)
    if s.size == 0:
        raise ValueError("Empty SVD")
    thresh = float(rcond) * float(s[0])
    rank = int(np.sum(s > thresh))
    return vh[rank:].conj().T


def _solve_e6_root_vector(
    *,
    alpha6: Sequence[int],
    basis78: np.ndarray,
    ad6: np.ndarray,
    rcond: float = 1e-10,
) -> np.ndarray:
    """
    Solve for X in span(basis78) such that [h_k, X] = alpha6[k] X for all k.
    Returns a (27,27) complex matrix (scaled arbitrarily).
    """
    alpha = np.array(alpha6, dtype=float).reshape(6)
    I = np.eye(78, dtype=np.complex128)
    blocks = [(ad6[k] - alpha[k] * I) for k in range(6)]
    A = np.vstack(blocks)  # (6*78, 78)
    ns = _nullspace(A, rcond=rcond)
    if ns.shape[1] == 0:
        raise RuntimeError(f"No root vector found for alpha6={alpha6}")
    x = ns[:, 0]
    # normalize
    mx = float(np.max(np.abs(x)))
    if mx == 0.0:
        raise RuntimeError("Degenerate null vector")
    x = x / mx
    X_flat = x @ basis78.reshape(78, -1)
    X = X_flat.reshape(27, 27)
    return X


def _basis_g1(mod, i: int, a: int):
    E8Z3 = mod.E8Z3
    z = E8Z3.zero()
    g1 = z.g1.copy()
    g1[i, a] = 1.0
    return E8Z3(e6=z.e6, sl3=z.sl3, g1=g1, g2=z.g2)


def _basis_g2(mod, i: int, a: int):
    E8Z3 = mod.E8Z3
    z = E8Z3.zero()
    g2 = z.g2.copy()
    g2[i, a] = 1.0
    return E8Z3(e6=z.e6, sl3=z.sl3, g1=z.g1, g2=g2)


def main() -> None:
    # Load the bracket machinery (no package import in this repo).
    br_mod = _load_module(
        "toe_e8_z3graded_bracket_jacobi",
        ROOT / "tools" / "toe_e8_z3graded_bracket_jacobi.py",
    )
    root_mod = _load_module(
        "verify_e8_root_system_from_trinification",
        ROOT / "tools" / "verify_e8_root_system_from_trinification.py",
    )

    E8Z3 = br_mod.E8Z3
    E6Projector = br_mod.E6Projector
    E8Z3Bracket = br_mod.E8Z3Bracket

    # Scales locked by the Jacobi tuner.
    z3 = json.loads(
        (ROOT / "artifacts" / "verify_e8_z3graded_trinification.json").read_text(
            encoding="utf-8"
        )
    )
    scales = z3["scales"]

    basis78 = _load_e6_basis78()
    triads = br_mod._load_signed_cubic_triads()
    proj = E6Projector(basis78)

    br = E8Z3Bracket(
        e6_projector=proj,
        cubic_triads=triads,
        scale_g1g1=float(scales["scale_g1g1"]),
        scale_g2g2=float(scales["scale_g2g2"]),
        scale_e6=float(scales["scale_e6"]),
        scale_sl3=float(scales["scale_sl3"]),
    )

    # Cartan basis H = (E6 h_i, A2 h_1,h_2) in the *weight-coordinate system* used by the root verifier.
    h6 = _load_e6_cartan_h()
    H_a2_1 = np.diag([1.0, -1.0, 0.0]).astype(np.complex128)
    H_a2_2 = np.diag([0.0, 1.0, -1.0]).astype(np.complex128)

    H_basis: List = []
    for k in range(6):
        H_basis.append(
            E8Z3(
                e6=h6[k].copy(),
                sl3=np.zeros((3, 3), dtype=np.complex128),
                g1=np.zeros((27, 3), dtype=np.complex128),
                g2=np.zeros((27, 3), dtype=np.complex128),
            )
        )
    H_basis.append(
        E8Z3(
            e6=np.zeros((27, 27), dtype=np.complex128),
            sl3=H_a2_1,
            g1=np.zeros((27, 3), dtype=np.complex128),
            g2=np.zeros((27, 3), dtype=np.complex128),
        )
    )
    H_basis.append(
        E8Z3(
            e6=np.zeros((27, 27), dtype=np.complex128),
            sl3=H_a2_2,
            g1=np.zeros((27, 3), dtype=np.complex128),
            g2=np.zeros((27, 3), dtype=np.complex128),
        )
    )

    # Simple roots (in this Cartan coordinate basis).
    dyn = json.loads(
        (ROOT / "artifacts" / "verify_e8_dynkin_from_trinification.json").read_text(
            encoding="utf-8"
        )
    )
    simples: List[List[int]] = dyn["simples"]

    # Precompute E6 adjoint Cartan action (only needed for E6-only simple roots in this simple system).
    ad6 = _e6_ad_mats(basis78, h6)

    # Mixed-root lookup table: g1 weight=(w27,w3), g2 weight=(-w27,-w3)
    w27 = root_mod.load_e6_27_weights_from_chevalley()
    w3 = root_mod.a2_weights_fund3()
    weight_to_g1: Dict[Tuple[int, ...], Tuple[int, int]] = {}
    weight_to_g2: Dict[Tuple[int, ...], Tuple[int, int]] = {}
    for i in range(27):
        for a in range(3):
            mu = tuple(int(x) for x in w27[i].tolist())
            nu = tuple(int(x) for x in w3[a].tolist())
            wt = tuple(list(mu) + list(nu))
            weight_to_g1[wt] = (i, a)
            weight_to_g2[tuple([-x for x in wt])] = (
                i,
                a,
            )  # (-mu,-nu) at same indices in g2

    # Build Chevalley generators for the chosen E8 simple roots.
    E: List = []
    F: List = []
    kind: List[Dict[str, object]] = []

    for alpha in simples:
        a8 = tuple(int(x) for x in alpha)
        a6 = a8[:6]
        a2 = a8[6:]
        if a2 == (0, 0):
            # E6 root: solve in the 78-dim e6 subspace.
            Xp = _solve_e6_root_vector(alpha6=a6, basis78=basis78, ad6=ad6)
            Xm = _solve_e6_root_vector(
                alpha6=[-x for x in a6], basis78=basis78, ad6=ad6
            )
            E.append(
                E8Z3(
                    e6=Xp,
                    sl3=np.zeros((3, 3), dtype=np.complex128),
                    g1=np.zeros((27, 3), dtype=np.complex128),
                    g2=np.zeros((27, 3), dtype=np.complex128),
                )
            )
            F.append(
                E8Z3(
                    e6=Xm,
                    sl3=np.zeros((3, 3), dtype=np.complex128),
                    g1=np.zeros((27, 3), dtype=np.complex128),
                    g2=np.zeros((27, 3), dtype=np.complex128),
                )
            )
            kind.append({"grade": "g0(e6)", "alpha8": list(a8)})
            continue

        # Mixed root: decide if it lives in g1 or g2.
        if a8 in weight_to_g1:
            i, a = weight_to_g1[a8]
            E.append(_basis_g1(br_mod, i, a))
            F.append(_basis_g2(br_mod, i, a))
            kind.append(
                {"grade": "g1", "alpha8": list(a8), "i27": int(i), "i3": int(a)}
            )
            continue
        if a8 in weight_to_g2:
            i, a = weight_to_g2[a8]
            E.append(_basis_g2(br_mod, i, a))
            F.append(_basis_g1(br_mod, i, a))
            kind.append(
                {"grade": "g2", "alpha8": list(a8), "i27": int(i), "i3": int(a)}
            )
            continue

        raise RuntimeError(f"Could not locate mixed root {a8} in g1/g2 weight tables")

    if len(E) != 8:
        raise RuntimeError("Expected 8 simple roots")

    # Normalize each pair so that [h_i, e_i] = 2 e_i (Chevalley convention).
    H: List = []
    f_scales: List[float] = []
    rels_local: List[Dict[str, object]] = []
    for i in range(8):
        H_i = br.bracket(E[i], F[i])
        he = br.bracket(H_i, E[i])
        fit = _fit_scalar_multiple(he, E[i])
        if abs(fit.coeff) < 1e-12:
            raise RuntimeError("Degenerate [H,E] coefficient")
        t = 2.0 / fit.coeff
        F_i2 = F[i].scale(t)
        H_i2 = br.bracket(E[i], F_i2)
        he2 = br.bracket(H_i2, E[i])
        fit2 = _fit_scalar_multiple(he2, E[i])
        H.append(H_i2)
        F[i] = F_i2
        f_scales.append(float(t))
        rels_local.append(
            {
                "i": i,
                "scale_f": float(t),
                "before": {
                    "coeff": float(fit.coeff),
                    "rel_resid": float(fit.rel_resid),
                },
                "after": {
                    "coeff": float(fit2.coeff),
                    "rel_resid": float(fit2.rel_resid),
                },
            }
        )

    # Build Cartan matrix A_ij from bracket: [H_i, E_j] = A_ij E_j.
    A = np.zeros((8, 8), dtype=int)
    A_fit: List[List[Dict[str, float]]] = [[{} for _ in range(8)] for _ in range(8)]
    max_rel_resid_h_e = 0.0
    for i in range(8):
        for j in range(8):
            hij = br.bracket(H[i], E[j])
            fit = _fit_scalar_multiple(hij, E[j])
            A_fit[i][j] = {"coeff": float(fit.coeff), "rel_resid": float(fit.rel_resid)}
            max_rel_resid_h_e = max(max_rel_resid_h_e, float(fit.rel_resid))
            A[i, j] = int(round(fit.coeff))

    # Verify [H_i, H_j] ≈ 0.
    max_hh = 0.0
    for i in range(8):
        for j in range(i + 1, 8):
            max_hh = max(max_hh, _norm(br.bracket(H[i], H[j])))

    # Verify [E_i, F_j] relations.
    max_ef_offdiag = 0.0
    max_ef_diag_rel = 0.0
    for i in range(8):
        for j in range(8):
            c = br.bracket(E[i], F[j])
            if i == j:
                # c should equal H_i
                denom = _norm(H[i]) + 1e-30
                max_ef_diag_rel = max(max_ef_diag_rel, _norm(c - H[i]) / denom)
            else:
                max_ef_offdiag = max(max_ef_offdiag, _norm(c))

    # Serre residuals.
    serre_e: Dict[str, float] = {}
    serre_f: Dict[str, float] = {}
    max_serre_e = 0.0
    max_serre_f = 0.0
    for i in range(8):
        for j in range(8):
            if i == j:
                continue
            n = 1 - int(A[i, j])
            # For simply-laced E8, n in {1,2}.
            x = E[j]
            for _ in range(n):
                x = br.bracket(E[i], x)
            y = F[j]
            for _ in range(n):
                y = br.bracket(F[i], y)
            ke = f"{i},{j}"
            serre_e[ke] = float(_norm(x))
            serre_f[ke] = float(_norm(y))
            max_serre_e = max(max_serre_e, serre_e[ke])
            max_serre_f = max(max_serre_f, serre_f[ke])

    # Match Cartan matrix to canonical E8 up to permutation.
    perm_to_canonical = _perm_match_cartan(A, _canonical_e8_cartan())

    status = "ok"
    if perm_to_canonical is None:
        status = "fail"
    if max_hh > 1e-8:
        status = "fail"
    if max_rel_resid_h_e > 1e-6:
        status = "fail"
    if max_ef_offdiag > 1e-6:
        status = "fail"
    if max_ef_diag_rel > 1e-6:
        status = "fail"
    if max_serre_e > 1e-6:
        status = "fail"
    if max_serre_f > 1e-6:
        status = "fail"

    out = {
        "status": status,
        "sources": {
            "e8_simple_roots": "artifacts/verify_e8_dynkin_from_trinification.json",
            "z3_bracket_scales": "artifacts/verify_e8_z3graded_trinification.json",
            "e6_cartan_h": "artifacts/e6_27rep_minuscule_generators.npy",
            "e6_basis78": "artifacts/e6_27rep_basis_export/E6_basis_78.npy",
            "cubic_triads": "artifacts/canonical_su3_gauge_and_cubic.json",
        },
        "scales": scales,
        "simple_roots": {"alpha8": simples, "where": kind},
        "normalization": {"f_scales": f_scales, "diagnostics": rels_local},
        "cartan": {
            "cartan_matrix_from_bracket": _as_int_matrix(A),
            "max_rel_resid_[H,E]": float(max_rel_resid_h_e),
            "max_abs_[H,H]": float(max_hh),
            "perm_to_canonical_e8": perm_to_canonical,
        },
        "chevalley": {
            "max_abs_[E_i,F_j] (i!=j)": float(max_ef_offdiag),
            "max_rel_[E_i,F_i]-H_i": float(max_ef_diag_rel),
        },
        "serre": {
            "max_norm_e": float(max_serre_e),
            "max_norm_f": float(max_serre_f),
        },
    }

    out_json = ROOT / "artifacts" / "verify_e8_chevalley_from_z3graded.json"
    out_md = ROOT / "artifacts" / "verify_e8_chevalley_from_z3graded.md"
    _write_json(out_json, out)

    md: List[str] = []
    md.append("# Verify E8 Chevalley from Z3-graded trinification bracket\n")
    md.append(f"- status: `{status}`")
    md.append(f"- max rel residual [H,E]: `{max_rel_resid_h_e:.3e}`")
    md.append(f"- max abs [H,H]: `{max_hh:.3e}`")
    md.append(f"- max abs [E_i,F_j] i!=j: `{max_ef_offdiag:.3e}`")
    md.append(f"- max rel [E_i,F_i]-H_i: `{max_ef_diag_rel:.3e}`")
    md.append(f"- max Serre residual (e): `{max_serre_e:.3e}`")
    md.append(f"- max Serre residual (f): `{max_serre_f:.3e}`")
    md.append(f"- perm_to_canonical_e8: `{perm_to_canonical}`\n")
    md.append("## Cartan matrix (raw order)\n")
    md.append("```")
    for row in A.tolist():
        md.append(" ".join(f"{int(x):2d}" for x in row))
    md.append("```")
    md.append(f"- JSON: `{out_json}`")
    _write_md(out_md, md)

    print(f"status={status} max_serre={max(max_serre_e, max_serre_f):.3e}")
    if status != "ok":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
