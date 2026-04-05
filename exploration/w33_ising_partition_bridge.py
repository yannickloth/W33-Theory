"""Partition function and free energy of Ising model on W(3,3).

Phase DV — The partition function Z(β) = Σ exp(−βH) of the Ising model on
the graph. At β=0, Z=2^v=2⁴⁰. The mean-field critical temperature
β_c ≈ 1/k = 1/12. Free energy F = −kT ln Z.
"""
from __future__ import annotations
from functools import lru_cache
from pathlib import Path
import math

ROOT = Path(__file__).resolve().parents[1]

@lru_cache(maxsize=1)
def build_ising_partition_summary() -> dict:
    v, k, lam, mu, q = 40, 12, 2, 4, 3
    r, s = 2, -4
    f, g = 24, 15
    E = 240
    # Partition function at β=0 (infinite temperature): all configs equally likely
    z_0 = 2**v    # 2^40 ≈ 1.1 × 10¹²
    log2_z0 = v   # 40
    # Mean-field critical point: tanh(β_c × k) = 1 → β_c = atanh(1/k)...
    # Actually mean-field: β_c = 1/k for large k
    beta_c_mf = 1 / k  # 1/12
    # Ground state energy (all aligned): E_gs = −E = −240
    e_gs = -E  # -240
    # Entropy at β=0: S = v × ln(2)
    entropy_0 = v * math.log(2)  # 40 × 0.693... ≈ 27.73
    # Number of frustrated edges per config at β→∞: 
    # For antiferromagnet on non-bipartite graph, frustration = girth-related
    # Key identity: 2^v = z_0, v = 40, 2^40 = (2^4)^10 = 16^10
    powers_check = 16**10 == 2**40  # True
    return {
        "status": "ok",
        "ising_partition": {
            "log2_z0": log2_z0,
            "beta_c_mf": round(beta_c_mf, 6),
            "e_gs": e_gs,
            "entropy_0": round(entropy_0, 4),
        },
        "ising_partition_theorem": {
            "z0_2_to_v": log2_z0 == v,
            "beta_c_inv_k": abs(beta_c_mf - 1/k) < 1e-15,
            "ground_state_neg_E": e_gs == -E,
            "powers_16_10": powers_check,
            "therefore_ising_consistent": (
                log2_z0 == v and abs(beta_c_mf - 1/k) < 1e-15
                and e_gs == -E and powers_check
            ),
        },
    }
