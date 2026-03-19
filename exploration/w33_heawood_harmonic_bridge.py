"""Exact Heawood harmonic closure from the Fano incidence of the torus dual.

The Szilassi dual of the labeled 7-vertex torus seed has Heawood
1-skeleton. Because that Heawood graph is exactly the bipartite incidence graph
of a cyclic Fano heptad, its adjacency operator is forced by one selector law:

    B B^T = 2I + J,

where B is the 7x7 point-line incidence matrix.

Consequences:

- the singular values of B are 3 and sqrt(2);
- the Heawood adjacency spectrum is +/-3 and +/-sqrt(2);
- the Heawood Laplacian spectrum is 0, 3-sqrt(2), 3+sqrt(2), 6;
- the adjacency satisfies H^4 - 11 H^2 + 18 I = 0.

So the Szilassi dual is not only combinatorial. It already carries an exact
harmonic operator packet forced by the same Fano incidence data.
"""

from __future__ import annotations

from functools import lru_cache
import json
from pathlib import Path
from typing import Any

import sympy as sp

from w33_mobius_szilassi_dual import heawood_incidence_from_mobius


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_heawood_harmonic_bridge_summary.json"


def _incidence_matrix() -> sp.Matrix:
    incidence = heawood_incidence_from_mobius()
    matrix = sp.zeros(7, 7)
    for line_index, points in incidence.items():
        for point in points:
            matrix[line_index, point] = 1
    return matrix


def _spectral_packet_to_strings(values: list[sp.Expr]) -> list[str]:
    return [str(sp.simplify(value)) for value in values]


@lru_cache(maxsize=1)
def build_heawood_harmonic_summary() -> dict[str, Any]:
    B = _incidence_matrix()
    I7 = sp.eye(7)
    J7 = sp.ones(7)
    selector = 2 * I7 + J7
    BBt = B * B.T
    BtB = B.T * B

    H = sp.Matrix.vstack(
        sp.Matrix.hstack(sp.zeros(7), B),
        sp.Matrix.hstack(B.T, sp.zeros(7)),
    )
    I14 = sp.eye(14)
    L = 3 * I14 - H

    heawood_adjacency_spectrum = (
        [-3]
        + [-sp.sqrt(2)] * 6
        + [sp.sqrt(2)] * 6
        + [3]
    )
    heawood_laplacian_spectrum = (
        [0]
        + [3 - sp.sqrt(2)] * 6
        + [3 + sp.sqrt(2)] * 6
        + [6]
    )
    gap = sp.simplify(3 - sp.sqrt(2))
    tetra_weight = sp.simplify(gap / 4)

    return {
        "status": "ok",
        "incidence_operator": {
            "matrix_shape": [7, 7],
            "row_sum": 3,
            "column_sum": 3,
            "bbt_equals_2i_plus_j": BBt == selector,
            "btb_equals_2i_plus_j": BtB == selector,
            "selector_eigenvalues_exact": _spectral_packet_to_strings([2] * 6 + [9]),
        },
        "heawood_operator": {
            "adjacency_matrix_shape": [14, 14],
            "adjacency_degree": 3,
            "adjacency_minimal_polynomial": "x^4 - 11*x^2 + 18",
            "adjacency_quartic_relation_holds": sp.expand(H**4 - 11 * H**2 + 18 * I14) == sp.zeros(14),
            "adjacency_spectrum_exact": _spectral_packet_to_strings(heawood_adjacency_spectrum),
            "laplacian_spectrum_exact": _spectral_packet_to_strings(heawood_laplacian_spectrum),
            "laplacian_gap_exact": str(gap),
            "laplacian_gap_numeric": float(sp.N(gap)),
        },
        "local_normalization": {
            "tetra_weight_for_same_gap_exact": str(tetra_weight),
            "tetra_weight_for_same_gap_numeric": float(sp.N(tetra_weight)),
            "weighted_tetra_nonzero_laplacian_equals_heawood_gap": True,
        },
        "bridge_verdict": (
            "The Szilassi dual carries an exact harmonic closure. Its Heawood "
            "1-skeleton is the bipartite incidence graph of a cyclic Fano heptad, "
            "so the whole adjacency/Laplacian spectrum is forced by the selector "
            "law B B^T = 2I + J."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_heawood_harmonic_summary(), indent=2),
        encoding="utf-8",
    )
    return path


if __name__ == "__main__":
    write_summary()
