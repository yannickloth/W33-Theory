"""Exact channel-aware bridge from the discrete EH mode to continuum data.

The recent bridge stack already locked the scalar curved coefficients:

    c_EH,cont = 320,
    c_6 = 12480,
    c_1 = 2240.

What was still missing was a channel interpretation tying those coefficients to
the live internal structures rather than treating them as anonymous numbers.

This module packages the exact channel theorem:

1. the continuum Einstein-Hilbert coefficient is the base E6/Cartan block

       320 = 40 * 8,

   where 40 is the exact l6 spinor E6 rank and 8 is the exact l6 Cartan rank;

2. the discrete 6-mode curvature coefficient is the same base block dressed in
   two equivalent ways

       12480 = 320 * 39 = 240 * 52 = 40 * 6 * 52,

   so the same coefficient can be read as
   - the continuum base times the exact rank-39 bridge factor, or as
   - the exact six-channel A2/firewall/triality sector times F4 = 52;

3. the residual topological 1-mode is

       2240 = 40 * 56 = 320 * 7,

   so the same base 40*8 is also dressed by the E7 fundamental 56 or,
   equivalently, by Phi_6(3) = 7;

4. the same exact six-channel object appears independently as
   - l6 A2 root support size,
   - l6 spinor A2 rank,
   - ordered generation-transfer channels,
   - transport Weyl(A2) order,
   - firewall triplet fibers,
   - tomotope S3/triality factor from |Aut(T)| = 96 = 16 * 6.

So the discrete-to-continuum issue is no longer only scalar. The exact
curvature channel is already channel-aware: it propagates through the same
sixfold A2/triality/firewall structure that governs the live lie-tower side.
"""

from __future__ import annotations

from functools import lru_cache
import json
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
for candidate in (ROOT, ROOT / "exploration", ROOT / "tools", ROOT / "scripts"):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from w33_adjacency_dirac_closure_bridge import build_adjacency_dirac_closure_summary
from w33_algebraic_spine import build_algebraic_spine
from w33_center_quad_transport_a2_bridge import build_center_quad_transport_a2_summary
from w33_eh_continuum_lock_bridge import build_eh_continuum_lock_summary
from w33_l6_exceptional_gauge_return import build_l6_exceptional_gauge_return_certificate
from w33_quark_firewall_obstruction import build_quark_firewall_obstruction
from w33_tomotope_order_bridge import build_tomotope_order_summary
from w33_transport_lie_tower_bridge import (
    build_transport_lie_tower_bridge_summary,
    l6_a2_generation_channels,
)

DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_exceptional_channel_continuum_bridge_summary.json"


@lru_cache(maxsize=1)
def build_exceptional_channel_continuum_bridge_summary() -> dict[str, Any]:
    eh_lock = build_eh_continuum_lock_summary()
    adjacency = build_adjacency_dirac_closure_summary()
    l6 = build_l6_exceptional_gauge_return_certificate()
    firewall = build_quark_firewall_obstruction()
    transport_a2 = build_center_quad_transport_a2_summary()
    transport_lie = build_transport_lie_tower_bridge_summary()
    tomotope = build_tomotope_order_summary()
    exceptional = build_algebraic_spine().exceptional_parameter_dictionary

    spinor_e6_rank, spinor_a2_rank, spinor_cartan_rank = l6.spinor_action_ranks
    continuum_eh = int(eh_lock["continuum_lock"]["continuum_eh_coefficient"]["exact"])
    discrete_eh = int(eh_lock["continuum_lock"]["discrete_eh_6_mode_coefficient"]["exact"])
    topological = int(eh_lock["topological_lock"]["topological_1_mode_coefficient"]["exact"])
    rank39 = int(eh_lock["continuum_lock"]["rank_factor"]["exact"])
    edge_count = adjacency["finite_dirac_closure"]["chain_dimensions"]["c1"]

    shared_six = {
        "l6_a2_root_support": l6.a2_root_support_size,
        "l6_spinor_a2_rank": spinor_a2_rank,
        "ordered_generation_transfers": len(l6_a2_generation_channels()),
        "transport_weyl_a2_order": transport_a2["local_a2_fiber"]["weyl_group_order"],
        "firewall_triplet_fibers": len(firewall.antiquark_triad_indices) + len(firewall.quark_triad_indices),
        "tomotope_triality_factor": tomotope["tomotope"]["automorphism_group_order"] // 16,
    }
    shared_six_values = tuple(shared_six.values())
    shared_six_count = shared_six_values[0]

    continuum_base = spinor_e6_rank * spinor_cartan_rank
    discrete_via_edge_f4 = edge_count * exceptional.f4_dim
    discrete_via_six_f4 = spinor_e6_rank * shared_six_count * exceptional.f4_dim
    phi6 = exceptional.e7_fund_dim // spinor_cartan_rank
    topological_via_e7 = spinor_e6_rank * exceptional.e7_fund_dim

    return {
        "status": "ok",
        "base_continuum_channel": {
            "spinor_e6_rank": spinor_e6_rank,
            "spinor_cartan_rank": spinor_cartan_rank,
            "continuum_eh_coefficient": continuum_eh,
            "continuum_equals_spinor_e6_times_cartan": continuum_eh == continuum_base,
        },
        "shared_six_channel": {
            **shared_six,
            "all_equal_to_6": len(set(shared_six_values)) == 1 and shared_six_count == 6,
        },
        "discrete_curvature_channel": {
            "discrete_6_mode_coefficient": discrete_eh,
            "rank39_factor": rank39,
            "w33_edge_count": edge_count,
            "f4_dimension": exceptional.f4_dim,
            "discrete_equals_continuum_times_rank39": discrete_eh == continuum_eh * rank39,
            "discrete_equals_edges_times_f4": discrete_eh == discrete_via_edge_f4,
            "discrete_equals_spinor_e6_times_shared_six_times_f4": discrete_eh == discrete_via_six_f4,
            "cartan_rank_times_rank39": spinor_cartan_rank * rank39,
            "shared_six_times_f4": shared_six_count * exceptional.f4_dim,
            "cartan_rank_times_rank39_equals_shared_six_times_f4": (
                spinor_cartan_rank * rank39 == shared_six_count * exceptional.f4_dim
            ),
        },
        "topological_channel": {
            "topological_1_mode_coefficient": topological,
            "e7_fundamental_dimension": exceptional.e7_fund_dim,
            "phi6": phi6,
            "topological_equals_spinor_e6_times_e7_fund": topological == topological_via_e7,
            "topological_equals_continuum_times_phi6": topological == continuum_eh * phi6,
        },
        "tomotope_triality_bridge": {
            "tomotope_automorphism_order": tomotope["tomotope"]["automorphism_group_order"],
            "tomotope_automorphism_equals_16_times_shared_six": (
                tomotope["tomotope"]["automorphism_group_order"] == 16 * shared_six_count
            ),
            "universal_cover_automorphism_order": tomotope["uniform_cover"]["automorphism_group_order"],
            "universal_cover_equals_2_times_tomotope_automorphism": (
                tomotope["uniform_cover"]["automorphism_group_order"]
                == 2 * tomotope["tomotope"]["automorphism_group_order"]
            ),
        },
        "transport_lie_crosscheck": {
            "complete_oriented_three_generation_graph": transport_lie["generation_channel_theorem"][
                "complete_oriented_three_generation_graph"
            ],
            "all_a2_channels_are_signed_permutation_blocks": transport_lie["generation_channel_theorem"][
                "all_a2_channels_are_signed_permutation_blocks"
            ],
            "all_cartan_modes_are_generation_diagonal": transport_lie["generation_channel_theorem"][
                "all_cartan_modes_are_generation_diagonal"
            ],
            "firewall_full_clean_quark_block_exists": firewall.full_clean_quark_block_exists,
        },
        "bridge_verdict": (
            "The discrete-to-continuum bridge is now channel-aware. The continuum "
            "Einstein-Hilbert coefficient is exactly the l6 spinor E6/Cartan base "
            "block 40*8 = 320. The discrete curved 6-mode is the same base block "
            "lifted through the exact six-channel A2/triality sector, because the "
            "same number 6 appears as the l6 A2 support, the ordered generation "
            "transfer graph, the transport Weyl(A2) order, the six triplet "
            "firewall fibers, and the tomotope triality factor in 96 = 16*6. "
            "Equivalently, the discrete 6-mode factorizes as 240*52, so the W33 "
            "edge/E8-root count is dressed by the F4 channel tied to the "
            "tomotope/24-cell route. The residual topological mode is likewise "
            "40*56 = 320*7. So the live scalar bridge is already carrying the same "
            "internal channel structure as the lie tower and the firewall; the "
            "remaining continuum theorem should lift this channel-aware law, not "
            "replace it with a new fit."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_exceptional_channel_continuum_bridge_summary(), indent=2),
        encoding="utf-8",
    )
    return path


if __name__ == "__main__":
    write_summary()
