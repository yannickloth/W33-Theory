"""Exact qutrit middle-degree bridge on the explicit curved seeds.

The finite side already supplies an exact 81-dimensional qutrit matter sector.
The curved external side now has exact harmonic middle cohomology:

- ``CP2_9`` with ``b2 = 1`` and signature split ``(1,0)``;
- ``K3_16`` with ``b2 = 22`` and signature split ``(3,19)``.

This module isolates the exact middle-degree channel obtained by tensoring the
qutrit matter sector with the external harmonic ``H^2`` sector.

It is deliberately narrower than the older total-harmonic lift:

- total external harmonics count ``b0 + b2 + b4``;
- the bridge branch lives, if harmonic, in the middle ``H^2`` channel only.

So the relevant exact package is ``81 ⊗ H^2(X)``, not merely ``81`` times the
total harmonic-form count.
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

from w33_curved_h2_host_bridge import build_curved_h2_host_bridge_summary
from w33_ternary_homological_code_bridge import build_ternary_homological_code_summary


DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_curved_h2_qutrit_bridge_summary.json"


@dataclass(frozen=True)
class CurvedH2QutritProfile:
    name: str
    logical_qutrits: int
    h2_dimension: int
    b2_plus: int
    b2_minus: int
    total_middle_degree_qutrit_channel: int
    positive_middle_degree_qutrit_channel: int
    negative_middle_degree_qutrit_channel: int
    rank2_h2_qutrit_branch_available: bool
    mixed_sign_middle_degree_qutrit_channel_available: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _profile(seed: dict[str, Any], logical_qutrits: int) -> CurvedH2QutritProfile:
    h2_dimension = int(seed["h2_dimension"])
    b2_plus = int(seed["b2_plus"])
    b2_minus = int(seed["b2_minus"])
    return CurvedH2QutritProfile(
        name=str(seed["name"]),
        logical_qutrits=logical_qutrits,
        h2_dimension=h2_dimension,
        b2_plus=b2_plus,
        b2_minus=b2_minus,
        total_middle_degree_qutrit_channel=logical_qutrits * h2_dimension,
        positive_middle_degree_qutrit_channel=logical_qutrits * b2_plus,
        negative_middle_degree_qutrit_channel=logical_qutrits * b2_minus,
        rank2_h2_qutrit_branch_available=h2_dimension >= 2,
        mixed_sign_middle_degree_qutrit_channel_available=(b2_plus > 0 and b2_minus > 0),
    )


def build_curved_h2_qutrit_bridge_summary() -> dict[str, Any]:
    logical_qutrits = int(build_ternary_homological_code_summary()["ternary_css_code"]["logical_qutrits"])
    host_summary = build_curved_h2_host_bridge_summary()
    profiles = [_profile(seed, logical_qutrits) for seed in host_summary["seed_profiles"]]
    cp2, k3 = profiles

    return {
        "status": "ok",
        "seed_profiles": [profile.to_dict() for profile in profiles],
        "bridge_constraints": {
            "logical_qutrits": logical_qutrits,
            "cp2_middle_degree_qutrit_channel": cp2.total_middle_degree_qutrit_channel,
            "k3_middle_degree_qutrit_channel": k3.total_middle_degree_qutrit_channel,
            "k3_minus_cp2_middle_degree_gap": (
                k3.total_middle_degree_qutrit_channel - cp2.total_middle_degree_qutrit_channel
            ),
            "cp2_is_not_rank2_middle_degree_host": not cp2.rank2_h2_qutrit_branch_available,
            "k3_is_rank2_middle_degree_host": k3.rank2_h2_qutrit_branch_available,
            "k3_has_both_middle_degree_sign_channels": k3.mixed_sign_middle_degree_qutrit_channel_available,
            "first_exact_middle_degree_qutrit_host_is_k3": (
                (not cp2.rank2_h2_qutrit_branch_available) and k3.rank2_h2_qutrit_branch_available
            ),
        },
        "bridge_verdict": (
            "The explicit external host theorem can now be read on the actual "
            "qutrit matter sector. Tensoring the exact 81-dimensional W33 "
            "qutrit package with harmonic H^2 gives a middle-degree channel of "
            "dimension 81 on CP2_9 and 1782 on K3_16. The K3 channel splits "
            "exactly as 243 positive plus 1539 negative qutrit modes, while "
            "CP2_9 contributes only the definite 81-dimensional positive packet. "
            "So if the live bridge branch is genuinely harmonic and middle-degree, "
            "the first exact qutrit host is already the K3-side H^2 package "
            "rather than the coarser total-harmonic lift."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_curved_h2_qutrit_bridge_summary(), indent=2),
        encoding="utf-8",
    )
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
