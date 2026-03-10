"""Refinement-invariant 4D curvature budget for the external bridge seeds.

The minimal-triangulation bridge already identified ``CP2`` and ``K3`` as
curved 4D simplicial seeds. This module sharpens that statement using exact
oriented 4-manifold invariants:

- Euler characteristic ``chi`` blocks flat metrics in the closed case;
- signature ``tau`` blocks conformal flatness and forces a nonzero Weyl-curvature
  channel through the Hirzebruch signature theorem.

For any closed oriented Riemannian 4-manifold,

    tau(M) = (1 / 12 pi^2) * integral (|W^+|^2 - |W^-|^2) dV

so

    integral |W|^2 dV >= 12 pi^2 |tau(M)|.

This gives a metric-independent lower bound on the quadratic curvature channel
that survives every barycentric refinement because the topology is unchanged.
It does not yet prove the Einstein-Hilbert coefficient, but it removes the last
ambiguity about whether the curved external factor can carry genuine 4D
curvature in the spectral-action sense.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from math import pi
from pathlib import Path
import sys
from typing import Any


if __package__ in {None, ""}:
    ROOT = Path(__file__).resolve().parents[1]
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
else:
    ROOT = Path(__file__).resolve().parents[1]

from w33_minimal_triangulation_bridge import (
    barycentric_subdivision_f_vector,
    cp2_seed,
    euler_characteristic_from_f_vector,
    k3_seed,
)


DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_curved_4d_curvature_budget_summary.json"


@dataclass(frozen=True)
class Curved4DSeed:
    name: str
    euler_characteristic: int
    signature: int
    nonflat_topologically_forced: bool
    nonconformally_flat_topologically_forced: bool
    hitchin_thorpe_plus: int
    hitchin_thorpe_minus: int
    weyl_l2_floor: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def weyl_l2_floor(signature: int) -> float:
    """Metric-independent lower bound from the signature theorem."""

    return 12.0 * (pi**2) * abs(signature)


def hitchin_thorpe_numbers(chi: int, tau: int) -> tuple[int, int]:
    return (2 * chi + 3 * tau, 2 * chi - 3 * tau)


def torus4_seed() -> Curved4DSeed:
    plus, minus = hitchin_thorpe_numbers(0, 0)
    return Curved4DSeed(
        name="T4",
        euler_characteristic=0,
        signature=0,
        nonflat_topologically_forced=False,
        nonconformally_flat_topologically_forced=False,
        hitchin_thorpe_plus=plus,
        hitchin_thorpe_minus=minus,
        weyl_l2_floor=weyl_l2_floor(0),
    )


def cp2_curvature_seed() -> Curved4DSeed:
    seed = cp2_seed()
    plus, minus = hitchin_thorpe_numbers(seed.euler_characteristic, 1)
    return Curved4DSeed(
        name="CP2",
        euler_characteristic=seed.euler_characteristic,
        signature=1,
        nonflat_topologically_forced=seed.flat_metric_topologically_forbidden,
        nonconformally_flat_topologically_forced=True,
        hitchin_thorpe_plus=plus,
        hitchin_thorpe_minus=minus,
        weyl_l2_floor=weyl_l2_floor(1),
    )


def k3_curvature_seed() -> Curved4DSeed:
    seed = k3_seed()
    plus, minus = hitchin_thorpe_numbers(seed.euler_characteristic, -16)
    return Curved4DSeed(
        name="K3",
        euler_characteristic=seed.euler_characteristic,
        signature=-16,
        nonflat_topologically_forced=seed.flat_metric_topologically_forbidden,
        nonconformally_flat_topologically_forced=True,
        hitchin_thorpe_plus=plus,
        hitchin_thorpe_minus=minus,
        weyl_l2_floor=weyl_l2_floor(-16),
    )


def refinement_invariance_checks(steps: tuple[int, ...] = (0, 1, 2)) -> dict[str, Any]:
    cp2 = cp2_seed()
    k3 = k3_seed()
    return {
        "steps": list(steps),
        "cp2_euler_characteristics": [
            euler_characteristic_from_f_vector(
                barycentric_subdivision_f_vector(cp2.f_vector, steps=step)
            )
            for step in steps
        ],
        "k3_euler_characteristics": [
            euler_characteristic_from_f_vector(
                barycentric_subdivision_f_vector(k3.f_vector, steps=step)
            )
            for step in steps
        ],
        "signature_is_topological_invariant": True,
    }


def build_curved_4d_curvature_budget_summary() -> dict[str, Any]:
    torus = torus4_seed()
    cp2 = cp2_curvature_seed()
    k3 = k3_curvature_seed()
    refinement = refinement_invariance_checks()

    return {
        "status": "ok",
        "comparison_seed": torus.to_dict(),
        "curved_seeds": [cp2.to_dict(), k3.to_dict()],
        "refinement_invariance": refinement,
        "bridge_verdict": (
            "CP2 and K3 are not merely non-flat seed candidates. Their nonzero "
            "signatures force a nonzero Weyl-curvature channel on every closed "
            "oriented metric, and that lower bound survives every barycentric "
            "refinement because the topology is unchanged. So the curved external "
            "4D bridge now has an exact quadratic-curvature budget, not just a "
            "heuristic 'curved somehow' label."
        ),
        "remaining_gap": (
            "The missing theorem is now narrower: lift this persistent external "
            "4D curvature budget into the actual spectral-action coefficients of "
            "the refined almost-commutative product, especially the Einstein-"
            "Hilbert channel."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_curved_4d_curvature_budget_summary(), indent=2),
        encoding="utf-8",
    )
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
