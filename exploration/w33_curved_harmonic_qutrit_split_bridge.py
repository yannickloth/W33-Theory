"""Exact degree split of the protected harmonic qutrit lift on curved seeds.

The older curved transport/matter bridge already recorded the total protected
harmonic matter counts

- ``243`` on ``CP2_9``,
- ``1944`` on ``K3_16``.

Those totals are exact, but they are coarser than the actual bridge question.
The explicit external Hodge package now allows the protected qutrit lift to be
split by degree:

    81 * (b0 + b2 + b4)
      = 81*b0   +   81*b2   +   81*b4.

On the current explicit closed 4D seeds, the endpoint terms are universal:

- ``b0 = b4 = 1`` on both seeds,
- so the endpoint packet is always ``81 + 81 = 162``.

All seed dependence therefore lives in the middle-degree qutrit channel
``81 x H^2``.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from fractions import Fraction
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

from w33_curved_external_hodge_product import build_curved_external_hodge_product_summary
from w33_ternary_homological_code_bridge import build_ternary_homological_code_summary


DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_curved_harmonic_qutrit_split_bridge_summary.json"


def _fraction_dict(value: Fraction) -> dict[str, Any]:
    exact = str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"
    return {"exact": exact, "float": float(value)}


@dataclass(frozen=True)
class CurvedHarmonicQutritSplitProfile:
    name: str
    logical_qutrits: int
    zero_modes_by_degree: tuple[int, int, int, int, int]
    endpoint_qutrit_channel: int
    middle_degree_qutrit_channel: int
    total_harmonic_qutrit_channel: int
    seed_dependent_growth_above_endpoints: int
    middle_fraction_of_total: Fraction

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["middle_fraction_of_total"] = _fraction_dict(self.middle_fraction_of_total)
        return data


def _profile(profile: dict[str, Any], logical_qutrits: int) -> CurvedHarmonicQutritSplitProfile:
    zero_modes = tuple(int(value) for value in profile["zero_modes_by_degree"])
    endpoint_qutrit_channel = logical_qutrits * (zero_modes[0] + zero_modes[4])
    middle_degree_qutrit_channel = logical_qutrits * zero_modes[2]
    total_harmonic_qutrit_channel = logical_qutrits * sum(zero_modes)
    return CurvedHarmonicQutritSplitProfile(
        name="CP2_9" if str(profile["name"]) == "CP2" else "K3_16",
        logical_qutrits=logical_qutrits,
        zero_modes_by_degree=zero_modes,
        endpoint_qutrit_channel=endpoint_qutrit_channel,
        middle_degree_qutrit_channel=middle_degree_qutrit_channel,
        total_harmonic_qutrit_channel=total_harmonic_qutrit_channel,
        seed_dependent_growth_above_endpoints=total_harmonic_qutrit_channel - endpoint_qutrit_channel,
        middle_fraction_of_total=Fraction(middle_degree_qutrit_channel, total_harmonic_qutrit_channel),
    )


def build_curved_harmonic_qutrit_split_bridge_summary() -> dict[str, Any]:
    logical_qutrits = int(build_ternary_homological_code_summary()["ternary_css_code"]["logical_qutrits"])
    external_profiles = build_curved_external_hodge_product_summary()["external_profiles"]
    profiles = [_profile(profile, logical_qutrits) for profile in external_profiles]
    cp2, k3 = profiles

    return {
        "status": "ok",
        "seed_profiles": [profile.to_dict() for profile in profiles],
        "bridge_constraints": {
            "logical_qutrits": logical_qutrits,
            "universal_endpoint_qutrit_channel": cp2.endpoint_qutrit_channel,
            "endpoint_qutrit_channel_matches_on_all_explicit_seeds": (
                cp2.endpoint_qutrit_channel == k3.endpoint_qutrit_channel
            ),
            "cp2_total_harmonic_qutrit_channel": cp2.total_harmonic_qutrit_channel,
            "k3_total_harmonic_qutrit_channel": k3.total_harmonic_qutrit_channel,
            "cp2_middle_degree_qutrit_channel": cp2.middle_degree_qutrit_channel,
            "k3_middle_degree_qutrit_channel": k3.middle_degree_qutrit_channel,
            "all_seed_dependence_is_middle_degree": (
                cp2.seed_dependent_growth_above_endpoints == cp2.middle_degree_qutrit_channel
                and k3.seed_dependent_growth_above_endpoints == k3.middle_degree_qutrit_channel
            ),
            "k3_minus_cp2_total_harmonic_gap": (
                k3.total_harmonic_qutrit_channel - cp2.total_harmonic_qutrit_channel
            ),
            "k3_minus_cp2_middle_degree_gap": (
                k3.middle_degree_qutrit_channel - cp2.middle_degree_qutrit_channel
            ),
        },
        "bridge_verdict": (
            "The older protected harmonic matter counts are now degree-resolved. "
            "On both explicit curved seeds the endpoint qutrit packet is the same "
            "universal 162-dimensional channel coming from b0 = b4 = 1. The only "
            "seed-dependent part is the middle-degree packet 81 x H^2: 81 on CP2_9 "
            "and 1782 on K3_16. So the full protected harmonic counts 243 and 1944 "
            "should be read as 162 plus the middle-degree branch, not as undivided "
            "global zero-mode totals. The external bridge-growth problem is "
            "therefore purely a middle-degree H^2 problem."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_curved_harmonic_qutrit_split_bridge_summary(), indent=2),
        encoding="utf-8",
    )
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
