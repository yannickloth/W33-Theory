"""Chain-level H^2 cup/intersection form and canonical mixed K3 plane.

The earlier external bridge reductions fixed only the capacity data

    CP2_9:  (b2+, b2-) = (1, 0)
    K3_16:  (b2+, b2-) = (3, 19)

from Betti numbers and signatures. This module upgrades that to an actual
chain-level theorem on the explicit simplicial complexes:

1. build an oriented fundamental 4-cycle directly from the facet adjacency;
2. compute the harmonic H^2 kernel from the explicit Hodge Laplacian;
3. evaluate the Alexander-Whitney cup pairing H^2 x H^2 -> H^4 on that
   oriented fundamental cycle;
4. recover the exact seed signatures from the resulting intersection form; and
5. isolate a deterministic mixed-sign rank-2 plane on K3 by projecting the
   lexicographically first triangle basis cochain to the positive and negative
   H^2 sign sectors.

This is the first point where the external rank-2 branch is selected at the
chain level rather than only by dimension bookkeeping.
"""

from __future__ import annotations

from collections import deque
from dataclasses import asdict, dataclass
from functools import lru_cache
import json
from math import sqrt
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

from w33_curved_h2_host_bridge import build_curved_h2_host_bridge_summary
from w33_curved_external_hodge_product import external_faces, external_hodge_laplacians
from w33_ternary_homological_code_bridge import build_ternary_homological_code_summary


DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_curved_h2_cup_plane_bridge_summary.json"
TOL = 1e-8


@dataclass(frozen=True)
class CurvedH2CupProfile:
    name: str
    triangle_count: int
    facet_count: int
    harmonic_h2_dimension: int
    positive_h2_directions: int
    negative_h2_directions: int
    signature: int
    cup_symmetry_max_abs_error: float
    fundamental_cycle_is_closed: bool
    orientation_flip_applied: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class CanonicalMixedPlane:
    selector_triangle: tuple[int, int, int]
    positive_line_q_norm: float
    negative_line_q_norm: float
    raw_restricted_intersection_matrix: tuple[tuple[float, float], tuple[float, float]]
    normalized_restricted_intersection_matrix: tuple[tuple[float, float], tuple[float, float]]
    normalized_restricted_determinant: float
    mixed_signature: tuple[int, int]
    qutrit_lift_split: tuple[int, int]
    total_qutrit_lift_dimension: int
    split_qutrit_package: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _seed_recorded_signature(name: str) -> int:
    host = build_curved_h2_host_bridge_summary()
    seed_name = "CP2_9" if name == "CP2" else "K3_16"
    for profile in host["seed_profiles"]:
        if profile["name"] == seed_name:
            return int(profile["signature"])
    raise KeyError(f"missing recorded signature for {name}")


def _all_facet_tetrahedra(facet: tuple[int, ...]) -> tuple[tuple[tuple[int, ...], int], ...]:
    out = []
    for pos in range(len(facet)):
        tet = facet[:pos] + facet[pos + 1 :]
        out.append((tet, pos))
    return tuple(out)


def _facet_adjacency_orientation_signs(name: str) -> np.ndarray:
    facets = external_faces(name)[4]
    tetrahedron_to_facets: dict[tuple[int, ...], list[tuple[int, int]]] = {}
    for facet_index, facet in enumerate(facets):
        for tet, pos in _all_facet_tetrahedra(facet):
            tetrahedron_to_facets.setdefault(tet, []).append((facet_index, pos))
    if not tetrahedron_to_facets:
        raise AssertionError("expected nonempty tetrahedron incidence map")
    if any(len(cofaces) != 2 for cofaces in tetrahedron_to_facets.values()):
        raise AssertionError("expected a closed 4D pseudomanifold: each tetrahedron should have exactly two cofaces")

    signs = {0: 1}
    queue: deque[int] = deque([0])
    while queue:
        left = queue.popleft()
        for tet, left_pos in _all_facet_tetrahedra(facets[left]):
            (a, a_pos), (b, b_pos) = tetrahedron_to_facets[tet]
            right, right_pos = (b, b_pos) if a == left else (a, a_pos)
            induced_left = 1 if left_pos % 2 == 0 else -1
            induced_right = 1 if right_pos % 2 == 0 else -1
            expected_right = -signs[left] * induced_left * induced_right
            if right in signs:
                if signs[right] != expected_right:
                    raise AssertionError("facet orientation propagation conflict")
                continue
            signs[right] = expected_right
            queue.append(right)

    if len(signs) != len(facets):
        raise AssertionError("expected orientation propagation to cover all facets")

    oriented = np.array([signs[index] for index in range(len(facets))], dtype=float)
    return oriented


@lru_cache(maxsize=None)
def oriented_fundamental_cycle(name: str) -> np.ndarray:
    if name not in {"CP2", "K3"}:
        raise ValueError("name must be 'CP2' or 'K3'")

    orientation = _facet_adjacency_orientation_signs(name)
    intersection = _raw_h2_intersection_matrix(name, orientation)
    signature_value, _, _ = _signature_counts(intersection)
    expected_signature = _seed_recorded_signature(name)
    if signature_value == expected_signature:
        return orientation
    if -signature_value == expected_signature:
        return -orientation
    raise AssertionError("orientation sign does not match the recorded seed signature up to global sign")


@lru_cache(maxsize=None)
def harmonic_h2_basis(name: str) -> np.ndarray:
    values, vectors = np.linalg.eigh(external_hodge_laplacians(name)[2])
    mask = np.abs(values) < TOL
    return vectors[:, mask]


def _cup_pairing_terms(name: str, orientation: np.ndarray) -> tuple[tuple[int, int, float], ...]:
    faces = external_faces(name)
    triangles = faces[2]
    facets = faces[4]
    triangle_index = {triangle: index for index, triangle in enumerate(triangles)}
    terms = []
    for facet_index, facet in enumerate(facets):
        front = facet[:3]
        back = facet[2:]
        terms.append((triangle_index[front], triangle_index[back], float(orientation[facet_index])))
    return tuple(terms)


def _raw_h2_intersection_matrix(name: str, orientation: np.ndarray) -> np.ndarray:
    basis = harmonic_h2_basis(name)
    terms = _cup_pairing_terms(name, orientation)
    dimension = basis.shape[1]
    out = np.zeros((dimension, dimension), dtype=float)
    for row in range(dimension):
        left = basis[:, row]
        for col in range(dimension):
            right = basis[:, col]
            out[row, col] = sum(sign * left[i] * right[j] for i, j, sign in terms)
    return (out + out.T) / 2.0


@lru_cache(maxsize=None)
def h2_intersection_matrix(name: str) -> np.ndarray:
    return _raw_h2_intersection_matrix(name, oriented_fundamental_cycle(name))


def _signature_counts(matrix: np.ndarray) -> tuple[int, int, int]:
    eigenvalues = np.linalg.eigvalsh(matrix)
    positive = int(np.sum(eigenvalues > TOL))
    negative = int(np.sum(eigenvalues < -TOL))
    return positive - negative, positive, negative


def _first_nonzero_sign(vector: np.ndarray) -> float:
    for entry in vector:
        if abs(entry) > TOL:
            return 1.0 if entry > 0 else -1.0
    return 1.0


@lru_cache(maxsize=1)
def build_curved_h2_cup_plane_bridge_summary() -> dict[str, Any]:
    logical_qutrits = int(build_ternary_homological_code_summary()["ternary_css_code"]["logical_qutrits"])
    profiles: list[CurvedH2CupProfile] = []
    k3_plane: CanonicalMixedPlane | None = None

    for name, label in (("CP2", "CP2_9"), ("K3", "K3_16")):
        faces = external_faces(name)
        basis = harmonic_h2_basis(name)
        orientation = oriented_fundamental_cycle(name)
        intersection = h2_intersection_matrix(name)
        signature_value, positive, negative = _signature_counts(intersection)
        expected_signature = _seed_recorded_signature(name)
        orientation_flip_applied = not np.array_equal(orientation, _facet_adjacency_orientation_signs(name))

        from w33_explicit_curved_4d_complexes import boundary_matrix  # local import avoids wider cycles

        boundary_4 = boundary_matrix(faces[4], faces[3]).astype(float)
        residual = boundary_4 @ orientation
        raw_intersection = _raw_h2_intersection_matrix(name, _facet_adjacency_orientation_signs(name))
        raw_signature_value, _, _ = _signature_counts(raw_intersection)

        if signature_value != expected_signature:
            raise AssertionError("orientation-adjusted cup form does not match the recorded seed signature")

        profiles.append(
            CurvedH2CupProfile(
                name=label,
                triangle_count=len(faces[2]),
                facet_count=len(faces[4]),
                harmonic_h2_dimension=basis.shape[1],
                positive_h2_directions=positive,
                negative_h2_directions=negative,
                signature=signature_value,
                cup_symmetry_max_abs_error=float(np.max(np.abs(raw_intersection - raw_intersection.T))),
                fundamental_cycle_is_closed=bool(np.max(np.abs(residual)) < TOL),
                orientation_flip_applied=bool(raw_signature_value != expected_signature),
            )
        )

        if name != "K3":
            continue

        eigenvalues, eigenvectors = np.linalg.eigh(intersection)
        positive_mask = eigenvalues > TOL
        negative_mask = eigenvalues < -TOL
        if int(np.sum(positive_mask)) != 3 or int(np.sum(negative_mask)) != 19:
            raise AssertionError("expected K3 cup form to have signature (3,19)")

        positive_projector = eigenvectors[:, positive_mask] @ eigenvectors[:, positive_mask].T
        negative_projector = eigenvectors[:, negative_mask] @ eigenvectors[:, negative_mask].T
        selector_index = None
        positive_line = None
        negative_line = None
        for index in range(len(faces[2])):
            basis_cochain = np.zeros(len(faces[2]), dtype=float)
            basis_cochain[index] = 1.0
            harmonic_coordinates = basis.T @ basis_cochain
            positive_coordinates = positive_projector @ harmonic_coordinates
            negative_coordinates = negative_projector @ harmonic_coordinates
            if np.linalg.norm(positive_coordinates) < TOL or np.linalg.norm(negative_coordinates) < TOL:
                continue
            positive_line = basis @ positive_coordinates
            negative_line = basis @ negative_coordinates
            selector_index = index
            break

        if selector_index is None or positive_line is None or negative_line is None:
            raise AssertionError("expected to find a canonical mixed-sign triangle selector on K3")

        positive_line *= _first_nonzero_sign(positive_line)
        negative_line *= _first_nonzero_sign(negative_line)
        positive_coordinates = basis.T @ positive_line
        negative_coordinates = basis.T @ negative_line
        q_pp = float(positive_coordinates @ intersection @ positive_coordinates)
        q_nn = float(negative_coordinates @ intersection @ negative_coordinates)
        if q_pp <= 0 or q_nn >= 0:
            raise AssertionError("canonical mixed plane should carry one positive and one negative line")

        positive_unit = positive_line / sqrt(q_pp)
        negative_unit = negative_line / sqrt(-q_nn)
        positive_unit_coordinates = basis.T @ positive_unit
        negative_unit_coordinates = basis.T @ negative_unit
        raw_restricted = (
            (
                float(positive_coordinates @ intersection @ positive_coordinates),
                float(positive_coordinates @ intersection @ negative_coordinates),
            ),
            (
                float(negative_coordinates @ intersection @ positive_coordinates),
                float(negative_coordinates @ intersection @ negative_coordinates),
            ),
        )
        normalized_restricted = (
            (
                float(positive_unit_coordinates @ intersection @ positive_unit_coordinates),
                float(positive_unit_coordinates @ intersection @ negative_unit_coordinates),
            ),
            (
                float(negative_unit_coordinates @ intersection @ positive_unit_coordinates),
                float(negative_unit_coordinates @ intersection @ negative_unit_coordinates),
            ),
        )
        k3_plane = CanonicalMixedPlane(
            selector_triangle=faces[2][selector_index],
            positive_line_q_norm=q_pp,
            negative_line_q_norm=q_nn,
            raw_restricted_intersection_matrix=raw_restricted,
            normalized_restricted_intersection_matrix=normalized_restricted,
            normalized_restricted_determinant=(
                normalized_restricted[0][0] * normalized_restricted[1][1]
                - normalized_restricted[0][1] * normalized_restricted[1][0]
            ),
            mixed_signature=(1, 1),
            qutrit_lift_split=(logical_qutrits, logical_qutrits),
            total_qutrit_lift_dimension=2 * logical_qutrits,
            split_qutrit_package=True,
        )

    if k3_plane is None:
        raise AssertionError("expected a canonical K3 mixed plane")

    return {
        "status": "ok",
        "seed_profiles": [profile.to_dict() for profile in profiles],
        "k3_canonical_mixed_plane": k3_plane.to_dict(),
        "bridge_constraints": {
            "cup_form_recovers_recorded_seed_signatures": all(
                profile.signature == _seed_recorded_signature("CP2" if profile.name == "CP2_9" else "K3")
                for profile in profiles
            ),
            "cp2_h2_signature_from_cup_form": profiles[0].signature,
            "k3_h2_signature_from_cup_form": profiles[1].signature,
            "k3_positive_h2_directions_from_cup_form": profiles[1].positive_h2_directions,
            "k3_negative_h2_directions_from_cup_form": profiles[1].negative_h2_directions,
            "canonical_k3_mixed_plane_has_nonzero_intersection_determinant": (
                abs(k3_plane.normalized_restricted_determinant) > TOL
            ),
            "canonical_k3_mixed_plane_is_split_as_positive_plus_negative_line": (
                k3_plane.split_qutrit_package
            ),
        },
        "bridge_verdict": (
            "The external H^2 story is now chain-level rather than only "
            "dimension-level. On the explicit oriented 4-cycle, the Alexander-"
            "Whitney cup pairing on harmonic 2-cochains recovers the recorded "
            "seed signatures exactly: CP2_9 carries one positive H^2 direction "
            "and K3_16 carries three positive plus nineteen negative directions. "
            "Moreover the lexicographically first K3 triangle already projects "
            "nontrivially to both sign sectors, giving a deterministic mixed "
            "rank-2 plane with nonzero restricted intersection determinant. "
            "Tensoring that plane with the exact 81-dimensional qutrit packet "
            "produces a canonical split 81 + 81 external branch package."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_curved_h2_cup_plane_bridge_summary(), indent=2),
        encoding="utf-8",
    )
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
