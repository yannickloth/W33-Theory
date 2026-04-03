"""
Phase CCCXCVII — Current K3 tail exactness failure certificate.

CCCXCVI gave a necessary-and-sufficient exactness test on the fixed K3 carrier
package. This phase proves the present refined K3 object fails that test for
one precise reason only: it satisfies the tail syzygies only trivially at the
zero point and never realizes the nonzero transport arithmetic pair `(12,217)`.
"""

from __future__ import annotations

from exploration.w33_current_k3_tail_exactness_failure_bridge import (
    build_current_k3_tail_exactness_failure_summary,
)


def test_phase_cccxcvii_current_k3_fails_exact_tail_realization_test() -> None:
    theorem = build_current_k3_tail_exactness_failure_summary()[
        "current_k3_tail_exactness_failure_theorem"
    ]
    assert theorem[
        "therefore_the_current_refined_k3_object_fails_the_exact_tail_realization_test_on_the_fixed_carrier_package"
    ] is True


def test_phase_cccxcvii_new_k3_data_is_required_on_same_carrier_package() -> None:
    theorem = build_current_k3_tail_exactness_failure_summary()[
        "current_k3_tail_exactness_failure_theorem"
    ]
    assert theorem[
        "therefore_any_exact_k3_tail_realization_requires_genuine_new_k3_side_data_on_the_same_fixed_carrier_package"
    ] is True
