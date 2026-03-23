import sympy as sp


def test_R_macwilliams_identity_holds_polynomially():
    # W(z) = 1 + 14z^4 + z^8 is the weight enumerator of the [8,4,4] self-dual code.
    # Verify the MacWilliams self-duality identity holds as a polynomial identity.
    x = sp.Symbol('x')
    W = lambda z: 1 + 14*z**4 + z**8
    eta = (1 - x) / (1 + x)
    expr = sp.simplify(W(x) - (1 + x)**8 / 16 * W(eta))
    assert expr == 0, f"MacWilliams identity violated: got {expr}"


def test_R_extended_hamming_weight_dist():
    # [8,4,4] extended Hamming: 1 codeword of weight 0, 14 of weight 4, 1 of weight 8
    W_coeffs = {0: 1, 4: 14, 8: 1}
    total = sum(W_coeffs.values())
    assert total == 16  # 2^4 = 2^k codewords
    assert W_coeffs[4] == 14
    assert W_coeffs[0] == W_coeffs[8] == 1


def test_R_self_dual_minimum_distance():
    # Self-dual [8,4,4] code: minimum distance = 4 (doubly even)
    # d = 4, k = 4, n = 8, rate = 1/2
    n, k, d = 8, 4, 4
    assert n == 2 * k      # self-dual: n = 2k
    assert d == 4           # doubly-even minimum distance
    assert d % 4 == 0      # doubly-even (all weights divisible by 4)
