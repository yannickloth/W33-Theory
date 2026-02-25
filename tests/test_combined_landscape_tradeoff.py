from __future__ import annotations


def test_combined_tradeoff_threshold() -> None:
    """Empirical trade-off: no random sample simultaneously has very low CKM and mass errors.

    This regression test codifies the Pareto frontier observed during development.
    If a future modification ever finds a point with ck_err < 0.3 *and* mass_err < 40,
    the test will fail and signal a dramatic change in the active-subspace landscape.
    """
    from scripts.combined_ckm_mass_landscape import (
        build_yukawa_tensor,
        analyze_active_subspace,
        random_active_points,
    )

    T = build_yukawa_tensor()
    rank, Vh = analyze_active_subspace(T)
    pts = random_active_points(T, Vh, rank, 2000, weight_mass=1.0)
    for pt in pts:
        ck = float(pt["ck_err"])
        mass = float(pt["mass_err"])
        assert not (ck < 0.3 and mass < 40), f"ck={ck}, mass={mass} violates tradeoff"
