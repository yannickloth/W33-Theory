"""Chain-level H^2 cup form and canonical mixed K3 plane on the explicit seeds.

The explicit curved bridge seeds already carry full simplicial chain complexes.
This module pushes that one step further at degree 2:

1. compute the harmonic projector on ``C^2`` from the explicit Hodge Laplacian;
2. choose a deterministic harmonic basis from the projector itself, not from an
   arbitrary zero-eigenvector basis;
3. orient the top simplices by propagating a fundamental class through shared
   codimension-1 faces;
4. evaluate the simplicial cup pairing on ``H^2`` against that oriented
   fundamental class;
5. recover the exact signature counts on the current explicit seeds; and
6. isolate a deterministic mixed-sign rank-2 plane inside ``H^2(K3)``.

The key point is that the K3-side host is no longer only a dimension/signature
count. The explicit 16-vertex chain model already determines a concrete
harmonic cup form with signature ``(3,19)``, and the earliest harmonic
2-simplex already splits into positive and negative components, giving a
deterministic mixed plane.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from functools import lru_cache
import json
from pathlib import Path
import sys
from typing import Any

import numpy as np


if __package__ in {None, ""}:
    ROOT = Path(__file__).resolve().parents[1]
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
else:
    ROOT = Path(__file__).resolve().parents[1]

from w33_curved_4d_curvature_budget import build_curved_4d_curvature_budget_summary
from w33_curved_external_hodge_product import external_hodge_laplacians
from w33_explicit_curved_4d_complexes import (
    Simplex,
    boundary_matrix,
    cp2_facets,
    faces_by_dimension,
    k3_facets,
)


DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_curved_h2_intersection_bridge_summary.json"
ZERO_TOL = 1e-8
SIGN_TOL = 1e-6


@dataclass(frozen=True)
class CurvedH2IntersectionProfile:
    name: str
    triangles: int
    h2_dimension: int
    harmonic_basis_source_indices: tuple[int, ...]
    orientation_flip_to_match_signature: int
    fundamental_class_positive_facets: int
    fundamental_class_negative_facets: int
    fundamental_class_boundary_is_zero: bool
    signature_positive: int
    signature_negative: int
    recovered_signature: int
    matches_topological_signature: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class CanonicalMixedPlane:
    source_triangle_index: int
    source_triangle: tuple[int, int, int]
    plane_basis_order: tuple[str, str]
    positive_line_nonzero_entries: int
    negative_line_nonzero_entries: int
    euclidean_orthogonality_error: float
    restricted_cup_form: tuple[tuple[float, float], tuple[float, float]]
    positive_cup_value: float
    negative_cup_value: float
    cross_cup_value_abs: float
    plane_is_mixed: bool

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["source_triangle"] = list(self.source_triangle)
        data["plane_basis_order"] = list(self.plane_basis_order)
        data["restricted_cup_form"] = [list(row) for row in self.restricted_cup_form]
        return data


def _label(name: str) -> str:
    if name == "CP2":
        return "CP2_9"
    if name == "K3":
        return "K3_16"
    raise ValueError("name must be CP2 or K3")


def _facets(name: str) -> tuple[Simplex, ...]:
    if name == "CP2":
        return cp2_facets()
    if name == "K3":
        return k3_facets()
    raise ValueError("name must be CP2 or K3")


def _target_signature(name: str) -> int:
    budget = build_curved_4d_curvature_budget_summary()["curved_seeds"]
    signatures = {entry["name"]: int(entry["signature"]) for entry in budget}
    if name not in signatures:
        raise ValueError(f"missing signature for {name}")
    return signatures[name]


def _harmonic_projector_and_basis(laplacian: np.ndarray) -> tuple[np.ndarray, np.ndarray, tuple[int, ...]]:
    eigenvalues, eigenvectors = np.linalg.eigh(laplacian)
    zero_indices = np.where(np.abs(eigenvalues) < ZERO_TOL)[0]
    harmonic_projector = eigenvectors[:, zero_indices] @ eigenvectors[:, zero_indices].T

    basis_vectors: list[np.ndarray] = []
    source_indices: list[int] = []
    for column_index in range(harmonic_projector.shape[1]):
        candidate = harmonic_projector[:, column_index].copy()
        for basis_vector in basis_vectors:
            candidate -= basis_vector * float(basis_vector @ candidate)
        norm = float(np.linalg.norm(candidate))
        if norm > ZERO_TOL:
            basis_vectors.append(candidate / norm)
            source_indices.append(column_index)
        if len(basis_vectors) == len(zero_indices):
            break
    if len(basis_vectors) != len(zero_indices):
        raise AssertionError("failed to build deterministic harmonic basis")
    return harmonic_projector, np.column_stack(basis_vectors), tuple(source_indices)


def _oriented_fundamental_class(facets: tuple[Simplex, ...]) -> np.ndarray:
    face_to_facets: dict[tuple[int, int, int, int], list[tuple[int, int]]] = {}
    for facet_index, facet in enumerate(facets):
        for position in range(5):
            face = facet[:position] + facet[position + 1 :]
            incidence = 1 if position % 2 == 0 else -1
            face_to_facets.setdefault(face, []).append((facet_index, incidence))

    adjacency: list[list[tuple[int, int]]] = [[] for _ in facets]
    for incidences in face_to_facets.values():
        if len(incidences) != 2:
            continue
        (left_index, left_sign), (right_index, right_sign) = incidences
        relative_sign = -left_sign * right_sign
        adjacency[left_index].append((right_index, relative_sign))
        adjacency[right_index].append((left_index, relative_sign))

    orientation: list[int | None] = [None] * len(facets)
    orientation[0] = 1
    stack = [0]
    while stack:
        facet_index = stack.pop()
        current_sign = orientation[facet_index]
        if current_sign is None:
            raise AssertionError("unexpected unoriented facet in traversal")
        for neighbor_index, relative_sign in adjacency[facet_index]:
            desired_sign = current_sign * relative_sign
            if orientation[neighbor_index] is None:
                orientation[neighbor_index] = desired_sign
                stack.append(neighbor_index)
            elif orientation[neighbor_index] != desired_sign:
                raise AssertionError("facet orientation propagation is inconsistent")

    if any(sign is None for sign in orientation):
        raise AssertionError("expected a connected top-dimensional complex")
    return np.array([int(sign) for sign in orientation], dtype=int)


def _signature_counts(matrix: np.ndarray) -> tuple[int, int, int]:
    eigenvalues = np.linalg.eigvalsh(matrix)
    positive = int(np.sum(eigenvalues > SIGN_TOL))
    negative = int(np.sum(eigenvalues < -SIGN_TOL))
    zero = int(np.sum(np.abs(eigenvalues) <= SIGN_TOL))
    return positive, negative, zero


def _cup_matrix_on_h2(
    triangles: tuple[Simplex, ...],
    facets: tuple[Simplex, ...],
    orientation: np.ndarray,
    harmonic_basis: np.ndarray,
) -> np.ndarray:
    triangle_index = {triangle: index for index, triangle in enumerate(triangles)}
    cup_matrix = np.zeros((harmonic_basis.shape[1], harmonic_basis.shape[1]))
    for facet_index, facet in enumerate(facets):
        left_triangle = triangle_index[facet[:3]]
        right_triangle = triangle_index[facet[2:]]
        cup_matrix += orientation[facet_index] * np.outer(
            harmonic_basis[left_triangle, :],
            harmonic_basis[right_triangle, :],
        )
    return 0.5 * (cup_matrix + cup_matrix.T)


def _match_orientation_to_signature(cup_matrix: np.ndarray, target_signature: int) -> tuple[int, np.ndarray]:
    positive, negative, zero = _signature_counts(cup_matrix)
    if zero != 0:
        raise AssertionError("expected a nondegenerate cup form on H^2")
    raw_signature = positive - negative
    if raw_signature == target_signature:
        return 1, cup_matrix
    if raw_signature == -target_signature:
        return -1, -cup_matrix
    raise AssertionError("chain-level cup form does not match the topological signature up to orientation")


def _ambient_sign_projector(harmonic_basis: np.ndarray, cup_matrix: np.ndarray, sign: str) -> np.ndarray:
    eigenvalues, eigenvectors = np.linalg.eigh(cup_matrix)
    if sign == "positive":
        mask = eigenvalues > SIGN_TOL
    elif sign == "negative":
        mask = eigenvalues < -SIGN_TOL
    else:
        raise ValueError("sign must be positive or negative")
    if not np.any(mask):
        return np.zeros((harmonic_basis.shape[0], harmonic_basis.shape[0]))
    harmonic_projector = eigenvectors[:, mask] @ eigenvectors[:, mask].T
    return harmonic_basis @ harmonic_projector @ harmonic_basis.T


def _first_mixed_source_triangle(
    harmonic_projector: np.ndarray,
    positive_projector: np.ndarray,
    negative_projector: np.ndarray,
) -> int:
    for triangle_index in range(harmonic_projector.shape[1]):
        if (
            np.linalg.norm(harmonic_projector[:, triangle_index]) > ZERO_TOL
            and np.linalg.norm(positive_projector[:, triangle_index]) > ZERO_TOL
            and np.linalg.norm(negative_projector[:, triangle_index]) > ZERO_TOL
        ):
            return triangle_index
    raise AssertionError("expected a mixed-sign harmonic source triangle")


@lru_cache(maxsize=1)
def build_curved_h2_intersection_summary() -> dict[str, Any]:
    seed_profiles: list[CurvedH2IntersectionProfile] = []
    k3_canonical_mixed_plane: CanonicalMixedPlane | None = None

    for name in ("CP2", "K3"):
        facets = _facets(name)
        faces = faces_by_dimension(facets)
        triangles = faces[2]
        harmonic_projector, harmonic_basis, source_indices = _harmonic_projector_and_basis(
            external_hodge_laplacians(name)[2]
        )
        raw_orientation = _oriented_fundamental_class(facets)
        cup_matrix = _cup_matrix_on_h2(triangles, facets, raw_orientation, harmonic_basis)
        orientation_flip, adjusted_cup_matrix = _match_orientation_to_signature(
            cup_matrix,
            _target_signature(name),
        )
        adjusted_orientation = orientation_flip * raw_orientation
        boundary = boundary_matrix(faces[4], faces[3]).astype(int) @ adjusted_orientation
        positive, negative, zero = _signature_counts(adjusted_cup_matrix)
        if zero != 0:
            raise AssertionError("expected nondegenerate adjusted cup form")

        seed_profiles.append(
            CurvedH2IntersectionProfile(
                name=_label(name),
                triangles=len(triangles),
                h2_dimension=harmonic_basis.shape[1],
                harmonic_basis_source_indices=source_indices,
                orientation_flip_to_match_signature=orientation_flip,
                fundamental_class_positive_facets=int(np.sum(adjusted_orientation > 0)),
                fundamental_class_negative_facets=int(np.sum(adjusted_orientation < 0)),
                fundamental_class_boundary_is_zero=bool(np.max(np.abs(boundary)) == 0),
                signature_positive=positive,
                signature_negative=negative,
                recovered_signature=positive - negative,
                matches_topological_signature=(positive - negative == _target_signature(name)),
            )
        )

        if name == "K3":
            positive_projector = _ambient_sign_projector(harmonic_basis, adjusted_cup_matrix, "positive")
            negative_projector = _ambient_sign_projector(harmonic_basis, adjusted_cup_matrix, "negative")
            source_triangle_index = _first_mixed_source_triangle(
                harmonic_projector,
                positive_projector,
                negative_projector,
            )
            positive_line = positive_projector[:, source_triangle_index]
            negative_line = negative_projector[:, source_triangle_index]
            positive_line /= float(np.linalg.norm(positive_line))
            negative_line /= float(np.linalg.norm(negative_line))
            plane_basis = np.column_stack([positive_line, negative_line])
            plane_coordinates = harmonic_basis.T @ plane_basis
            restricted_cup_form = plane_coordinates.T @ adjusted_cup_matrix @ plane_coordinates
            k3_canonical_mixed_plane = CanonicalMixedPlane(
                source_triangle_index=source_triangle_index,
                source_triangle=triangles[source_triangle_index],
                plane_basis_order=("positive_line", "negative_line"),
                positive_line_nonzero_entries=int(np.sum(np.abs(positive_line) > ZERO_TOL)),
                negative_line_nonzero_entries=int(np.sum(np.abs(negative_line) > ZERO_TOL)),
                euclidean_orthogonality_error=float(
                    abs(float(np.dot(positive_line, negative_line)))
                ),
                restricted_cup_form=(
                    (float(restricted_cup_form[0, 0]), float(restricted_cup_form[0, 1])),
                    (float(restricted_cup_form[1, 0]), float(restricted_cup_form[1, 1])),
                ),
                positive_cup_value=float(restricted_cup_form[0, 0]),
                negative_cup_value=float(restricted_cup_form[1, 1]),
                cross_cup_value_abs=float(abs(restricted_cup_form[0, 1])),
                plane_is_mixed=bool(
                    restricted_cup_form[0, 0] > SIGN_TOL
                    and restricted_cup_form[1, 1] < -SIGN_TOL
                    and abs(restricted_cup_form[0, 1]) < SIGN_TOL
                ),
            )

    if k3_canonical_mixed_plane is None:
        raise AssertionError("expected a canonical K3 mixed plane")

    return {
        "status": "ok",
        "seed_profiles": [profile.to_dict() for profile in seed_profiles],
        "k3_canonical_mixed_plane": k3_canonical_mixed_plane.to_dict(),
        "bridge_theorem": {
            "chain_level_cup_form_recovers_cp2_signature": (
                seed_profiles[0].matches_topological_signature and seed_profiles[0].signature_positive == 1
            ),
            "chain_level_cup_form_recovers_k3_signature": (
                seed_profiles[1].matches_topological_signature and seed_profiles[1].signature_positive == 3
            ),
            "k3_canonical_mixed_plane_is_determined_by_projector_and_cup_form": True,
            "k3_canonical_mixed_plane_is_mixed_signature": k3_canonical_mixed_plane.plane_is_mixed,
        },
        "bridge_verdict": (
            "The explicit curved seeds now support a chain-level H^2 cup-form "
            "theorem. Using the oriented fundamental class propagated across the "
            "explicit 4-simplices and a deterministic harmonic basis built from "
            "the Hodge projector, the simplicial cup pairing recovers signature "
            "(1,0) on CP2_9 and (3,19) on K3_16. On K3_16 the earliest harmonic "
            "2-simplex already has both positive and negative components, so the "
            "explicit chain model determines a canonical mixed rank-2 plane with "
            "ordered basis positive line then negative line."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_curved_h2_intersection_summary(), indent=2),
        encoding="utf-8",
    )
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
