"""Exact closure of the full Monster 3-primary sector in the live ternary bridge.

The rigorous Monster/Landauer bridge in the live W33 program is the local
Monster ``3B`` shell

    3^(1+12) = 3^13,

not the full Monster order.  But once that local shell is exact, the next
question is whether the full Monster 3-primary content still sits inside the
same ternary bookkeeping.

It does.  The Monster order has exact 3-adic valuation

    v_3(|M|) = 20,

so its ternary primary part is

    |M|_3 = 3^20.

The live local shell already supplies

    3^13 = 3^6 * 3^4 * 3^3,

and its exact shell complement is

    3^7 = 3^4 * 3^3.

Therefore

    3^20 = 3^13 * 3^7 = 3^(Phi_3 + Phi_6),

with

    Phi_3 = 13,
    Phi_6 = 7.

This closes the Monster/Landauer side globally:

  - the full Monster ternary entropy is ``20 ln 3``,
  - the local shell contributes ``13 ln 3``,
  - the exact complement contributes ``7 ln 3``,
  - and the curved continuum bridge already recovers those same two numbers as

        (c_6 / c_EH) / q = 39 / 3 = 13,
        a_2 / c_EH = 7.

So the full Monster 3-primary content is not extra numerology sitting above the
live q=3 program.  It is exactly the sum of the shell and complement sectors
that the live bridge already reconstructs.
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

from w33_curvature_cyclotomic_lock_bridge import build_curvature_cyclotomic_lock_summary
from w33_curved_roundtrip_closure_bridge import build_curved_roundtrip_closure_summary
from w33_monster_landauer_ternary_bridge import build_monster_landauer_ternary_bridge_summary
from w33_monster_shell_factorization_bridge import build_monster_shell_factorization_summary


DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_monster_3adic_closure_bridge_summary.json"

MONSTER_ORDER = 808017424794512875886459904961710757005754368000000000
MONSTER_PRIMES = {
    2: 46,
    3: 20,
    5: 9,
    7: 6,
    11: 2,
    13: 3,
    17: 1,
    19: 1,
    23: 1,
    29: 1,
    31: 1,
    41: 1,
    47: 1,
    59: 1,
    71: 1,
}

BASE = 3
LN3 = log(BASE)


def _fraction_dict(value: Fraction) -> dict[str, Any]:
    exact = str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"
    return {"exact": exact, "float": float(value)}


def _cost_entry(states: int) -> dict[str, Any]:
    trits = MONSTER_PRIMES[BASE] if states == BASE ** MONSTER_PRIMES[BASE] else 0
    if not trits:
        value = int(states)
        while value % BASE == 0:
            value //= BASE
            trits += 1
        if value != 1:
            raise ValueError(f"{states} is not a pure power of {BASE}")
    return {
        "states": int(states),
        "trits": int(trits),
        "landauer_over_kT": {
            "exact": "ln(3)" if trits == 1 else f"{trits} ln(3)",
            "float": trits * LN3,
        },
    }


def _verify_monster_order() -> bool:
    computed = 1
    for prime, exponent in MONSTER_PRIMES.items():
        computed *= prime**exponent
    return computed == MONSTER_ORDER


@lru_cache(maxsize=1)
def build_monster_3adic_closure_summary() -> dict[str, Any]:
    if not _verify_monster_order():
        raise AssertionError("Monster order factorization mismatch")

    monster = build_monster_landauer_ternary_bridge_summary()
    factorization = build_monster_shell_factorization_summary()
    cyclotomic = build_curvature_cyclotomic_lock_summary()
    roundtrip = build_curved_roundtrip_closure_summary()

    shell_states = int(monster["monster_local_shell"]["extraspecial_shell"]["states"])
    shell_trits = int(monster["monster_local_shell"]["extraspecial_shell"]["trits"])
    complement_states = int(monster["monster_local_shell"]["shell_complement"]["states"])
    complement_trits = int(monster["monster_local_shell"]["shell_complement"]["trits"])
    heisenberg_states = int(monster["monster_local_shell"]["heisenberg_irrep"]["states"])
    logical_states = int(monster["monster_local_shell"]["logical_qutrit_sector"]["states"])
    generation_states = int(monster["monster_local_shell"]["generation_block"]["states"])

    q = int(cyclotomic["cyclotomic_factors"]["q"])
    phi3 = int(cyclotomic["cyclotomic_factors"]["phi3"])
    phi6 = int(cyclotomic["cyclotomic_factors"]["phi6"])

    full_three_primary_states = BASE ** MONSTER_PRIMES[BASE]
    full_three_primary = _cost_entry(full_three_primary_states)
    shell = _cost_entry(shell_states)
    complement = _cost_entry(complement_states)

    discrete_eh = Fraction(roundtrip["roundtrip_curved_coefficients"]["discrete_eh_from_finite"]["exact"])
    continuum_eh = Fraction(roundtrip["roundtrip_curved_coefficients"]["continuum_eh_from_finite"]["exact"])
    topological = Fraction(roundtrip["roundtrip_curved_coefficients"]["topological_from_finite"]["exact"])

    gravity_over_q = (discrete_eh / continuum_eh) / q
    topology_over_continuum = topological / continuum_eh
    shell_share = Fraction(shell_trits, full_three_primary["trits"])
    complement_share = Fraction(complement_trits, full_three_primary["trits"])

    return {
        "status": "ok",
        "monster_3_primary_order": {
            "monster_order": int(MONSTER_ORDER),
            "order_factorization": "2^46 * 3^20 * 5^9 * 7^6 * 11^2 * 13^3 * 17 * 19 * 23 * 29 * 31 * 41 * 47 * 59 * 71",
            "order_factorization_verifies_exactly": _verify_monster_order(),
            "three_primary_part": full_three_primary,
        },
        "local_global_ternary_closure": {
            "shell_states": int(shell_states),
            "shell_trits": int(shell_trits),
            "complement_states": int(complement_states),
            "complement_trits": int(complement_trits),
            "heisenberg_states": int(heisenberg_states),
            "logical_states": int(logical_states),
            "generation_states": int(generation_states),
            "full_three_primary_equals_shell_times_complement": full_three_primary_states
            == shell_states * complement_states,
            "full_three_primary_equals_heisenberg_times_logical_squared_times_generation_squared": (
                full_three_primary_states == heisenberg_states * logical_states * logical_states * generation_states * generation_states
            ),
            "full_three_primary_trits_equal_phi3_plus_phi6": int(full_three_primary["trits"]) == phi3 + phi6,
            "shell_trits_equal_phi3": int(shell_trits) == phi3,
            "complement_trits_equal_phi6": int(complement_trits) == phi6,
            "shell_plus_complement_trits_equals_monster_three_primary": int(full_three_primary["trits"])
            == int(shell_trits) + int(complement_trits),
            "shell_complement_matches_factorized_logical_generation_block": (
                factorization["shell_factorization"]["complement_equals_logical_times_generation"]
            ),
        },
        "landauer_budget": {
            "full_monster_three_primary": full_three_primary,
            "local_shell": shell,
            "shell_complement": complement,
            "landauer_additivity_exact": full_three_primary["trits"] == shell["trits"] + complement["trits"],
            "shell_share_of_full_monster_three_primary": _fraction_dict(shell_share),
            "complement_share_of_full_monster_three_primary": _fraction_dict(complement_share),
        },
        "curved_thermodynamic_dictionary": {
            "q": int(q),
            "phi3": int(phi3),
            "phi6": int(phi6),
            "discrete_to_continuum_ratio": _fraction_dict(discrete_eh / continuum_eh),
            "gravity_over_q": _fraction_dict(gravity_over_q),
            "topological_over_continuum": _fraction_dict(topology_over_continuum),
            "shell_from_curved_gravity_exact": gravity_over_q == shell_trits,
            "complement_from_curved_topology_exact": topology_over_continuum == complement_trits,
            "full_monster_three_primary_from_curved_coefficients_exact": (
                Fraction(full_three_primary["trits"]) == gravity_over_q + topology_over_continuum
            ),
            "monster_three_trits_equal_phi3_plus_phi6": Fraction(full_three_primary["trits"]) == phi3 + phi6,
        },
        "bridge_verdict": (
            "The full Monster ternary content now closes exactly inside the live "
            "q=3 bridge. The full Monster order has 3-primary part 3^20, while the "
            "rigorous local bridge already gives the 3B shell 3^13 and its exact "
            "complement 3^7. Therefore 3^20 = 3^13 * 3^7 = 3^(Phi_3 + Phi_6), so "
            "the full Monster ternary entropy is 20 ln(3) = 13 ln(3) + 7 ln(3). "
            "This is the same split seen by the curved bridge: the discrete gravity "
            "ratio gives 39/q = 13, the topological ratio gives 7, and together they "
            "reconstruct the full Monster 3-adic valuation 20 exactly. So the local "
            "Monster/Landauer theorem is now closed globally at the 3-primary level, "
            "not only at the shell level."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_monster_3adic_closure_summary(), indent=2),
        encoding="utf-8",
    )
    return path


if __name__ == "__main__":
    write_summary()
