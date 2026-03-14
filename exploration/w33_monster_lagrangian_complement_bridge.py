"""Exact Lagrangian/max-abelian realization of the Monster 3^7 complement.

The Monster/Landauer bridge already fixed three exact facts:

1. the local 3B shell is the extraspecial factor ``3^(1+12) = 3^13``;
2. the shell complement is the sporadic 3-primary part ``|2Suz|_3 = 3^7``;
3. the same exponent ``7`` is the curved topological ratio ``a2 / c_EH``.

The next structural question is whether that ``3^7`` complement only appears as
an external cofactor or whether it is already native to the local Heisenberg
shell itself.

It is native.  In an extraspecial group ``p^(1+2n)``, every maximal abelian
subgroup has order ``p^(n+1)``; in the live ``3^(1+12)`` shell that gives

    3^(6+1) = 3^7.

The existing offline Monster/Golay bridge in this repo already constructs that
same value concretely as the lifted Lagrangian subgroup order in symplectic
``F3^12``.

So the live complement now has two exact factorisations:

    3^7 = 3^4 * 3^3     (logical * generation),
    3^7 = 3^1 * 3^6     (center * Heisenberg/Lagrangian).

The quotient by the center is exactly ``3^6 = 729``, and that same ``729`` is
simultaneously:

    - the Heisenberg irrep dimension,
    - the number of ternary Golay codewords,
    - the full operator-basis size ``27^2`` for the live ``sl(27)`` bridge.

Therefore the old topological complement ``7`` is not just ``4 + 3``.  It is
also exactly ``1 + 6``: one center/selector trit plus the active Heisenberg
sector.
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

from scripts.w33_monster_3b_s12_sl27_bridge import analyze as analyze_monster_3b_s12_sl27
from w33_monster_3b_centralizer_bridge import build_monster_3b_centralizer_summary
from w33_monster_shell_factorization_bridge import build_monster_shell_factorization_summary
from w33_transport_spectral_selector_bridge import build_transport_spectral_selector_summary


DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_monster_lagrangian_complement_bridge_summary.json"
BASE = 3


def _fraction_dict(value: Fraction) -> dict[str, Any]:
    exact = str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"
    return {"exact": exact, "float": float(value)}


@lru_cache(maxsize=1)
def build_monster_lagrangian_complement_summary() -> dict[str, Any]:
    bridge = analyze_monster_3b_s12_sl27()
    if bridge.get("available") is not True:
        raise AssertionError(f"monster 3B / s12 / sl27 bridge unavailable: {bridge}")

    centralizer = build_monster_3b_centralizer_summary()
    shell_factorization = build_monster_shell_factorization_summary()
    selector = build_transport_spectral_selector_summary()

    shell_states = int(centralizer["centralizer_factorization"]["shell_states"])
    complement_states = int(centralizer["centralizer_factorization"]["two_suz_three_primary_states"])
    complement_trits = int(centralizer["centralizer_factorization"]["two_suz_three_primary_trits"])

    logical_states = int(shell_factorization["shell_factorization"]["logical_states"])
    generation_states = int(shell_factorization["shell_factorization"]["generation_states"])
    logical_trits = int(shell_factorization["shell_factorization"]["logical_trits"])
    generation_trits = int(shell_factorization["shell_factorization"]["generation_trits"])

    max_abelian_states = int(bridge["golay_lagrangian"]["max_abelian_subgroup_order"])
    center_states = BASE
    center_trits = 1
    lagrangian_quotient_states = max_abelian_states // center_states
    lagrangian_quotient_trits = complement_trits - center_trits

    heisenberg_irrep_states = int(bridge["heisenberg"]["irrep_dim"])
    golay_codewords = int(bridge["golay"]["n_codewords"])
    sl27_operator_basis_dim = int(bridge["sl27"]["operator_basis_dim"])
    selector_line_dimension = int(selector["dynamic_selection_bridge"]["invariant_line_h0_dimension"])
    active_heisenberg_trits = int(shell_factorization["shell_factorization"]["heisenberg_trits"])
    topological_over_continuum = Fraction(centralizer["curved_dictionary"]["topology_over_continuum"]["exact"])

    return {
        "status": "ok",
        "lagrangian_realization": {
            "local_shell_label": "3^(1+12)",
            "shell_states": int(shell_states),
            "complement_states": int(complement_states),
            "max_abelian_subgroup_order": int(max_abelian_states),
            "center_states": int(center_states),
            "lagrangian_quotient_states": int(lagrangian_quotient_states),
            "lagrangian_quotient_trits": int(lagrangian_quotient_trits),
            "complement_equals_lifted_max_abelian_exactly": complement_states == max_abelian_states,
            "lagrangian_quotient_equals_heisenberg_irrep": lagrangian_quotient_states == heisenberg_irrep_states,
            "lagrangian_quotient_equals_golay_codewords": lagrangian_quotient_states == golay_codewords,
            "lagrangian_quotient_equals_sl27_operator_basis": lagrangian_quotient_states == sl27_operator_basis_dim,
            "center_times_lagrangian_quotient_equals_complement": (
                center_states * lagrangian_quotient_states == complement_states
            ),
        },
        "dual_factorization": {
            "complement_equals_logical_times_generation": complement_states == logical_states * generation_states,
            "logical_states": int(logical_states),
            "generation_states": int(generation_states),
            "center_states": int(center_states),
            "heisenberg_irrep_states": int(heisenberg_irrep_states),
            "selector_line_dimension": int(selector_line_dimension),
            "active_heisenberg_trits": int(active_heisenberg_trits),
            "logical_plus_generation_trits": [int(logical_trits), int(generation_trits)],
            "center_plus_heisenberg_trits": [int(selector_line_dimension), int(active_heisenberg_trits)],
            "complement_trits_equal_logical_plus_generation": complement_trits == logical_trits + generation_trits,
            "complement_trits_equal_center_plus_heisenberg": (
                complement_trits == selector_line_dimension + active_heisenberg_trits
            ),
            "dual_trit_splits_agree_exactly": (
                complement_trits == logical_trits + generation_trits == selector_line_dimension + active_heisenberg_trits
            ),
        },
        "curved_dictionary": {
            "topological_over_continuum": _fraction_dict(topological_over_continuum),
            "topological_equals_complement_trits": topological_over_continuum == complement_trits,
            "topological_equals_logical_plus_generation": topological_over_continuum == logical_trits + generation_trits,
            "topological_equals_center_plus_heisenberg": (
                topological_over_continuum == selector_line_dimension + active_heisenberg_trits
            ),
        },
        "bridge_verdict": (
            "The old 3^7 Monster complement is now a native local-shell object, not "
            "just a sporadic remainder. Inside the local 3^(1+12) shell, the lifted "
            "Lagrangian/max-abelian subgroup already has order 3^7, exactly matching "
            "the 3-primary part of the 2Suz factor in C_M(3B). More sharply, this "
            "same complement has two exact factorizations: 3^7 = 3^4 * 3^3 on the "
            "live W33 side (logical times generation) and 3^7 = 3 * 3^6 on the local "
            "Heisenberg side (center times Heisenberg/Lagrangian quotient). The "
            "quotient 3^6 = 729 is simultaneously the Heisenberg irrep dimension, the "
            "number of ternary Golay codewords, and the full sl(27) operator basis. "
            "So the topological factor 7 now has a dual exact meaning: 7 = 4 + 3 and "
            "also 7 = 1 + 6."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_monster_lagrangian_complement_summary(), indent=2),
        encoding="utf-8",
    )
    return path


if __name__ == "__main__":
    write_summary()
