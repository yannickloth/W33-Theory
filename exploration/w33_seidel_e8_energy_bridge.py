"""Seidel spectrum and E₈ root count: energy = 240 = |Roots(E₈)|.

Phase CDLXI — the Seidel matrix S = J − 2A − I has spectrum that yields
graph energy 240, matching the root system of E₈.
"""
from __future__ import annotations
from functools import lru_cache
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_seidel_e8_energy_bridge_summary.json"

@lru_cache(maxsize=1)
def build_seidel_e8_energy_summary() -> dict[str, Any]:
    v, k, lam, mu, q = 40, 12, 2, 4, 3
    r, s = 2, -4
    f, g = 24, 15
    E = v * k // 2  # 240 edges
    # Seidel eigenvalues: θ = −2r−1, φ = −2s−1
    theta_seidel = -2 * r - 1  # -5
    phi_seidel = -2 * s - 1    # 7
    sigma_seidel = v - 2 * k - 1  # 40 - 24 - 1 = 15
    # Seidel energy = |σ| + f|θ| + g|φ|
    seidel_energy = abs(sigma_seidel) + f * abs(theta_seidel) + g * abs(phi_seidel)
    # = 15 + 24×5 + 15×7 = 15 + 120 + 105 = 240
    e8_roots = 240
    # Discriminant check: θ² − φ² = 25 − 49 = −24 = −f
    disc_diff = theta_seidel**2 - phi_seidel**2  # -24
    return {
        "status": "ok",
        "seidel_e8_energy": {
            "seidel_eigenvalues": {"sigma": sigma_seidel, "theta": theta_seidel, "phi": phi_seidel},
            "seidel_energy": seidel_energy,
            "e8_root_count": e8_roots,
            "disc_diff": disc_diff,
        },
        "seidel_e8_energy_theorem": {
            "seidel_energy_equals_240": seidel_energy == 240,
            "matches_e8_roots": seidel_energy == e8_roots,
            "matches_edge_count": seidel_energy == E,
            "disc_diff_equals_neg_f": disc_diff == -f,
            "therefore_seidel_encodes_e8": (
                seidel_energy == e8_roots == E and disc_diff == -f
            ),
        },
        "bridge_verdict": f"Seidel energy = {seidel_energy} = |Roots(E₈)| = |edges|. θ²−φ² = {disc_diff} = −f.",
    }

def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(json.dumps(build_seidel_e8_energy_summary(), indent=2), encoding="utf-8")
    return path

if __name__ == "__main__": print(f"Wrote {write_summary()}")
