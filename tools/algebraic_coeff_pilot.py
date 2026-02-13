#!/usr/bin/env python3
"""Algebraic‑coefficient pilot for l3 patches.

Goal: try coefficients c_T in Q(ζ_n) (n=3,7) so that
    sum_T c_T * S_T = - J
for a selected failing triple.  Writes `artifacts/algebraic_coeff_pilot.json`.

Behavior:
- quick early‑exit if all S_T are zero on the failing triple (CE/H^3 obstruction).
- otherwise try linear solve over rational coefficients in the cyclotomic basis
  (LSQ -> rationalize -> SNF check).

This is a diagnostic helper (not a full search sweep).
"""
from __future__ import annotations

import importlib.util
import json
from fractions import Fraction
from pathlib import Path
from typing import List, Tuple

import numpy as np

# optional PSLQ
try:
    from sympy.ntheory import pslq
except Exception:
    try:
        from sympy.ntheory.modular import pslq
    except Exception:
        try:
            import mpmath as _mp

            def pslq(vec):
                mp_vec = [_mp.mpf(str(float(x))) for x in vec]
                return _mp.pslq(mp_vec)

        except Exception:
            pslq = None

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "artifacts" / "algebraic_coeff_pilot.json"
MAX_DEN = 720
TOL = 1e-10


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys_mod = __import__("sys")
    sys_mod.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def flatten(e):
    return np.concatenate(
        [e.e6.reshape(-1), e.sl3.reshape(-1), e.g1.reshape(-1), e.g2.reshape(-1)]
    )


def cyclotomic_basis(zeta_order: int) -> Tuple[np.complex128, List[complex]]:
    # Return (primitive_root, [1, zeta, zeta^2, ..., zeta^{phi-1}])
    n = zeta_order
    z = np.exp(2j * np.pi / n)
    # for prime n, degree = n-1; for 3 and 7 this holds
    deg = phi = n - 1
    basis = [z**k for k in range(phi)]
    return z, basis


def attempt_field_search(
    field_order: int, S_flats: List[np.ndarray], Jflat: np.ndarray
) -> dict:
    z, basis = cyclotomic_basis(field_order)
    phi = len(basis)
    m = len(S_flats)
    vec_len = Jflat.size
    # build complex matrix with columns = basis[k] * S_flats[t]
    cols = []
    for t in range(m):
        S = S_flats[t]
        for k in range(phi):
            cols.append(basis[k] * S)
    A = np.column_stack(cols) if cols else np.zeros((vec_len, 0), dtype=np.complex128)
    # real system
    A_real = (
        np.vstack([np.real(A).T, np.imag(A).T]).T
        if A.size
        else np.zeros((2 * vec_len, 0), dtype=float)
    )
    b_real = -np.concatenate([np.real(Jflat), np.imag(Jflat)])

    res = {"field_order": field_order, "phi": phi, "solvable": False}
    if A_real.size == 0:
        res["note"] = "empty coefficient matrix"
        return res

    # least-squares solution
    x, *_ = np.linalg.lstsq(A_real, b_real, rcond=None)
    residual = np.linalg.norm(A_real.dot(x) - b_real)
    res["lsq_residual"] = float(residual)
    res["lsq_rank"] = int(np.linalg.matrix_rank(A_real))

    if residual > 1e-8:
        return res

    # rationalize each coefficient (they should be rational if exact in the cyclotomic basis)
    rats = []
    dens = []
    for xi in x:
        fr = Fraction(float(xi)).limit_denominator(MAX_DEN)
        rats.append(fr)
        dens.append(fr.denominator)
    lcm_den = 1
    from math import gcd

    for d in dens:
        lcm_den = lcm_den * d // gcd(lcm_den, d)

    # integer matrix check (SNF-like): A_real * x = b_real  -> multiply through by lcm_den
    Aint = np.rint(A_real * lcm_den).astype(int)
    bint = np.rint(b_real * lcm_den).astype(int)
    # quick integer-check via residual
    int_residual = np.linalg.norm(Aint.dot([int(fr.numerator) for fr in rats]) - bint)
    res["lcm_denominator"] = int(lcm_den)
    res["int_residual"] = float(int_residual)

    # assemble algebraic coefficients per triad
    coeffs = []
    for t in range(m):
        comp = 0 + 0j
        for k in range(phi):
            idx = t * phi + k
            comp += complex(rats[idx].numerator) / rats[idx].denominator * basis[k]
        coeffs.append(comp)
    res["coeffs_complex"] = [complex(c) for c in coeffs]
    # verify exact cancellation
    lhs = sum(c * S for c, S in zip(coeffs, S_flats))
    res["verify_norm"] = float(np.linalg.norm(lhs + Jflat))

    if res["verify_norm"] < 1e-10:
        res["solvable"] = True
        res["coeffs_rational_in_basis"] = [str(fr) for fr in rats]
    return res


def main():
    # load failing triple (prefer exhaustive artifact)
    exh_path = ROOT / "artifacts" / "exhaustive_homotopy_rationalized_l3.json"
    if not exh_path.exists():
        raise RuntimeError(
            "exhaustive artifact missing; run exhaustive_homotopy_check_rationalized_l3.py first"
        )
    ex = json.loads(exh_path.read_text(encoding="utf-8"))
    ft = ex.get("sectors", {}).get("g1_g1_g2", {}).get("first_fail")
    if not ft:
        raise RuntimeError("no failing triple recorded in exhaustive artifact")
    a_idx = tuple(ft["a"]) if isinstance(ft.get("a"), list) else tuple(ft.get("a"))
    b_idx = tuple(ft["b"])
    c_idx = tuple(ft["c"])

    # load toe + helpers
    toe = _load_module(ROOT / "tools" / "toe_e8_z3graded_bracket_jacobi.py", "toe_e8")
    exh_mod = _load_module(
        ROOT / "tools" / "exhaustive_homotopy_check_rationalized_l3.py", "exh_hj"
    )
    basis_elem_g1 = exh_mod.basis_elem_g1
    basis_elem_g2 = exh_mod.basis_elem_g2

    # build bracket objects (reuse linfty helpers for bad9 mapping)
    e6_basis = np.load(
        ROOT / "artifacts" / "e6_27rep_basis_export" / "E6_basis_78.npy"
    ).astype(np.complex128)
    proj = toe.E6Projector(e6_basis)
    all_triads = toe._load_signed_cubic_triads()
    # bad9 mapping (same as other scripts)
    bad9 = set()
    fb = ROOT / "artifacts" / "firewall_bad_triads_mapping.json"
    if fb.exists():
        try:
            bad9_list = json.loads(fb.read_text(encoding="utf-8")).get(
                "bad_triangles_Schlafli_e6id", []
            )
            bad9 = set(tuple(sorted(t)) for t in bad9_list)
        except Exception:
            bad9 = set()
    try:
        linfty_mod = _load_module(
            ROOT / "tools" / "build_linfty_firewall_extension.py", "linfty_mod"
        )
        bad9 = linfty_mod._load_bad9()
    except Exception:
        pass

    br_l2 = toe.E8Z3Bracket(
        e6_projector=proj,
        cubic_triads=[t for t in all_triads if tuple(sorted(t[:3])) not in bad9],
        scale_g1g1=1.0,
        scale_g2g2=-1.0 / 6.0,
        scale_e6=1.0,
        scale_sl3=1.0 / 6.0,
    )
    fiber_triads = [t for t in all_triads if tuple(sorted(t[:3])) in bad9]
    br_fibers = [
        toe.E8Z3Bracket(
            e6_projector=proj,
            cubic_triads=[T],
            scale_g1g1=1.0,
            scale_g2g2=-1.0 / 6.0,
            scale_e6=1.0,
            scale_sl3=1.0 / 6.0,
        )
        for T in fiber_triads
    ]

    # construct x,y,z for the failing triple (g1,g1,g2 expected)
    x = basis_elem_g1(toe, tuple(a_idx))
    y = basis_elem_g1(toe, tuple(b_idx))
    z = basis_elem_g2(toe, tuple(c_idx))

    J = toe._jacobi(br_l2, x, y, z)
    Jflat = flatten(J)

    # compute S_flats
    S_flats = []
    for brf in br_fibers:
        j1 = brf.bracket(x, br_l2.bracket(y, z))
        j2 = brf.bracket(y, br_l2.bracket(z, x))
        j3 = brf.bracket(z, br_l2.bracket(x, y))
        f1 = br_l2.bracket(brf.bracket(x, y), z)
        f2 = br_l2.bracket(brf.bracket(y, z), x)
        f3 = br_l2.bracket(brf.bracket(z, x), y)
        ff1 = brf.bracket(x, brf.bracket(y, z))
        ff2 = brf.bracket(y, brf.bracket(z, x))
        ff3 = brf.bracket(z, brf.bracket(x, y))
        S = j1 + j2 + j3 + f1 + f2 + f3 + ff1 + ff2 + ff3
        S_flats.append(flatten(S))

    # quick degeneracy check
    max_norms = [float(np.max(np.abs(S))) if S.size else 0.0 for S in S_flats]
    degenerate = all(n < TOL for n in max_norms)

    out: dict = {
        "failed_triple": {"a": a_idx, "b": b_idx, "c": c_idx},
        "J_norm": float(np.linalg.norm(Jflat)),
        "S_flats_max_norms": max_norms,
        "degenerate_on_fiber_support": bool(degenerate),
    }

    if degenerate:
        out["note"] = (
            "All per‑triad S_T evaluate to zero on the failing triple — no l3 supported on the 9 fibers "
            "can cancel this Jacobi (CE/H^3 obstruction)."
        )
        OUT.write_text(json.dumps(out, indent=2), encoding="utf-8")
        print(
            "Degenerate: S_flats zero on failing triple — algebraic coefficients won't help."
        )
        return

    # otherwise attempt field solves (ζ3 then ζ7)
    results = []
    for n in (3, 7):
        try:
            r = attempt_field_search(n, S_flats, Jflat)
            results.append(r)
        except Exception as e:
            results.append({"field_order": n, "error": str(e)})

    out["field_attempts"] = results
    OUT.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print("Wrote:", OUT)


if __name__ == "__main__":
    main()
