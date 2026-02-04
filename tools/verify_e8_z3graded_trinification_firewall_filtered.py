#!/usr/bin/env python3
"""
Certificate: applying the W33 firewall as a hard deletion of the 9 "fiber" cubic triads breaks Jacobi
in the Z3-graded (e6 ⊕ sl3) ⊕ (27⊗3) ⊕ (27*⊗3*) E8 build.

This complements the discrete-root firewall Jacobi probes by testing the *representation-theoretic*
trinification bracket built in `tools/toe_e8_z3graded_bracket_jacobi.py`.

Inputs:
  - tools/toe_e8_z3graded_bracket_jacobi.py
  - artifacts/e6_27rep_basis_export/E6_basis_78.npy
  - artifacts/canonical_su3_gauge_and_cubic.json
  - artifacts/firewall_bad_triads_mapping.json            (9 forbidden triads in E6-id labels)

Outputs:
  - artifacts/verify_e8_z3graded_trinification_firewall_filtered.json
  - artifacts/verify_e8_z3graded_trinification_firewall_filtered.md
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from typing import Dict, List, Sequence, Tuple

import numpy as np

ROOT = Path(__file__).resolve().parents[1]

OUT_JSON = (
    ROOT / "artifacts" / "verify_e8_z3graded_trinification_firewall_filtered.json"
)
OUT_MD = ROOT / "artifacts" / "verify_e8_z3graded_trinification_firewall_filtered.md"


def _load_tool() -> object:
    path = ROOT / "tools" / "toe_e8_z3graded_bracket_jacobi.py"
    spec = importlib.util.spec_from_file_location(
        "toe_e8_z3graded_bracket_jacobi", path
    )
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def _triad_key(i: int, j: int, k: int) -> Tuple[int, int, int]:
    a, b, c = sorted((int(i), int(j), int(k)))
    return (a, b, c)


def _load_firewall_bad_triads() -> set[Tuple[int, int, int]]:
    fw = json.loads(
        (ROOT / "artifacts" / "firewall_bad_triads_mapping.json").read_text(
            encoding="utf-8"
        )
    )
    bad = {_triad_key(*t) for t in fw["bad_triangles_Schlafli_e6id"]}
    if len(bad) != 9:
        raise RuntimeError(f"Expected 9 bad triads, got {len(bad)}")
    return bad


def _run_jacobi_battery(
    tool: object, br: object, *, trials: int, seed: int
) -> Dict[str, Dict[str, float]]:
    rng = np.random.default_rng(seed)

    def rand_g0():
        return tool._random_element(
            rng,
            e6_basis,
            scale0=2,
            scale1=0,
            scale2=0,
            include_g1=False,
            include_g2=False,
        )

    def rand_g1():
        return tool._random_element(
            rng,
            e6_basis,
            scale0=0,
            scale1=2,
            scale2=0,
            include_g0=False,
            include_g2=False,
        )

    def rand_g2():
        return tool._random_element(
            rng,
            e6_basis,
            scale0=0,
            scale1=0,
            scale2=2,
            include_g0=False,
            include_g1=False,
        )

    def rand_all():
        return tool._random_element(rng, e6_basis, scale0=2, scale1=2, scale2=2)

    cases = [
        ("g0_g0_g0", (rand_g0, rand_g0, rand_g0)),
        ("g1_g1_g1", (rand_g1, rand_g1, rand_g1)),
        ("g2_g2_g2", (rand_g2, rand_g2, rand_g2)),
        ("g1_g1_g2", (rand_g1, rand_g1, rand_g2)),
        ("g1_g2_g2", (rand_g1, rand_g2, rand_g2)),
        ("mixed_all", (rand_all, rand_all, rand_all)),
    ]

    out: Dict[str, Dict[str, float]] = {}
    for name, (fx, fy, fz) in cases:
        max_res = 0.0
        mean_res = 0.0
        for _ in range(trials):
            j = tool._jacobi(br, fx(), fy(), fz())
            r = float(tool._elt_norm(j))
            mean_res += r
            if r > max_res:
                max_res = r
        out[name] = {
            "trials": float(trials),
            "max_residual": float(max_res),
            "mean_residual": float(mean_res / trials),
        }
    return out


if __name__ == "__main__":
    tool = _load_tool()

    basis_path = ROOT / "artifacts" / "e6_27rep_basis_export" / "E6_basis_78.npy"
    if not basis_path.exists():
        raise RuntimeError(
            "Missing artifacts/e6_27rep_basis_export/E6_basis_78.npy. "
            "Run: python3 tools/build_e6_27rep_minuscule.py --export-basis78"
        )
    e6_basis = np.load(basis_path).astype(np.complex128)
    proj = tool.E6Projector(e6_basis)

    triads_all: Sequence[Tuple[int, int, int, int]] = tool._load_signed_cubic_triads()
    bad9 = _load_firewall_bad_triads()
    triads_filtered: List[Tuple[int, int, int, int]] = [
        t for t in triads_all if _triad_key(t[0], t[1], t[2]) not in bad9
    ]
    if len(triads_filtered) != 36:
        raise RuntimeError(f"Expected 36 remaining triads, got {len(triads_filtered)}")

    # Locked scales from the unfiltered certificate.
    scale = {
        "scale_g1g1": 1.0,
        "scale_g2g2": -1.0 / 6.0,
        "scale_e6": 1.0,
        "scale_sl3": 1.0 / 6.0,
    }

    br_full = tool.E8Z3Bracket(
        e6_projector=proj,
        cubic_triads=triads_all,
        scale_g1g1=scale["scale_g1g1"],
        scale_g2g2=scale["scale_g2g2"],
        scale_e6=scale["scale_e6"],
        scale_sl3=scale["scale_sl3"],
    )
    br_fw = tool.E8Z3Bracket(
        e6_projector=proj,
        cubic_triads=triads_filtered,
        scale_g1g1=scale["scale_g1g1"],
        scale_g2g2=scale["scale_g2g2"],
        scale_e6=scale["scale_e6"],
        scale_sl3=scale["scale_sl3"],
    )

    # This is moderately expensive (each Jacobi evaluation does several 27x27/27x3 ops).
    # Keep the default trial count modest so the certificate runs quickly in CI/WSL.
    trials = 200
    jacobi_full = _run_jacobi_battery(tool, br_full, trials=trials, seed=0)
    jacobi_fw = _run_jacobi_battery(tool, br_fw, trials=trials, seed=0)

    out = {
        "status": "ok",
        "triads": {
            "total": int(len(triads_all)),
            "firewall_bad": int(len(bad9)),
            "remaining": int(len(triads_filtered)),
            "bad_triads": [list(t) for t in sorted(bad9)],
        },
        "scales": scale,
        "jacobi": {"unfiltered": jacobi_full, "firewall_filtered": jacobi_fw},
        "notes": [
            "Unfiltered bracket is a Z3-graded E8 construction and should satisfy Jacobi (numerically ~0).",
            "Firewall filtering here is implemented as deleting the 9 constant-u (fiber) cubic triads.",
        ],
    }

    OUT_JSON.write_text(json.dumps(out, indent=2, sort_keys=True), encoding="utf-8")

    md: List[str] = []
    md.append("# Z3-graded E8 Jacobi under firewall triad deletion")
    md.append("")
    md.append(f"- Trials per case: `{trials}`")
    md.append(
        f"- Cubic triads: `{out['triads']['total']}` → remaining `{out['triads']['remaining']}`"
    )
    md.append("")
    md.append("## Jacobi residuals (max / mean)")
    md.append("")
    md.append(
        "| case | unfiltered max | unfiltered mean | firewall max | firewall mean |"
    )
    md.append("|---|---:|---:|---:|---:|")
    for case in out["jacobi"]["unfiltered"].keys():
        a = out["jacobi"]["unfiltered"][case]
        b = out["jacobi"]["firewall_filtered"][case]
        md.append(
            f"| `{case}` | {a['max_residual']:.3e} | {a['mean_residual']:.3e} | {b['max_residual']:.3e} | {b['mean_residual']:.3e} |"
        )
    md.append("")
    md.append(f"Wrote `{OUT_JSON}`")
    md.append(f"Wrote `{OUT_MD}`")
    OUT_MD.write_text("\n".join(md) + "\n", encoding="utf-8")

    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")
