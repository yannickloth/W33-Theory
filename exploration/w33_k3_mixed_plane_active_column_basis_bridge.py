"""The mixed-plane wall lives on a full-rank 36-column active complement.

CDXXXI established that the row-entry witness does not depend on a special
choice among the active curvature columns. The next question is whether the
active/inactive split itself carries exact structure, or whether it is only a
support bookkeeping artifact.

It carries exact structure:

- the off-diagonal curvature block has rank 36;
- exactly 36 columns are active, and their restricted block already has rank
  36, so they form a full-rank basis complement for the live wall;
- the remaining 9 inactive columns are not arbitrary: their induced graph
  complement splits into 3 disjoint triples.

So the live wall no longer ranges over all 45 sign channels. Exact K3 tail
realization is equivalent to the first nonzero row-entry witness on the
full-rank 36-column active complement.
"""

from __future__ import annotations

from functools import lru_cache
import json
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_PATH = (
    ROOT / "data" / "w33_k3_mixed_plane_active_column_basis_bridge_summary.json"
)


def _inactive_complement_triples(inactive_columns: list[int], adjacency: set[tuple[int, int]]) -> list[list[int]]:
    remaining = set(inactive_columns)
    triples: list[list[int]] = []
    while remaining:
        start = min(remaining)
        stack = [start]
        component = set()
        while stack:
            node = stack.pop()
            if node in component:
                continue
            component.add(node)
            for other in inactive_columns:
                if other == node or other in component:
                    continue
                edge = (min(node, other), max(node, other))
                if edge in adjacency:
                    stack.append(other)
        triples.append(sorted(component))
        remaining -= component
    return sorted(triples)


@lru_cache(maxsize=1)
def build_k3_mixed_plane_active_column_basis_summary() -> dict[str, Any]:
    from w33_center_quad_transport_bridge import reconstructed_quotient_graph
    from w33_k3_mixed_plane_column_chart_universality_bridge import (
        build_k3_mixed_plane_column_chart_universality_summary,
    )
    from w33_transport_twisted_precomplex_bridge import (
        _rank_mod_p,
        adapted_transport_precomplex_data,
    )

    column = build_k3_mixed_plane_column_chart_universality_summary()
    host = column["canonical_mixed_plane_support"]

    data = adapted_transport_precomplex_data()
    block = np.array(data["curvature_iq"], dtype=int) % 3
    active_columns = [col for col in range(block.shape[1]) if np.any(block[:, col])]
    inactive_columns = [col for col in range(block.shape[1]) if not np.any(block[:, col])]
    active_rank = _rank_mod_p(block[:, active_columns])

    graph, _ = reconstructed_quotient_graph()
    inactive_complement_edges = {
        (left, right)
        for index, left in enumerate(inactive_columns)
        for right in inactive_columns[index + 1 :]
        if not graph.has_edge(left, right)
    }
    inactive_triples = _inactive_complement_triples(inactive_columns, inactive_complement_edges)

    return {
        "status": "ok",
        "canonical_mixed_plane_support": host,
        "mixed_plane_active_column_basis": {
            "total_curvature_columns": block.shape[1],
            "active_columns": active_columns,
            "inactive_columns": inactive_columns,
            "active_column_count": len(active_columns),
            "inactive_column_count": len(inactive_columns),
            "off_diagonal_curvature_rank": _rank_mod_p(block),
            "active_column_restricted_rank": active_rank,
            "inactive_column_complement_triples": inactive_triples,
        },
        "k3_mixed_plane_active_column_basis_theorem": {
            "the_36_active_columns_already_match_the_full_off_diagonal_curvature_rank": (
                len(active_columns) == 36
                and _rank_mod_p(block) == 36
                and active_rank == 36
            ),
            "the_remaining_9_columns_form_a_rigid_inert_block_split_into_3_complement_triples": (
                len(inactive_columns) == 9
                and inactive_triples == [[36, 40, 44], [37, 41, 42], [38, 39, 43]]
            ),
            "therefore_exact_k3_tail_realization_is_equivalent_to_the_first_nonzero_row_entry_witness_on_the_full_rank_36_column_active_complement": (
                len(active_columns) == 36
                and _rank_mod_p(block) == 36
                and active_rank == 36
                and inactive_triples == [[36, 40, 44], [37, 41, 42], [38, 39, 43]]
                and host["ordered_line_types"] == ["positive", "negative"]
                and list(host["mixed_signature"]) == [1, 1]
                and list(host["qutrit_lift_split"]) == [81, 81]
            ),
            "the_live_external_wall_no_longer_ranges_over_all_45_sign_channels": (
                len(active_columns) == 36
                and len(inactive_columns) == 9
                and active_rank == 36
            ),
        },
        "bridge_verdict": (
            "The mixed-plane wall now lives on a full-rank 36-column active "
            "complement. Those 36 active columns already realize the full "
            "off-diagonal curvature rank, while the remaining 9 inactive "
            "columns form a rigid inert block split into three complement "
            "triples. So exact K3 tail realization is equivalent to the first "
            "nonzero row-entry witness on that 36-column active complement."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_k3_mixed_plane_active_column_basis_summary(), indent=2),
        encoding="utf-8",
    )
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
