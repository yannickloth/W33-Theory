"""Kirchhoff spanning-tree 2-adic valuation: τ = 2⁸¹ · 5²³.

Phase CDLI — verify the Kirchhoff matrix-tree theorem applied to W(3,3) and
its connection to Betti numbers, the Golay code, and the Leech lattice.
"""
from __future__ import annotations
from functools import lru_cache
import json, math
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_kirchhoff_tree_structure_bridge_summary.json"

@lru_cache(maxsize=1)
def build_kirchhoff_tree_structure_summary() -> dict[str, Any]:
    v, k, lam, mu, q = 40, 12, 2, 4, 3
    f, g = 24, 15
    r, s = 2, -4
    b1 = q**4  # 81
    tau_formula_exp2 = b1  # exponent of 2 = 81
    tau_formula_exp5 = f - 1  # exponent of 5 = 23
    kr = k - r  # 10
    ks = k - s  # 16
    tau = (kr**f * ks**g) // v
    exp2 = 0
    tmp = tau
    while tmp % 2 == 0:
        exp2 += 1; tmp //= 2
    exp5 = 0
    while tmp % 5 == 0:
        exp5 += 1; tmp //= 5
    remaining = tmp
    return {
        "status": "ok",
        "kirchhoff_tree_structure": {
            "tau_formula": f"(1/v) × (k-r)^f × (k-s)^g = (1/{v}) × {kr}^{f} × {ks}^{g}",
            "two_adic_valuation": exp2,
            "five_adic_valuation": exp5,
            "remaining_cofactor": remaining,
            "exp2_equals_b1": exp2 == b1,
            "exp5_equals_f_minus_1": exp5 == f - 1,
        },
        "kirchhoff_tree_structure_theorem": {
            "the_2_adic_valuation_equals_b1_equals_81": exp2 == b1,
            "the_5_adic_valuation_equals_f_minus_1_equals_23": exp5 == f - 1,
            "the_remaining_cofactor_is_1": remaining == 1,
            "therefore_tau_equals_2_to_81_times_5_to_23": exp2 == b1 and exp5 == f - 1 and remaining == 1,
        },
        "bridge_verdict": f"τ(W33) = 2^{exp2} · 5^{exp5}, exp(2) = b₁ = {b1}, exp(5) = f-1 = {f-1}.",
    }

def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(json.dumps(build_kirchhoff_tree_structure_summary(), indent=2), encoding="utf-8")
    return path

if __name__ == "__main__": print(f"Wrote {write_summary()}")
