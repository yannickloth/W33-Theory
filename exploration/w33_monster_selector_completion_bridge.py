"""Exact selector-completion bridge for the local Monster 3B shell.

The previous Monster/Landauer closures fixed the local complement as

    3^7 = 3 * 3^6 = 3 * 729.

This still leaves one structural question open: does the ``729`` factor split
in a canonical way inside the live W33 theory?

It does.  The same ``729`` is simultaneously:

    - the Heisenberg irrep dimension,
    - the number of ternary Golay codewords,
    - the full ``gl(27)`` operator-basis size ``27^2``.

And inside the live bridge that ``729`` has an exact completion/deletion split

    729 = 728 + 1,

where

    728 = dim sl(27) = number of nonzero Golay codewords,
      1 = the unique selector/vacuum line.

The selector/vacuum line is not ad hoc: it is the unique invariant line on the
transport side and the unique all-ones/null line on the W33 side.

Therefore the local complement has the exact form

    3^7 = 3 * (728 + 1),

so the Monster local shell now closes through:

    center trit * (traceless sl(27) excitations + selector line).
"""

from __future__ import annotations

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
from w33_lie_tower_s12_bridge import build_lie_tower_s12_bridge_summary
from w33_monster_lagrangian_complement_bridge import build_monster_lagrangian_complement_summary
from w33_transport_path_groupoid_bridge import build_transport_path_groupoid_summary
from w33_transport_spectral_selector_bridge import build_transport_spectral_selector_summary


DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_monster_selector_completion_bridge_summary.json"


@lru_cache(maxsize=1)
def build_monster_selector_completion_summary() -> dict[str, Any]:
    monster = analyze_monster_3b_s12_sl27()
    if monster.get("available") is not True:
        raise AssertionError(f"monster 3B / s12 / sl27 bridge unavailable: {monster}")

    lie_s12 = build_lie_tower_s12_bridge_summary()
    lagrangian = build_monster_lagrangian_complement_summary()
    selector = build_transport_spectral_selector_summary()
    path_groupoid = build_transport_path_groupoid_summary()

    complement_states = int(lagrangian["lagrangian_realization"]["complement_states"])
    center_states = int(lagrangian["lagrangian_realization"]["center_states"])
    heisenberg_completion_states = int(lagrangian["lagrangian_realization"]["lagrangian_quotient_states"])

    sl27_traceless_dim = int(monster["sl27"]["traceless_dim"])
    nonzero_codewords = int(monster["golay"]["n_nonzero"])
    full_codewords = int(monster["golay"]["n_codewords"])
    selector_line_dimension = int(selector["dynamic_selection_bridge"]["invariant_line_h0_dimension"])
    projective_line = tuple(int(v) for v in path_groupoid["ternary_reduction"]["unique_invariant_projective_line"])
    w33_kernel_dimension = int(selector["w33_base_selector"]["kernel_dimension_mod_3"])

    return {
        "status": "ok",
        "selector_completion": {
            "complement_states": int(complement_states),
            "center_states": int(center_states),
            "heisenberg_completion_states": int(heisenberg_completion_states),
            "sl27_traceless_dimension": int(sl27_traceless_dim),
            "nonzero_golay_codewords": int(nonzero_codewords),
            "full_golay_codewords": int(full_codewords),
            "selector_line_dimension": int(selector_line_dimension),
            "projective_selector_line": list(projective_line),
            "w33_kernel_dimension_mod_3": int(w33_kernel_dimension),
            "full_codewords_equal_sl27_plus_selector": full_codewords == sl27_traceless_dim + selector_line_dimension,
            "nonzero_codewords_equal_sl27_traceless": nonzero_codewords == sl27_traceless_dim,
            "complement_equals_center_times_selector_completion": (
                complement_states == center_states * full_codewords
            ),
            "selector_completion_decomposition_exact": (
                complement_states == center_states * (sl27_traceless_dim + selector_line_dimension)
            ),
        },
        "cross_bridge_dictionary": {
            "sl27_z3_total_dimension": int(lie_s12["sl27_z3_bridge"]["total_dimension"]),
            "sl27_bridge_claim_holds": bool(lie_s12["sl27_z3_bridge"]["bridge_claim_holds"]),
            "golay_nonzero_equals_sl27_total": nonzero_codewords == int(lie_s12["sl27_z3_bridge"]["total_dimension"]),
            "transport_selector_is_unique": selector_line_dimension == 1,
            "w33_all_ones_spans_mod_3_kernel": bool(selector["w33_base_selector"]["all_ones_spans_mod_3_kernel"]),
            "transport_projective_selector_line_is_unique": len(projective_line) == 2,
            "path_groupoid_has_unique_invariant_line": (
                int(path_groupoid["ternary_reduction"]["common_fixed_subspace_dimension"]) == 1
            ),
        },
        "bridge_verdict": (
            "The local Monster complement is now resolved all the way down to the "
            "selector level. The same 729 that appears as the Heisenberg irrep "
            "dimension, the full ternary Golay code, and the full gl(27) operator "
            "basis also splits canonically as 728 + 1, where 728 is the live sl(27) "
            "traceless sector and 1 is the unique selector/vacuum line. That line is "
            "already canonical in the live bridge: it is the unique invariant line on "
            "the transport side and the unique all-ones/null line on the W33 side. So "
            "the Monster local-shell complement now has the exact structural form "
            "3^7 = 3*(728+1), i.e. one center trit multiplying the completed sl(27) "
            "package of traceless excitations plus selector."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_monster_selector_completion_summary(), indent=2),
        encoding="utf-8",
    )
    return path


if __name__ == "__main__":
    write_summary()
