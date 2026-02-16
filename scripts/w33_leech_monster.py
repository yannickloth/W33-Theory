#!/usr/bin/env python3
"""
Leech lattice, Monster group numerology, and Moonshine observables

Pillar 57 — Leech / Monster / Moonshine

Provides computational evidence linking three copies of E8 (E8^3) and the
Leech lattice; highlights numerology connecting Leech kissing number (196560)
with Monster representation dimensions (196883) and group-size ratios.

Usage:
    python scripts/w33_leech_monster.py

"""
from __future__ import annotations

from typing import Dict

from scripts.w33_cryptographic_lattice import analyze_leech_connection


def e4_coeffs(n_terms: int = 8):
    """Return the first n_terms coefficients of E4(q)=Theta_{E8}(q).

    Coefficients are integers: E4 = 1 + 240 q + 2160 q^2 + 6720 q^3 + 17520 q^4 + ...
    """
    base = [1, 240, 2160, 6720, 17520, 30240, 60480, 82560]
    return base[:n_terms]


def poly_power(coeffs, power: int, n_terms: int):
    """Compute first n_terms coefficients of (sum coeffs[i] q^i)^power."""
    out = [0] * n_terms
    out[0] = 1 if power == 0 else coeffs[0] ** power
    # naive convolution (sufficient for small n_terms)
    from itertools import product

    # start from 1st power by repeated convolution
    cur = coeffs[:n_terms]
    for _ in range(1, power):
        nxt = [0] * n_terms
        for i in range(n_terms):
            if cur[i] == 0:
                continue
            for j in range(n_terms - i):
                if j >= len(coeffs):
                    break
                nxt[i + j] += cur[i] * coeffs[j]
        cur = nxt
    return cur[:n_terms]


def j_coeffs(n_terms: int = 6):
    """Return first few Fourier coefficients of the Klein j‑invariant.

    j(q) = q^{-1} + 196884 q + 21493760 q^2 + 864299970 q^3 + ...
    We return coefficients for positive powers (q^1, q^2, ...).
    """
    known = [196884, 21493760, 864299970, 20245856256, 333202640600]
    return known[:n_terms]


def analyze_leech_monster() -> Dict:
    """Compute Leech/Monster numerology derived from W(3,3)/E8 data.

    Returns a dictionary of integers and sanity checks suitable for unit tests.
    """
    data = analyze_leech_connection()

    e8_roots = data["e8_roots"]
    e8_cubed_roots = data["e8_cubed_roots"]
    leech_kissing = data["leech_kissing"]
    ratio = data["ratio"]

    # Smallest nontrivial Monster representation dimension (McKay--Thompson)
    monster_min_rep = 196_883
    monster_diff = monster_min_rep - leech_kissing

    psp_cubed_order = data.get("psp_cubed_order")
    co0_order = data.get("co0_order")
    excess_symmetry_factor = data.get("excess_symmetry_factor")

    interpretation = (
        "E8^3 provides 720 root vectors; the Leech kissing number 196560 "
        "is 273×720. The smallest Monster rep (196883) is close (difference=323), "
        "suggesting deep but nontrivial connections (Moonshine numerology)."
    )

    # modular/j comparisons
    e4 = e4_coeffs(n_terms=6)
    e4_cubed = poly_power(e4, 3, 6)
    # coefficient of q^1 in Theta(E8)^3 equals 720 (E8^3 minimal vectors)
    theta_e8_cubed_q1 = e4_cubed[1] if len(e4_cubed) > 1 else None

    j1 = j_coeffs(1)[0]
    j_minus_leech = j1 - leech_kissing

    return {
        "e8_roots": e8_roots,
        "e8_cubed_roots": e8_cubed_roots,
        "leech_kissing": leech_kissing,
        "ratio": ratio,
        "monster_min_rep": monster_min_rep,
        "monster_diff": monster_diff,
        "psp_cubed_order": psp_cubed_order,
        "co0_order": co0_order,
        "excess_symmetry_factor": excess_symmetry_factor,
        "theta_e8_cubed_q1": theta_e8_cubed_q1,
        "j1": j1,
        "j_minus_leech": j_minus_leech,
        "interpretation": interpretation,
    }


if __name__ == "__main__":
    out = analyze_leech_monster()
    print("PILLAR 57: LEECH / MONSTER / MOONSHINE NUMEROLOGY")
    print("- E8 roots:", out["e8_roots"])
    print("- E8^3 roots:", out["e8_cubed_roots"])
    print("- Leech kissing number:", out["leech_kissing"])
    print("- Ratio (Leech/E8^3):", out["ratio"])
    print("- Monster smallest nontrivial rep:", out["monster_min_rep"])
    print("- Difference (Monster - Leech):", out["monster_diff"])
    print("- Interpretation:", out["interpretation"])
