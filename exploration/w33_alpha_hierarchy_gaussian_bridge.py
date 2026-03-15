"""Exact Gaussian-shell lock behind the alpha/charm hierarchy bridge.

The promoted fermion hierarchy already shows

    alpha_tree^{-1} = 137,
    m_c / m_t = 1 / 136,
    136 = lambda mu (mu^2 + 1).

This module packages the stronger structural statement suggested by that lock:

    137 = |(k-1) + i mu|^2 = |11 + 4i|^2,
    136 = (lambda mu) |mu + i|^2 = 8 * 17,
    137 = 136 + 1.

So the tree electromagnetic count, the first up-sector suppressor, and the
rank-1 vacuum selector are one exact nested Gaussian shell. The missing unit is
not arbitrary; it is the same trivial selector line that already appears in the
vacuum-unity and transport-selector bridges.
"""

from __future__ import annotations

from fractions import Fraction
from functools import lru_cache
import json
from pathlib import Path
from typing import Any

from w33_q3_fermion_hierarchy_bridge import build_q3_fermion_hierarchy_summary
from w33_vacuum_unity_bridge import build_vacuum_unity_summary


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_alpha_hierarchy_gaussian_bridge_summary.json"

Q = 3
K = 12
LAMBDA = 2
MU = 4

OUTER_GAUSSIAN_VECTOR = (K - 1, MU)
INNER_GAUSSIAN_VECTOR = (MU, 1)
OUTER_GAUSSIAN_NORM = Fraction(OUTER_GAUSSIAN_VECTOR[0] ** 2 + OUTER_GAUSSIAN_VECTOR[1] ** 2, 1)
INNER_GAUSSIAN_NORM = Fraction(INNER_GAUSSIAN_VECTOR[0] ** 2 + INNER_GAUSSIAN_VECTOR[1] ** 2, 1)
TRANSPORT_PREFATOR = Fraction(LAMBDA * MU, 1)
UP_SECTOR_SUPPRESSOR = TRANSPORT_PREFATOR * INNER_GAUSSIAN_NORM


def _fraction_dict(value: Fraction) -> dict[str, Any]:
    exact = str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"
    return {"exact": exact, "float": float(value)}


@lru_cache(maxsize=1)
def build_alpha_hierarchy_gaussian_summary() -> dict[str, Any]:
    hierarchy = build_q3_fermion_hierarchy_summary()
    vacuum = build_vacuum_unity_summary()

    alpha_tree = Fraction(
        hierarchy["electromagnetic_to_flavour_lock"]["alpha_tree_inverse"]["exact"]
    )
    alpha_full = Fraction(hierarchy["electromagnetic_to_flavour_lock"]["alpha_inverse_exact"]["exact"])
    up_sector = Fraction(hierarchy["electromagnetic_to_flavour_lock"]["up_sector_suppressor"]["exact"])
    vertex_correction = Fraction(
        hierarchy["electromagnetic_to_flavour_lock"]["vertex_correction_term"]["exact"]
    )
    selector_line_dimension = Fraction(vacuum["selector_cross_bridge"]["selector_line_dimension"], 1)

    return {
        "status": "ok",
        "nested_gaussian_shells": {
            "outer_alpha_formula": "|(k-1) + i mu|^2",
            "outer_alpha_vector": list(OUTER_GAUSSIAN_VECTOR),
            "outer_alpha_norm": _fraction_dict(OUTER_GAUSSIAN_NORM),
            "inner_hierarchy_formula": "|mu + i|^2",
            "inner_hierarchy_vector": list(INNER_GAUSSIAN_VECTOR),
            "inner_hierarchy_norm": _fraction_dict(INNER_GAUSSIAN_NORM),
            "transport_prefactor_formula": "lambda mu = q^2 - 1",
            "transport_prefactor": _fraction_dict(TRANSPORT_PREFATOR),
            "up_sector_formula": "(lambda mu) |mu + i|^2",
            "up_sector_suppressor": _fraction_dict(UP_SECTOR_SUPPRESSOR),
        },
        "selector_split": {
            "alpha_tree_inverse": _fraction_dict(alpha_tree),
            "selector_line_dimension": _fraction_dict(selector_line_dimension),
            "alpha_tree_equals_up_sector_plus_selector": alpha_tree == up_sector + selector_line_dimension,
            "alpha_tree_minus_one_equals_up_sector": alpha_tree - selector_line_dimension == up_sector,
            "alpha_full_inverse": _fraction_dict(alpha_full),
            "vertex_correction_term": _fraction_dict(vertex_correction),
            "alpha_full_equals_nested_shell_plus_vertex_correction": alpha_full == up_sector + selector_line_dimension + vertex_correction,
        },
        "hierarchy_lock": {
            "mc_over_mt": hierarchy["dimensionless_hierarchy_ratios"]["mc_over_mt"],
            "mu_over_mc": hierarchy["dimensionless_hierarchy_ratios"]["mu_over_mc"],
            "charm_ratio_is_inverse_selector_reduced_tree_alpha": Fraction(
                hierarchy["dimensionless_hierarchy_ratios"]["mc_over_mt"]["exact"]
            )
            == Fraction(1, alpha_tree - selector_line_dimension),
            "second_up_step_is_extra_mu_factor": Fraction(
                hierarchy["dimensionless_hierarchy_ratios"]["mu_over_mc"]["exact"]
            )
            == Fraction(1, MU * up_sector),
        },
        "gaussian_selector_theorem": {
            "alpha_tree_is_outer_gaussian_norm": alpha_tree == OUTER_GAUSSIAN_NORM,
            "up_sector_is_transport_times_inner_gaussian_norm": up_sector == TRANSPORT_PREFATOR * INNER_GAUSSIAN_NORM,
            "vacuum_selector_supplies_the_missing_one": alpha_tree == up_sector + selector_line_dimension,
            "full_alpha_is_selector_split_plus_vertex_correction": alpha_full == up_sector + selector_line_dimension + vertex_correction,
        },
        "bridge_verdict": (
            "The clean alpha/charm lock is now a nested Gaussian-shell theorem. "
            "The tree electromagnetic count is the outer norm |11+4i|^2 = 137, "
            "the first up-sector suppressor is the transport-dressed inner norm "
            "8|4+i|^2 = 136, and the missing unit is exactly the rank-1 vacuum "
            "selector already forced elsewhere in the theory. So the charm/top "
            "ratio is not merely close to alpha_tree^{-1}-1; it is the inverse "
            "of the selector-reduced tree electromagnetic shell."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_alpha_hierarchy_gaussian_summary(), indent=2),
        encoding="utf-8",
    )
    return path


if __name__ == "__main__":
    write_summary()
