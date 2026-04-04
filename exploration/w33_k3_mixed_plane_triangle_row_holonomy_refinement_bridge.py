"""Triangle-row support is strictly finer than adapted holonomy class.

CDXXVI localized the mixed-plane wall to one supported transport-triangle row
of the off-diagonal curvature block. The next exact question is whether that
row witness is already determined by the older triangle-holonomy shadow.

It is not. In the adapted transport picture, all six reduced holonomy classes
occur, and each of those six classes contains transport triangles with:

- zero supported off-diagonal rows,
- one supported row,
- two supported rows.

So the local row witness is genuinely precomplex-local data. It strictly
refines both the parity shadow and the full reduced holonomy class.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from functools import lru_cache
import json
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_PATH = (
    ROOT
    / "data"
    / "w33_k3_mixed_plane_triangle_row_holonomy_refinement_bridge_summary.json"
)
MODULUS = 3


def _matrix_key(matrix: np.ndarray) -> str:
    return str([[int(entry) for entry in row] for row in matrix.tolist()])


@lru_cache(maxsize=1)
def build_k3_mixed_plane_triangle_row_holonomy_refinement_summary() -> dict[str, Any]:
    from w33_k3_mixed_plane_triangle_row_curvature_witness_bridge import (
        build_k3_mixed_plane_triangle_row_curvature_witness_summary,
    )
    from w33_transport_curvature_bridge import _adapted_basis
    from w33_transport_path_groupoid_bridge import directed_a2_edge_matrix
    from w33_transport_twisted_precomplex_bridge import adapted_transport_precomplex_data

    witness = build_k3_mixed_plane_triangle_row_curvature_witness_summary()
    host = witness["canonical_mixed_plane_support"]

    data = adapted_transport_precomplex_data()
    block = data["curvature_iq"] % MODULUS
    triangles = data["triangles"]

    basis, basis_inverse = _adapted_basis((1, 2))
    rows_by_triangle = defaultdict(int)
    for row in range(block.shape[0]):
        if block[row].any():
            rows_by_triangle[row // 2] += 1

    class_counts = Counter()
    row_distribution_by_class: dict[str, Counter[int]] = defaultdict(Counter)
    example_triangle_by_class_and_rows: dict[tuple[str, int], tuple[int, int, int]] = {}

    for index, triangle in enumerate(triangles):
        left, middle, right = triangle
        holonomy = (
            directed_a2_edge_matrix(right, left) % MODULUS
            @ directed_a2_edge_matrix(middle, right) % MODULUS
            @ directed_a2_edge_matrix(left, middle) % MODULUS
        ) % MODULUS
        adapted = (basis_inverse @ holonomy @ basis) % MODULUS
        class_key = _matrix_key(adapted)
        row_count = rows_by_triangle.get(index, 0)
        class_counts[class_key] += 1
        row_distribution_by_class[class_key][row_count] += 1
        example_triangle_by_class_and_rows.setdefault((class_key, row_count), triangle)

    normalized_distributions = {
        class_key: dict(sorted(counter.items()))
        for class_key, counter in sorted(row_distribution_by_class.items())
    }
    normalized_examples = {
        f"{class_key}|rows={row_count}": list(example)
        for (class_key, row_count), example in sorted(example_triangle_by_class_and_rows.items())
    }

    return {
        "status": "ok",
        "canonical_mixed_plane_support": host,
        "triangle_row_holonomy_refinement": {
            "holonomy_class_count": len(class_counts),
            "holonomy_class_sizes": dict(sorted(class_counts.items())),
            "row_support_distribution_by_holonomy_class": normalized_distributions,
            "example_triangle_by_holonomy_class_and_supported_rows": normalized_examples,
        },
        "k3_mixed_plane_triangle_row_holonomy_refinement_theorem": {
            "all_six_reduced_holonomy_classes_occur_in_the_transport_triangle_picture": (
                len(class_counts) == 6
            ),
            "every_reduced_holonomy_class_contains_triangles_with_zero_one_and_two_supported_rows": (
                all(
                    row_distribution_by_class[class_key][0] > 0
                    and row_distribution_by_class[class_key][1] > 0
                    and row_distribution_by_class[class_key][2] > 0
                    for class_key in class_counts
                )
            ),
            "in_particular_identity_holonomy_already_splits_into_zero_one_and_two_row_local_types": (
                normalized_distributions["[[1, 0], [0, 1]]"] == {0: 224, 1: 103, 2: 201}
            ),
            "therefore_triangle_row_support_is_strictly_finer_than_reduced_holonomy_class": (
                len(class_counts) == 6
                and all(
                    row_distribution_by_class[class_key][0] > 0
                    and row_distribution_by_class[class_key][1] > 0
                    and row_distribution_by_class[class_key][2] > 0
                    for class_key in class_counts
                )
            ),
            "the_live_external_wall_is_genuinely_precomplex_local_not_merely_a_holonomy_shadow_selection_problem": (
                host["ordered_line_types"] == ["positive", "negative"]
                and list(host["mixed_signature"]) == [1, 1]
                and list(host["qutrit_lift_split"]) == [81, 81]
                and normalized_distributions["[[1, 0], [0, 1]]"] == {0: 224, 1: 103, 2: 201}
                and all(
                    row_distribution_by_class[class_key][0] > 0
                    and row_distribution_by_class[class_key][1] > 0
                    and row_distribution_by_class[class_key][2] > 0
                    for class_key in class_counts
                )
            ),
        },
        "bridge_verdict": (
            "The mixed-plane K3 wall is now known to live beyond the triangle "
            "holonomy shadow. Every one of the six reduced holonomy classes "
            "already contains triangles with zero, one, and two supported "
            "off-diagonal curvature rows, including the identity class. So the "
            "local witness is genuinely precomplex-local data, not something "
            "recoverable from parity or holonomy class alone."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(
            build_k3_mixed_plane_triangle_row_holonomy_refinement_summary(), indent=2
        ),
        encoding="utf-8",
    )
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
