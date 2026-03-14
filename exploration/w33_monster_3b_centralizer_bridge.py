"""Exact 3B-centralizer closure for the Monster/Landauer ternary bridge.

The local Monster/Landauer theorem already proved that the rigorous ternary
object is the Monster ``3B`` shell

    3^(1+12) = 3^13,

with exact complement

    3^7.

The sharper structural question is whether that complement is just an abstract
remainder or whether it lives on a native group factor inside the actual 3B
centralizer.

It does.  The ATLAS 3B centralizer is

    C_M(3B) = 3^(1+12) . 2Suz

and the sporadic Suzuki factor has order

    |Suz| = 2^13 * 3^7 * 5^2 * 7 * 11 * 13,

so

    |2Suz|_3 = 3^7.

Therefore the full Monster 3-primary part is already concentrated inside the
local 3B centralizer:

    |M|_3 = |C_M(3B)|_3 = 3^13 * 3^7 = 3^20.

This identifies the old shell complement structurally:

    complement = (2Suz)_3 = 3^7 = 3^4 * 3^3,

so the sporadic factor carries exactly the logical-plus-generation trits.  The
curved bridge then reconstructs the same split as

    (c_6 / c_EH) / q = 13,
    a_2 / c_EH       = 7.

So the Monster/Landauer ternary bridge is now local not only at the shell
level, but at the actual 3B-centralizer factorization level.
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
from w33_monster_3adic_closure_bridge import MONSTER_ORDER, MONSTER_PRIMES
from w33_monster_shell_factorization_bridge import build_monster_shell_factorization_summary


DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_monster_3b_centralizer_bridge_summary.json"

BASE = 3
LN3 = log(BASE)
SUZ_ORDER = 2**13 * 3**7 * 5**2 * 7 * 11 * 13
TWO_SUZ_ORDER = 2 * SUZ_ORDER
SHELL_STATES = 3**13
CENTRALIZER_ORDER = SHELL_STATES * TWO_SUZ_ORDER


def _valuation(n: int, p: int) -> int:
    value = int(n)
    exponent = 0
    while value % p == 0:
        value //= p
        exponent += 1
    return exponent


def _fraction_dict(value: Fraction) -> dict[str, Any]:
    exact = str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"
    return {"exact": exact, "float": float(value)}


def _cost_entry(states: int) -> dict[str, Any]:
    trits = _valuation(states, BASE)
    if states != BASE**trits:
        raise ValueError(f"{states} is not a pure power of {BASE}")
    return {
        "states": int(states),
        "trits": int(trits),
        "landauer_over_kT": {
            "exact": "ln(3)" if trits == 1 else f"{trits} ln(3)",
            "float": trits * LN3,
        },
    }


@lru_cache(maxsize=1)
def build_monster_3b_centralizer_summary() -> dict[str, Any]:
    factorization = build_monster_shell_factorization_summary()
    roundtrip = build_curved_roundtrip_closure_summary()

    monster_three_primary_states = BASE ** MONSTER_PRIMES[BASE]
    centralizer_three_primary_states = BASE ** _valuation(CENTRALIZER_ORDER, BASE)
    two_suz_three_primary_states = BASE ** _valuation(TWO_SUZ_ORDER, BASE)

    monster_three_primary = _cost_entry(monster_three_primary_states)
    shell = _cost_entry(SHELL_STATES)
    two_suz_three_primary = _cost_entry(two_suz_three_primary_states)

    logical_states = int(factorization["shell_factorization"]["logical_states"])
    generation_states = int(factorization["shell_factorization"]["generation_states"])

    discrete_eh = Fraction(roundtrip["roundtrip_curved_coefficients"]["discrete_eh_from_finite"]["exact"])
    continuum_eh = Fraction(roundtrip["roundtrip_curved_coefficients"]["continuum_eh_from_finite"]["exact"])
    topological = Fraction(roundtrip["roundtrip_curved_coefficients"]["topological_from_finite"]["exact"])
    gravity_over_q = (discrete_eh / continuum_eh) / 3
    topology_over_continuum = topological / continuum_eh

    return {
        "status": "ok",
        "three_b_centralizer": {
            "monster_order": int(MONSTER_ORDER),
            "monster_three_primary_part": monster_three_primary,
            "centralizer_label": "3^(1+12).2Suz",
            "centralizer_order": int(CENTRALIZER_ORDER),
            "centralizer_three_primary_part": _cost_entry(centralizer_three_primary_states),
            "centralizer_three_primary_matches_monster": centralizer_three_primary_states == monster_three_primary_states,
        },
        "centralizer_factorization": {
            "shell_states": int(SHELL_STATES),
            "shell_trits": int(shell["trits"]),
            "two_suz_order": int(TWO_SUZ_ORDER),
            "two_suz_three_primary_states": int(two_suz_three_primary_states),
            "two_suz_three_primary_trits": int(two_suz_three_primary["trits"]),
            "centralizer_three_primary_equals_shell_times_two_suz_three_primary": (
                centralizer_three_primary_states == SHELL_STATES * two_suz_three_primary_states
            ),
            "two_suz_three_primary_equals_logical_times_generation": (
                two_suz_three_primary_states == logical_states * generation_states
            ),
            "logical_states": int(logical_states),
            "generation_states": int(generation_states),
        },
        "landauer_budget": {
            "centralizer_three_primary": _cost_entry(centralizer_three_primary_states),
            "shell": shell,
            "two_suz_three_primary": two_suz_three_primary,
            "landauer_additivity_exact": int(monster_three_primary["trits"]) == int(shell["trits"]) + int(two_suz_three_primary["trits"]),
        },
        "curved_dictionary": {
            "gravity_over_q": _fraction_dict(gravity_over_q),
            "topology_over_continuum": _fraction_dict(topology_over_continuum),
            "shell_from_curved_gravity_exact": gravity_over_q == shell["trits"],
            "two_suz_from_curved_topology_exact": topology_over_continuum == two_suz_three_primary["trits"],
            "centralizer_three_primary_from_curved_coefficients_exact": (
                Fraction(monster_three_primary["trits"]) == gravity_over_q + topology_over_continuum
            ),
        },
        "bridge_verdict": (
            "The Monster/Landauer ternary bridge is now local at the actual 3B-"
            "centralizer level. The ATLAS centralizer is 3^(1+12).2Suz, the shell "
            "contributes 3^13, and the 3-primary part of 2Suz contributes exactly "
            "3^7. Therefore |M|_3 = |C_M(3B)|_3 = 3^13 * 3^7 = 3^20. More sharply, "
            "the sporadic 2Suz factor carries exactly the same logical-plus-"
            "generation complement 3^7 = 3^4 * 3^3 that already appears in the live "
            "W33 code/generation split, and the curved bridge reconstructs the same "
            "two numbers as 39/3 = 13 and a2/c_EH = 7."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_monster_3b_centralizer_summary(), indent=2),
        encoding="utf-8",
    )
    return path


if __name__ == "__main__":
    write_summary()
