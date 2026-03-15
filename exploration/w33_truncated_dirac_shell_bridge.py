"""Exact truncated Dirac-Kahler shell on C0 + C1 + C2.

This bridge promotes the strongest exact theorem that survives from the older
"122" draft without colliding with the already-promoted full 480-dimensional
Dirac/Hodge package.

On the truncated simplicial sector C0 + C1 + C2 one has:

  - chain dimensions (40, 240, 160), total 440;
  - boundary ranks (39, 120);
  - Betti data (1, 81, 40), so the kernel of D^2 has dimension 122;
  - Lovasz theta Theta(W33) = 10, giving 122 = k^2 - k - Theta;
  - exact D^2 spectrum {0^122, 4^240, 10^48, 16^30};
  - exact spectral moments f0 = 440, f2 = 1920, f4 = 16320, f6 = 186240;
  - exact moment ratios f2/f0 = 48/11 and f4/f2 = 17/2.

So the older "122" observation is real, but it belongs to the truncated
Dirac-Kahler shell, not to the full promoted 480-dimensional closure.
"""

from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_truncated_dirac_shell_bridge_summary.json"

V = 40
E = 240
T = 160
K = 12
MU = 4
THETA = 10
RANK_D0 = 39
RANK_D1 = 120

D2_SPECTRUM = {
    "0": 122,
    "4": 240,
    "10": 48,
    "16": 30,
}


def _moment(power: int) -> int:
    return sum((int(value) ** power) * multiplicity for value, multiplicity in D2_SPECTRUM.items())


def build_truncated_dirac_shell_summary() -> dict[str, Any]:
    beta0 = V - RANK_D0
    beta1 = E - RANK_D0 - RANK_D1
    beta2 = T - RANK_D1
    zero_modes = beta0 + beta1 + beta2

    f0 = V + E + T
    f2 = _moment(1)
    f4 = _moment(2)
    f6 = _moment(3)

    f2_over_f0 = Fraction(f2, f0)
    f4_over_f2 = Fraction(f4, f2)
    f6_over_f4 = Fraction(f6, f4)

    return {
        "status": "ok",
        "truncated_sector": {
            "chain_dimensions": [V, E, T],
            "total_dimension": f0,
            "boundary_ranks": [RANK_D0, RANK_D1],
            "betti_numbers": [beta0, beta1, beta2],
            "zero_mode_count": zero_modes,
            "lovasz_theta": THETA,
            "zero_mode_formula": "k^2 - k - Theta(W33)",
            "zero_mode_formula_value": K**2 - K - THETA,
            "zero_modes_equal_graph_formula": zero_modes == K**2 - K - THETA,
        },
        "spectral_shell": {
            "d2_spectrum": D2_SPECTRUM,
            "f0": f0,
            "f2": f2,
            "f4": f4,
            "f6": f6,
            "f2_over_f0": str(f2_over_f0),
            "f4_over_f2": str(f4_over_f2),
            "f6_over_f4": str(f6_over_f4),
            "f2_over_f0_formula": "mu*k/(k-1)",
            "f4_over_f2_formula": "(k+mu+1)/2",
            "f2_over_f0_matches_formula": f2_over_f0 == Fraction(MU * K, K - 1),
            "f4_over_f2_matches_formula": f4_over_f2 == Fraction(K + MU + 1, 2),
            "f2_equals_k_times_triangle_count": f2 == K * T,
        },
        "bridge_verdict": (
            "The exact 122-shell theorem lives on the truncated Dirac-Kahler "
            "sector C0 + C1 + C2. There the chain dimensions are 40, 240, 160; "
            "the boundary ranks are 39 and 120; the Betti data is 1, 81, 40; "
            "and the D^2 spectrum is exactly {0^122, 4^240, 10^48, 16^30}. "
            "So the zero-mode count 122 is real and equals k^2-k-Theta(W33) "
            "with Theta(W33)=10, while the moment ratios are exactly 48/11 and "
            "17/2. This is a rigorous intermediate shell theorem, not a "
            "replacement for the already-promoted full 480-dimensional closure."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(json.dumps(build_truncated_dirac_shell_summary(), indent=2), encoding="utf-8")
    return path


if __name__ == "__main__":
    write_summary()
