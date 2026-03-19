"""Exact middle-shell bridge on the torus/Klein route.

The promoted torus/Fano/Klein route already carries the affine packet

    42 = |AGL(1,7)|.

This module promotes the strongest exact middle-shell fact about that packet:

    42 = 2*21 = 3*14 = 6*7,

where

    21 = AG(2,1) = Heawood edges,
    14 = dim(G2) = Heawood vertices,
    6  = shared exceptional transfer channel,
    7  = Phi_6 = beta_0(QCD),
    2  = the sheet-flip / point-line duality factor.

So the affine torus shell is already the exact crossover packet linking the
mod-7 affine side, the Klein/Hurwitz side, the G2 packet, and the live
physics-facing six-by-seven selector.
"""

from __future__ import annotations

from functools import lru_cache
import json
from pathlib import Path
from typing import Any

from w33_heawood_shell_ladder_bridge import build_heawood_shell_ladder_summary
from w33_hurwitz_237_selector_bridge import build_hurwitz_237_selector_summary
from w33_surface_physics_shell_bridge import build_surface_physics_shell_summary


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_affine_middle_shell_bridge_summary.json"


@lru_cache(maxsize=1)
def build_affine_middle_shell_summary() -> dict[str, Any]:
    hurwitz = build_hurwitz_237_selector_summary()
    heawood = build_heawood_shell_ladder_summary()
    physics = build_surface_physics_shell_summary()

    duality_factor = int(hurwitz["hurwitz_237_dictionary"]["duality_sheet_flip_order"])
    q = int(hurwitz["hurwitz_237_dictionary"]["q"])
    affine_order = int(hurwitz["hurwitz_237_dictionary"]["affine_shell_order"])
    phi6 = int(hurwitz["hurwitz_237_dictionary"]["phi6"])
    ag21_length = int(heawood["heawood_shell_dictionary"]["ag21_length"])
    g2_dimension = int(heawood["heawood_shell_dictionary"]["g2_dimension"])
    shared_six = int(physics["standard_model_gauge_dictionary"]["shared_six_channel"])

    return {
        "status": "ok",
        "affine_middle_shell_dictionary": {
            "duality_factor": duality_factor,
            "q": q,
            "phi6": phi6,
            "ag21_length": ag21_length,
            "g2_dimension": g2_dimension,
            "shared_six_channel": shared_six,
            "affine_shell_order": affine_order,
        },
        "exact_factorizations": {
            "affine_shell_equals_2_times_ag21": affine_order == duality_factor * ag21_length,
            "affine_shell_equals_q_times_g2": affine_order == q * g2_dimension,
            "affine_shell_equals_shared_six_times_phi6": affine_order == shared_six * phi6,
            "ag21_equals_3_times_phi6": ag21_length == q * phi6,
            "g2_equals_2_times_phi6": g2_dimension == duality_factor * phi6,
            "shared_six_equals_2_times_q": shared_six == duality_factor * q,
        },
        "bridge_verdict": (
            "The affine torus shell is the exact middle packet of the promoted "
            "torus/Klein route. It is simultaneously 42 = 2*21, 42 = 3*14, and "
            "42 = 6*7, so the same object is being seen as sheet-flip times "
            "Heawood/AG21 edge packet, field value q times G2 packet, and shared "
            "exceptional transfer channel times the exact QCD selector Phi_6. "
            "That makes 42 the compressed crossover shell between the affine "
            "mod-7 route and the physics-facing selector ladder, before the "
            "successive lifts to 84, 168, and 336."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_affine_middle_shell_summary(), indent=2),
        encoding="utf-8",
    )
    return path


if __name__ == "__main__":
    write_summary()
