"""Exact surface congruence selector for complete-graph and complete-face seeds.

For orientable triangular embeddings and their dual complete-face-adjacency
surfaces, the genus laws are

    g_v = (v - 3)(v - 4) / 12,
    g_f = (f - 3)(f - 4) / 12.

The admissible integrality classes are the same on both sides:

    v, f ≡ 0, 3, 4, 7 (mod 12).

Inside the promoted surface package:

    4 = tetrahedron = self-dual fixed point,
    7 = first positive toroidal dual pair value,
    Csaszar lives on the v = 7 side,
    Szilassi lives on the f = 7 side.

So the toroidal route is already selected by a genuine residue law rather than
by an isolated lucky example.
"""

from __future__ import annotations

from fractions import Fraction
from functools import lru_cache
import json
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
for candidate in (ROOT, ROOT / "exploration"):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from w33_surface_neighborly_bridge import (
    csaszar_seed,
    orientable_surface_complete_face_adjacency_genus,
    orientable_surface_complete_graph_genus,
    szilassi_seed,
    tetrahedron_counts,
)


DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_surface_congruence_selector_bridge_summary.json"


def _integral_residues_mod_12(formula: str) -> list[int]:
    residues = []
    for r in range(12):
        value = (
            orientable_surface_complete_graph_genus(r)
            if formula == "vertex"
            else orientable_surface_complete_face_adjacency_genus(r)
        )
        if value.denominator == 1:
            residues.append(r)
    return residues


def _first_positive_admissible_values(limit: int = 24) -> list[int]:
    values = []
    for n in range(4, limit + 1):
        if orientable_surface_complete_graph_genus(n).denominator == 1:
            values.append(n)
    return values


@lru_cache(maxsize=1)
def build_surface_congruence_selector_summary() -> dict[str, Any]:
    vertex_residues = _integral_residues_mod_12("vertex")
    face_residues = _integral_residues_mod_12("face")
    admissible_values = _first_positive_admissible_values()
    tetrahedron = tetrahedron_counts()
    csaszar = csaszar_seed()
    szilassi = szilassi_seed()

    tetra_value = tetrahedron["vertices"]
    torus_value = csaszar.vertices

    return {
        "status": "ok",
        "surface_selector": {
            "vertex_genus_formula": "g = (v - 3)(v - 4) / 12",
            "face_genus_formula": "g = (f - 3)(f - 4) / 12",
            "vertex_integral_residues_mod_12": vertex_residues,
            "face_integral_residues_mod_12": face_residues,
            "residue_classes_match_exactly": vertex_residues == face_residues,
            "admissible_residues_are_0_3_4_7": vertex_residues == [0, 3, 4, 7],
            "first_positive_admissible_values": admissible_values,
        },
        "fixed_and_first_torus_values": {
            "tetrahedron_fixed_point_value": tetra_value,
            "tetrahedron_vertex_genus": tetrahedron["genus"],
            "tetrahedron_face_genus": orientable_surface_complete_face_adjacency_genus(tetra_value).numerator,
            "tetrahedron_is_self_dual_fixed_point": (
                tetra_value == tetrahedron["vertices"]
                and tetra_value == tetrahedron["faces"]
                and orientable_surface_complete_graph_genus(tetra_value)
                == orientable_surface_complete_face_adjacency_genus(tetra_value)
                == Fraction(0, 1)
            ),
            "first_toroidal_dual_value": torus_value,
            "csaszar_vertex_value": csaszar.vertices,
            "szilassi_face_value": szilassi.faces,
            "first_toroidal_dual_value_is_7": torus_value == 7 == szilassi.faces,
            "csaszar_and_szilassi_share_first_toroidal_value": csaszar.vertices == szilassi.faces == 7,
        },
        "bridge_verdict": (
            "The Csaszar/Szilassi route is not just a lucky torus example. The "
            "complete-graph and complete-face genus laws select the same exact "
            "integrality classes 0,3,4,7 mod 12, the tetrahedron is the "
            "self-dual fixed point at 4, and 7 is the first positive toroidal "
            "dual value. So the surface side already comes with a genuine "
            "residue selector for admissible extremal seeds."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_surface_congruence_selector_summary(), indent=2),
        encoding="utf-8",
    )
    return path


if __name__ == "__main__":
    write_summary()
