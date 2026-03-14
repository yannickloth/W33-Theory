"""Vogel placement of the promoted s12 / Golay / Klein shell.

The live repo already proved a negative theorem for the exceptional line:
the dimensions 242, 486, and 728 are not positive non-degenerate exceptional
Vogel hits. The positive theorem that goes with it is:

    728 = dim sl(27) = dim A_26.

So the promoted s12 shell lands naturally on the classical A-line, while the
W33 package supplies the exact exceptional dressings:

    364 = 14 * 26,
    728 = 28 * 26 = 14 * 52.

In other words, the final promoted algebra is not "all exceptional". It is a
classical A_26 closure dressed by the live G2 / D4 / F4 factors coming from the
W33/tomotope/triality side.
"""

from __future__ import annotations

from functools import lru_cache
import json
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
for candidate in (ROOT, ROOT / "tools", ROOT / "exploration"):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from tools.vogel_rational_hit_crosswalk import build_crosswalk, classical_hits
from w33_s12_klein_projective_bridge import build_s12_klein_projective_summary


DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_s12_vogel_spine_bridge_summary.json"


@lru_cache(maxsize=1)
def build_s12_vogel_spine_summary() -> dict[str, Any]:
    projective = build_s12_klein_projective_summary()
    crosswalk = build_crosswalk([242, 486, 728])

    sl27_dim = int(projective["harmonic_cube_square_dictionary"]["sl27_shell_dimension"])
    projective_shell = int(
        projective["harmonic_cube_square_dictionary"]["projectivized_shell_size"]
    )

    a_hits = classical_hits(sl27_dim)["A"]
    if a_hits != [26]:
        raise ValueError(f"Expected A_26 hit for 728, got {a_hits}")
    a26_rank = a_hits[0]

    positive_hits = set(crosswalk["positive_hit_dims"])
    target_728 = crosswalk["targets"]["728"]
    nearest_728 = target_728["nearest_hit"]

    g2_dim = 14
    d4_dim = 28
    f4_dim = 52
    e8_dim = 248
    finite_w33_dim = 480

    return {
        "status": "ok",
        "vogel_a_line_dictionary": {
            "sl27_dimension": sl27_dim,
            "a_family_rank": a26_rank,
            "projective_shell_dimension": projective_shell,
            "g2_dimension": g2_dim,
            "d4_dimension": d4_dim,
            "f4_dimension": f4_dim,
            "e8_dimension": e8_dim,
            "finite_w33_dimension": finite_w33_dim,
            "sl27_is_exactly_a26": sl27_dim == a26_rank * (a26_rank + 2),
            "projective_shell_equals_g2_times_a26_rank": projective_shell == g2_dim * a26_rank,
            "sl27_equals_d4_dimension_times_a26_rank": sl27_dim == d4_dim * a26_rank,
            "sl27_equals_g2_times_f4": sl27_dim == g2_dim * f4_dim,
            "sl27_equals_finite_w33_plus_e8": sl27_dim == finite_w33_dim + e8_dim,
        },
        "exceptional_line_firewall": {
            "positive_exceptional_hit_dims": sorted(positive_hits),
            "dim_242_in_positive_exceptional_hit_set": 242 in positive_hits,
            "dim_486_in_positive_exceptional_hit_set": 486 in positive_hits,
            "dim_728_in_positive_exceptional_hit_set": 728 in positive_hits,
            "nearest_positive_exceptional_hits_to_728": list(nearest_728["nearest_dims"]),
            "distance_from_728_to_nearest_positive_exceptional_hit": int(nearest_728["distance"]),
            "dim_728_roots_on_exceptional_line": list(target_728["roots"]),
        },
        "bridge_verdict": (
            "The promoted s12 shell has a clean Vogel placement. It does not land "
            "on the positive non-degenerate exceptional line; instead it lands "
            "exactly on the classical A-line as A_26 = sl(27). The W33 package "
            "then supplies exact exceptional dressings around that classical core: "
            "the projectivized shell is 364 = 14*26, the full shell is "
            "728 = 28*26 = 14*52, and the same 728 also decomposes as 480 + 248. "
            "So the final promoted algebra is best read as an A_26 closure dressed "
            "by the live G2 / D4 / F4 / E8 factors, not as a failed attempt to "
            "force everything directly onto Vogel's exceptional line."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_s12_vogel_spine_summary(), indent=2),
        encoding="utf-8",
    )
    return path


if __name__ == "__main__":
    write_summary()
