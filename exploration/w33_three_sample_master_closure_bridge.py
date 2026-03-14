"""Three-sample master closure for the promoted W33 package.

This module packages the live curved bridge into one exact equivalence:

    three successive curved refinement samples
        <-> gravity/topology coefficients
        <-> electroweak generator x = 3/13
        <-> q = 3, Phi_3 = 13, Phi_6 = 7
        <-> SRG(40,12,2,4) and spectrum (12,2,-4)
        <-> finite Dirac/Hodge package {0^82,4^320,10^48,16^30}
        <-> exceptional counts 40, 240, 8, 6, 96

So the promoted public-facing package is now an exact minimal-data closure:
once the curved tower gives the three coefficient channels, every promoted
internal and public quantity is forced, and the finite package predicts back
the same curved data.
"""

from __future__ import annotations

from functools import lru_cache
import json
from pathlib import Path

from w33_curved_continuum_extractor_bridge import build_curved_continuum_extractor_summary
from w33_curved_weinberg_lock_bridge import build_curved_weinberg_lock_bridge_summary
from w33_curved_rosetta_reconstruction_bridge import build_curved_rosetta_reconstruction_summary
from w33_curved_finite_spectral_reconstruction_bridge import (
    build_curved_finite_spectral_reconstruction_summary,
)
from w33_curved_roundtrip_closure_bridge import build_curved_roundtrip_closure_summary
from w33_curved_inverse_rosetta_bridge import build_curved_inverse_rosetta_summary


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_three_sample_master_closure_bridge_summary.json"


@lru_cache(maxsize=1)
def build_three_sample_master_closure_summary() -> dict[str, object]:
    curved = build_curved_continuum_extractor_summary()
    weinberg = build_curved_weinberg_lock_bridge_summary()
    rosetta = build_curved_rosetta_reconstruction_summary()
    finite = build_curved_finite_spectral_reconstruction_summary()
    roundtrip = build_curved_roundtrip_closure_summary()
    inverse = build_curved_inverse_rosetta_summary()

    representative_seed = curved["seeds"][0]
    three_samples = representative_seed["samples"][:3]

    return {
        "status": "ok",
        "minimal_curved_data": {
            "seed_name": representative_seed["seed_name"],
            "steps": [sample["step"] for sample in three_samples],
            "discrete_eh": three_samples[0]["discrete_eh"]["exact"],
            "continuum_eh": three_samples[0]["continuum_eh"]["exact"],
            "topological_a2": three_samples[0]["topological_a2"]["exact"],
            "same_on_all_three_steps": len(
                {
                    (
                        sample["discrete_eh"]["exact"],
                        sample["continuum_eh"]["exact"],
                        sample["topological_a2"]["exact"],
                    )
                    for sample in three_samples
                }
            )
            == 1,
        },
        "public_generator_layer": {
            "master_variable": weinberg["master_variable"]["exact"]["exact"],
            "tan_theta_c": weinberg["promoted_observables_from_curved_x"]["tan_theta_c"]["exact"]["exact"],
            "sin2_theta_12": weinberg["promoted_observables_from_curved_x"]["sin2_theta_12"]["exact"]["exact"],
            "sin2_theta_23": weinberg["promoted_observables_from_curved_x"]["sin2_theta_23"]["exact"]["exact"],
            "sin2_theta_13": weinberg["promoted_observables_from_curved_x"]["sin2_theta_13"]["exact"]["exact"],
            "omega_lambda": weinberg["promoted_observables_from_curved_x"]["omega_lambda"]["exact"]["exact"],
            "higgs_ratio_square": weinberg["promoted_observables_from_curved_x"]["higgs_ratio_square"]["exact"]["exact"],
        },
        "rosetta_layer": {
            "q": rosetta["reconstructed_cyclotomic_data"]["q"],
            "phi3": rosetta["reconstructed_cyclotomic_data"]["phi3"]["exact"],
            "phi6": rosetta["reconstructed_cyclotomic_data"]["phi6"]["exact"],
            "srg_data": rosetta["reconstructed_srg_data"],
            "spectral_data": rosetta["reconstructed_spectral_data"],
        },
        "finite_spectral_layer": {
            "betti_numbers": finite["reconstructed_hodge_data"]["betti_numbers"],
            "boundary_ranks": finite["reconstructed_hodge_data"]["boundary_ranks"],
            "df2_spectrum": finite["reconstructed_finite_dirac_package"]["df2_spectrum"],
            "a0_f": finite["reconstructed_finite_dirac_package"]["seeley_dewitt_moments"]["a0_f"],
            "a2_f": finite["reconstructed_finite_dirac_package"]["seeley_dewitt_moments"]["a2_f"],
            "a4_f": finite["reconstructed_finite_dirac_package"]["seeley_dewitt_moments"]["a4_f"],
        },
        "exceptional_layer": inverse["reconstructed_internal_data"],
        "closure_checks": {
            "curved_to_generator": all(sample["matches_master_variable"] for sample in weinberg["curved_samples"]),
            "generator_to_rosetta": rosetta["matches_live_rosetta_data"]["all_promoted_observables_match"],
            "rosetta_to_finite": finite["matches_live_internal_package"]["moments_match"]
            and finite["matches_live_internal_package"]["df2_spectrum_match"],
            "finite_back_to_curved": roundtrip["all_samples_close_exactly"],
            "curved_to_exceptional": inverse["all_samples_constant"],
            "full_master_closure": (
                all(sample["matches_master_variable"] for sample in weinberg["curved_samples"])
                and rosetta["matches_live_rosetta_data"]["all_promoted_observables_match"]
                and finite["matches_live_internal_package"]["moments_match"]
                and finite["matches_live_internal_package"]["df2_spectrum_match"]
                and roundtrip["all_samples_close_exactly"]
                and inverse["all_samples_constant"]
            ),
        },
        "bridge_verdict": (
            "The promoted W33 package is now an exact three-sample closure. "
            "Three successive curved refinement samples fix the coefficient "
            "triple (12480, 320, 2240), which fixes x = 3/13, which fixes "
            "q = 3, Phi_3 = 13, Phi_6 = 7, SRG(40,12,2,4), the spectrum "
            "(12,2,-4), the finite package {0^82,4^320,10^48,16^30} with "
            "moments (480,2240,17600), and the promoted exceptional counts "
            "(40,240,8,6,96). The finite package then predicts back the same "
            "curved coefficients and x = 3/13 exactly."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(json.dumps(build_three_sample_master_closure_summary(), indent=2), encoding="utf-8")
    return path


if __name__ == "__main__":
    write_summary()
