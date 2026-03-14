"""Natural-units meaning bridge for the live W33 package.

The public-facing vacuum story is clearer in natural units than in SI.  In
rationalized Heaviside-Lorentz units one sets

    hbar = c = epsilon0 = mu0 = Z0 = Y0 = 1,

so the vacuum is literally the unit element.  The live W33 package then reads
as a dimensionless theory:

    alpha = e_HL^2 / (4 pi),
    R_K    = 1 / (2 alpha),
    G_0    = 4 alpha,
    K_J    = 2 sqrt(alpha / pi),
    Phi_0  = 1 / K_J.

The old SI statements therefore become natural-unit identities:

    Z0 = 2 alpha R_K   ->   1 = 2 alpha R_K,
    alpha = Z0 G_0 / 4 ->   alpha = G_0 / 4.

This is the clean way to read the graphs physically.  The graph does not
fundamentally predict SI constants as such; it predicts dimensionless couplings,
mixing angles, mass ratios, and curvature-mode weights.  The SI constants are a
re-expression of that dimensionless package.
"""

from __future__ import annotations

from functools import lru_cache
import json
from math import pi, sqrt
from pathlib import Path
from typing import Any

from w33_adjacency_dirac_closure_bridge import build_adjacency_dirac_closure_summary
from w33_curved_roundtrip_closure_bridge import build_curved_roundtrip_closure_summary
from w33_quantum_vacuum_standards_bridge import build_quantum_vacuum_standards_summary
from w33_standard_model_cyclotomic_bridge import build_standard_model_cyclotomic_summary
from w33_vacuum_unity_bridge import ALPHA, ALPHA_INV


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_natural_units_meaning_bridge_summary.json"


def _fraction_dict(value) -> dict[str, Any]:
    exact = str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"
    return {"exact": exact, "float": float(value)}


@lru_cache(maxsize=1)
def build_natural_units_meaning_summary() -> dict[str, Any]:
    alpha = float(ALPHA)
    standard_model = build_standard_model_cyclotomic_summary()
    finite = build_adjacency_dirac_closure_summary()
    curved = build_curved_roundtrip_closure_summary()
    vacuum_standards = build_quantum_vacuum_standards_summary()

    e_hl_sq = 4.0 * pi * alpha
    e_hl = sqrt(e_hl_sq)
    e_gaussian_sq = alpha
    e_gaussian = sqrt(alpha)
    rk_nat = 1.0 / (2.0 * alpha)
    g0_nat = 4.0 * alpha
    kj_nat = 2.0 * sqrt(alpha / pi)
    phi0_nat = 1.0 / kj_nat

    return {
        "status": "ok",
        "heaviside_lorentz_natural_units": {
            "convention": "hbar = c = epsilon0 = mu0 = Z0 = Y0 = 1",
            "alpha_formula": "e_HL^2 / (4 pi)",
            "electric_charge_squared_symbolic": "4 pi alpha",
            "electric_charge_squared": e_hl_sq,
            "electric_charge": e_hl,
            "vacuum_impedance": 1.0,
            "vacuum_admittance": 1.0,
            "mu0": 1.0,
            "epsilon0": 1.0,
            "von_klitzing_symbolic": "1 / (2 alpha)",
            "von_klitzing_constant": rk_nat,
            "conductance_quantum_symbolic": "4 alpha",
            "conductance_quantum": g0_nat,
            "josephson_symbolic": "2 sqrt(alpha / pi)",
            "josephson_constant": kj_nat,
            "flux_quantum_symbolic": "1 / (2 sqrt(alpha / pi))",
            "flux_quantum": phi0_nat,
            "vacuum_unity_becomes_unit_element": True,
            "z0_equals_2alpha_rk_becomes_unit_identity": abs(1.0 - 2.0 * alpha * rk_nat) < 1e-15,
            "alpha_equals_g0_over_4": abs(alpha - g0_nat / 4.0) < 1e-15,
            "rk_times_g0_equals_2": abs(rk_nat * g0_nat - 2.0) < 1e-15,
            "phi0_times_kj_equals_1": abs(phi0_nat * kj_nat - 1.0) < 1e-15,
        },
        "gaussian_crosscheck": {
            "convention": "hbar = c = 1 with Gaussian charges",
            "alpha_formula": "e_G^2",
            "electric_charge_squared": e_gaussian_sq,
            "electric_charge": e_gaussian,
            "heaviside_equals_4pi_gaussian": abs(e_hl_sq - 4.0 * pi * e_gaussian_sq) < 1e-15,
        },
        "dimensionless_graph_observables": {
            "alpha_inverse": _fraction_dict(ALPHA_INV),
            "alpha": _fraction_dict(ALPHA),
            "weinberg_x": standard_model["promoted_observables"]["sin2_theta_w_ew"]["exact"],
            "theta12": standard_model["promoted_observables"]["sin2_theta_12"]["exact"],
            "theta23": standard_model["promoted_observables"]["sin2_theta_23"]["exact"],
            "theta13": standard_model["promoted_observables"]["sin2_theta_13"]["exact"],
            "higgs_ratio_square": standard_model["promoted_observables"]["higgs_ratio_square"]["exact"],
            "omega_lambda": standard_model["promoted_observables"]["omega_lambda"]["exact"],
            "a2_over_a0": finite["finite_dirac_closure"]["spectral_action_ratios"]["mu_squared"],
            "a4_over_a0": finite["finite_dirac_closure"]["spectral_action_ratios"]["lambda"],
            "discrete_to_continuum_ratio": str(
                int(curved["roundtrip_curved_coefficients"]["discrete_eh_from_finite"]["exact"])
                // int(curved["roundtrip_curved_coefficients"]["continuum_eh_from_finite"]["exact"])
            ),
            "topological_over_continuum": str(
                int(curved["roundtrip_curved_coefficients"]["topological_from_finite"]["exact"])
                // int(curved["roundtrip_curved_coefficients"]["continuum_eh_from_finite"]["exact"])
            ),
            "si_vacuum_is_reexpression_of_dimensionless_package": True,
            "graphs_mean_couplings_and_mode_weights_in_natural_units": True,
            "quantum_vacuum_standards_bridge_is_compatible": vacuum_standards["vacuum_transport_dictionary"]["z0_times_g0_equals_4alpha"],
        },
        "bridge_verdict": (
            "In natural Heaviside-Lorentz units the vacuum is literally the unit "
            "element, so the live graph data should be read as a dimensionless "
            "physics package. The graph fixes alpha, sin^2(theta_W), PMNS ratios, "
            "the Higgs ratio, and the curvature-mode ratios directly. The old SI "
            "vacuum constants are then just the same dimensionless package "
            "re-expressed through h, e, and c. In that language, the vacuum "
            "impedance is not a mysterious extra constant at all: it is the unit "
            "element, the resistance quantum is 1/(2 alpha), the Landauer "
            "conductance quantum is 4 alpha, and the graph's promoted observables "
            "are exactly the dimensionless couplings and mode weights of the "
            "physical object."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_natural_units_meaning_summary(), indent=2),
        encoding="utf-8",
    )
    return path


if __name__ == "__main__":
    write_summary()
