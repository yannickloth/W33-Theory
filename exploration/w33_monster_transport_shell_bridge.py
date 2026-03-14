"""Exact transport-shell dictionary for the Monster q^7 complement.

The q^5-completion bridge already proved that the local Monster complement

    3^7 = 2187

has the exact live split

    2187 = 2160 + 27,

where ``2160`` is the semisimple transport-curvature channel and ``27`` is the
generation block.

The next structural question is whether that ``2160`` is merely one transport
count or whether it is already a native dictionary across the exact W33
transport/operator/Lie package.

It is:

    2160 = q^2 * 240 = q * 720 = 16 * 135

with factors

    240  = W33 edge / E8-root count,
    720  = exact transport-edge count on the 45-point quotient graph,
    135  = exact local-line connection-bundle dimension,
    16   = exact A2 transfer-block rank,
    27   = exact generation block.

So the local Monster complement becomes

    3^7 = (q^2 * |E_W33|) + q^3
        = (q * |E_transport|) + q^3
        = (rank block_A2 * dim bundle_135) + q^3.

This is the sharpest transport-side realization yet of the Monster complement.
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

from w33_center_quad_transport_complement_bridge import (
    build_center_quad_transport_complement_summary,
)
from w33_center_quad_transport_operator_bridge import (
    build_center_quad_transport_operator_summary,
)
from w33_exceptional_tensor_rank_bridge import build_exceptional_tensor_rank_summary
from w33_monster_q5_completion_bridge import build_monster_q5_completion_summary


DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_monster_transport_shell_bridge_summary.json"


@lru_cache(maxsize=1)
def build_monster_transport_shell_summary() -> dict[str, Any]:
    monster_q5 = build_monster_q5_completion_summary()
    transport = build_center_quad_transport_complement_summary()
    transport_operator = build_center_quad_transport_operator_summary()
    tensor_rank = build_exceptional_tensor_rank_summary()

    q = int(monster_q5["q5_restoration"]["q"])
    complement_states = int(monster_q5["monster_completion_dictionary"]["complement_states"])
    semisimple_curved_states = int(
        monster_q5["transport_curvature_dictionary"]["semisimple_curved_states"]
    )
    generation_states = int(monster_q5["transport_curvature_dictionary"]["generation_states"])
    w33_edge_count = int(monster_q5["w33_q5_dictionary"]["edge_count"])
    transport_edge_count = int(transport["transport_graph_srg"]["edge_count"])
    local_line_bundle_dimension = int(
        transport_operator["connection_bundle"]["total_dimension"]
    )
    a2_transfer_block_rank = int(tensor_rank["base_ranks"]["a2_transfer_block_rank"])

    return {
        "status": "ok",
        "transport_shell_dictionary": {
            "q": q,
            "w33_edge_count": w33_edge_count,
            "transport_edge_count": transport_edge_count,
            "local_line_bundle_dimension": local_line_bundle_dimension,
            "a2_transfer_block_rank": a2_transfer_block_rank,
            "semisimple_transport_shell": semisimple_curved_states,
            "generation_states": generation_states,
            "monster_complement_states": complement_states,
            "semisimple_equals_q_squared_times_w33_edges": (
                semisimple_curved_states == q**2 * w33_edge_count
            ),
            "semisimple_equals_q_times_transport_edges": (
                semisimple_curved_states == q * transport_edge_count
            ),
            "semisimple_equals_a2_block_rank_times_bundle_dimension": (
                semisimple_curved_states
                == a2_transfer_block_rank * local_line_bundle_dimension
            ),
        },
        "monster_transport_completion": {
            "complement_equals_semisimple_plus_generation": (
                complement_states == semisimple_curved_states + generation_states
            ),
            "complement_equals_q_squared_edges_plus_q_cubed": (
                complement_states == q**2 * w33_edge_count + q**3
            ),
            "complement_equals_q_transport_edges_plus_q_cubed": (
                complement_states == q * transport_edge_count + q**3
            ),
            "complement_equals_block_bundle_plus_generation": (
                complement_states
                == a2_transfer_block_rank * local_line_bundle_dimension + generation_states
            ),
        },
        "bridge_verdict": (
            "The local Monster complement is now a transport-shell theorem, not "
            "just a q-power identity. The semisimple transport-curvature shell "
            "2160 is simultaneously q^2 times the W33 edge/E8-root count, q "
            "times the exact transport-edge count on the 45-point quotient, and "
            "the product of the exact A2 transfer-block rank 16 with the exact "
            "135-dimensional local-line connection bundle. Adding back the exact "
            "27-state generation block then recovers the whole local Monster "
            "complement: 3^7 = 2160 + 27. So the Monster q^7 factor is now "
            "realized directly inside the live transport/operator/Lie stack."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_monster_transport_shell_summary(), indent=2),
        encoding="utf-8",
    )
    return path


if __name__ == "__main__":
    write_summary()
