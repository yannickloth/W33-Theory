#!/usr/bin/env python3
"""
Diagnostic: where does the Jacobi failure live when we apply the firewall as triad deletion?

We use the Z3-graded E8 bracket construction in:
  - tools/toe_e8_z3graded_bracket_jacobi.py

and delete the 9 forbidden (constant-u / fiber) cubic triads from:
  - artifacts/firewall_bad_triads_mapping.json

Outputs:
  - artifacts/e8_z3graded_firewall_jacobi_components.json
  - artifacts/e8_z3graded_firewall_jacobi_components.md
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

ROOT = Path(__file__).resolve().parents[1]

OUT_JSON = ROOT / "artifacts" / "e8_z3graded_firewall_jacobi_components.json"
OUT_MD = ROOT / "artifacts" / "e8_z3graded_firewall_jacobi_components.md"


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


def _load_bad9() -> set[Tuple[int, int, int]]:
    fw = json.loads(
        (ROOT / "artifacts" / "firewall_bad_triads_mapping.json").read_text(
            encoding="utf-8"
        )
    )
    bad = {_triad_key(*t) for t in fw["bad_triangles_Schlafli_e6id"]}
    if len(bad) != 9:
        raise RuntimeError(f"Expected 9 bad triads, got {len(bad)}")
    return bad


def _max_abs(x: np.ndarray) -> float:
    return float(np.max(np.abs(x))) if x.size else 0.0


if __name__ == "__main__":
    tool = _load_tool()

    basis_path = ROOT / "artifacts" / "e6_27rep_basis_export" / "E6_basis_78.npy"
    e6_basis = np.load(basis_path).astype(np.complex128)
    proj = tool.E6Projector(e6_basis)

    triads_all = tool._load_signed_cubic_triads()
    bad9 = _load_bad9()
    triads_fw = [t for t in triads_all if _triad_key(t[0], t[1], t[2]) not in bad9]

    scale = {
        "scale_g1g1": 1.0,
        "scale_g2g2": -1.0 / 6.0,
        "scale_e6": 1.0,
        "scale_sl3": 1.0 / 6.0,
    }

    br = tool.E8Z3Bracket(
        e6_projector=proj,
        cubic_triads=triads_fw,
        scale_g1g1=scale["scale_g1g1"],
        scale_g2g2=scale["scale_g2g2"],
        scale_e6=scale["scale_e6"],
        scale_sl3=scale["scale_sl3"],
    )

    rng = np.random.default_rng(0)

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
        ("g1_g1_g1", (rand_g1, rand_g1, rand_g1)),
        ("g2_g2_g2", (rand_g2, rand_g2, rand_g2)),
        ("g1_g1_g2", (rand_g1, rand_g1, rand_g2)),
        ("g1_g2_g2", (rand_g1, rand_g2, rand_g2)),
        ("mixed_all", (rand_all, rand_all, rand_all)),
    ]

    trials = 80
    results: Dict[str, Dict[str, object]] = {}
    for name, (fx, fy, fz) in cases:
        comp_max = {"e6": 0.0, "sl3": 0.0, "g1": 0.0, "g2": 0.0}
        comp_mean = {"e6": 0.0, "sl3": 0.0, "g1": 0.0, "g2": 0.0}
        dominant = {"e6": 0, "sl3": 0, "g1": 0, "g2": 0}
        max_total = 0.0

        for _ in range(trials):
            j = tool._jacobi(br, fx(), fy(), fz())
            mags = {
                "e6": _max_abs(j.e6),
                "sl3": _max_abs(j.sl3),
                "g1": _max_abs(j.g1),
                "g2": _max_abs(j.g2),
            }
            for k, v in mags.items():
                comp_mean[k] += v
                if v > comp_max[k]:
                    comp_max[k] = v
            dom = max(mags.items(), key=lambda kv: kv[1])[0]
            dominant[dom] += 1
            max_total = max(max_total, max(mags.values()))

        for k in comp_mean:
            comp_mean[k] /= trials

        results[name] = {
            "trials": trials,
            "max_total": max_total,
            "component_max": comp_max,
            "component_mean": comp_mean,
            "dominant_component_hist": dominant,
        }

    out = {
        "status": "ok",
        "triads": {
            "total": len(triads_all),
            "firewall_bad": len(bad9),
            "remaining": len(triads_fw),
        },
        "scales": scale,
        "jacobi_component_stats": results,
        "note": "Magnitudes are max-abs per component of the Jacobiator (E8Z3 element).",
    }
    OUT_JSON.write_text(json.dumps(out, indent=2, sort_keys=True), encoding="utf-8")

    md: List[str] = []
    md.append("# Firewall-filtered Jacobiator: component breakdown (Z3-graded build)")
    md.append("")
    md.append(f"- trials per case: `{trials}`")
    md.append(
        f"- triads: `{len(triads_all)}` → `{len(triads_fw)}` (firewall deletes `{len(bad9)}`)"
    )
    md.append("")
    md.append("| case | max total | dom e6 | dom sl3 | dom g1 | dom g2 |")
    md.append("|---|---:|---:|---:|---:|---:|")
    for name in results:
        r = results[name]
        h = r["dominant_component_hist"]
        md.append(
            f"| `{name}` | {r['max_total']:.3e} | {h['e6']} | {h['sl3']} | {h['g1']} | {h['g2']} |"
        )
    md.append("")
    md.append("## Per-case maxima (max-abs)")
    for name in results:
        r = results[name]
        md.append(f"- `{name}`: {r['component_max']}")
    md.append("")
    md.append(f"Wrote `{OUT_JSON}`")
    md.append(f"Wrote `{OUT_MD}`")
    OUT_MD.write_text("\n".join(md) + "\n", encoding="utf-8")

    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")
