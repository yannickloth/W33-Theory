"""Mixed-plane K3 realization reduces to one nonzero row-entry witness.

CDXXVI localized the mixed-plane wall to one supported transport-triangle row
of the off-diagonal curvature block. The next exact question is whether that
row has internal geometric structure, or whether it is still an arbitrary
vector row.

It is rigid. In the exact transport-twisted precomplex, every supported row of
the off-diagonal curvature block is one-sparse:

- exactly one nonzero column appears;
- that single nonzero entry is always `1` or `2` in `F3`.

So the positive mixed-plane wall sharpens one more step. Exact K3 tail
realization is equivalent to one support-preserving nonzero row-entry witness
on the same fixed mixed-plane host.
"""

from __future__ import annotations

from collections import Counter
from functools import lru_cache
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_PATH = (
    ROOT / "data" / "w33_k3_mixed_plane_row_entry_witness_bridge_summary.json"
)


@lru_cache(maxsize=1)
def build_k3_mixed_plane_row_entry_witness_summary() -> dict[str, Any]:
    from w33_k3_mixed_plane_triangle_row_curvature_witness_bridge import (
        build_k3_mixed_plane_triangle_row_curvature_witness_summary,
    )
    from w33_transport_twisted_precomplex_bridge import adapted_transport_precomplex_data

    triangle = build_k3_mixed_plane_triangle_row_curvature_witness_summary()
    host = triangle["canonical_mixed_plane_support"]
    data = adapted_transport_precomplex_data()

    block = data["curvature_iq"] % 3
    supported_rows = [row for row in range(block.shape[0]) if block[row].any()]

    row_support_sizes = Counter()
    entry_values = Counter()
    component_counts = Counter()
    first_examples: dict[tuple[int, int, str], tuple[int, tuple[int, int, int]]] = {}

    for row in supported_rows:
        triangle_index = row // 2
        component = "invariant_row" if row % 2 == 0 else "sign_row"
        nonzero_columns = [idx for idx, value in enumerate(block[row].tolist()) if value]
        row_support_sizes[len(nonzero_columns)] += 1
        component_counts[component] += 1
        if len(nonzero_columns) == 1:
            value = int(block[row, nonzero_columns[0]])
            entry_values[value] += 1
            first_examples.setdefault(
                (nonzero_columns[0], value, component),
                (row, data["triangles"][triangle_index]),
            )

    return {
        "status": "ok",
        "canonical_mixed_plane_support": host,
        "row_entry_witness": {
            "supported_row_count": len(supported_rows),
            "row_support_size_distribution": dict(sorted(row_support_sizes.items())),
            "entry_value_distribution": dict(sorted(entry_values.items())),
            "row_component_distribution": dict(sorted(component_counts.items())),
            "first_example_by_column_value_component": {
                f"col={column},value={value},component={component}": {
                    "row_index": row,
                    "triangle": list(triangle_data),
                }
                for (column, value, component), (row, triangle_data) in sorted(first_examples.items())
            },
        },
        "k3_mixed_plane_row_entry_witness_theorem": {
            "every_supported_row_of_the_off_diagonal_curvature_block_is_one_sparse": (
                row_support_sizes == Counter({1: 4046})
            ),
            "every_supported_row_entry_lies_in_f3_star": (
                entry_values == Counter({1: 2029, 2: 2017})
            ),
            "both_invariant_and_sign_row_components_carry_supported_entries": (
                component_counts == Counter({"sign_row": 2028, "invariant_row": 2018})
            ),
            "therefore_exact_k3_tail_realization_is_equivalent_to_one_support_preserving_nonzero_row_entry_witness_on_the_same_fixed_host": (
                row_support_sizes == Counter({1: 4046})
                and entry_values == Counter({1: 2029, 2: 2017})
                and component_counts == Counter({"sign_row": 2028, "invariant_row": 2018})
                and host["ordered_line_types"] == ["positive", "negative"]
                and list(host["mixed_signature"]) == [1, 1]
                and list(host["qutrit_lift_split"]) == [81, 81]
            ),
            "the_live_external_wall_is_now_the_first_nonzero_row_entry_witness_on_the_same_fixed_host": (
                row_support_sizes == Counter({1: 4046})
                and entry_values == Counter({1: 2029, 2: 2017})
            ),
        },
        "bridge_verdict": (
            "The mixed-plane K3 wall is now localized at the level of a single "
            "matrix entry. Every supported row of the exact off-diagonal "
            "curvature block is one-sparse, and its unique nonzero entry is "
            "always 1 or 2 in F3. So exact K3 tail realization is equivalent "
            "to one support-preserving nonzero row-entry witness on the same "
            "fixed mixed-plane host."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_k3_mixed_plane_row_entry_witness_summary(), indent=2),
        encoding="utf-8",
    )
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
