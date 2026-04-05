"""Graph energy and McClelland bound.

Phase DXXV — The energy of G = Σ |λᵢ| = |k|×1 + |r|×f + |s|×g
= 12 + 48 + 60 = 120. The McClelland bound: E(G) ≤ √(v × 2E) = √(40×480)
= √19200 ≈ 138.6. So 120/138.6 ≈ 0.866 of the bound.
"""
from __future__ import annotations
from functools import lru_cache
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

@lru_cache(maxsize=1)
def build_graph_energy_summary() -> dict:
    v, k, lam, mu, q = 40, 12, 2, 4, 3
    r, s = 2, -4
    f, g = 24, 15
    E_edges = 240
    # Graph energy
    energy = abs(k) * 1 + abs(r) * f + abs(s) * g
    # = 12 + 48 + 60 = 120
    # McClelland upper bound
    mcclelland = math.sqrt(v * 2 * E_edges)  # √19200 ≈ 138.56
    ratio = energy / mcclelland
    # Koolen-Moulton bound: E(G) ≤ k + √((v-1)(2E - k²)) = 12 + √(39×(480-144))
    # = 12 + √(39×336) = 12 + √13104 = 12 + 114.47 ≈ 126.47
    km_bound = k + math.sqrt((v - 1) * (2 * E_edges - k**2))
    # Energy per vertex: 120/40 = 3 = q
    energy_per_vertex = energy / v  # 3.0
    # Energy per edge: 120/240 = 0.5 = 1/2
    energy_per_edge = energy / E_edges  # 0.5
    return {
        "status": "ok",
        "graph_energy": {
            "energy": energy,
            "mcclelland": round(mcclelland, 4),
            "energy_per_vertex": energy_per_vertex,
            "energy_per_edge": energy_per_edge,
        },
        "graph_energy_theorem": {
            "energy_120": energy == 120,
            "below_mcclelland": energy < mcclelland,
            "energy_per_v_q": energy_per_vertex == q,
            "energy_per_e_half": energy_per_edge == 0.5,
            "therefore_energy_verified": (
                energy == 120 and energy < mcclelland
                and energy_per_vertex == q and energy_per_edge == 0.5
            ),
        },
    }
