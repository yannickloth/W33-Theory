from __future__ import annotations

from collections import defaultdict

from scripts.ce2_omega_correlation import compute_omega_distribution, compute_sign_vs_omega_stats


def test_ce2_omega_distribution_counts() -> None:
    # the simple-family CE2 sign map should see 576 omega-zero entries
    # and 144 each of the nonzero values (empirical observation).
    hist = compute_omega_distribution()
    assert hist == {0: 576, 1: 144, 2: 144}


def test_ce2_sign_vs_omega_bias() -> None:
    # nonzero omegas are not constant but have a reproducible bias
    stats = compute_sign_vs_omega_stats()
    # w=1: 88 negative signs, 56 positive signs
    assert stats[1][-1] == 88
    assert stats[1][1] == 56
    # w=2: 56 positive signs, 88 negative signs
    assert stats[2][1] == 56
    assert stats[2][-1] == 88
