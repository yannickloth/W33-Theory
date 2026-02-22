#!/usr/bin/env python3
"""
Final verification: the gauge algebra g₀ acts as derivations on FULL E8
but NOT on the firewall-filtered bracket.

This confirms that the firewall BREAKS gauge covariance, and the
9 fiber triads RESTORE it.

Derivation property: [a, [x, y]] = [[a,x], y] + [x, [a,y]]

If this holds for all a ∈ g₀ and x,y ∈ g₁ ⊕ g₂, then g₀ acts as derivations.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from typing import Set, Tuple

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


def test_derivation_property(tool, proj, triads, e6_basis, rng, trials=50, label=""):
    """
    Test: [a, [x, y]] = [[a,x], y] + [x, [a,y]] for a ∈ g₀, x,y ∈ g₁
    """
    br = tool.E8Z3Bracket(
        e6_projector=proj,
        cubic_triads=triads,
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

    errors = []
    for _ in range(trials):
        a = rand_g0()
        x = rand_g1()
        y = rand_g1()

        # LHS: [a, [x, y]]
        lhs = br.bracket(a, br.bracket(x, y))

        # RHS: [[a,x], y] + [x, [a,y]]
        rhs = br.bracket(br.bracket(a, x), y) + br.bracket(x, br.bracket(a, y))

        diff = lhs - rhs
        err = max(
            _max_abs(diff.e6), _max_abs(diff.sl3), _max_abs(diff.g1), _max_abs(diff.g2)
        )
        errors.append(err)

    return {
        "label": label,
        "triads": len(triads),
        "max_error": max(errors),
        "mean_error": np.mean(errors),
        "is_derivation": max(errors) < 1e-10,
    }


def main():
    tool = _load_bracket_tool()

    basis_path = ROOT / "artifacts" / "e6_27rep_basis_export" / "E6_basis_78.npy"
    e6_basis = np.load(basis_path).astype(np.complex128)
    proj = tool.E6Projector(e6_basis)

    all_triads = tool._load_signed_cubic_triads()
    bad9 = _load_bad9()
    affine_triads = [t for t in all_triads if _triad_key(t[0], t[1], t[2]) not in bad9]
    fiber_triads = [t for t in all_triads if _triad_key(t[0], t[1], t[2]) in bad9]

    rng = np.random.default_rng(42)

    print("=" * 70)
    print("DERIVATION PROPERTY TEST: g₀ acts on g₁ by derivations?")
    print("=" * 70)
    print("\nDerivation property: [a, [x, y]] = [[a,x], y] + [x, [a,y]]")
    print("for a ∈ g₀ = e₆ ⊕ sl₃ and x,y ∈ g₁ = 27⊗3")
    print()

    # Test 1: Full 45 triads
    result_full = test_derivation_property(
        tool, proj, all_triads, e6_basis, rng, trials=50, label="Full E8 (45 triads)"
    )

    # Test 2: Firewall-filtered (36 triads)
    result_affine = test_derivation_property(
        tool,
        proj,
        affine_triads,
        e6_basis,
        rng,
        trials=50,
        label="Firewall-filtered (36 triads)",
    )

    # Test 3: Fiber-only (9 triads)
    result_fiber = test_derivation_property(
        tool,
        proj,
        fiber_triads,
        e6_basis,
        rng,
        trials=50,
        label="Fiber-only (9 triads)",
    )

    print("| Configuration | Triads | Max Error | Is Derivation? |")
    print("|---------------|--------|-----------|----------------|")
    for r in [result_full, result_affine, result_fiber]:
        status = "✅ YES" if r["is_derivation"] else "❌ NO"
        print(
            f"| {r['label']:30} | {r['triads']:6} | {r['max_error']:.2e} | {status:14} |"
        )

    print("\n" + "=" * 70)
    print("INTERPRETATION")
    print("=" * 70)

    if result_full["is_derivation"] and not result_affine["is_derivation"]:
        print(
            """
✓ CONFIRMED: The full E8 (45 triads) has g₀ acting as derivations.
✗ CONFIRMED: The firewall-filtered bracket (36 triads) does NOT.

This means:
  - The firewall BREAKS gauge covariance (g₀ no longer acts as derivations)
  - The 9 fiber triads RESTORE gauge covariance
  - Confinement (fiber triads) is REQUIRED for gauge invariance

Physical interpretation:
  - You cannot have perturbative QCD without confinement
  - The confined sector (9 fibers) is not optional
  - Gauge + confinement form an irreducible package
"""
        )
    elif result_full["is_derivation"] and result_affine["is_derivation"]:
        print(
            """
Both brackets have g₀ acting as derivations.
The derivation property is preserved even without the fiber triads.
(This would mean the firewall is compatible with gauge covariance.)
"""
        )
    else:
        print(
            f"""
Unexpected result:
  Full E8: derivation = {result_full['is_derivation']}
  Affine: derivation = {result_affine['is_derivation']}
"""
        )


if __name__ == "__main__":
    main()
