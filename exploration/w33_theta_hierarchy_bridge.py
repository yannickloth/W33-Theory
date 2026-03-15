"""Exact Lovasz-theta / hierarchy selector bridge for W33.

This promotes the clean theorem-grade part of the older "CC/FN" drafts
without overclaiming a full fermion-mass derivation.

For the canonical W33 graph SRG(40,12,2,4):

  - the Lovasz theta number is exactly Theta(W33) = 10;
  - its reciprocal is exactly 1/10 = mu/v;
  - the same Theta appears in the truncated Dirac-Kahler shell identity
    122 = k^2 - k - Theta(W33).

So one exact combinatorial invariant controls both the truncated 122-shell and
the natural small selector 1/10. This is a real graph theorem; what remains
open is the stronger claim that this already closes the full fermion spectrum.
"""

from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_theta_hierarchy_bridge_summary.json"

V = 40
K = 12
LAM = 2
MU = 4
S = -4
THETA = Fraction(-V * S, K - S)
THETA_BAR = Fraction(V, THETA)

BETA = [1, 81, 40]
ZERO_MODE_COUNT = sum(BETA)
SMALL_SELECTOR = Fraction(1, THETA)


def build_theta_hierarchy_summary() -> dict[str, Any]:
    return {
        "status": "ok",
        "theta_dictionary": {
            "srg_parameters": [V, K, LAM, MU],
            "least_eigenvalue": S,
            "lovasz_theta_formula": "-v*s/(k-s)",
            "lovasz_theta_alternate_formula": "v*mu/(k+mu)",
            "lovasz_theta": str(THETA),
            "theta_complement": str(THETA_BAR),
            "theta_times_theta_complement": str(THETA * THETA_BAR),
            "theta_times_theta_complement_equals_v": THETA * THETA_BAR == V,
        },
        "hierarchy_selector": {
            "small_selector_formula": "1/Theta(W33) = mu/v",
            "small_selector": str(SMALL_SELECTOR),
            "mu_over_v": str(Fraction(MU, V)),
            "selector_matches_mu_over_v": SMALL_SELECTOR == Fraction(MU, V),
            "selector_times_theta_is_unity": SMALL_SELECTOR * THETA == 1,
        },
        "truncated_shell_lock": {
            "betti_numbers": BETA,
            "zero_mode_count": ZERO_MODE_COUNT,
            "zero_mode_formula": "k^2 - k - Theta(W33)",
            "zero_mode_formula_value": int(K**2 - K - THETA),
            "betti_sum_equals_formula": ZERO_MODE_COUNT == int(K**2 - K - THETA),
        },
        "bridge_verdict": (
            "The exact graph invariant Theta(W33)=10 controls two promoted "
            "layers at once. Its reciprocal is the natural small selector "
            "1/10 = mu/v, while the same Theta enters the truncated "
            "Dirac-Kahler shell identity 122 = k^2-k-Theta(W33). So one exact "
            "combinatorial invariant governs both the honest 122-shell theorem "
            "and the natural hierarchy-scale selector, without pretending that "
            "the full fermion spectrum is already closed by Theta alone."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(json.dumps(build_theta_hierarchy_summary(), indent=2), encoding="utf-8")
    return path


if __name__ == "__main__":
    write_summary()
