"""Exact Klein-quadric / Clifford / topological-channel bridge.

The promoted algebra shell already contains a rigid Klein/quartic packet:

    external plane points        = 13 = Phi_3
    plane-quartic bitangents     = 28 = q^3 + 1
    Klein-quartic triangles      = 56 = E7_fund = 2 * 28
    ambient Klein space size     = 364 = 28 * 13
    traceless sl(27) shell       = 728 = 56 * 13

The curved bridge already identifies the live topological coefficient as

    a2 = 2240 = 40 * 56,

where 40 is the promoted W33 slice and 56 is the promoted E7-fundamental
dimension.

This module packages the resulting exact lift:

    Clifford external plane (13)
        -> quartic bitangent shell (28)
        -> quartic / E7 shell (56)
        -> ambient Klein shell (364 = 28 * 13)
        -> full sl(27) shell (728 = 56 * 13)
        -> live topological coefficient (2240 = 40 * 56)

So the topological channel is not just another scalar in the curved bridge. It
is already the Klein/quartic packet lifted by the exact W33 slice.
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

from w33_algebraic_spine import build_algebraic_spine
from w33_eh_continuum_lock_bridge import build_eh_continuum_lock_summary
from w33_klein_harmonic_vogel_bridge import build_klein_harmonic_vogel_summary
from w33_s12_klein_projective_bridge import build_s12_klein_projective_summary


DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_klein_clifford_topological_bridge_summary.json"


@lru_cache(maxsize=1)
def build_klein_clifford_topological_summary() -> dict[str, Any]:
    s12 = build_s12_klein_projective_summary()
    klein = build_klein_harmonic_vogel_summary()
    eh = build_eh_continuum_lock_summary()
    exceptional = build_algebraic_spine().exceptional_parameter_dictionary

    q = int(s12["harmonic_cube_square_dictionary"]["q"])
    phi3 = int(
        s12["quartic_parallelism_guide_rail"]["clifford_parallelism_external_plane_points"]
    )
    bitangents = int(s12["quartic_parallelism_guide_rail"]["plane_quartic_bitangent_count"])
    ambient_pg53 = int(s12["harmonic_cube_square_dictionary"]["ambient_pg53_points"])
    w33_slice = int(s12["harmonic_cube_square_dictionary"]["w33_klein_slice_points"])

    quartic_triangles = int(klein["harmonic_quartic_dictionary"]["klein_quartic_triangles"])
    sl27_shell = int(klein["harmonic_quartic_dictionary"]["sl27_shell_dimension"])
    g2_dim = int(klein["harmonic_quartic_dictionary"]["g2_dimension"])

    topological = int(eh["topological_lock"]["topological_1_mode_coefficient"]["exact"])
    q_cubic_plus_1 = int(eh["topological_lock"]["q_cubic_plus_1"])
    e7_fund = int(exceptional.e7_fund_dim)
    phi6 = q * q - q + 1
    cartan_rank = e7_fund // phi6

    return {
        "status": "ok",
        "clifford_quartic_lift": {
            "q": q,
            "phi3": phi3,
            "phi6": phi6,
            "clifford_parallelism_external_plane_points": phi3,
            "plane_quartic_bitangent_count": bitangents,
            "klein_quartic_triangle_count": quartic_triangles,
            "e7_fundamental_dimension": e7_fund,
            "w33_klein_slice_points": w33_slice,
            "topological_1_mode_coefficient": topological,
            "quartic_triangles_equal_e7_fund": quartic_triangles == e7_fund,
            "quartic_triangles_equal_two_times_bitangents": quartic_triangles == 2 * bitangents,
            "quartic_triangles_equal_cartan_times_phi6": quartic_triangles == cartan_rank * phi6,
            "bitangents_equal_q_cubic_plus_1": bitangents == q_cubic_plus_1,
            "topological_equals_w33_slice_times_quartic_triangles": (
                topological == w33_slice * quartic_triangles
            ),
            "topological_equals_w33_slice_times_e7_fund": topological == w33_slice * e7_fund,
        },
        "ambient_shell_lift": {
            "ambient_pg53_points": ambient_pg53,
            "sl27_shell_dimension": sl27_shell,
            "g2_dimension": g2_dim,
            "ambient_equals_bitangents_times_phi3": ambient_pg53 == bitangents * phi3,
            "ambient_equals_g2_times_a26_rank": ambient_pg53 == g2_dim * 26,
            "sl27_equals_quartic_triangles_times_phi3": sl27_shell == quartic_triangles * phi3,
            "sl27_equals_two_times_ambient": sl27_shell == 2 * ambient_pg53,
            "sl27_equals_e7_fund_times_phi3": sl27_shell == e7_fund * phi3,
        },
        "bridge_verdict": (
            "The promoted topological channel is already the Klein/quartic packet "
            "lifted by the live W33 slice. The Clifford external plane contributes "
            "13 = Phi_3, the quartic bitangents contribute 28 = q^3 + 1, the "
            "quartic triangles contribute 56 = E7_fund = 2*28, the ambient Klein "
            "shell closes as 364 = 28*13, the full sl(27) shell closes as "
            "728 = 56*13, and the live topological coefficient is exactly "
            "2240 = 40*56. So the topological 1-mode is already the quartic/E7 "
            "channel dressed by the exact W33 Klein slice, not an unrelated "
            "residual scalar."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_klein_clifford_topological_summary(), indent=2),
        encoding="utf-8",
    )
    return path


if __name__ == "__main__":
    write_summary()
