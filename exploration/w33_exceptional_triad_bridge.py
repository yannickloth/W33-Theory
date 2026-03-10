"""Comparison bridge between the projective abstract trio and the convex exceptional trio.

This module evaluates the user's hunch that the abstract trio

- 11-cell,
- tomotope,
- 57-cell,

plays the role of an abstract/projective analogue of

- 600-cell,
- 24-cell,
- 120-cell.

The conclusion is deliberately precise:

- there is a real exceptional-triad analogy at the level of finite 4-dimensional
  outliers grouped on Klitzing's page;
- but the correspondence is not direct by Schl\"afli type or by exact facet /
  vertex-figure data.

In particular:

- 11-cell has type {3,5,3}, not {3,3,5};
- 57-cell has type {5,3,5}, not {5,3,3};
- tomotope is not regular, and its regular cover has type {3,12,4}, not {3,4,3}.

So the 11-cell and 57-cell are better viewed as exceptional locally projective
counterparts in the icosahedral/dodecahedral channel, while the tomotope is a
semiregular projective cousin in the tetrahedron/octahedron/cube channel that
touches the 24-cell most closely.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path
import sys
from typing import Any


if __package__ in {None, ""}:
    ROOT = Path(__file__).resolve().parents[1]
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
else:
    ROOT = Path(__file__).resolve().parents[1]


DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_exceptional_triad_bridge_summary.json"


@dataclass(frozen=True)
class PolychoronProfile:
    name: str
    category: str
    regular: bool
    self_dual: bool | None
    schlafli_type: str | None
    regular_cover_type: str | None
    facets: tuple[str, ...]
    vertex_figure: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def strip_hemi(name: str) -> str:
    if name.startswith("hemi-"):
        return name[len("hemi-") :]
    if name.startswith("hemi"):
        return name[len("hemi") :]
    return name


def normalized_component_set(profile: PolychoronProfile) -> set[str]:
    components = {strip_hemi(profile.vertex_figure)}
    components.update(strip_hemi(facet) for facet in profile.facets)
    return components


def classical_exceptional_trio() -> tuple[PolychoronProfile, ...]:
    return (
        PolychoronProfile(
            name="600-cell",
            category="classical",
            regular=True,
            self_dual=False,
            schlafli_type="{3,3,5}",
            regular_cover_type=None,
            facets=("tetrahedron",),
            vertex_figure="icosahedron",
        ),
        PolychoronProfile(
            name="24-cell",
            category="classical",
            regular=True,
            self_dual=True,
            schlafli_type="{3,4,3}",
            regular_cover_type=None,
            facets=("octahedron",),
            vertex_figure="cube",
        ),
        PolychoronProfile(
            name="120-cell",
            category="classical",
            regular=True,
            self_dual=False,
            schlafli_type="{5,3,3}",
            regular_cover_type=None,
            facets=("dodecahedron",),
            vertex_figure="tetrahedron",
        ),
    )


def projective_exceptional_trio() -> tuple[PolychoronProfile, ...]:
    return (
        PolychoronProfile(
            name="11-cell",
            category="projective",
            regular=True,
            self_dual=True,
            schlafli_type="{3,5,3}",
            regular_cover_type=None,
            facets=("hemi-icosahedron",),
            vertex_figure="hemi-dodecahedron",
        ),
        PolychoronProfile(
            name="tomotope",
            category="projective",
            regular=False,
            self_dual=None,
            schlafli_type=None,
            regular_cover_type="{3,12,4}",
            facets=("tetrahedron", "hemioctahedron"),
            vertex_figure="hemicuboctahedron",
        ),
        PolychoronProfile(
            name="57-cell",
            category="projective",
            regular=True,
            self_dual=True,
            schlafli_type="{5,3,5}",
            regular_cover_type=None,
            facets=("hemi-dodecahedron",),
            vertex_figure="hemi-icosahedron",
        ),
    )


def direct_classical_analogy(projective: PolychoronProfile, classical: PolychoronProfile) -> bool:
    return (
        projective.schlafli_type == classical.schlafli_type
        and normalized_component_set(projective) == normalized_component_set(classical)
    )


def component_overlap(projective: PolychoronProfile, classical: PolychoronProfile) -> int:
    return len(normalized_component_set(projective) & normalized_component_set(classical))


def best_classical_overlaps() -> dict[str, dict[str, Any]]:
    classical = classical_exceptional_trio()
    overlaps: dict[str, dict[str, Any]] = {}
    for projective in projective_exceptional_trio():
        scores = {target.name: component_overlap(projective, target) for target in classical}
        best = max(scores.values())
        overlaps[projective.name] = {
            "scores": scores,
            "best_score": best,
            "best_matches": sorted(name for name, score in scores.items() if score == best),
        }
    return overlaps


def build_exceptional_triad_summary() -> dict[str, Any]:
    classical = classical_exceptional_trio()
    projective = projective_exceptional_trio()
    overlaps = best_classical_overlaps()

    return {
        "status": "ok",
        "classical_exceptional_trio": [profile.to_dict() for profile in classical],
        "projective_exceptional_trio": [profile.to_dict() for profile in projective],
        "direct_analogy_matrix": {
            source.name: {
                target.name: direct_classical_analogy(source, target)
                for target in classical
            }
            for source in projective
        },
        "component_overlaps": overlaps,
        "triad_verdict": {
            "11_cell": (
                "Not a direct 600-cell analogue: it has type {3,5,3} with hemi-icosahedral "
                "facets and hemi-dodecahedral vertex figures, so it straddles the "
                "icosahedron/dodecahedron channel instead of matching a convex exceptional."
            ),
            "tomotope": (
                "Closest to the 24-cell channel, but not a direct abstract 24-cell: it is "
                "uniform rather than regular, mixes tetrahedra with hemioctahedra, has "
                "hemicuboctahedral vertex figures, and its regular cover has type {3,12,4}."
            ),
            "57_cell": (
                "Not a direct 120-cell analogue: it has type {5,3,5} with hemi-dodecahedral "
                "facets and hemi-icosahedral vertex figures, again living in the "
                "icosahedron/dodecahedron projective channel."
            ),
        },
        "global_verdict": (
            "There is a meaningful exceptional-triad analogy, but not a one-to-one "
            "identification with the convex exceptional trio. The 11-cell and 57-cell "
            "form a projective icosahedron/dodecahedron pair, while the tomotope is the "
            "semiregular tetrahedron/hemioctahedron member that sits nearest the 24-cell."
        ),
        "duality_note": (
            "The classical trio is arranged as a dual pair plus a self-dual middle "
            "(600-cell <-> 120-cell, with 24-cell self-dual). The projective trio is "
            "different: 11-cell and 57-cell are each self-dual, while the tomotope is "
            "the nonregular middle object."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(json.dumps(build_exceptional_triad_summary(), indent=2), encoding="utf-8")
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
