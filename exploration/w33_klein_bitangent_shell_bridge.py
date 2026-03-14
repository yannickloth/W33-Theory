"""Exact Klein bitangent shell ladder across ambient, classical, and topological channels.

The promoted Klein/quartic packet already proved

    28 = q^3 + 1                         (quartic bitangents)
    364 = 28 * 13                        (ambient Klein shell)
    728 = 28 * 26                        (full sl(27) = A_26 shell)
    2240 = 40 * 56 = 28 * 80            (live topological coefficient)

This module packages the stronger common statement:

    the same bitangent shell 28 dresses

        Phi_3 = 13          -> 364
        rank(A_26) = 26     -> 728
        |Str| = |chi| = 80  -> 2240

So the quartic bitangent packet is not merely one more geometric shadow. It is
the exact common multiplier that links the ambient Klein space, the classical
A-line shell, and the live finite Euler/supertrace topological channel.
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

from w33_klein_clifford_topological_bridge import (
    build_klein_clifford_topological_summary,
)
from w33_monster_supertrace_bridge import build_monster_supertrace_summary
from w33_s12_vogel_spine_bridge import build_s12_vogel_spine_summary


DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_klein_bitangent_shell_bridge_summary.json"


@lru_cache(maxsize=1)
def build_klein_bitangent_shell_summary() -> dict[str, Any]:
    klein_topology = build_klein_clifford_topological_summary()
    vogel = build_s12_vogel_spine_summary()
    supertrace = build_monster_supertrace_summary()

    clifford = klein_topology["clifford_quartic_lift"]
    ambient = klein_topology["ambient_shell_lift"]
    vogel_a = vogel["vogel_a_line_dictionary"]
    spectral = supertrace["spectral_dictionary"]

    bitangents = int(clifford["plane_quartic_bitangent_count"])
    phi3 = int(clifford["phi3"])
    quartic_triangles = int(clifford["klein_quartic_triangle_count"])
    w33_slice = int(clifford["w33_klein_slice_points"])
    topological = int(clifford["topological_1_mode_coefficient"])
    ambient_pg53 = int(ambient["ambient_pg53_points"])
    sl27_shell = int(ambient["sl27_shell_dimension"])
    a26_rank = int(vogel_a["a_family_rank"])
    supertrace_magnitude = int(spectral["supertrace_magnitude"])
    euler_magnitude = abs(int(spectral["euler_characteristic"]))

    topological_over_ambient = Fraction(topological, ambient_pg53)
    topological_over_sl27 = Fraction(topological, sl27_shell)

    return {
        "status": "ok",
        "bitangent_shell_dictionary": {
            "bitangent_shell": bitangents,
            "phi3": phi3,
            "a26_rank": a26_rank,
            "quartic_triangle_shell": quartic_triangles,
            "w33_slice": w33_slice,
            "supertrace_magnitude": supertrace_magnitude,
            "euler_magnitude": euler_magnitude,
            "ambient_pg53_points": ambient_pg53,
            "sl27_shell_dimension": sl27_shell,
            "topological_1_mode_coefficient": topological,
            "ambient_equals_bitangents_times_phi3": ambient_pg53 == bitangents * phi3,
            "sl27_equals_bitangents_times_a26_rank": sl27_shell == bitangents * a26_rank,
            "topological_equals_bitangents_times_supertrace_magnitude": (
                topological == bitangents * supertrace_magnitude
            ),
            "topological_equals_bitangents_times_euler_magnitude": (
                topological == bitangents * euler_magnitude
            ),
            "quartic_triangles_equals_two_times_bitangents": quartic_triangles == 2 * bitangents,
            "quartic_triangles_equals_cartan_times_phi6": quartic_triangles == 8 * 7,
            "topological_equals_w33_slice_times_quartic_triangles": (
                topological == w33_slice * quartic_triangles
            ),
            "a26_rank_equals_two_times_phi3": a26_rank == 2 * phi3,
            "dressings": [1, phi3, a26_rank, supertrace_magnitude],
            "shell_ladder": [bitangents, ambient_pg53, sl27_shell, topological],
            "topological_over_ambient": str(topological_over_ambient),
            "topological_over_sl27": str(topological_over_sl27),
        },
        "bridge_verdict": (
            "The quartic bitangent shell is now a live algebraic ladder rather "
            "than a standalone quartic count. The same 28 = q^3 + 1 simultaneously "
            "dresses Phi_3 = 13 to give the ambient Klein shell 364, dresses "
            "rank(A_26) = 26 to give the full sl(27) shell 728, and dresses the "
            "exact finite Euler/McKean-Singer magnitude 80 to give the live "
            "topological coefficient 2240. So the ambient Klein shell, the "
            "classical A-line shell, and the curved topological 1-mode are all one "
            "bitangent-shell law."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_klein_bitangent_shell_summary(), indent=2),
        encoding="utf-8",
    )
    return path


if __name__ == "__main__":
    write_summary()
