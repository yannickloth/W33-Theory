"""Unit tests for the cross-ratio utilities."""

import pytest
import sympy as sp

from scripts.w33_cross_ratio import cross_ratio, mobius_transform, random_mobius, apply_mobius_to_list


def test_real_invariance():
    # choose four distinct real points and compare with tolerance
    pts = [0.1, 2.5, -1.0, 3.3]
    cr = cross_ratio(*pts)
    # apply several random mobius transforms and check the cross ratio remains
    for _ in range(5):
        a, b, c, d = random_mobius()
        transformed = apply_mobius_to_list(pts, a, b, c, d)
        diff = float(cross_ratio(*transformed) - cr)
        assert abs(diff) < 1e-9


def test_symbolic_invariance():
    # symbolic variables
    z1, z2, z3, z4 = sp.symbols('z1 z2 z3 z4')
    cr = cross_ratio(z1, z2, z3, z4)
    # compose a symbolic mobius transformation
    a, b, c, d = sp.symbols('a b c d')
    transformed = [mobius_transform(z, a, b, c, d) for z in (z1, z2, z3, z4)]
    cr2 = cross_ratio(*transformed)
    expr = sp.simplify(cr2 - cr)
    # should cancel to 0 assuming ad-bc != 0
    assert expr == 0


def test_finite_field():
    # compute cross ratio in GF(7)
    cr1 = cross_ratio(1, 2, 3, 4, field=7)
    # try invariance under mobius using mod arithmetic; retry until valid
    for _ in range(10):
        a, b, c, d = random_mobius(field=7)
        try:
            transformed = apply_mobius_to_list([1, 2, 3, 4], a, b, c, d, field=7)
        except ZeroDivisionError:
            # singular map on one of the points; try again
            continue
        try:
            cr2 = cross_ratio(*transformed, field=7)
        except ZeroDivisionError:
            continue
        assert cr1 == cr2
        break
    else:
        pytest.skip("couldn't find nondegenerate mobius transform modulo 7")


def test_field_errors():
    with pytest.raises(ValueError):
        cross_ratio(1,2,3,4, field=8)  # non-prime
    with pytest.raises(ValueError):
        random_mobius(field=8)  # non-prime

    with pytest.raises(ZeroDivisionError):
        # choose points that make denom zero mod 5 (a=d case)
        cross_ratio(1,2,3,1, field=5)
