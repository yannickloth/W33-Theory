import math

import numpy as np

from scripts.derive_cp_from_J import delta_from_jarlskog, jarlskog_from_angles


def test_roundtrip_example_angles():
    # angles used in W33 CKM example (degrees → radians)
    t12 = math.radians(12.15)
    t13 = math.radians(0.119)
    t23 = math.radians(2.38)
    delta_expected = math.radians(68.0)

    J = jarlskog_from_angles(t12, t13, t23, delta_expected)
    dp, da = delta_from_jarlskog(J, t12, t13, t23)

    # one of the returned solutions should match expected (within numerical tol)
    assert np.isclose(dp, delta_expected, rtol=1e-8, atol=1e-10) or np.isclose(
        da, delta_expected, rtol=1e-8, atol=1e-10
    )


def test_zero_denominator_raises():
    # theta13 = 0 makes denominator zero
    t12 = math.radians(12.0)
    t13 = 0.0
    t23 = math.radians(2.0)
    with __import__("pytest").raises(ValueError):
        delta_from_jarlskog(1e-6, t12, t13, t23)


def test_out_of_range_raises_and_tol_behavior():
    t12 = math.radians(12.15)
    t13 = math.radians(0.119)
    t23 = math.radians(2.38)
    # build denominator by using delta = pi/2 (max sin)
    denom = (
        math.sin(t12)
        * math.cos(t12)
        * math.sin(t23)
        * math.cos(t23)
        * math.sin(t13)
        * (math.cos(t13) ** 2)
    )

    # J slightly above allowable range -> should raise
    J_bad = denom * (1.0 + 1e-8)
    with __import__("pytest").raises(ValueError):
        delta_from_jarlskog(J_bad, t12, t13, t23)

    # J barely outside due to tiny numerical noise should be accepted (clamped)
    J_ok = denom * (1.0 + 1e-13)
    dp, da = delta_from_jarlskog(J_ok, t12, t13, t23)
    # dp should be approximately pi/2 (principal value)
    assert np.isclose(dp, math.pi / 2, atol=1e-8)
