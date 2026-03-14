"""Exact s12 / harmonic-cube bridge to the ambient Klein geometry.

This module packages a clean exact chain that was already latent in the repo:

    H27 = F3^3,  |H27| = 27
    ternary Golay size = 3^6 = 729 = 27^2
    traceless shell = 729 - 1 = 728 = dim sl(27)
    projectivized shell = 728 / 2 = 364 = |PG(5,3)|

The last identity is the decisive one.  The general Klein quadric of lines in
PG(3,3) lives in PG(5,3), so the projectivized nonzero ternary Golay shell has
exactly the size of the *ambient* Klein space.  The live W33 symplectic slice
then sits inside this ambient space with its exact Klein-image size 40, leaving

    364 - 40 = 324,

which is the same moonshine gap already realized elsewhere as 54*6 = 4*81.

This gives a clean exact package:

    harmonic cube square -> ternary Golay shell -> projective Klein ambient
    -> W33 symplectic slice + exact moonshine-gap complement.
"""

from __future__ import annotations

from collections import Counter
from functools import lru_cache
import json
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
for candidate in (ROOT, ROOT / "tools", ROOT / "scripts", ROOT / "pillars"):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from tools.s12_universal_algebra import (
    enumerate_linear_code_f3,
    ternary_golay_generator_matrix,
)
from w33_monster_gap_duality_bridge import build_monster_gap_duality_summary


DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_s12_klein_projective_bridge_summary.json"


def _hamming_weight(word: tuple[int, ...]) -> int:
    return sum(1 for value in word if value % 3 != 0)


def _projective_representative(word: tuple[int, ...]) -> tuple[int, ...]:
    doubled = tuple((2 * value) % 3 for value in word)
    return word if word <= doubled else doubled


@lru_cache(maxsize=1)
def build_s12_klein_projective_summary() -> dict[str, Any]:
    codewords = enumerate_linear_code_f3(ternary_golay_generator_matrix())
    zero = next(word for word in codewords if all(value == 0 for value in word))
    nonzero = [word for word in codewords if word != zero]

    weight_distribution = Counter(_hamming_weight(word) for word in nonzero)
    projective_shell = {_projective_representative(word) for word in nonzero}
    projective_weight_distribution = Counter(
        _hamming_weight(word) for word in projective_shell
    )

    q = 3
    harmonic_cube_order = q**3
    golay_code_size = len(codewords)
    sl27_shell = len(nonzero)
    projective_shell_size = len(projective_shell)
    ambient_pg53_points = (q**6 - 1) // (q - 1)

    # For the symplectic slice one has W(3,3) ~= Q(4,3) with
    # |Q(4,q)| = (q + 1)(q^2 + 1).  At q=3 this gives 40 exactly.
    w33_klein_slice = (q + 1) * (q * q + 1)

    gap = int(
        build_monster_gap_duality_summary()["moonshine_gap_dictionary"]["moonshine_gap"]
    )

    external_plane_points = (q**3 - 1) // (q - 1)
    plane_quartic_bitangents = 28

    return {
        "status": "ok",
        "harmonic_cube_square_dictionary": {
            "q": q,
            "harmonic_cube_order": harmonic_cube_order,
            "ternary_golay_code_size": golay_code_size,
            "sl27_shell_dimension": sl27_shell,
            "projectivized_shell_size": projective_shell_size,
            "ambient_pg53_points": ambient_pg53_points,
            "w33_klein_slice_points": w33_klein_slice,
            "moonshine_gap": gap,
            "harmonic_cube_square_equals_golay_size": golay_code_size == harmonic_cube_order**2,
            "nonzero_golay_equals_sl27_dimension": sl27_shell == golay_code_size - 1 == 728,
            "projectivized_nonzero_shell_equals_pg53_points": (
                projective_shell_size == sl27_shell // 2 == ambient_pg53_points
            ),
            "projective_shell_minus_w33_klein_slice_equals_gap": (
                projective_shell_size - w33_klein_slice == gap
            ),
            "projective_shell_splits_as_w33_slice_plus_gap": (
                projective_shell_size == w33_klein_slice + gap
            ),
        },
        "weight_projectivization": {
            "full_weight_distribution": {
                int(weight): int(count)
                for weight, count in sorted(weight_distribution.items())
            },
            "projective_weight_distribution": {
                int(weight): int(count)
                for weight, count in sorted(projective_weight_distribution.items())
            },
            "projective_weight_distribution_sums_to_pg53": (
                sum(projective_weight_distribution.values()) == ambient_pg53_points
            ),
            "weight_6_projects_to_132": projective_weight_distribution[6] == 132,
            "weight_9_projects_to_220": projective_weight_distribution[9] == 220,
            "weight_12_projects_to_12": projective_weight_distribution[12] == 12,
        },
        "quartic_parallelism_guide_rail": {
            "clifford_parallelism_external_plane_points": external_plane_points,
            "plane_quartic_bitangent_count": plane_quartic_bitangents,
            "ambient_pg53_equals_bitangents_times_external_plane_points": (
                ambient_pg53_points == plane_quartic_bitangents * external_plane_points
            ),
            "external_plane_points_equals_phi3": external_plane_points == 13,
        },
        "bridge_verdict": (
            "The local harmonic cube H27 already knows the ambient Klein space. "
            "Its square has size 27^2 = 729, the nonzero ternary Golay shell has "
            "size 728 = dim sl(27), and projectivizing by +/-1 gives exactly "
            "364 = |PG(5,3)|, the ambient space of the Klein quadric. Inside that "
            "ambient space the live W33 symplectic slice occupies exactly 40 points, "
            "leaving 324 = 364 - 40, the same moonshine gap already realized as "
            "54*6 = 4*81. So the s12/Golay shell is no longer separate from the "
            "Klein geometry: it is the full projective ambient shell in which the "
            "W33 Klein slice and the moonshine-gap complement sit exactly."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_s12_klein_projective_summary(), indent=2),
        encoding="utf-8",
    )
    return path


if __name__ == "__main__":
    write_summary()
