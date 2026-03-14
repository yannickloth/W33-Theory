"""Exact factorization of the Monster 3B ternary shell into live W33 sectors.

The Monster/Landauer ternary lock already identifies the local Monster shell

    3^(1+12) = 3^13

as the correct thermodynamic object.  The next exact question is whether that
shell is merely numerically compatible with the live W33 data or actually
factors through it.

It does:

    3^13 = 3^6 * 3^4 * 3^3

with factors

    3^6 = 729  -> the Heisenberg irrep / shared six-channel core,
    3^4 = 81   -> the exact W33 ternary logical sector,
    3^3 = 27   -> the exact generation block.

So the shell trit count splits exactly as

    13 = 6 + 4 + 3.

This immediately explains the promoted public fractions:

    sin^2(theta_W)  = 3/13    generation / shell,
    sin^2(theta_12) = 4/13    logical / shell,
    6/13            = 6/13    active Heisenberg / shell,
    sin^2(theta_23) = 7/13    complement / shell = (4+3)/13,

and therefore

    sin^2(theta_23) = sin^2(theta_12) + sin^2(theta_W).

The same factorization also repackages the curved ratios:

    c_6 / c_EH = 39 = 13 * 3,
    a2 / c_EH  = 7  = 4 + 3.

So the Monster 3B shell is not just another count source. It is an exact
ternary envelope whose factors are already the live code/generation/A2 blocks.
"""

from __future__ import annotations

from fractions import Fraction
from functools import lru_cache
import json
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
for candidate in (ROOT, ROOT / "exploration", ROOT / "scripts", ROOT / "tools"):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from w33_monster_landauer_ternary_bridge import build_monster_landauer_ternary_bridge_summary
from w33_curved_roundtrip_closure_bridge import build_curved_roundtrip_closure_summary


DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_monster_shell_factorization_bridge_summary.json"


def _fraction_dict(value: Fraction) -> dict[str, Any]:
    exact = str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"
    return {"exact": exact, "float": float(value)}


@lru_cache(maxsize=1)
def build_monster_shell_factorization_summary() -> dict[str, Any]:
    monster = build_monster_landauer_ternary_bridge_summary()
    roundtrip = build_curved_roundtrip_closure_summary()

    shell_trits = int(monster["monster_local_shell"]["extraspecial_shell"]["trits"])
    heisenberg_trits = int(monster["monster_local_shell"]["heisenberg_irrep"]["trits"])
    logical_trits = int(monster["monster_local_shell"]["logical_qutrit_sector"]["trits"])
    generation_trits = int(monster["monster_local_shell"]["generation_block"]["trits"])
    complement_trits = int(monster["monster_local_shell"]["shell_complement"]["trits"])

    shell_states = int(monster["monster_local_shell"]["extraspecial_shell"]["states"])
    heisenberg_states = int(monster["monster_local_shell"]["heisenberg_irrep"]["states"])
    logical_states = int(monster["monster_local_shell"]["logical_qutrit_sector"]["states"])
    generation_states = int(monster["monster_local_shell"]["generation_block"]["states"])
    complement_states = int(monster["monster_local_shell"]["shell_complement"]["states"])

    weinberg = Fraction(generation_trits, shell_trits)
    theta12 = Fraction(logical_trits, shell_trits)
    active_heisenberg_share = Fraction(heisenberg_trits, shell_trits)
    theta23 = Fraction(complement_trits, shell_trits)

    discrete_to_continuum = Fraction(
        roundtrip["roundtrip_curved_coefficients"]["discrete_eh_from_finite"]["exact"]
    ) / Fraction(roundtrip["roundtrip_curved_coefficients"]["continuum_eh_from_finite"]["exact"])
    topological_over_continuum = Fraction(
        roundtrip["roundtrip_curved_coefficients"]["topological_from_finite"]["exact"]
    ) / Fraction(roundtrip["roundtrip_curved_coefficients"]["continuum_eh_from_finite"]["exact"])

    return {
        "status": "ok",
        "shell_factorization": {
            "shell_states": int(shell_states),
            "heisenberg_states": int(heisenberg_states),
            "logical_states": int(logical_states),
            "generation_states": int(generation_states),
            "complement_states": int(complement_states),
            "shell_equals_heisenberg_times_logical_times_generation": shell_states
            == heisenberg_states * logical_states * generation_states,
            "complement_equals_logical_times_generation": complement_states
            == logical_states * generation_states,
            "shell_trits": int(shell_trits),
            "heisenberg_trits": int(heisenberg_trits),
            "logical_trits": int(logical_trits),
            "generation_trits": int(generation_trits),
            "complement_trits": int(complement_trits),
            "shell_trits_split": [int(heisenberg_trits), int(logical_trits), int(generation_trits)],
            "shell_trits_factorization_exact": shell_trits == heisenberg_trits + logical_trits + generation_trits,
            "complement_trits_split": [int(logical_trits), int(generation_trits)],
            "complement_trits_factorization_exact": complement_trits == logical_trits + generation_trits,
        },
        "promoted_ratio_factorization": {
            "weinberg_from_generation_over_shell": _fraction_dict(weinberg),
            "theta12_from_logical_over_shell": _fraction_dict(theta12),
            "active_heisenberg_share": _fraction_dict(active_heisenberg_share),
            "theta23_from_complement_over_shell": _fraction_dict(theta23),
            "theta23_equals_theta12_plus_weinberg": theta23 == theta12 + weinberg,
            "theta23_plus_active_heisenberg_share_equals_one": theta23 + active_heisenberg_share == 1,
        },
        "curved_ratio_factorization": {
            "discrete_to_continuum_ratio": _fraction_dict(discrete_to_continuum),
            "topological_over_continuum": _fraction_dict(topological_over_continuum),
            "discrete_to_continuum_equals_shell_times_generation": discrete_to_continuum
            == shell_trits * generation_trits,
            "topological_over_continuum_equals_logical_plus_generation": topological_over_continuum
            == logical_trits + generation_trits,
        },
        "bridge_verdict": (
            "The Monster 3B ternary shell factors exactly through live W33 data. "
            "The shell is 3^13 = 3^6 * 3^4 * 3^3, i.e. the Heisenberg irrep, the "
            "exact 81-qutrit code sector, and the exact 27-state generation block. "
            "So the shell trits split as 13 = 6 + 4 + 3, the complementary shell "
            "splits as 7 = 4 + 3, and the promoted fractions are exact shell shares: "
            "3/13, 4/13, 6/13, 7/13. This explains theta_23 = theta_12 + theta_W "
            "structurally, not just algebraically, and repackages the curved ratios "
            "as 39 = 13*3 and 7 = 4+3."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_monster_shell_factorization_summary(), indent=2),
        encoding="utf-8",
    )
    return path


if __name__ == "__main__":
    write_summary()
