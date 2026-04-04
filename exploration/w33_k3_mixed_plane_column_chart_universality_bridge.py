"""Every supported curvature column is a valid local chart for the wall.

CDXXIX reduced the mixed-plane K3 realization problem to one support-preserving
nonzero row-entry witness on the fixed host. The next question is whether that
entry still depends on a special curvature column.

It does not. In the exact transport-twisted precomplex:

- the curvature block has 45 columns in total;
- exactly 36 of them are active, carrying supported row entries;
- every active column carries both invariant and sign-row support;
- every active column carries both nonzero field values 1 and 2.

So the live wall is not a column-choice problem. Exact K3 tail realization is
equivalent to a support-preserving nonzero row-entry witness in any fixed
supported curvature column.
"""

from __future__ import annotations

from collections import Counter
from functools import lru_cache
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_PATH = (
    ROOT / "data" / "w33_k3_mixed_plane_column_chart_universality_bridge_summary.json"
)


@lru_cache(maxsize=1)
def build_k3_mixed_plane_column_chart_universality_summary() -> dict[str, Any]:
    from w33_k3_mixed_plane_row_entry_witness_bridge import (
        build_k3_mixed_plane_row_entry_witness_summary,
    )
    from w33_transport_twisted_precomplex_bridge import adapted_transport_precomplex_data

    row_entry = build_k3_mixed_plane_row_entry_witness_summary()
    host = row_entry["canonical_mixed_plane_support"]
    block = adapted_transport_precomplex_data()["curvature_iq"] % 3

    column_profiles: dict[int, dict[str, Any]] = {}
    component_presence = Counter()
    value_presence = Counter()
    supported_column_count = 0

    for column in range(block.shape[1]):
        supported_rows = [row for row in range(block.shape[0]) if int(block[row, column]) != 0]
        row_components = Counter("invariant_row" if row % 2 == 0 else "sign_row" for row in supported_rows)
        values = Counter(int(block[row, column]) for row in supported_rows)

        if supported_rows:
            supported_column_count += 1
        if len(row_components) == 2:
            component_presence["both_components"] += 1
        if len(values) == 2:
            value_presence["both_values"] += 1

        column_profiles[column] = {
            "supported_row_count": len(supported_rows),
            "row_component_distribution": dict(sorted(row_components.items())),
            "entry_value_distribution": dict(sorted(values.items())),
        }

    return {
        "status": "ok",
        "canonical_mixed_plane_support": host,
        "column_chart_profiles": column_profiles,
        "column_chart_universality": {
            "curvature_column_count": len(column_profiles),
            "supported_column_count": supported_column_count,
            "columns_with_both_row_components": component_presence["both_components"],
            "columns_with_both_nonzero_values": value_presence["both_values"],
        },
        "k3_mixed_plane_column_chart_universality_theorem": {
            "exactly_36_of_the_45_curvature_columns_are_active": (
                len(column_profiles) == 45 and supported_column_count == 36
            ),
            "every_active_curvature_column_carries_both_invariant_and_sign_row_support": (
                component_presence["both_components"] == supported_column_count == 36
            ),
            "every_active_curvature_column_carries_both_nonzero_f3_values": (
                value_presence["both_values"] == supported_column_count == 36
            ),
            "therefore_exact_k3_tail_realization_is_equivalent_to_a_nonzero_row_entry_witness_in_any_fixed_supported_curvature_column": (
                len(column_profiles) == 45
                and supported_column_count == 36
                and component_presence["both_components"] == supported_column_count
                and value_presence["both_values"] == supported_column_count
                and host["ordered_line_types"] == ["positive", "negative"]
                and list(host["mixed_signature"]) == [1, 1]
                and list(host["qutrit_lift_split"]) == [81, 81]
            ),
            "the_live_external_wall_is_not_a_choice_among_the_36_active_columns": (
                len(column_profiles) == 45
                and supported_column_count == 36
                and component_presence["both_components"] == supported_column_count
                and value_presence["both_values"] == supported_column_count
            ),
        },
        "bridge_verdict": (
            "The curvature block has 45 columns, but exactly 36 are active. "
            "Each active column already sees both row components and both "
            "nonzero field values. So exact K3 tail realization is equivalent "
            "to a support-preserving nonzero row-entry witness in any fixed "
            "supported curvature column, not to a special choice among the "
            "36 active columns."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_k3_mixed_plane_column_chart_universality_summary(), indent=2),
        encoding="utf-8",
    )
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
