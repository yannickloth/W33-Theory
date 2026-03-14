"""Exact q^5-restoration bridge for the local Monster selector completion.

The selector-completion bridge already proved that the local Monster complement
has the exact form

    3^7 = 3 * (728 + 1),

where ``728`` is the live traceless ``sl(27)`` sector and ``1`` is the unique
selector/vacuum line.

The next structural question is whether that completion is only a formal
``728+1`` fix or whether it restores the native q=3 geometry more deeply.

It does.  The exact block-cyclic ``sl(27)`` bridge has grade split

    (242, 243, 243) = (q^5 - 1, q^5, q^5)

at q = 3.  Adding back the unique selector line restores the deficient first
block and yields

    729 = 243 + 243 + 243 = 3 * q^5.

Therefore the local Monster complement becomes

    3^7 = 3 * 729 = 3 * (243 + 243 + 243) = q^7.

So the selector completion is not arbitrary. It restores three exact q^5
blocks, and the local Monster complement is exactly the next q-power above the
live q^5 state count.
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

from w33_lie_tower_s12_bridge import build_lie_tower_s12_bridge_summary
from w33_monster_selector_completion_bridge import (
    build_monster_selector_completion_summary,
)
from w33_standard_model_cyclotomic_bridge import build_standard_model_cyclotomic_summary
from w33_transport_borel_factor_bridge import build_transport_borel_factor_summary
from w33_witting_srg_bridge import build_witting_srg_bridge_summary


DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_monster_q5_completion_bridge_summary.json"


@lru_cache(maxsize=1)
def build_monster_q5_completion_summary() -> dict[str, Any]:
    lie_s12 = build_lie_tower_s12_bridge_summary()
    selector_completion = build_monster_selector_completion_summary()
    standard_model = build_standard_model_cyclotomic_summary()
    transport_borel = build_transport_borel_factor_summary()
    witting = build_witting_srg_bridge_summary()

    q = int(standard_model["cyclotomic_data"]["q"])
    q5 = q**5
    q7 = q**7

    grade_split = [int(v) for v in lie_s12["s12_grade_only_model"]["grade_split"]]
    selector_line = int(selector_completion["selector_completion"]["selector_line_dimension"])
    restored_blocks = [grade_split[0] + selector_line, grade_split[1], grade_split[2]]

    full_codewords = int(selector_completion["selector_completion"]["full_golay_codewords"])
    complement_states = int(selector_completion["selector_completion"]["complement_states"])
    edge_count = int(witting["orthogonality_graph"]["edges"])
    semisimple_curved_states = int(
        transport_borel["triangle_channel_split"]["semisimple_curved_total"]
    )
    generation_states = q**3

    return {
        "status": "ok",
        "q5_restoration": {
            "q": int(q),
            "q5": int(q5),
            "q7": int(q7),
            "grade_split": list(grade_split),
            "selector_line_dimension": int(selector_line),
            "grade0_equals_q5_minus_1": grade_split[0] == q5 - 1,
            "grade1_equals_q5": grade_split[1] == q5,
            "grade2_equals_q5": grade_split[2] == q5,
            "restored_blocks": list(restored_blocks),
            "restored_blocks_are_three_q5_blocks": restored_blocks == [q5, q5, q5],
            "full_codewords": int(full_codewords),
            "full_codewords_equal_3q5": full_codewords == 3 * q5,
        },
        "monster_completion_dictionary": {
            "complement_states": int(complement_states),
            "complement_equals_center_times_full_codewords": (
                complement_states == q * full_codewords
            ),
            "complement_equals_q_times_three_q5_blocks": (
                complement_states == q * (restored_blocks[0] + restored_blocks[1] + restored_blocks[2])
            ),
            "complement_equals_q7": complement_states == q7,
        },
        "w33_q5_dictionary": {
            "edge_count": int(edge_count),
            "edge_count_equals_q5_minus_q": edge_count == q5 - q,
            "grade0_minus_edge_count": grade_split[0] - edge_count,
            "restored_block_minus_edge_count": restored_blocks[0] - edge_count,
        },
        "transport_curvature_dictionary": {
            "semisimple_curved_states": int(semisimple_curved_states),
            "generation_states": int(generation_states),
            "semisimple_curved_equals_q_squared_times_edges": (
                semisimple_curved_states == q**2 * edge_count
            ),
            "semisimple_curved_equals_q7_minus_q3": (
                semisimple_curved_states == q7 - q**3
            ),
            "complement_equals_semisimple_curved_plus_generation": (
                complement_states == semisimple_curved_states + generation_states
            ),
            "complement_equals_q_squared_edges_plus_q_cubed": (
                complement_states == q**2 * edge_count + q**3
            ),
        },
        "bridge_verdict": (
            "The selector completion restores the native q=3 geometry all the way. "
            "The old sl(27) grade split is exactly (q^5-1,q^5,q^5), and adding back "
            "the unique selector line restores it to three exact q^5 blocks: "
            "729 = 243+243+243 = 3*q^5. Therefore the local Monster complement is "
            "not just 3*(728+1); it is exactly q*3*q^5 = q^7. Better, because the "
            "live W33 edge count is q^5-q and the semisimple transport-curvature "
            "channel is q^2 times that edge count, the same complement also has the "
            "exact curved split q^7 = q^2(q^5-q) + q^3. At q=3 this is 2187 = 2160 "
            "+ 27: semisimple transport curvature plus the generation block. So the "
            "local Monster closure now sits directly on the same q^5 arithmetic and "
            "transport-curvature geometry that already govern the live W33 program."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_monster_q5_completion_summary(), indent=2),
        encoding="utf-8",
    )
    return path


if __name__ == "__main__":
    write_summary()
