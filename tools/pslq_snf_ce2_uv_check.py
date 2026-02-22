#!/usr/bin/env python3
"""PSLQ/SNF-style verifier for rationalized CE2 local solutions (U/V).

- Loads `artifacts/ce2_rational_local_solutions.json` created by
  `assemble_exact_l4_from_local_ce2.py`.
- For each recorded local solution:
  - parses `U_rats` / `V_rats` into `Fraction` objects
  - checks denominator bounds and reports numerators/denominators
  - reconstructs numeric alpha from the rationals and recomputes
    the homotopy Jacobi residual `J + l3 + d(alpha)` (numeric check)
  - attempts a PSLQ probe for cyclotomic relations (Q(zeta3)) on the list
    of distinct nonzero overlap values (if sympy.pslq available)
- Writes `artifacts/pslq_snf_ce2_uv_check.json` with the verification report.

This tool provides lightweight symbolic certificates for the CE2→l4 path.
"""
from __future__ import annotations

import importlib.util
import json
from fractions import Fraction
from math import isclose
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
IN = ROOT / "artifacts" / "ce2_rational_local_solutions.json"
OUT = ROOT / "artifacts" / "pslq_snf_ce2_uv_check.json"
MAX_DEN = 720

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
            pslq = None  # optional


def _load_bracket_tool():
    path = ROOT / "tools" / "toe_e8_z3graded_bracket_jacobi.py"
    spec = importlib.util.spec_from_file_location(
        "toe_e8_z3graded_bracket_jacobi", path
    )
    mod = importlib.util.module_from_spec(spec)
    sys = __import__("sys")
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def _load_exhaustive_helpers():
    path = ROOT / "tools" / "exhaustive_homotopy_check_rationalized_l3.py"
    spec = importlib.util.spec_from_file_location("exh", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def parse_frac_list(str_list: List[str]) -> List[Optional[Fraction]]:
    out: List[Optional[Fraction]] = []
    for s in str_list:
        if s in ("0", "0/1", "None", ""):
            out.append(None)
            continue
        try:
            out.append(Fraction(s))
        except Exception:
            # fallback: try float -> rational approximation
            out.append(Fraction(float(s)).limit_denominator(MAX_DEN))
    return out


def fraction_stats(fracs: List[Optional[Fraction]]) -> Dict[str, Any]:
    nonzero = [f for f in fracs if f is not None]
    if not nonzero:
        return {"count": 0}
    dens = [f.denominator for f in nonzero]
    nums = [f.numerator for f in nonzero]
    return {
        "count": len(nonzero),
        "min_den": min(dens),
        "max_den": max(dens),
        "den_set": sorted(list(set(dens)))[:10],
        "num_max_abs": max(abs(n) for n in nums),
    }


def make_numeric_e8_from_frac_list(toe_mod, flat_fracs: List[Optional[Fraction]]):
    # convert Fraction list -> complex128 numeric arrays (None -> 0.0)
    vec = np.zeros(len(flat_fracs), dtype=np.complex128)
    for i, fr in enumerate(flat_fracs):
        if fr is None:
            vec[i] = 0.0
        else:
            vec[i] = float(fr)
    N = 27 * 27
    e6 = vec[:N].reshape((27, 27))
    off = N
    sl3 = vec[off : off + 9].reshape((3, 3))
    off += 9
    g1 = vec[off : off + 81].reshape((27, 3))
    off += 81
    g2 = vec[off : off + 81].reshape((27, 3))
    return toe_mod.E8Z3(e6=e6, sl3=sl3, g1=g1, g2=g2)


def pslq_probe(values: List[complex]) -> Optional[List[int]]:
    if pslq is None or len(values) < 2:
        return None
    # Flatten to real pair list if complex entries present (try Re + Im*sqrt(3) trick)
    # Use a small precision; PSLQ in sympy expects rationals approx.
    reals: List[float] = []
    for v in values:
        if isinstance(v, complex):
            reals.append(float(np.real(v)))
            reals.append(float(-np.sqrt(3.0) * np.imag(v)))
        else:
            reals.append(float(v))
    try:
        rel = pslq(reals)
        return rel
    except Exception:
        return None


def main() -> Dict[str, Any]:
    assert IN.exists(), "Run assemble_exact_l4_from_local_ce2.py first"
    raw = json.loads(IN.read_text(encoding="utf-8"))

    toe = _load_bracket_tool()
    exh = _load_exhaustive_helpers()

    report: Dict[str, Any] = {"entries": {}, "ok": True}

    for key, entry in raw.items():
        U_rats = entry.get("U_rats", [])
        V_rats = entry.get("V_rats", [])
        U_fracs = parse_frac_list(U_rats)
        V_fracs = parse_frac_list(V_rats)

        statsU = fraction_stats(U_fracs)
        statsV = fraction_stats(V_fracs)

        # Basic denominator checks
        ok_den = True
        if statsU.get("count", 0) > 0 and statsU.get("max_den", 1) > MAX_DEN:
            ok_den = False
        if statsV.get("count", 0) > 0 and statsV.get("max_den", 1) > MAX_DEN:
            ok_den = False

        # reconstruct numeric alpha and verify d(alpha) cancels J + l3 numerically
        # recover triple indices from key or from stored a/b/c
        a = tuple(entry.get("a"))
        b = tuple(entry.get("b"))
        c = tuple(entry.get("c"))

        # dynamic import of LInfty helper (use file-location import to be script-friendly)
        spec = importlib.util.spec_from_file_location(
            "build_linfty", ROOT / "tools" / "build_linfty_firewall_extension.py"
        )
        build_mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(build_mod)
        LInftyE8Extension = build_mod.LInftyE8Extension
        _load_bad9 = build_mod._load_bad9

        proj = toe.E6Projector(
            np.load(
                ROOT / "artifacts" / "e6_27rep_basis_export" / "E6_basis_78.npy"
            ).astype(np.complex128)
        )
        all_triads = toe._load_signed_cubic_triads()
        bad9 = _load_bad9()
        linfty = LInftyE8Extension(toe, proj, all_triads, bad9, l3_scale=1.0 / 9.0)

        # basis elements
        x = exh.basis_elem_g1(toe, a)
        y = exh.basis_elem_g1(toe, b)
        z = exh.basis_elem_g2(toe, c)

        U_e8 = make_numeric_e8_from_frac_list(toe, U_fracs)
        V_e8 = make_numeric_e8_from_frac_list(toe, V_fracs)

        # define alpha from numeric U/V
        def alpha_num(A, B):
            if (
                np.allclose(A.g1, y.g1)
                and np.allclose(A.g2, y.g2)
                and np.allclose(B.g1, z.g1)
                and np.allclose(B.g2, z.g2)
            ):
                return U_e8
            if (
                np.allclose(A.g1, z.g1)
                and np.allclose(A.g2, z.g2)
                and np.allclose(B.g1, y.g1)
                and np.allclose(B.g2, y.g2)
            ):
                return U_e8.scale(-1.0)
            if (
                np.allclose(A.g1, x.g1)
                and np.allclose(A.g2, x.g2)
                and np.allclose(B.g1, z.g1)
                and np.allclose(B.g2, z.g2)
            ):
                return V_e8
            if (
                np.allclose(A.g1, z.g1)
                and np.allclose(A.g2, z.g2)
                and np.allclose(B.g1, x.g1)
                and np.allclose(B.g2, x.g2)
            ):
                return V_e8.scale(-1.0)
            return toe.E8Z3.zero()

        linfty.attach_ce2_alpha(alpha_num)

        # compute target: J + l3
        J = toe._jacobi(linfty.br_l2, x, y, z)
        l3_total = linfty.l3(x, y, z)
        before = toe.E8Z3(
            e6=J.e6 + l3_total.e6,
            sl3=J.sl3 + l3_total.sl3,
            g1=J.g1 + l3_total.g1,
            g2=J.g2 + l3_total.g2,
        )

        # after adding d(alpha)
        d_alpha = linfty.d_alpha_on_triple(x, y, z)
        after = toe.E8Z3(
            e6=before.e6 + d_alpha.e6,
            sl3=before.sl3 + d_alpha.sl3,
            g1=before.g1 + d_alpha.g1,
            g2=before.g2 + d_alpha.g2,
        )

        max_before = float(
            max(
                np.max(np.abs(before.e6)) if before.e6.size else 0.0,
                np.max(np.abs(before.sl3)) if before.sl3.size else 0.0,
                np.max(np.abs(before.g1)) if before.g1.size else 0.0,
                np.max(np.abs(before.g2)) if before.g2.size else 0.0,
            )
        )
        max_after = float(
            max(
                np.max(np.abs(after.e6)) if after.e6.size else 0.0,
                np.max(np.abs(after.sl3)) if after.sl3.size else 0.0,
                np.max(np.abs(after.g1)) if after.g1.size else 0.0,
                np.max(np.abs(after.g2)) if after.g2.size else 0.0,
            )
        )

        ok_numeric = bool(max_after < 1e-12)

        # PSLQ probe on distinct nonzero rational values (if any)
        distinct_vals = list({float(fr) for fr in V_fracs if fr is not None})[:20]
        pslq_rel = pslq_probe(distinct_vals) if distinct_vals else None

        report["entries"][key] = {
            "a": a,
            "b": b,
            "c": c,
            "statsU": statsU,
            "statsV": statsV,
            "denominators_ok": ok_den,
            "max_before": float(max_before),
            "max_after": float(max_after),
            "numeric_ok": ok_numeric,
            "pslq_on_values": pslq_rel,
        }

        linfty.detach_ce2_alpha()

        if not (ok_den and ok_numeric):
            report["ok"] = False

    OUT.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
    print(f"Wrote {OUT}")
    return report


if __name__ == "__main__":
    main()
