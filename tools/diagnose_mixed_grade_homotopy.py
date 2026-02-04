#!/usr/bin/env python3
"""
Diagnose and fix the mixed-grade homotopy Jacobi residual.

The pure-grade cases (g1,g1,g1) and (g2,g2,g2) are PERFECT (residual ~ 1e-15).
The mixed case has residual ~ 1e3.

Possibilities:
1. l_3 needs different scaling for mixed grades
2. Need l_4 bracket
3. The g0 (e6 ⊕ sl3) sector behaves differently
4. The residual IS the physics (anomaly cancellation)

This script diagnoses which.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from typing import Dict, Set, Tuple

import numpy as np

ROOT = Path(__file__).resolve().parents[1]


def _load_bracket_tool():
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
    return tuple(sorted((int(i), int(j), int(k))))


def _load_bad9() -> Set[Tuple[int, int, int]]:
    path = ROOT / "artifacts" / "firewall_bad_triads_mapping.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    return {_triad_key(*t) for t in data["bad_triangles_Schlafli_e6id"]}


def _max_abs(x: np.ndarray) -> float:
    return float(np.max(np.abs(x))) if x.size else 0.0


def diagnose_mixed_grade_anomaly(tool, proj, all_triads, bad9, e6_basis, rng):
    """
    Break down the mixed-grade anomaly by which combination of grades is involved.
    """
    # Brackets
    affine = [t for t in all_triads if _triad_key(t[0], t[1], t[2]) not in bad9]
    fiber = [t for t in all_triads if _triad_key(t[0], t[1], t[2]) in bad9]

    br_affine = tool.E8Z3Bracket(
        e6_projector=proj,
        cubic_triads=affine,
        scale_g1g1=1.0,
        scale_g2g2=-1.0 / 6.0,
        scale_e6=1.0,
        scale_sl3=1.0 / 6.0,
    )
    br_fiber = tool.E8Z3Bracket(
        e6_projector=proj,
        cubic_triads=fiber,
        scale_g1g1=1.0,
        scale_g2g2=-1.0 / 6.0,
        scale_e6=1.0,
        scale_sl3=1.0 / 6.0,
    )
    br_full = tool.E8Z3Bracket(
        e6_projector=proj,
        cubic_triads=all_triads,
        scale_g1g1=1.0,
        scale_g2g2=-1.0 / 6.0,
        scale_e6=1.0,
        scale_sl3=1.0 / 6.0,
    )

    # Test specific grade combinations
    def rand_g0():
        coeff = rng.integers(-2, 3, size=(78,), dtype=np.int64)
        e6 = np.tensordot(coeff.astype(np.complex128), e6_basis, axes=(0, 0))
        sl3 = rng.integers(-2, 3, size=(3, 3)).astype(np.complex128)
        sl3 = sl3 - np.trace(sl3) / 3 * np.eye(3)
        return tool.E8Z3(
            e6=e6,
            sl3=sl3,
            g1=np.zeros((27, 3), dtype=np.complex128),
            g2=np.zeros((27, 3), dtype=np.complex128),
        )

    def rand_g1():
        return tool.E8Z3(
            e6=np.zeros((27, 27), dtype=np.complex128),
            sl3=np.zeros((3, 3), dtype=np.complex128),
            g1=rng.integers(-2, 3, size=(27, 3)).astype(np.complex128),
            g2=np.zeros((27, 3), dtype=np.complex128),
        )

    def rand_g2():
        return tool.E8Z3(
            e6=np.zeros((27, 27), dtype=np.complex128),
            sl3=np.zeros((3, 3), dtype=np.complex128),
            g1=np.zeros((27, 3), dtype=np.complex128),
            g2=rng.integers(-2, 3, size=(27, 3)).astype(np.complex128),
        )

    # Test cases: all grade combinations
    cases = {
        "g0_g0_g0": (rand_g0, rand_g0, rand_g0),
        "g0_g0_g1": (rand_g0, rand_g0, rand_g1),
        "g0_g0_g2": (rand_g0, rand_g0, rand_g2),
        "g0_g1_g1": (rand_g0, rand_g1, rand_g1),
        "g0_g1_g2": (rand_g0, rand_g1, rand_g2),
        "g0_g2_g2": (rand_g0, rand_g2, rand_g2),
        "g1_g1_g1": (rand_g1, rand_g1, rand_g1),
        "g1_g1_g2": (rand_g1, rand_g1, rand_g2),
        "g1_g2_g2": (rand_g1, rand_g2, rand_g2),
        "g2_g2_g2": (rand_g2, rand_g2, rand_g2),
    }

    results = {}
    trials = 30

    for name, (fx, fy, fz) in cases.items():
        affine_max = 0.0
        full_max = 0.0

        for _ in range(trials):
            x, y, z = fx(), fy(), fz()

            j_affine = tool._jacobi(br_affine, x, y, z)
            j_full = tool._jacobi(br_full, x, y, z)

            mag_aff = max(
                _max_abs(j_affine.e6),
                _max_abs(j_affine.sl3),
                _max_abs(j_affine.g1),
                _max_abs(j_affine.g2),
            )
            mag_full = max(
                _max_abs(j_full.e6),
                _max_abs(j_full.sl3),
                _max_abs(j_full.g1),
                _max_abs(j_full.g2),
            )

            affine_max = max(affine_max, mag_aff)
            full_max = max(full_max, mag_full)

        results[name] = {
            "affine_jacobi_max": affine_max,
            "full_jacobi_max": full_max,
            "is_full_exact": full_max < 1e-10,
            "needs_l3": affine_max > 1e-10,
        }

    return results


def test_g0_invariance(tool, proj, all_triads, bad9, e6_basis, rng):
    """
    Test if g0 (the gauge algebra e6 ⊕ sl3) acts as derivations on both l2 and l3.

    For L∞ coherence, g0 should act as automorphisms.
    """
    affine = [t for t in all_triads if _triad_key(t[0], t[1], t[2]) not in bad9]

    br = tool.E8Z3Bracket(
        e6_projector=proj,
        cubic_triads=affine,
        scale_g1g1=1.0,
        scale_g2g2=-1.0 / 6.0,
        scale_e6=1.0,
        scale_sl3=1.0 / 6.0,
    )

    def rand_g0():
        coeff = rng.integers(-2, 3, size=(78,), dtype=np.int64)
        e6 = np.tensordot(coeff.astype(np.complex128), e6_basis, axes=(0, 0))
        sl3 = rng.integers(-2, 3, size=(3, 3)).astype(np.complex128)
        sl3 = sl3 - np.trace(sl3) / 3 * np.eye(3)
        return tool.E8Z3(
            e6=e6,
            sl3=sl3,
            g1=np.zeros((27, 3), dtype=np.complex128),
            g2=np.zeros((27, 3), dtype=np.complex128),
        )

    def rand_g1():
        return tool.E8Z3(
            e6=np.zeros((27, 27), dtype=np.complex128),
            sl3=np.zeros((3, 3), dtype=np.complex128),
            g1=rng.integers(-2, 3, size=(27, 3)).astype(np.complex128),
            g2=np.zeros((27, 3), dtype=np.complex128),
        )

    # Test: [g0, [g1, g1]] = [[g0,g1], g1] + [g1, [g0,g1]] (derivation property)
    derivation_errors = []
    for _ in range(30):
        a = rand_g0()
        x = rand_g1()
        y = rand_g1()

        lhs = br.bracket(a, br.bracket(x, y))
        rhs = br.bracket(br.bracket(a, x), y) + br.bracket(x, br.bracket(a, y))
        diff = lhs - rhs

        err = max(
            _max_abs(diff.e6), _max_abs(diff.sl3), _max_abs(diff.g1), _max_abs(diff.g2)
        )
        derivation_errors.append(err)

    return {
        "derivation_max_error": max(derivation_errors),
        "derivation_mean_error": np.mean(derivation_errors),
        "is_derivation": max(derivation_errors) < 1e-10,
    }


def main():
    tool = _load_bracket_tool()

    basis_path = ROOT / "artifacts" / "e6_27rep_basis_export" / "E6_basis_78.npy"
    e6_basis = np.load(basis_path).astype(np.complex128)
    proj = tool.E6Projector(e6_basis)

    all_triads = tool._load_signed_cubic_triads()
    bad9 = _load_bad9()

    rng = np.random.default_rng(42)

    print("=" * 60)
    print("DIAGNOSING MIXED-GRADE HOMOTOPY JACOBI")
    print("=" * 60)

    print("\n1. Testing all grade combinations...")
    results = diagnose_mixed_grade_anomaly(tool, proj, all_triads, bad9, e6_basis, rng)

    print("\n| Case | Affine-only Jacobi | Full Jacobi | Needs l_3? |")
    print("|------|-------------------|-------------|------------|")
    for name, data in sorted(results.items()):
        aff = data["affine_jacobi_max"]
        full = data["full_jacobi_max"]
        need = "YES" if data["needs_l3"] else "no"
        print(f"| {name:12} | {aff:12.2e} | {full:12.2e} | {need:10} |")

    print("\n2. Testing g0 derivation property...")
    deriv = test_g0_invariance(tool, proj, all_triads, bad9, e6_basis, rng)
    print(f"   Derivation max error: {deriv['derivation_max_error']:.2e}")
    print(f"   g0 acts as derivations: {deriv['is_derivation']}")

    # Analysis
    print("\n" + "=" * 60)
    print("ANALYSIS")
    print("=" * 60)

    # Count which cases need l_3
    needs_l3 = [k for k, v in results.items() if v["needs_l3"]]
    no_l3 = [k for k, v in results.items() if not v["needs_l3"]]

    print(f"\nCases that need l_3 (affine Jacobi ≠ 0): {len(needs_l3)}")
    for case in needs_l3:
        print(f"  - {case}")

    print(f"\nCases where affine is already exact: {len(no_l3)}")
    for case in no_l3:
        print(f"  - {case}")

    # Key insight
    print("\n" + "=" * 60)
    print("KEY INSIGHT")
    print("=" * 60)

    # Check if g0-only is exact
    g0_cases = [k for k in results if k.startswith("g0_g0")]
    g0_exact = all(results[k]["affine_jacobi_max"] < 1e-10 for k in g0_cases)

    if g0_exact:
        print("\n✓ g0 sector (e6 ⊕ sl3) is a Lie subalgebra (Jacobi exact)")
        print("  This is expected: g0 = gauge algebra, no firewall restriction")

    # Check matter sectors
    matter_cases = ["g1_g1_g1", "g2_g2_g2"]
    matter_need_l3 = [k for k in matter_cases if results[k]["needs_l3"]]

    if matter_need_l3:
        print(f"\n✓ Matter sectors {matter_need_l3} need l_3")
        print("  These involve the cubic triads → firewall affects them")

    # Mixed cases
    mixed = [k for k in results if "g0" in k and ("g1" in k or "g2" in k)]
    mixed_need = [k for k in mixed if results[k]["needs_l3"]]

    if mixed_need:
        print(f"\n! Mixed gauge-matter cases {mixed_need} need l_3")
        print("  The g0 action on g1/g2 involves the cubic → affected by firewall")


if __name__ == "__main__":
    main()
