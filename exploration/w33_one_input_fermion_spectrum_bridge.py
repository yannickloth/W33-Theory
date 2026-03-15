"""One-input fermion spectrum closure from the promoted W33 package.

This bridge packages the strongest honest statement currently available on the
fermion-mass side.

The graph-fixed electroweak scale already determines the quark ladder:

    m_t = v_EW / sqrt(2),
    m_c = m_t / 136,
    m_u = m_t / 73984,
    m_b = m_c * 13/4,
    m_s = m_b / 44,
    m_d = m_s / 20.

The charged-lepton ladder is then reduced to one residual seed m_e:

    m_mu = 208 m_e,
    Koide Q = 2/3 fixes m_tau / m_e algebraically.

The promoted neutrino side is reduced to the same electron seed through the
exceptional F4 coefficient

    m_nu / m_e^2 = 26 / 123

once the Dirac neutrino seed is identified with the electron channel.

So the public fermion statement is no longer "many unrelated masses". It is:
the graph fixes the full dimensionless fermion ladder, and one residual
electron seed carries the remaining dimensionful freedom on the lepton side.
"""

from __future__ import annotations

from fractions import Fraction
from functools import lru_cache
import json
from pathlib import Path
from typing import Any

import sympy as sp

from w33_f4_neutrino_scale_bridge import build_f4_neutrino_scale_summary
from w33_q3_fermion_hierarchy_bridge import build_q3_fermion_hierarchy_summary


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_one_input_fermion_spectrum_bridge_summary.json"

V_EW = 246


def _fraction_dict(value: Fraction) -> dict[str, Any]:
    exact = str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"
    return {"exact": exact, "float": float(value)}


def _sympy_dict(value: sp.Expr) -> dict[str, Any]:
    return {"exact": str(sp.simplify(value)), "float": float(sp.N(value, 30))}


@lru_cache(maxsize=1)
def build_one_input_fermion_spectrum_summary() -> dict[str, Any]:
    hierarchy = build_q3_fermion_hierarchy_summary()
    neutrino = build_f4_neutrino_scale_summary()

    ratios = hierarchy["dimensionless_hierarchy_ratios"]
    mc_over_mt = Fraction(ratios["mc_over_mt"]["exact"])
    mu_over_mc = Fraction(ratios["mu_over_mc"]["exact"])
    mb_over_mc = Fraction(ratios["mb_over_mc"]["exact"])
    ms_over_mb = Fraction(ratios["ms_over_mb"]["exact"])
    md_over_ms = Fraction(ratios["md_over_ms"]["exact"])
    mmu_over_me = Fraction(ratios["mmu_over_me"]["exact"])

    mt_over_vew = sp.sqrt(2) / 2
    mc_over_vew = sp.Rational(mc_over_mt.numerator, mc_over_mt.denominator) * mt_over_vew
    mu_over_vew = sp.Rational((mc_over_mt * mu_over_mc).numerator, (mc_over_mt * mu_over_mc).denominator) * mt_over_vew
    mb_over_vew = sp.Rational((mc_over_mt * mb_over_mc).numerator, (mc_over_mt * mb_over_mc).denominator) * mt_over_vew
    ms_over_vew = sp.Rational((mc_over_mt * mb_over_mc * ms_over_mb).numerator, (mc_over_mt * mb_over_mc * ms_over_mb).denominator) * mt_over_vew
    md_over_vew = sp.Rational((mc_over_mt * mb_over_mc * ms_over_mb * md_over_ms).numerator, (mc_over_mt * mb_over_mc * ms_over_mb * md_over_ms).denominator) * mt_over_vew

    tau_sqrt_over_e = sp.simplify(2 + 8 * sp.sqrt(13) + sp.sqrt(627 + 48 * sp.sqrt(13)))
    tau_over_e = sp.simplify(tau_sqrt_over_e**2)
    tau_over_e_minpoly = sp.minpoly(tau_over_e, sp.symbols("y"))

    mnu_over_me_sq = Fraction(
        neutrino["exceptional_scale_dictionary"]["mnu_over_me_squared_if_dirac_seed_is_electron"]["exact"]
    )

    return {
        "status": "ok",
        "graph_fixed_seed": {
            "vev_ew_gev": V_EW,
            "mt_over_vew": _sympy_dict(mt_over_vew),
            "mc_over_vew": _sympy_dict(mc_over_vew),
            "mu_over_vew": _sympy_dict(mu_over_vew),
            "mb_over_vew": _sympy_dict(mb_over_vew),
            "ms_over_vew": _sympy_dict(ms_over_vew),
            "md_over_vew": _sympy_dict(md_over_vew),
        },
        "dimensionless_fermion_ladder": {
            "mc_over_mt": _fraction_dict(mc_over_mt),
            "mu_over_mc": _fraction_dict(mu_over_mc),
            "mu_over_mt": _fraction_dict(mc_over_mt * mu_over_mc),
            "mb_over_mc": _fraction_dict(mb_over_mc),
            "ms_over_mb": _fraction_dict(ms_over_mb),
            "md_over_ms": _fraction_dict(md_over_ms),
            "mmu_over_me": _fraction_dict(mmu_over_me),
        },
        "charged_lepton_one_seed_closure": {
            "residual_seed": "m_e",
            "mmu_over_me": _fraction_dict(mmu_over_me),
            "koide_q": _fraction_dict(Fraction(2, 3)),
            "sqrt_mtau_over_me": _sympy_dict(tau_sqrt_over_e),
            "mtau_over_me": _sympy_dict(tau_over_e),
            "mtau_over_me_minpoly": str(sp.expand(tau_over_e_minpoly)),
        },
        "exceptional_neutrino_closure": {
            "residual_seed": "m_e",
            "mnu_over_me_squared_if_dirac_seed_is_electron": _fraction_dict(mnu_over_me_sq),
            "f4_dimension": neutrino["exceptional_scale_dictionary"]["f4_dimension"],
            "mr_over_vew": neutrino["exceptional_scale_dictionary"]["mr_over_vew"],
        },
        "fermion_spectrum_theorem": {
            "quark_ladder_fixed_by_graph_scale_and_q3_ratios": True,
            "charged_lepton_ladder_reduced_to_one_electron_seed": True,
            "koide_packet_closes_tau_over_e_algebraically": True,
            "neutrino_scale_reduced_to_same_electron_seed_plus_f4_coefficient": True,
            "remaining_fermion_frontier_is_one_seed_plus_final_internal_spectral_packet": True,
        },
        "bridge_verdict": (
            "The fermion-mass side now has a one-input closure statement. The "
            "graph-fixed electroweak scale determines the full quark ladder, "
            "the charged-lepton side collapses to one residual electron seed "
            "with exact muon shell 208 and an algebraic Koide tau packet, and "
            "the promoted neutrino side reduces to that same seed through the "
            "exceptional F4 coefficient 26/123. So the remaining fermion "
            "frontier is no longer a free family of masses, but one residual "
            "electron seed plus the final slot-specific Yukawa spectral packet."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_one_input_fermion_spectrum_summary(), indent=2),
        encoding="utf-8",
    )
    return path


if __name__ == "__main__":
    write_summary()
