from fractions import Fraction


def test_bivector_curvature_smoke():
    q, k, lam, mu = 3, 12, 2, 4
    Phi4 = 10
    assert Fraction(k, lam) == Fraction(mu * (mu - 1), 2) == 6
    assert lam * Phi4 == Fraction(mu**2 * (mu**2 - 1), 12) == 20
    assert Fraction(k, lam) * (lam * Phi4) == 120
