#!/usr/bin/env python3
"""
Vogel universality (universal Lie algebra) checks and W(3,3) numerology.

This script is *not* part of the canonical pillar test suite; it is a compact,
computational companion to the recent literature on Vogel's universal Lie
algebra formalism and the classification of Jacobi identities.

Key references (open access / arXiv):
  - A. Morozov, A. Sleptsov, "Vogel’s universality and the classification
    problem for Jacobi identities", Eur. Phys. J. C 85, 1233 (2025).
    DOI: 10.1140/epjc/s10052-025-14943-y
  - L. Bishler, A. Mironov, "Refined Vogel universality and Macdonald
    dimensions", arXiv:2504.13831 (2025).
  - L. Bishler, A. Mironov, A. Morozov, "Macdonald deformation of the Vogel
    universality and hyperpolynomials", arXiv:2505.16569 (2025).

Run:
  python scripts/w33_vogel_universality.py
"""

from __future__ import annotations

import sys
from fractions import Fraction
from pathlib import Path

# Ensure we can import sibling modules from scripts/ when executed as a file.
SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from w33_homology import build_clique_complex, build_w33, compute_homology


def class_order_from_label(name: str) -> int:
    digits = ""
    for ch in name.strip():
        if ch.isdigit():
            digits += ch
        else:
            break
    return int(digits) if digits else 0


# ---------------------------------------------------------------------------
# Vogel / Dynkin locus polynomials (Morozov–Sleptsov 2025, eqs. (11)–(16))
# ---------------------------------------------------------------------------


def P_sl(alpha, beta, gamma):
    return (alpha + beta) * (beta + gamma) * (alpha + gamma)


def P_osp(alpha, beta, gamma):
    return (
        (alpha + 2 * beta)
        * (2 * alpha + beta)
        * (beta + 2 * gamma)
        * (2 * beta + gamma)
        * (alpha + 2 * gamma)
        * (2 * alpha + gamma)
    )


def P_exc(alpha, beta, gamma):
    return (
        (alpha - 2 * beta - 2 * gamma)
        * (beta - 2 * alpha - 2 * gamma)
        * (gamma - 2 * alpha - 2 * beta)
    )


def omega_factor(alpha, beta, gamma):
    # extra factor raising degrees to P_15 / P_22 (eq. (15))
    return (
        (alpha + beta + 2 * gamma)
        * (beta + gamma + 2 * alpha)
        * (gamma + alpha + 2 * beta)
    )


def P_Lie(alpha, beta, gamma):
    return (
        P_sl(alpha, beta, gamma) * P_osp(alpha, beta, gamma) * P_exc(alpha, beta, gamma)
    )


def P_G2(alpha, beta, gamma):
    t = alpha + beta + gamma
    return 18 * (alpha * alpha + beta * beta + gamma * gamma) - 25 * (t * t)


def P_F4(alpha, beta, gamma):
    t = alpha + beta + gamma
    return 81 * (alpha * alpha + beta * beta + gamma * gamma) - 65 * (t * t)


def P_E6(alpha, beta, gamma):
    t = alpha + beta + gamma
    return 18 * (alpha * alpha + beta * beta + gamma * gamma) - 13 * (t * t)


def P_E7(alpha, beta, gamma):
    t = alpha + beta + gamma
    return 81 * (alpha * alpha + beta * beta + gamma * gamma) - 53 * (t * t)


def P_E8(alpha, beta, gamma):
    t = alpha + beta + gamma
    return 225 * (alpha * alpha + beta * beta + gamma * gamma) - 137 * (t * t)


def P_Lie_refined(alpha, beta, gamma):
    # \mathcal{P}_{Lie} from eq. (14): replaces P_exc with algebra-specific loci.
    return (
        P_sl(alpha, beta, gamma)
        * P_osp(alpha, beta, gamma)
        * P_G2(alpha, beta, gamma)
        * P_F4(alpha, beta, gamma)
        * P_E6(alpha, beta, gamma)
        * P_E7(alpha, beta, gamma)
        * P_E8(alpha, beta, gamma)
    )


def dim_adj(alpha, beta, gamma):
    """Universal adjoint dimension formula (standard Vogel normalization)."""
    t = alpha + beta + gamma
    return (alpha - 2 * t) * (beta - 2 * t) * (gamma - 2 * t) / (alpha * beta * gamma)


def vogel_parameters() -> dict[str, tuple[object, object, object]]:
    """Minimal Vogel parameter table (common normalization)."""
    return {
        # exceptional (ordered as in many Vogel tables)
        "G2": (Fraction(-2), Fraction(10, 3), Fraction(8, 3)),
        "F4": (-2, 5, 6),
        "E6": (-2, 6, 8),
        "E7": (-2, 8, 12),
        "E8": (-2, 12, 20),
    }


def analyze_vogel_universality() -> dict[str, object]:
    params = vogel_parameters()

    dims_expected = {"G2": 14, "F4": 52, "E6": 78, "E7": 133, "E8": 248}
    dims = {}
    loci = {}
    refined = {}

    for name, (a, b, c) in params.items():
        dims[name] = float(dim_adj(a, b, c)) if name != "G2" else int(dim_adj(a, b, c))
        loci[name] = {
            "P_sl": P_sl(a, b, c),
            "P_osp": P_osp(a, b, c),
            "P_exc": P_exc(a, b, c),
            "P_Lie": P_Lie(a, b, c),
            "omega": omega_factor(a, b, c),
        }
        refined[name] = {
            "P_G2": P_G2(a, b, c),
            "P_F4": P_F4(a, b, c),
            "P_E6": P_E6(a, b, c),
            "P_E7": P_E7(a, b, c),
            "P_E8": P_E8(a, b, c),
            "P_Lie_refined": P_Lie_refined(a, b, c),
        }

        # sanity: adjoint dims
        exp = dims_expected[name]
        got = dims[name]
        if isinstance(got, float):
            assert abs(got - exp) < 1e-9
        else:
            assert int(got) == exp

        # Dynkin locus should vanish
        assert loci[name]["P_Lie"] == 0
        # The algebra-specific polynomial should vanish at that algebra
        assert refined[name][f"P_{name}"] == 0

    # W33 invariants
    n, vertices, adj, edges = build_w33()
    simplices = build_clique_complex(n, adj)
    hom = compute_homology(simplices)
    b1 = int(hom["betti_numbers"][1])

    # "81" is a key coefficient in (13) for F4 and E7.
    vogel_coeff_81 = {"F4": 81, "E7": 81}

    return {
        "vogel": {
            "params": {k: [str(x) for x in v] for k, v in params.items()},
            "dims": dims,
            "expected_dims": dims_expected,
            "loci": loci,
            "refined": refined,
            "coeff_81_algebras": sorted(vogel_coeff_81.keys()),
        },
        "w33": {
            "n_vertices": n,
            "n_edges": len(edges),
            "b1": b1,
            "b1_equals_81": b1 == 81,
        },
    }


def main() -> dict[str, object]:
    out = analyze_vogel_universality()

    print("=" * 78)
    print("VOGEL UNIVERSALITY (2025+) — COMPUTATIONAL CHECKS")
    print("=" * 78)

    v = out["vogel"]
    w = out["w33"]

    print("\n§1. Universal adjoint dimensions")
    for name in ["G2", "F4", "E6", "E7", "E8"]:
        got = v["dims"][name]
        exp = v["expected_dims"][name]
        print(f"  {name:>2}: dim_adj = {got} (expected {exp})")

    print("\n§2. Dynkin locus polynomials (vanish on simple Lie algebras)")
    for name in ["G2", "F4", "E6", "E7", "E8"]:
        p = v["loci"][name]["P_Lie"]
        print(f"  {name:>2}: P_Lie = {p}")

    print("\n§3. Algebra-specific refined loci (eq. (13))")
    for name in ["G2", "F4", "E6", "E7", "E8"]:
        p = v["refined"][name][f"P_{name}"]
        print(f"  {name:>2}: P_{name} = {p}")

    print("\n§4. W(3,3) invariant touching Vogel coefficient 81")
    print(f"  b1(W33) = {w['b1']}  (expected 81)")
    print(f"  81 appears as coefficient in (13) for: {v['coeff_81_algebras']}")
    assert w["b1_equals_81"] is True

    print("\nALL CHECKS PASSED ✓")
    return out


if __name__ == "__main__":
    main()
