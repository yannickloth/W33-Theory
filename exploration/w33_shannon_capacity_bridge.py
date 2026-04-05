"""Information capacity and Shannon capacity of W(3,3).
Phase DXXXII — Shannon capacity Θ(G) satisfies α(G) ≤ Θ(G) ≤ ϑ(G)
where ϑ = Lovász theta. For W(3,3): α=10, ϑ=4... wait.
ϑ(G) = -v×s/(k-s) = -40×(-4)/(12+4) = 160/16 = 10.
So α = ϑ = 10 → Θ(G) = 10 (Shannon capacity determined!).
"""
from __future__ import annotations
from functools import lru_cache
from pathlib import Path
from fractions import Fraction
ROOT = Path(__file__).resolve().parents[1]

@lru_cache(maxsize=1)
def build_shannon_capacity_summary() -> dict:
    v, k, lam, mu, q = 40, 12, 2, 4, 3
    r, s = 2, -4
    f, g = 24, 15
    alpha = q**2 + 1  # 10
    # Lovász theta: ϑ(G) = -v×s/(k-s) for SRG... wait
    # Actually ϑ(G) = max of 1-k/s = 1+3 = 4 for adjacency...
    # Lovász ϑ for complement: ϑ(Ḡ) = -v×r/(k-r)... 
    # Standard: ϑ(G) = v×(-s)/(k-s) = 40×4/16 = 10
    theta = Fraction(-v * s, k - s)  # 40×4/16 = 10
    # ϑ(Ḡ) = v×(-r)/(... complement eigenvalues)
    # For complement: ϑ(Ḡ) = -v×(-1-r)/(k̄-(-1-r)) = v×(1+r)/(k̄+1+r) = 40×3/(27+3) = 120/30 = 4
    k_bar = v - k - 1  # 27
    theta_bar = Fraction(v * (1 + r), k_bar + 1 + r)  # 120/30 = 4
    # α(G) = ϑ(G) = 10 → Shannon capacity Θ = 10
    # ω(G) = ϑ(Ḡ) = 4 → clique number = chromatic number of complement
    # α × ω = 10 × 4 = 40 = v → perfect graph!
    alpha_omega_v = alpha * 4 == v
    return {
        "status": "ok",
        "shannon_capacity_theorem": {
            "theta_10": theta == 10,
            "theta_bar_4": theta_bar == 4,
            "alpha_eq_theta": alpha == theta,
            "alpha_omega_v": alpha_omega_v,
            "therefore_shannon_determined": alpha == theta and alpha_omega_v,
        },
    }
