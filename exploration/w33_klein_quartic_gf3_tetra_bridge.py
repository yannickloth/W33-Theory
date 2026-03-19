"""Exact GF(3) Klein-quartic tetra packet bridge.

For the projective Klein quartic model

    x^3 y + y^3 z + z^3 x = 0

over GF(3), the rational point set collapses to exactly four projective points:

    (1,0,0), (0,1,0), (0,0,1), (1,1,1).

Those four points are in general position (no three are collinear), so their
induced projective packet is a combinatorial tetrahedron/K4. This lands
directly on the promoted surface selector and torus/Klein shell:

    4 = q + 1 = mu = tetrahedron fixed point,
    24 = |Aut(K4)| = |Hurwitz units| = |Aut(Q8)|.

This module is intentionally narrow. It proves the GF(3) packet exactly; it
does not claim a uniform q+1 point-count theorem over all finite fields.
"""

from __future__ import annotations

from functools import lru_cache
import itertools
import json
from math import factorial
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
for candidate in (ROOT, ROOT / "exploration"):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from w33_d4_f4_tomotope_reye_bridge import build_d4_f4_tomotope_reye_summary
from w33_surface_congruence_selector_bridge import build_surface_congruence_selector_summary


DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_klein_quartic_gf3_tetra_bridge_summary.json"
FIELD = 3


def _mod(x: int) -> int:
    return x % FIELD


def _normalize(vec: tuple[int, int, int]) -> tuple[int, int, int]:
    for value in vec:
        if value != 0:
            inv = pow(value, -1, FIELD)
            return tuple(_mod(inv * coord) for coord in vec)
    raise ValueError("zero vector is not projective")


def _on_klein_quartic(vec: tuple[int, int, int]) -> bool:
    x, y, z = vec
    return _mod(x**3 * y + y**3 * z + z**3 * x) == 0


def _projective_points_on_klein_quartic() -> tuple[tuple[int, int, int], ...]:
    points = set()
    for vec in itertools.product(range(FIELD), repeat=3):
        if vec == (0, 0, 0):
            continue
        if _on_klein_quartic(vec):
            points.add(_normalize(vec))
    return tuple(sorted(points))


def _det3(a: tuple[int, int, int], b: tuple[int, int, int], c: tuple[int, int, int]) -> int:
    return _mod(
        a[0] * (b[1] * c[2] - b[2] * c[1])
        - a[1] * (b[0] * c[2] - b[2] * c[0])
        + a[2] * (b[0] * c[1] - b[1] * c[0])
    )


def _no_three_collinear(points: tuple[tuple[int, int, int], ...]) -> bool:
    return all(_det3(*triple) != 0 for triple in itertools.combinations(points, 3))


@lru_cache(maxsize=1)
def build_klein_quartic_gf3_tetra_summary() -> dict[str, Any]:
    points = _projective_points_on_klein_quartic()
    explicit_packet = (
        (0, 0, 1),
        (0, 1, 0),
        (1, 0, 0),
        (1, 1, 1),
    )
    no_three = _no_three_collinear(points)
    surface = build_surface_congruence_selector_summary()
    d4 = build_d4_f4_tomotope_reye_summary()

    tetra_value = int(surface["fixed_and_first_torus_values"]["tetrahedron_fixed_point_value"])
    first_torus_value = int(surface["fixed_and_first_torus_values"]["first_toroidal_dual_value"])
    hurwitz_unit_order = int(d4["q8_to_24cell_bridge"]["aut_q8_order"])
    packet_size = len(points)
    complete_graph_edge_count = packet_size * (packet_size - 1) // 2
    tetra_automorphism_order = factorial(packet_size)

    return {
        "status": "ok",
        "gf3_klein_quartic_packet": {
            "equation": "x^3 y + y^3 z + z^3 x = 0",
            "field": FIELD,
            "projective_points": [list(point) for point in points],
            "point_count": packet_size,
            "explicit_packet": [list(point) for point in explicit_packet],
            "explicit_packet_matches_exactly": points == explicit_packet,
            "point_count_equals_q_plus_1": packet_size == FIELD + 1,
            "point_count_equals_mu": packet_size == FIELD + 1,
            "no_three_points_are_collinear": no_three,
            "induced_projective_packet_is_k4": no_three and packet_size == 4,
            "complete_graph_edge_count": complete_graph_edge_count,
            "tetra_automorphism_order": tetra_automorphism_order,
        },
        "surface_and_hurwitz_dictionary": {
            "mu": FIELD + 1,
            "tetrahedron_fixed_point_value": tetra_value,
            "first_toroidal_dual_value": first_torus_value,
            "hurwitz_unit_order": hurwitz_unit_order,
            "point_count_matches_surface_fixed_point": packet_size == tetra_value,
            "tetra_automorphism_order_matches_hurwitz_units": (
                tetra_automorphism_order == hurwitz_unit_order
            ),
        },
        "bridge_verdict": (
            "The repo's Klein quartic model already has a sharp q=3 fixed packet. "
            "Over GF(3) it has exactly four projective points, namely the three "
            "coordinate points together with (1,1,1), and no three of them are "
            "collinear. So the Klein quartic collapses to a combinatorial "
            "tetrahedron/K4 packet exactly at q=3. That packet is the same "
            "4 = q+1 = mu and the same tetrahedral fixed point selected by the "
            "surface congruence bridge, while its automorphism order is "
            "24 = |Hurwitz units| = |Aut(Q8)|."
        ),
        "scope_note": (
            "This is a finite-field theorem for the projective Klein quartic model "
            "over GF(3). It does not claim a uniform q+1 point-count law over all "
            "finite fields."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_klein_quartic_gf3_tetra_summary(), indent=2),
        encoding="utf-8",
    )
    return path


if __name__ == "__main__":
    write_summary()
