"""Exact (2,3,7) Hurwitz selector packaged by the live torus/Klein shell.

The Klein quartic is the classical genus-3 Hurwitz surface, governed by the
triangle signature (2,3,7).  The live torus/Fano/Klein route already packages
those three integers exactly:

    2  = the point-line / heptad-sheet swap,
    3  = q,
    7  = Phi_6(q) = beta_0(QCD),

so the affine torus shell is

    42 = 2 * 3 * 7.

The promoted symmetry shells then lift as

    84  = 2 * 42,
    168 = 4 * 42,
    336 = 8 * 42.

This module does not claim that the affine shell *is* the full Hurwitz
triangle group.  The exact theorem is narrower: the live torus/Klein shell
already carries the full (2,3,7) signature multiplicatively, and the promoted
168/336 packets are the corresponding preserving/full symmetry lifts.
"""

from __future__ import annotations

from functools import lru_cache
import json
from pathlib import Path
from typing import Any

from w33_heawood_klein_symmetry_bridge import build_heawood_klein_symmetry_summary
from w33_mod7_fano_duality_bridge import build_mod7_fano_duality_summary
from w33_surface_physics_shell_bridge import build_surface_physics_shell_summary


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_hurwitz_237_selector_bridge_summary.json"


@lru_cache(maxsize=1)
def build_hurwitz_237_selector_summary() -> dict[str, Any]:
    mod7 = build_mod7_fano_duality_summary()
    heawood = build_heawood_klein_symmetry_summary()
    physics_shell = build_surface_physics_shell_summary()

    duality_order = 2
    q = 3
    phi6 = int(physics_shell["standard_model_gauge_dictionary"]["beta0_qcd"])
    affine_order = int(mod7["affine_group"]["full_affine_group_order"])
    single_surface_flags = int(physics_shell["surface_physics_shell_dictionary"]["single_surface_flags"])
    preserving_order = int(
        heawood["bipartition_preserving_symmetry"]["heawood_bipartition_preserving_order"]
    )
    full_order = int(heawood["full_symmetry"]["full_heawood_automorphism_order"])

    return {
        "status": "ok",
        "hurwitz_237_dictionary": {
            "triangle_signature": [duality_order, q, phi6],
            "duality_sheet_flip_order": duality_order,
            "q": q,
            "phi6": phi6,
            "affine_shell_order": affine_order,
            "single_surface_flags": single_surface_flags,
            "heawood_preserving_order": preserving_order,
            "heawood_full_order": full_order,
        },
        "exact_factorizations": {
            "affine_shell_equals_2_3_7": affine_order == duality_order * q * phi6,
            "affine_shell_is_agl_1_7": affine_order == 42,
            "decimal_c6_splits_into_c3_and_z2": mod7["decimal_duality_bridge"][
                "c6_splits_into_c3_and_z2_shadow"
            ],
            "single_surface_flags_equals_2_times_affine_shell": (
                single_surface_flags == 2 * affine_order
            ),
            "heawood_preserving_equals_4_times_affine_shell": (
                preserving_order == 4 * affine_order
            ),
            "heawood_full_equals_8_times_affine_shell": full_order == 8 * affine_order,
        },
        "bridge_verdict": (
            "The live torus/Klein route already packages the classical Hurwitz "
            "(2,3,7) selector multiplicatively. The sheet-flip/duality factor is "
            "2, the field selector is q=3, and the physics selector is "
            "Phi_6(q)=beta_0(QCD)=7, so the affine torus shell is exactly "
            "42 = 2*3*7. The promoted surface and symmetry packets are then exact "
            "successive lifts: 84 = 2*42, 168 = 4*42, and 336 = 8*42. So the "
            "Hurwitz signature is already present inside the promoted torus/Klein "
            "physics shell before any continuum rhetoric is added."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_hurwitz_237_selector_summary(), indent=2),
        encoding="utf-8",
    )
    return path


if __name__ == "__main__":
    write_summary()
