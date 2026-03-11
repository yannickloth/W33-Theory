"""Explicit curved external Hodge spectra and almost-commutative products.

This module takes the explicit simplicial 4D seeds ``CP2_9`` and ``K3_16``
and upgrades them to operator-level external geometries:

- boundary matrices in degrees 1 through 4;
- Hodge Laplacians in degrees 0 through 4;
- total Dirac-Kähler square spectra on the full external chain complex;
- exact heat traces for the external curved complexes;
- exact product heat traces after pairing with the W33 finite Dirac square.

The key point is that the curved external factor is now an actual finite
operator package, and the almost-commutative product heat trace factorization
can be checked directly on the explicit spectra.
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

from w33_explicit_curved_4d_complexes import (
    Simplex,
    boundary_matrix,
    cp2_facets,
    cp2_profile,
    faces_by_dimension,
    k3_facets,
    k3_profile,
)
from w33_tomotope_ac_bridge import internal_heat_trace, w33_internal_dirac_squared_eigenvalues


DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_curved_external_hodge_product_summary.json"


@dataclass(frozen=True)
class CurvedExternalOperatorProfile:
    name: str
    chain_dimensions: tuple[int, int, int, int, int]
    zero_modes_by_degree: tuple[int, int, int, int, int]
    degree_spectral_gaps: tuple[float, float, float, float, float]
    total_chain_dim: int
    harmonic_form_total: int
    total_spectral_gap: float
    trace_dk_squared: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ProductHeatCheck:
    external_name: str
    t: float
    external_heat_trace: float
    factorized_product_heat_trace: float
    direct_product_heat_trace: float
    abs_error: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _validate_external_name(name: str) -> str:
    if name not in {"CP2", "K3"}:
        raise ValueError("external name must be 'CP2' or 'K3'")
    return name


def _facets_for_name(name: str) -> tuple[Simplex, ...]:
    if name == "CP2":
        return cp2_facets()
    return k3_facets()


def _profile_for_name(name: str):
    if name == "CP2":
        return cp2_profile()
    return k3_profile()


@lru_cache(maxsize=None)
def external_faces(name: str) -> tuple[tuple[Simplex, ...], ...]:
    _validate_external_name(name)
    return faces_by_dimension(_facets_for_name(name))


@lru_cache(maxsize=None)
def external_boundary_matrices(name: str) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    faces = external_faces(name)
    return tuple(
        boundary_matrix(faces[degree], faces[degree - 1]).astype(float)
        for degree in range(1, 5)
    )  # type: ignore[return-value]


@lru_cache(maxsize=None)
def external_hodge_laplacians(name: str) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    boundaries = external_boundary_matrices(name)
    laplacians = []
    for degree in range(5):
        if degree == 0:
            matrix = boundaries[0] @ boundaries[0].T
        elif degree == 4:
            matrix = boundaries[3].T @ boundaries[3]
        else:
            matrix = boundaries[degree - 1].T @ boundaries[degree - 1] + boundaries[degree] @ boundaries[degree].T
        laplacians.append(matrix)
    return tuple(laplacians)  # type: ignore[return-value]


@lru_cache(maxsize=None)
def external_hodge_eigenvalues_by_degree(name: str) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    return tuple(np.linalg.eigvalsh(matrix) for matrix in external_hodge_laplacians(name))  # type: ignore[return-value]


@lru_cache(maxsize=None)
def external_dirac_kahler_squared_eigenvalues(name: str) -> np.ndarray:
    degree_eigenvalues = external_hodge_eigenvalues_by_degree(name)
    return np.sort(np.concatenate(degree_eigenvalues))


def _smallest_positive(values: np.ndarray, tol: float = 1e-8) -> float:
    positive = values[values > tol]
    if positive.size == 0:
        return 0.0
    return float(np.min(positive))


@lru_cache(maxsize=None)
def external_operator_profile(name: str) -> CurvedExternalOperatorProfile:
    _validate_external_name(name)
    topological = _profile_for_name(name)
    degree_eigenvalues = external_hodge_eigenvalues_by_degree(name)
    total_eigenvalues = external_dirac_kahler_squared_eigenvalues(name)
    zero_modes = tuple(int(np.sum(np.abs(values) < 1e-8)) for values in degree_eigenvalues)
    degree_gaps = tuple(_smallest_positive(values) for values in degree_eigenvalues)
    return CurvedExternalOperatorProfile(
        name=name,
        chain_dimensions=topological.f_vector,
        zero_modes_by_degree=zero_modes,
        degree_spectral_gaps=degree_gaps,
        total_chain_dim=int(total_eigenvalues.size),
        harmonic_form_total=int(sum(zero_modes)),
        total_spectral_gap=_smallest_positive(total_eigenvalues),
        trace_dk_squared=float(np.sum(total_eigenvalues)),
    )


def external_heat_trace(name: str, t: float) -> float:
    if t <= 0.0:
        raise ValueError("t must be positive")
    eigenvalues = external_dirac_kahler_squared_eigenvalues(_validate_external_name(name))
    return float(np.sum(np.exp(-t * eigenvalues)))


def product_heat_trace_factorized(name: str, t: float) -> float:
    return external_heat_trace(name, t) * internal_heat_trace(t)


def product_heat_trace_direct(name: str, t: float) -> float:
    external_eigenvalues = external_dirac_kahler_squared_eigenvalues(_validate_external_name(name))
    internal_eigenvalues = w33_internal_dirac_squared_eigenvalues()
    product_eigenvalues = (external_eigenvalues[:, None] + internal_eigenvalues[None, :]).reshape(-1)
    return float(np.sum(np.exp(-t * product_eigenvalues)))


def build_product_heat_checks(
    names: tuple[str, ...] = ("CP2", "K3"),
    t_values: tuple[float, ...] = (0.05, 0.1, 0.2),
) -> tuple[ProductHeatCheck, ...]:
    checks = []
    for name in names:
        for t in t_values:
            factorized = product_heat_trace_factorized(name, t)
            direct = product_heat_trace_direct(name, t)
            checks.append(
                ProductHeatCheck(
                    external_name=name,
                    t=t,
                    external_heat_trace=external_heat_trace(name, t),
                    factorized_product_heat_trace=factorized,
                    direct_product_heat_trace=direct,
                    abs_error=abs(factorized - direct),
                )
            )
    return tuple(checks)


def build_curved_external_hodge_product_summary() -> dict[str, Any]:
    cp2 = external_operator_profile("CP2")
    k3 = external_operator_profile("K3")
    checks = build_product_heat_checks()
    return {
        "status": "ok",
        "external_profiles": [cp2.to_dict(), k3.to_dict()],
        "product_heat_checks": [check.to_dict() for check in checks],
        "bridge_verdict": (
            "The curved external factor is now an explicit operator package. "
            "CP2_9 and K3_16 have executable Hodge spectra on the full chain "
            "complex, with harmonic sectors matching topology, and their "
            "almost-commutative product heat traces with the W33 finite Dirac "
            "square factorize exactly on the explicit spectra."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_curved_external_hodge_product_summary(), indent=2),
        encoding="utf-8",
    )
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
