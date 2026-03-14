"""Exact Monster/Landauer bridge via the Monster 3B ternary local shell.

The old UOR/Landauer/Monster work leaned on the full Monster order and a
binary ``ln 2`` picture.  The live W(3,3) stack is ternary, not binary, and it
already carries an exact Monster-local shell:

    3B centralizer -> 3^(1+12) . 2Suz

The rigorous thermodynamic object is therefore the ``3^(1+12)`` shell, not the
full Monster order.  Landauer's principle acts on state counts, so for an
equiprobable d-state reset the exact cost is

    E_min / (kT) = ln d.

Applied to the live local shell, this gives the exact ternary ledger

    ln(3^13), ln(3^6), ln(3^7), ln(3^4), ln(3^3),

coming respectively from:

    - the Monster 3B extraspecial shell       3^13,
    - the Heisenberg irrep                    3^6 = 729,
    - the shell/irrep complement              3^7,
    - the W33 ternary code logical sector     3^4 = 81,
    - the W33/E6 generation block             3^3 = 27.

This is the exact bridge:

    Phi_3 = 13 = shell trits,
    6     = active Heisenberg/A2/firewall trits,
    Phi_6 = 7 = complementary shell trits.

The promoted public fractions then become exact normalized Landauer ratios:

    sin^2(theta_W) = 3/13 = ln(27)  / ln(3^13),
    sin^2(theta_12)= 4/13 = ln(81)  / ln(3^13),
    sin^2(theta_23)= 7/13 = ln(3^7) / ln(3^13),

while the curved gravity ratio becomes

    c_6 / c_EH = 39 = 13 * 3.

So the exact Monster/Landauer bridge is local, ternary, and already aligned
with the live q=3 cyclotomic package.
"""

from __future__ import annotations

from fractions import Fraction
from functools import lru_cache
import json
from math import log
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
for candidate in (ROOT, ROOT / "exploration", ROOT / "scripts", ROOT / "tools"):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from w33_curved_roundtrip_closure_bridge import build_curved_roundtrip_closure_summary
from w33_lie_tower_s12_bridge import build_lie_tower_s12_bridge_summary
from w33_standard_model_cyclotomic_bridge import build_standard_model_cyclotomic_summary
from w33_ternary_homological_code_bridge import build_ternary_homological_code_summary


DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_monster_landauer_ternary_bridge_summary.json"
BASE = 3
LN3 = log(BASE)


def _fraction_dict(value: Fraction) -> dict[str, Any]:
    exact = str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"
    return {"exact": exact, "float": float(value)}


def _valuation(n: int, p: int) -> int:
    value = int(n)
    exponent = 0
    while value % p == 0:
        value //= p
        exponent += 1
    if value != 1:
        raise ValueError(f"{n} is not a pure power of {p}")
    return exponent


def _cost_entry(states: int) -> dict[str, Any]:
    trits = _valuation(states, BASE)
    return {
        "states": int(states),
        "trits": int(trits),
        "landauer_over_kT": {
            "exact": "ln(3)" if trits == 1 else f"{trits} ln(3)",
            "float": trits * LN3,
        },
    }


@lru_cache(maxsize=1)
def build_monster_landauer_ternary_bridge_summary() -> dict[str, Any]:
    lie_tower = build_lie_tower_s12_bridge_summary()
    standard_model = build_standard_model_cyclotomic_summary()
    roundtrip = build_curved_roundtrip_closure_summary()
    ternary_code = build_ternary_homological_code_summary()

    q = int(standard_model["cyclotomic_data"]["q"])
    phi3 = int(standard_model["cyclotomic_data"]["phi3"])
    phi6 = int(standard_model["cyclotomic_data"]["phi6"])

    shell_states = int(lie_tower["monster_heisenberg_closure"]["extraspecial_order"])
    irrep_states = int(lie_tower["monster_heisenberg_closure"]["heisenberg_irrep_dimension"])
    logical_states = int(ternary_code["ternary_css_code"]["logical_qutrits"])
    generation_states = q**3
    complement_states = shell_states // irrep_states

    shell = _cost_entry(shell_states)
    irrep = _cost_entry(irrep_states)
    logical = _cost_entry(logical_states)
    generation = _cost_entry(generation_states)
    complement = _cost_entry(complement_states)

    sin2_theta_w = Fraction(standard_model["promoted_observables"]["sin2_theta_w_ew"]["exact"])
    sin2_theta_12 = Fraction(standard_model["promoted_observables"]["sin2_theta_12"]["exact"])
    sin2_theta_23 = Fraction(standard_model["promoted_observables"]["sin2_theta_23"]["exact"])
    tan_theta_c = Fraction(standard_model["promoted_observables"]["tan_theta_c"]["exact"])

    weinberg_ratio = Fraction(generation["trits"], shell["trits"])
    theta12_ratio = Fraction(logical["trits"], shell["trits"])
    theta23_ratio = Fraction(complement["trits"], shell["trits"])

    discrete_eh = Fraction(roundtrip["roundtrip_curved_coefficients"]["discrete_eh_from_finite"]["exact"])
    continuum_eh = Fraction(roundtrip["roundtrip_curved_coefficients"]["continuum_eh_from_finite"]["exact"])
    topological = Fraction(roundtrip["roundtrip_curved_coefficients"]["topological_from_finite"]["exact"])
    discrete_to_continuum = discrete_eh / continuum_eh
    topological_over_continuum = topological / continuum_eh

    return {
        "status": "ok",
        "monster_local_shell": {
            "monster_class": str(lie_tower["monster_heisenberg_closure"]["monster_class"]),
            "extraspecial_shell": shell,
            "heisenberg_irrep": irrep,
            "shell_complement": complement,
            "logical_qutrit_sector": logical,
            "generation_block": generation,
        },
        "ternary_lock_dictionary": {
            "q": int(q),
            "phi3": int(phi3),
            "phi6": int(phi6),
            "phi3_equals_shell_trits": int(phi3) == int(shell["trits"]),
            "shared_six_equals_irrep_trits": int(irrep["trits"]) == 6,
            "phi6_equals_complement_trits": int(phi6) == int(complement["trits"]),
            "phi6_equals_shell_minus_irrep": int(phi6) == int(shell["trits"]) - int(irrep["trits"]),
            "logical_qutrits": int(ternary_code["ternary_css_code"]["logical_qutrits"]),
            "logical_trits": int(logical["trits"]),
            "heisenberg_irrep_equals_q_squared_times_logical_qutrits": int(irrep_states) == (q * q) * int(
                ternary_code["ternary_css_code"]["logical_qutrits"]
            ),
        },
        "landauer_ratio_dictionary": {
            "weinberg_from_generation_over_shell": _fraction_dict(weinberg_ratio),
            "tan_theta_c_from_generation_over_shell": _fraction_dict(weinberg_ratio),
            "theta12_from_logical_over_shell": _fraction_dict(theta12_ratio),
            "theta23_from_complement_over_shell": _fraction_dict(theta23_ratio),
            "weinberg_matches_promoted_value": weinberg_ratio == sin2_theta_w,
            "cabibbo_matches_promoted_value": weinberg_ratio == tan_theta_c,
            "theta12_matches_promoted_value": theta12_ratio == sin2_theta_12,
            "theta23_matches_promoted_value": theta23_ratio == sin2_theta_23,
            "discrete_to_continuum_ratio": _fraction_dict(discrete_to_continuum),
            "discrete_to_continuum_equals_shell_times_generation_trits": discrete_to_continuum
            == shell["trits"] * generation["trits"],
            "topological_over_continuum": _fraction_dict(topological_over_continuum),
            "topological_over_continuum_equals_complement_trits": topological_over_continuum == complement["trits"],
        },
        "bridge_verdict": (
            "The exact Monster/Landauer bridge is local and ternary. The Monster "
            "3B shell contributes 3^13 states, so its exact Landauer cost is "
            "13 kT ln 3 rather than a binary ln 2 object. Its Heisenberg irrep "
            "contributes 3^6 states, leaving a complementary 3^7 shell. Those "
            "three ternary exponents match the live q=3 package exactly: "
            "Phi_3=13 is the shell size in trits, the shared six-channel "
            "A2/firewall/tomotope core is the active 3^6 Heisenberg sector, and "
            "Phi_6=7 is the complementary shell. More sharply, the promoted "
            "fractions now have exact Landauer forms "
            "sin^2(theta_W)=ln(27)/ln(3^13)=3/13, "
            "sin^2(theta_12)=ln(81)/ln(3^13)=4/13, and "
            "sin^2(theta_23)=ln(3^7)/ln(3^13)=7/13, while the curved gravity "
            "ratio satisfies c_6/c_EH = 39 = 13*3. So the Monster/Landauer side "
            "is now aligned with the live W33 theory at the exact 3-local shell, "
            "not only at the level of moonshine numerology."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_monster_landauer_ternary_bridge_summary(), indent=2),
        encoding="utf-8",
    )
    return path


if __name__ == "__main__":
    write_summary()
