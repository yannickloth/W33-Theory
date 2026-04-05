"""
Phase CDXLIX — cyclotomic PMNS closure.

The PMNS matrix from Φ₃=13 and Φ₆=7 is unitary with all mixing observables
within 0.5σ and the testable relation θ₂₃ = θ_W + θ₁₂ holding exactly.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPLORATION = ROOT / "exploration"
if str(EXPLORATION) not in sys.path:
    sys.path.insert(0, str(EXPLORATION))

from w33_cyclotomic_pmns_closure_bridge import (
    build_cyclotomic_pmns_closure_summary,
)


def test_phase_cdxlix_pmns_fully_closed() -> None:
    theorem = build_cyclotomic_pmns_closure_summary()[
        "cyclotomic_pmns_closure_theorem"
    ]
    assert theorem[
        "therefore_the_cyclotomic_pmns_matrix_is_fully_closed"
    ] is True


def test_phase_cdxlix_unitarity() -> None:
    theorem = build_cyclotomic_pmns_closure_summary()[
        "cyclotomic_pmns_closure_theorem"
    ]
    assert theorem["the_pmns_matrix_is_unitary_to_machine_precision"] is True
    assert theorem["the_determinant_has_magnitude_one"] is True


def test_phase_cdxlix_testable_relation() -> None:
    theorem = build_cyclotomic_pmns_closure_summary()[
        "cyclotomic_pmns_closure_theorem"
    ]
    assert theorem[
        "the_testable_relation_theta23_equals_thetaW_plus_theta12_holds_exactly"
    ] is True


def test_phase_cdxlix_all_within_half_sigma() -> None:
    theorem = build_cyclotomic_pmns_closure_summary()[
        "cyclotomic_pmns_closure_theorem"
    ]
    assert theorem[
        "all_four_mixing_observables_agree_within_half_sigma"
    ] is True
