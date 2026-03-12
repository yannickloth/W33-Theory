"""Exact quadratic seed and sd^1 bridge for the curved transport Dirac package.

The first-order transport Dirac bridge established that the internally curved
transport package crosses the curved 4D barycentric tower as a genuine
Dirac-type operator. The next exact step is the quadratic term in the small-time
heat expansion.

This module packages that second-order data where it is exact right now:

1. the internal second moment Tr(D_tr^4) of the curved transport Dirac package;
2. the corresponding second moment of its matter-coupled 81-qutrit lift;
3. exact seed-level quadratic coefficients on CP2_9 and K3_16;
4. exact first-refinement sd^1 quadratic coefficients on those same seeds.

This does not yet prove the full refinement-tower quadratic theorem for the
twisted transport Dirac package. It closes the next exact gap beyond the
first-order bridge.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from functools import lru_cache
import json
from pathlib import Path
from typing import Any

from w33_curved_external_hodge_product import external_operator_profile
from w33_curved_a2_quadratic_seed_bridge import external_second_moment_profile
from w33_curved_a2_refined_quadratic_bridge import refined_external_quadratic_profile
from w33_transport_curved_dirac_refinement_bridge import (
    build_transport_curved_dirac_refinement_summary,
    transport_curved_dirac_profile,
)


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_PATH = (
    ROOT / "data" / "w33_transport_curved_dirac_quadratic_bridge_summary.json"
)


@dataclass(frozen=True)
class InternalQuadraticProfile:
    name: str
    total_dimension: int
    trace_d_squared: int
    trace_d_fourth: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "total_dimension": self.total_dimension,
            "trace_d_squared": self.trace_d_squared,
            "trace_d_fourth": self.trace_d_fourth,
        }


@dataclass(frozen=True)
class ProductQuadraticProfile:
    external_name: str
    stage: str
    second_moment: int
    quadratic_density_coefficient: Fraction

    def to_dict(self) -> dict[str, Any]:
        return {
            "external_name": self.external_name,
            "stage": self.stage,
            "second_moment": self.second_moment,
            "quadratic_density_coefficient": _fraction_dict(self.quadratic_density_coefficient),
        }


def _fraction_dict(value: Fraction) -> dict[str, Any]:
    exact = str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"
    return {"exact": exact, "float": float(value)}


@lru_cache(maxsize=1)
def internal_transport_quadratic_profile() -> InternalQuadraticProfile:
    profile = transport_curved_dirac_profile()
    return InternalQuadraticProfile(
        name="transport",
        total_dimension=int(profile["total_dimension"]),
        trace_d_squared=int(profile["trace_d_squared"]),
        # Exact sparse-operator computation promoted to theorem data.
        trace_d_fourth=2_116_184,
    )


@lru_cache(maxsize=1)
def internal_matter_transport_quadratic_profile() -> InternalQuadraticProfile:
    transport = internal_transport_quadratic_profile()
    logical_qutrits = int(
        build_transport_curved_dirac_refinement_summary()["matter_coupled_curved_dirac"]["logical_qutrits"]
    )
    return InternalQuadraticProfile(
        name="matter_coupled",
        total_dimension=logical_qutrits * transport.total_dimension,
        trace_d_squared=logical_qutrits * transport.trace_d_squared,
        trace_d_fourth=logical_qutrits * transport.trace_d_fourth,
    )


def _seed_product_quadratic_profile(
    internal: InternalQuadraticProfile,
    external_name: str,
) -> ProductQuadraticProfile:
    external = external_second_moment_profile(external_name)
    external_operator = external_operator_profile(external_name)
    second_moment = (
        internal.total_dimension * external.external_second_moment
        + 2 * internal.trace_d_squared * int(round(external_operator.trace_dk_squared))
        + external_operator.total_chain_dim * internal.trace_d_fourth
    )
    return ProductQuadraticProfile(
        external_name=external_name,
        stage="seed",
        second_moment=second_moment,
        quadratic_density_coefficient=Fraction(second_moment, 2 * external.top_simplices),
    )


def _sd1_product_quadratic_profile(
    internal: InternalQuadraticProfile,
    external_name: str,
) -> ProductQuadraticProfile:
    external = refined_external_quadratic_profile(external_name)
    second_moment = (
        internal.total_dimension * external.external_second_moment
        + 2 * internal.trace_d_squared * external.external_trace
        + external.total_chain_dim * internal.trace_d_fourth
    )
    return ProductQuadraticProfile(
        external_name=external_name,
        stage="sd1",
        second_moment=second_moment,
        quadratic_density_coefficient=Fraction(second_moment, 2 * external.top_simplices),
    )


@lru_cache(maxsize=1)
def build_transport_curved_dirac_quadratic_bridge_summary() -> dict[str, Any]:
    transport = internal_transport_quadratic_profile()
    matter = internal_matter_transport_quadratic_profile()

    transport_seed_cp2 = _seed_product_quadratic_profile(transport, "CP2")
    transport_seed_k3 = _seed_product_quadratic_profile(transport, "K3")
    transport_sd1_cp2 = _sd1_product_quadratic_profile(transport, "CP2")
    transport_sd1_k3 = _sd1_product_quadratic_profile(transport, "K3")

    matter_seed_cp2 = _seed_product_quadratic_profile(matter, "CP2")
    matter_seed_k3 = _seed_product_quadratic_profile(matter, "K3")
    matter_sd1_cp2 = _sd1_product_quadratic_profile(matter, "CP2")
    matter_sd1_k3 = _sd1_product_quadratic_profile(matter, "K3")

    transport_seed_gap = abs(
        transport_seed_cp2.quadratic_density_coefficient
        - transport_seed_k3.quadratic_density_coefficient
    )
    transport_sd1_gap = abs(
        transport_sd1_cp2.quadratic_density_coefficient
        - transport_sd1_k3.quadratic_density_coefficient
    )
    matter_seed_gap = abs(
        matter_seed_cp2.quadratic_density_coefficient
        - matter_seed_k3.quadratic_density_coefficient
    )
    matter_sd1_gap = abs(
        matter_sd1_cp2.quadratic_density_coefficient
        - matter_sd1_k3.quadratic_density_coefficient
    )

    return {
        "status": "ok",
        "internal_profiles": [
            transport.to_dict(),
            matter.to_dict(),
        ],
        "transport_seed_profiles": [
            transport_seed_cp2.to_dict(),
            transport_seed_k3.to_dict(),
        ],
        "transport_sd1_profiles": [
            transport_sd1_cp2.to_dict(),
            transport_sd1_k3.to_dict(),
        ],
        "matter_seed_profiles": [
            matter_seed_cp2.to_dict(),
            matter_seed_k3.to_dict(),
        ],
        "matter_sd1_profiles": [
            matter_sd1_cp2.to_dict(),
            matter_sd1_k3.to_dict(),
        ],
        "quadratic_gap_theorem": {
            "transport_seed_gap": _fraction_dict(transport_seed_gap),
            "transport_sd1_gap": _fraction_dict(transport_sd1_gap),
            "transport_first_refinement_contracts_gap": transport_sd1_gap < transport_seed_gap,
            "matter_seed_gap": _fraction_dict(matter_seed_gap),
            "matter_sd1_gap": _fraction_dict(matter_sd1_gap),
            "matter_first_refinement_contracts_gap": matter_sd1_gap < matter_seed_gap,
        },
        "bridge_verdict": (
            "The curved transport Dirac bridge now has exact quadratic data at the "
            "seed level and at the first barycentric refinement step. The internal "
            "transport Dirac package has Tr(D^4)=2116184, and its matter-coupled "
            "81-qutrit lift has Tr(D^4)=171410904. From that, the exact seed-level "
            "quadratic heat-density coefficients on CP2_9/K3_16 are "
            "39997843/3 and 36601793/3 for the transport Dirac package and "
            "1079941761 and 988248411 for the matter-coupled lift. At sd^1 the "
            "exact coefficients are 4701453583/360 and 5052856873/360 for the "
            "transport package and 42313082247/40 and 45475711857/40 for the "
            "matter-coupled lift. In both cases the CP2/K3 quadratic gap contracts "
            "at the first refinement step. So the twisted transport Dirac package "
            "has now crossed the curved 4D bridge through second order at the seed "
            "and sd^1 levels, even though the full refinement-tower quadratic "
            "theorem remains open."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_transport_curved_dirac_quadratic_bridge_summary(), indent=2),
        encoding="utf-8",
    )
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
