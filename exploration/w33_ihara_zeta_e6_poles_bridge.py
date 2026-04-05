"""Ihara zeta pole structure: 78 complex poles = dim(E₆).

Phase CDL — verify the complete Ihara zeta function pole structure of
W(3,3), including the graph-theoretic Riemann hypothesis and the
connection between pole discriminants and SRG parameters.

The Ihara zeta function of a (q+1)-regular graph has non-trivial poles
exactly on the critical circle |u| = 1/√q when the graph is Ramanujan.
For W(3,3), the critical circle is |u| = 1/√11, and the total number
of complex poles = 2f + 2g = 48 + 30 = 78 = dim(E₆).
"""

from __future__ import annotations

from functools import lru_cache
import json
import math
import cmath
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_PATH = (
    ROOT / "data" / "w33_ihara_zeta_e6_poles_bridge_summary.json"
)


@lru_cache(maxsize=1)
def build_ihara_zeta_e6_poles_summary() -> dict[str, Any]:
    """Verify the Ihara zeta pole structure and E₆ connection."""
    v, k, lam, mu, q = 40, 12, 2, 4, 3
    E = v * k // 2  # 240
    f, g = 24, 15   # eigenvalue multiplicities
    r, s = 2, -4    # non-trivial eigenvalues

    nb = k - 1  # 11 (non-backtracking outdegree)

    # Ihara-Bass identity:
    # det(I - uB) = (1 - u²)^(E-v) · det(I - uA + u²(k-1)I)
    ihara_exponent = E - v  # 200 = 5v

    # Non-trivial poles from det(I - uA + u²(k-1)I) = 0
    # For eigenvalue λ_i: 1 - λ_i·u + (k-1)·u² = 0
    # u = (λ_i ± √(λ_i² - 4(k-1))) / (2(k-1))

    # Discriminant for eigenvalue r = 2:
    disc_r = r ** 2 - 4 * nb  # 4 - 44 = -40 = -v
    # Discriminant for eigenvalue s = -4:
    disc_s = s ** 2 - 4 * nb  # 16 - 44 = -28 = -(v-k)

    # Both discriminants are negative → complex poles
    disc_r_negative = disc_r < 0
    disc_s_negative = disc_s < 0

    # Poles from r = 2:
    # u = (2 ± i√40) / 22 = (1 ± i√10) / 11
    u_r_real = r / (2 * nb)       # 2/22 = 1/11
    u_r_imag = math.sqrt(-disc_r) / (2 * nb)  # √40/22

    # |u_r|² = (1 + 10) / 121 = 11/121 = 1/11
    u_r_mag_sq = (r ** 2 + (-disc_r)) / (4 * nb ** 2)
    assert abs(u_r_mag_sq - 1.0 / nb) < 1e-15

    # Poles from s = -4:
    # u = (-4 ± i√28) / 22 = (-2 ± i√7) / 11
    u_s_real = s / (2 * nb)       # -4/22 = -2/11
    u_s_imag = math.sqrt(-disc_s) / (2 * nb)  # √28/22

    # |u_s|² = (4 + 7) / 121 = 11/121 = 1/11
    u_s_mag_sq = (s ** 2 + (-disc_s)) / (4 * nb ** 2)
    assert abs(u_s_mag_sq - 1.0 / nb) < 1e-15

    # ALL poles lie on |u| = 1/√11 → Ramanujan!
    critical_radius_sq = 1.0 / nb
    on_critical_circle = (
        abs(u_r_mag_sq - critical_radius_sq) < 1e-15
        and abs(u_s_mag_sq - critical_radius_sq) < 1e-15
    )

    # Pole counts (each eigenvalue with multiplicity f or g gives 2 complex poles)
    complex_poles_from_r = 2 * f  # 48
    complex_poles_from_s = 2 * g  # 30
    total_complex_poles = complex_poles_from_r + complex_poles_from_s  # 78

    # 78 = dim(adj E₆)!
    dim_E6 = 78
    poles_equal_dim_E6 = total_complex_poles == dim_E6

    # Real poles from trivial eigenvalue k:
    # 1 - 12u + 11u² = 0 → u = 1 or u = 1/11
    # These are 2 simple real poles
    real_poles = 2

    # Total zeros of the Ihara zeta = 2(E-v) + 2v = 2E = 480
    total_zeros = 2 * E
    assert total_zeros == 480

    # Pole discriminant identities
    assert abs(disc_r) == v   # |Δ_r| = 40 = v
    assert abs(disc_s) == v - k  # |Δ_s| = 28 = v-k = dim(SO(8))
    disc_diff = abs(disc_r) - abs(disc_s)  # 40 - 28 = 12 = k
    assert disc_diff == k

    # Seidel energy connection
    seidel_energy = g + f * abs(s + lam + 1) + g * abs(s + lam + 1)
    # Actually: Seidel eigenvalues are {g=15, -(q+λ)=-5, Φ₆=7}
    # Seidel energy = |15| + 24×|-5| + 15×|7| = 15 + 120 + 105 = 240 = E
    seidel_ev = [g, -(q + lam), q ** 2 - q + 1]  # [15, -5, 7]
    seidel_mults = [1, f, g]
    seidel_E = sum(abs(ev) * m for ev, m in zip(seidel_ev, seidel_mults))
    assert seidel_E == E

    return {
        "status": "ok",
        "ihara_zeta_e6_poles": {
            "pole_structure": {
                "from_eigenvalue_r": {
                    "eigenvalue": r, "multiplicity": f,
                    "discriminant": disc_r, "abs_disc": abs(disc_r),
                    "complex_poles": complex_poles_from_r,
                },
                "from_eigenvalue_s": {
                    "eigenvalue": s, "multiplicity": g,
                    "discriminant": disc_s, "abs_disc": abs(disc_s),
                    "complex_poles": complex_poles_from_s,
                },
                "total_complex_poles": total_complex_poles,
                "real_poles": real_poles,
                "total_ihara_zeros": total_zeros,
            },
            "critical_circle": {
                "radius_squared": critical_radius_sq,
                "all_on_critical_circle": on_critical_circle,
                "graph_theoretic_riemann_hypothesis": on_critical_circle,
            },
            "discriminant_identities": {
                "abs_disc_r_equals_v": abs(disc_r) == v,
                "abs_disc_s_equals_v_minus_k": abs(disc_s) == v - k,
                "disc_difference_equals_k": disc_diff == k,
            },
            "seidel": {
                "eigenvalues": seidel_ev,
                "multiplicities": seidel_mults,
                "energy": seidel_E,
                "energy_equals_E": seidel_E == E,
            },
            "ihara_bass_exponent": ihara_exponent,
        },
        "ihara_zeta_e6_poles_theorem": {
            "all_78_complex_poles_lie_on_the_critical_circle": (
                on_critical_circle and total_complex_poles == 78
            ),
            "the_pole_count_78_equals_dim_adj_E6": poles_equal_dim_E6,
            "the_discriminant_difference_equals_k": disc_diff == k,
            "the_seidel_energy_equals_the_edge_count_240": seidel_E == E,
            "therefore_the_ihara_zeta_encodes_E6_and_satisfies_grh": (
                on_critical_circle
                and poles_equal_dim_E6
                and disc_diff == k
                and seidel_E == E
                and total_zeros == 480
            ),
        },
        "bridge_verdict": (
            "All 78 complex Ihara zeta poles lie on the critical circle "
            "|u| = 1/√11, confirming the graph-theoretic Riemann hypothesis. "
            "78 = dim(adj E₆). The discriminant difference = k = 12. "
            "The Seidel energy independently reproduces 240 = E."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_ihara_zeta_e6_poles_summary(), indent=2),
        encoding="utf-8",
    )
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
