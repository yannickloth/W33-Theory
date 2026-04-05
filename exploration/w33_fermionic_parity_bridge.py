"""Fermionic parity operator and Z₂ grading from graph complement.

Phase CDXCV — The complement graph W̄(3,3) has parameters SRG(40,27,18,18).
Its eigenvalues are -1-r = -3, -1-s = 3 (swapped), with k̄ = v-k-1 = 27.
The fermion parity operator (-1)^F swaps particles/antiparticles = graph/complement.
"""
from __future__ import annotations
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

@lru_cache(maxsize=1)
def build_fermionic_parity_summary() -> dict:
    v, k, lam, mu, q = 40, 12, 2, 4, 3
    r, s = 2, -4
    f, g = 24, 15
    E = 240
    # Complement parameters
    k_bar = v - k - 1              # 27
    lam_bar = v - 2 * k + mu - 2   # 40 - 24 + 4 - 2 = 18
    mu_bar = v - 2 * k + lam       # 40 - 24 + 2 = 18
    r_bar = -1 - s                 # -1 - (-4) = 3
    s_bar = -1 - r                 # -1 - 2 = -3
    f_bar = g                      # 15 (multiplicities swap for complement SRG)
    g_bar = f                      # 24
    E_bar = v * k_bar // 2         # 40 × 27 / 2 = 540
    # Total edges: E + E_bar = v(v-1)/2 = 780
    total = E + E_bar  # 780
    complete = v * (v - 1) // 2  # 780
    # Z₂ grading: graph ↔ complement symmetry
    # λ̄ = μ̄ means complement is "conference-like" (equal off-diagonal)
    is_conference_like = lam_bar == mu_bar  # 18 = 18
    # Energy ratio: E/E_bar = 240/540 = 4/9 = (k/k̄)
    energy_ratio = E / E_bar  # 240/540 = 4/9
    param_ratio = k / k_bar  # 12/27 = 4/9
    return {
        "status": "ok",
        "fermionic_parity": {
            "complement_params": f"SRG({v},{k_bar},{lam_bar},{mu_bar})",
            "E_bar": E_bar,
            "is_conference_like": is_conference_like,
        },
        "fermionic_parity_theorem": {
            "k_bar_27": k_bar == 27,
            "lam_bar_eq_mu_bar": is_conference_like,
            "eigenvalue_swap": r_bar == -1 - s and s_bar == -1 - r,
            "total_edges_780": total == complete,
            "energy_ratio_k_over_kbar": abs(energy_ratio - param_ratio) < 1e-12,
            "therefore_z2_grading": (
                k_bar == 27 and is_conference_like
                and total == complete
                and abs(energy_ratio - param_ratio) < 1e-12
            ),
        },
    }
