"""Executable tomotope cover-family bridge for the refinement/scaling program.

This module packages the part of the tomotope story that genuinely addresses
the finite-spectrum firewall:

1. The tomotope has infinitely many distinct minimal regular covers.
2. The paper constructs an explicit toroidal family ``Q_k`` and regular covers
   ``P_k`` above the tomotope.
3. The native geometric carrier of that family grows like ``k^3``, while the
   monodromy grows like ``k^6``.

That gives the project a real infinite family, but not yet a 4D Weyl-law
theorem. The intended use is to separate the valid cover mechanism from the
still-open 4D continuum bridge.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from math import gcd, log
import json
from pathlib import Path
import sys
from typing import Any

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from tools.tomotope_reye_e8_connection import (  # type: ignore[import-not-found]
        CELL_24_DATA,
        REYE_CONFIGURATION,
        TOMOTOPE_DATA,
    )
else:
    from tools.tomotope_reye_e8_connection import (
        CELL_24_DATA,
        REYE_CONFIGURATION,
        TOMOTOPE_DATA,
    )


ROOT = Path(__file__).resolve().parents[1]
REYE_REPORT_PATH = ROOT / "data" / "w33_twist_transport_reye.json"
DEFAULT_OUTPUT_PATH = ROOT / "data" / "tomotope_cover_bridge_summary.json"


@dataclass(frozen=True)
class QkLevel:
    """Finite quotient data for the tomotope cover family."""

    k: int
    block_side: int
    unit_cube_count: int
    quotient_group_order: int
    monodromy_order: int
    regular_polytope: bool
    vertices: int | None
    edges: int | None
    triangles: int | None
    tetrahedra: int | None
    octahedra: int | None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _validate_positive_int(name: str, value: int) -> None:
    if not isinstance(value, int) or value < 1:
        raise ValueError(f"{name} must be a positive integer")


def qk_level(k: int) -> QkLevel:
    """Return the explicit ``Q_k`` data from Section 5 of The Tomotope.

    For ``k > 1`` the paper gives the full face counts of the uniform toroid
    ``Q_k``. For ``k = 1`` it records that ``Q_1`` is only a pre-polytope, so
    we keep the group data but omit the face counts.
    """

    _validate_positive_int("k", k)

    block_side = 2 * k
    unit_cube_count = block_side**3
    quotient_group_order = 24 * unit_cube_count
    monodromy_order = 576 * (block_side**6)
    regular_polytope = k > 1

    if regular_polytope:
        volume = k**3
        vertices = 4 * volume
        edges = 24 * volume
        triangles = 32 * volume
        tetrahedra = 8 * volume
        octahedra = 4 * volume
    else:
        vertices = None
        edges = None
        triangles = None
        tetrahedra = None
        octahedra = None

    return QkLevel(
        k=k,
        block_side=block_side,
        unit_cube_count=unit_cube_count,
        quotient_group_order=quotient_group_order,
        monodromy_order=monodromy_order,
        regular_polytope=regular_polytope,
        vertices=vertices,
        edges=edges,
        triangles=triangles,
        tetrahedra=tetrahedra,
        octahedra=octahedra,
    )


def qk_covers_qm(k: int, m: int) -> bool:
    """The geometric toroid ``Q_k`` covers ``Q_m`` exactly when ``m`` divides ``k``."""

    _validate_positive_int("k", k)
    _validate_positive_int("m", m)
    return k % m == 0


def theorem_5_9_pair(p: int, q: int) -> bool:
    """Return whether the tomotope paper's Theorem 5.9 applies to ``(p, q)``."""

    _validate_positive_int("p", p)
    _validate_positive_int("q", q)
    return p > 1 and q > 1 and p % 2 == 1 and q % 2 == 1 and gcd(p, q) == 1


def _growth_degree(value_small: int, value_large: int, k_small: int, k_large: int) -> float:
    if value_small <= 0 or value_large <= 0:
        raise ValueError("growth degree requires positive values")
    return log(value_large / value_small) / log(k_large / k_small)


def native_cover_dimension(k_small: int = 2, k_large: int = 6) -> float:
    """Recover the cubic growth degree from any two regular levels."""

    level_small = qk_level(k_small)
    level_large = qk_level(k_large)
    if level_small.vertices is None or level_large.vertices is None:
        raise ValueError("native cover dimension requires k > 1")
    return _growth_degree(level_small.vertices, level_large.vertices, k_small, k_large)


def monodromy_growth_degree(k_small: int = 1, k_large: int = 3) -> float:
    """Recover the degree-6 monodromy growth predicted by Lemma 5.8."""

    level_small = qk_level(k_small)
    level_large = qk_level(k_large)
    return _growth_degree(
        level_small.monodromy_order,
        level_large.monodromy_order,
        k_small,
        k_large,
    )


def _load_reye_report() -> dict[str, Any]:
    return json.loads(REYE_REPORT_PATH.read_text(encoding="utf-8"))


def build_cover_bridge_summary(sample_ks: tuple[int, ...] = (1, 2, 3, 5)) -> dict[str, Any]:
    """Assemble a machine-readable summary for the tomotope cover route."""

    if not sample_ks:
        raise ValueError("sample_ks must be non-empty")

    reye_report = _load_reye_report()
    levels = [qk_level(k).to_dict() for k in sample_ks]
    odd_cover_pairs = [
        {"p": 3, "q": 5},
        {"p": 3, "q": 7},
        {"p": 5, "q": 7},
    ]

    return {
        "status": "ok",
        "tomotope_seed": {
            "vertices": TOMOTOPE_DATA["structure"]["vertices"],
            "edges": TOMOTOPE_DATA["structure"]["edges"],
            "faces": TOMOTOPE_DATA["structure"]["faces"],
            "automorphism_order": TOMOTOPE_DATA["automorphism_group"]["order"],
        },
        "qk_family": {
            "sample_levels": levels,
            "quotient_group_formula": "|W_k| = 24 * (2k)^3",
            "monodromy_formula": "|Mon(Q_k)| = 576 * (2k)^6 = 36864 * k^6",
            "cover_rule": "Q_k covers Q_m iff m divides k",
            "theorem_5_9_pairs": odd_cover_pairs,
        },
        "native_scaling": {
            "carrier_growth_degree": native_cover_dimension(),
            "monodromy_growth_degree": monodromy_growth_degree(),
            "carrier_dimension_is_four": False,
            "needs_external_4d_factor": True,
            "verdict": (
                "The tomotope supplies a bona fide infinite cover family, but the "
                "explicit toroidal carrier scales like k^3. By itself this is a "
                "3D refinement tower, not the missing 4D Weyl-law theorem."
            ),
        },
        "reye_24cell_bridge": {
            "tomotope_edges": TOMOTOPE_DATA["structure"]["edges"],
            "tomotope_faces": TOMOTOPE_DATA["structure"]["faces"],
            "reye_points": reye_report["T5_reye_point_count"],
            "reye_lines": reye_report["T5_reye_line_count"],
            "reye_valid_configs": reye_report["T5_reye_configs_valid"],
            "cell24_axes": CELL_24_DATA["key_structures"]["diameter_axes"],
            "cell24_hexagons": CELL_24_DATA["key_structures"]["great_hexagons"],
            "d4_root_count": CELL_24_DATA["vertices"],
            "reye_notation": REYE_CONFIGURATION["notation"],
        },
        "bridge_recommendation": (
            "Use the tomotope cover family as the genuine infinite internal tower. "
            "Then couple it either to an external 4D refinement family or to an "
            "almost-commutative 4D spectral triple if the goal is a true 4D "
            "spectral-action limit."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    summary = build_cover_bridge_summary()
    path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
