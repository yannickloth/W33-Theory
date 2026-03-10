"""Executable almost-commutative bridge for W(3,3) plus tomotope covers.

This module does not claim a finished continuum theorem. It encodes the next
mathematically coherent bridge layer:

1. External 4D refinement family: the discrete 4-torus `(C_n)^4`.
2. Internal finite geometry: the exact W(3,3) finite Dirac operator on 162
   matter-plus-conjugate states.
3. Internal infinite cover tower: the tomotope `Q_k` family.

At the squared-operator level the almost-commutative product is the exact
Kronecker sum

    Delta_ext tensor 1 + 1 tensor D_F^2,

so heat traces factorize exactly. The point is to make the 4D scale parameter
live in the external family while the tomotope remains an internal tower.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from functools import lru_cache
import json
from math import log, sin, pi
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

from tools.tomotope_cover_bridge import qk_level
from w33_finite_spectral_triple import TOTAL_DIM, finite_dirac_162


DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_tomotope_ac_bridge_summary.json"


@dataclass(frozen=True)
class BridgeLevel:
    """Concrete product-level bridge data for one `(n, k)` pair."""

    external_n: int
    tomotope_k: int
    external_vertex_count: int
    external_degree: int
    internal_hilbert_dim: int
    product_hilbert_dim: int
    tomotope_unit_cube_count: int
    tomotope_regular_polytope: bool
    external_growth_degree: float
    tomotope_carrier_growth_degree: float
    factorization_error_at_t_0_1: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _validate_positive_int(name: str, value: int) -> None:
    if not isinstance(value, int) or value < 1:
        raise ValueError(f"{name} must be a positive integer")


def cycle_laplacian_eigenvalues(n: int, scale_to_unit: bool = True) -> np.ndarray:
    """Eigenvalues of the cycle graph Laplacian on `C_n`.

    With `scale_to_unit=True` we multiply by `n^2`, which is the natural mesh
    rescaling for a unit-length refinement family.
    """

    _validate_positive_int("n", n)
    eigs = np.array([4.0 * sin(pi * k / n) ** 2 for k in range(n)], dtype=float)
    if scale_to_unit:
        eigs *= n**2
    return eigs


def torus4_laplacian_eigenvalues(n: int, scale_to_unit: bool = True) -> np.ndarray:
    """Eigenvalues of the Cartesian 4-torus `(C_n)^4` Laplacian."""

    one_d = cycle_laplacian_eigenvalues(n, scale_to_unit=scale_to_unit)
    grid = (
        one_d[:, None, None, None]
        + one_d[None, :, None, None]
        + one_d[None, None, :, None]
        + one_d[None, None, None, :]
    )
    return np.sort(grid.reshape(-1))


@lru_cache(maxsize=1)
def w33_internal_dirac_squared_eigenvalues() -> np.ndarray:
    dirac = finite_dirac_162()
    eigs = np.linalg.eigvalsh(dirac.astype(float))
    return np.sort(eigs**2)


def external_heat_trace(n: int, t: float) -> float:
    eigs = torus4_laplacian_eigenvalues(n)
    return float(np.sum(np.exp(-t * eigs)))


def internal_heat_trace(t: float) -> float:
    eigs = w33_internal_dirac_squared_eigenvalues()
    return float(np.sum(np.exp(-t * eigs)))


def product_squared_eigenvalues(n: int) -> np.ndarray:
    """Eigenvalues of `Delta_ext ⊗ 1 + 1 ⊗ D_F^2`."""

    ext = torus4_laplacian_eigenvalues(n)
    internal = w33_internal_dirac_squared_eigenvalues()
    return np.sort((ext[:, None] + internal[None, :]).reshape(-1))


def product_heat_trace(n: int, t: float) -> float:
    eigs = product_squared_eigenvalues(n)
    return float(np.sum(np.exp(-t * eigs)))


def _growth_degree(v_small: int, v_large: int, n_small: int, n_large: int) -> float:
    return log(v_large / v_small) / log(n_large / n_small)


def external_growth_degree(n_small: int = 2, n_large: int = 4) -> float:
    return _growth_degree(n_large**4, n_small**4, n_large, n_small)


def tomotope_carrier_growth_degree(k_small: int = 2, k_large: int = 4) -> float:
    small = qk_level(k_small)
    large = qk_level(k_large)
    if small.vertices is None or large.vertices is None:
        raise ValueError("tomotope carrier growth degree requires k > 1")
    return _growth_degree(large.vertices, small.vertices, k_large, k_small)


def build_bridge_level(external_n: int = 4, tomotope_k: int = 2) -> BridgeLevel:
    _validate_positive_int("external_n", external_n)
    _validate_positive_int("tomotope_k", tomotope_k)

    tomo = qk_level(tomotope_k)
    factorized = external_heat_trace(external_n, 0.1) * internal_heat_trace(0.1)
    direct = product_heat_trace(external_n, 0.1)
    return BridgeLevel(
        external_n=external_n,
        tomotope_k=tomotope_k,
        external_vertex_count=external_n**4,
        external_degree=8,
        internal_hilbert_dim=TOTAL_DIM,
        product_hilbert_dim=(external_n**4) * TOTAL_DIM,
        tomotope_unit_cube_count=tomo.unit_cube_count,
        tomotope_regular_polytope=tomo.regular_polytope,
        external_growth_degree=external_growth_degree(),
        tomotope_carrier_growth_degree=tomotope_carrier_growth_degree(),
        factorization_error_at_t_0_1=abs(direct - factorized),
    )


def build_bridge_summary(external_n: int = 4, tomotope_k: int = 2) -> dict[str, Any]:
    level = build_bridge_level(external_n=external_n, tomotope_k=tomotope_k)
    tomo = qk_level(tomotope_k)

    return {
        "status": "ok",
        "bridge_level": level.to_dict(),
        "external_family": {
            "name": "(C_n)^4",
            "scaled_laplacian": "n^2 * Delta_graph",
            "vertex_count_formula": "n^4",
            "degree": 8,
            "zero_mode_count": 1,
        },
        "internal_w33": {
            "hilbert_dim": TOTAL_DIM,
            "dirac_square_eigenvalue_count": int(w33_internal_dirac_squared_eigenvalues().size),
        },
        "tomotope_internal_tower": {
            "k": tomotope_k,
            "unit_cube_count": tomo.unit_cube_count,
            "regular_polytope": tomo.regular_polytope,
            "monodromy_order": tomo.monodromy_order,
        },
        "product_operator": {
            "formula": "Delta_ext tensor 1 + 1 tensor D_F^2",
            "heat_trace_factorizes": True,
        },
        "verdict": (
            "The external 4D torus family supplies the genuine quartic scale "
            "parameter. The tomotope Q_k family remains a real internal tower, "
            "but its native carrier growth is cubic, so it does not replace the "
            "external 4D factor."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(json.dumps(build_bridge_summary(), indent=2), encoding="utf-8")
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
