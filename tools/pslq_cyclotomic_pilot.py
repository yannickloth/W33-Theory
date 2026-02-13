#!/usr/bin/env python3
"""Pilot PSLQ search for relations over Q(\zeta_3) (i.e. Q(\sqrt{-3}))

- For each failing triple (from exhaustive homotopy artifact) compute S·J overlaps.
- Try to find integer coefficient pairs (u_i, v_i) so that
    sum_i (u_i + v_i * sqrt(-3)) * overlap_i == 0
  by using PSLQ on the real linear combination that represents the real part
  equation: sum_i (u_i * Re(ov_i) - v_i * sqrt(3) * Im(ov_i)) == 0
  and then verifying the imaginary equation.
- Writes artifact: artifacts/pslq_cyclotomic_pilot.json
"""
from __future__ import annotations

import importlib.util
import json
from math import sqrt
from pathlib import Path
from typing import List, Tuple

import numpy as np
from sympy import N

try:
    from sympy.ntheory import pslq
except Exception:
    try:
        from sympy.ntheory.modular import pslq
    except Exception:
        try:
            import mpmath as _mp

            def pslq(vec):
                # accept sympy/mapped numeric types; convert to mpmath mpf
                mp_vec = [_mp.mpf(str(float(x))) for x in vec]
                return _mp.pslq(mp_vec)

        except Exception:
            pslq = None

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "artifacts" / "pslq_cyclotomic_pilot.json"
EXH = ROOT / "artifacts" / "exhaustive_homotopy_rationalized_l3.json"


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    import sys as _sys

    _sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def flatten(e):
    return np.concatenate(
        [e.e6.reshape(-1), e.sl3.reshape(-1), e.g1.reshape(-1), e.g2.reshape(-1)]
    )


def analyze_one(
    toe, a_idx: Tuple[int, int], b_idx: Tuple[int, int], c_idx: Tuple[int, int]
):
    # reuse logic from pslq_snf_mixed_patch_check / verify_exhaustive_failures_snf_pslq
    exh_spec = importlib.util.spec_from_file_location(
        "exh_mod", ROOT / "tools" / "exhaustive_homotopy_check_rationalized_l3.py"
    )
    exh_mod = importlib.util.module_from_spec(exh_spec)
    import sys as _sys

    _sys.modules[exh_spec.name] = exh_mod
    exh_spec.loader.exec_module(exh_mod)
    basis_elem_g1 = exh_mod.basis_elem_g1
    basis_elem_g2 = exh_mod.basis_elem_g2

    # build brackets and fiber triads
    e6_basis = np.load(
        ROOT / "artifacts" / "e6_27rep_basis_export" / "E6_basis_78.npy"
    ).astype(np.complex128)
    toe_mod = toe
    proj = toe_mod.E6Projector(e6_basis)
    all_triads = toe_mod._load_signed_cubic_triads()

    # find bad9 mapping
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
    if not bad9:
        try:
            linfty_mod = _load_module(
                ROOT / "tools" / "build_linfty_firewall_extension.py", "linfty_mod"
            )
            bad9 = linfty_mod._load_bad9()
        except Exception:
            pass

    br_l2 = toe_mod.E8Z3Bracket(
        e6_projector=proj,
        cubic_triads=[t for t in all_triads if tuple(sorted(t[:3])) not in bad9],
        scale_g1g1=1.0,
        scale_g2g2=-1.0 / 6.0,
        scale_e6=1.0,
        scale_sl3=1.0 / 6.0,
    )
    fiber_triads = [t for t in all_triads if tuple(sorted(t[:3])) in bad9]
    br_fibers = [
        toe_mod.E8Z3Bracket(
            e6_projector=proj,
            cubic_triads=[T],
            scale_g1g1=1.0,
            scale_g2g2=-1.0 / 6.0,
            scale_e6=1.0,
            scale_sl3=1.0 / 6.0,
        )
        for T in fiber_triads
    ]

    # basis elements
    x = basis_elem_g1(toe_mod, tuple(a_idx))
    y = basis_elem_g1(toe_mod, tuple(b_idx))
    z = basis_elem_g2(toe_mod, tuple(c_idx))

    J = toe_mod._jacobi(br_l2, x, y, z)
    Jflat = flatten(J)

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

    if len(S_flats) == 0:
        return {"degenerate": True, "note": "S_flats empty"}

    overlaps = [complex(np.vdot(S, Jflat)) for S in S_flats]

    results = {
        "degenerate": False,
        "overlaps": [complex(o) for o in overlaps],
        "pslq_zeta3": None,
    }

    # attempt PSLQ over Q(sqrt(-3)) by PSLQ on real-list: [Re(o_i), -sqrt(3)*Im(o_i)]
    if pslq is None:
        results["pslq_note"] = "sympy.pslq not available"
        return results

    sqrt3 = sqrt(3.0)
    re_list = [float(np.real(o)) for o in overlaps]
    neg_sqrt3_im_list = [float(-sqrt3 * np.imag(o)) for o in overlaps]
    # build sympy high-precision vector
    sp_vec = [N(v, 80) for v in (re_list + neg_sqrt3_im_list)]

    try:
        rel = pslq(sp_vec)
    except Exception:
        rel = None

    if rel:
        k = len(overlaps)
        u = [int(rel[i]) for i in range(k)]
        v = [int(rel[k + i]) for i in range(k)]
        # verify both real and imag equations
        re_check = sum(
            u_i * np.real(o) - v_i * sqrt3 * np.imag(o)
            for u_i, v_i, o in zip(u, v, overlaps)
        )
        im_check = sum(
            u_i * np.imag(o) + v_i * sqrt3 * np.real(o)
            for u_i, v_i, o in zip(u, v, overlaps)
        )
        ok = abs(re_check) < 1e-9 and abs(im_check) < 1e-9
        results["pslq_zeta3"] = {
            "u": u,
            "v": v,
            "re_check": float(re_check),
            "im_check": float(im_check),
            "valid": bool(ok),
        }
    else:
        results["pslq_zeta3"] = None

    return results


def main():
    toe = _load_module(ROOT / "tools" / "toe_e8_z3graded_bracket_jacobi.py", "toe_e8")
    if not EXH.exists():
        raise RuntimeError(
            "exhaustive artifact missing; run tools/exhaustive_homotopy_check_rationalized_l3.py first"
        )
    data = json.loads(EXH.read_text(encoding="utf-8"))
    sectors = data.get("sectors", {})

    out = {"exhaustive_artifact": str(EXH), "results": {}}
    for sname, info in sectors.items():
        if not info.get("passed", True):
            first = info.get("first_fail")
            if not first:
                continue
            a = tuple(first["a"])
            b = tuple(first["b"])
            c = tuple(first["c"])
            print(f"Piloting cyclotomic PSLQ for sector {sname} triple {a},{b},{c}...")
            res = analyze_one(toe, a, b, c)
            out["results"][sname] = {
                "triple": {"a": a, "b": b, "c": c},
                "analysis": res,
            }

    OUT.write_text(json.dumps(out, default=str, indent=2), encoding="utf-8")
    print("Wrote:", OUT)


if __name__ == "__main__":
    main()
