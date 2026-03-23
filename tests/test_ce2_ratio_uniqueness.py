import math


def test_ce2_ratio_is_minimal_eisenstein_ratio():
    # The CE2 ratio R is derived from the W33 graph parameters as
    #   R = sqrt((v+1)^2 - (v+1)T + T^2) / (v+1+T)
    # with (v,T) = (40,160).
    v, T = 40, 160
    R = math.sqrt((v + 1)**2 - (v + 1) * T + T**2) / (v + 1 + T)
    assert abs(R - (math.sqrt(20721) / 201.0)) < 1e-15

    # In the Eisenstein norm picture, this means we want minimal integers (a,b)
    # with ratio |a + b*omega|/(a+b) = R. The claim is that (a,b) = (v+1, T)
    # is the minimal primitive solution.
    a0, b0 = v + 1, T
    assert math.gcd(a0, b0) == 1

    R2 = R * R
    solutions = []
    for a in range(1, 500):
        for b in range(1, 500):
            lhs = a * a - a * b + b * b
            rhs = R2 * (a + b) * (a + b)
            if abs(lhs - rhs) < 1e-9:
                solutions.append((a, b))

    # Solutions should include the base pair (v+1,T) and its swap.
    assert (a0, b0) in solutions
    assert (b0, a0) in solutions

    # Confirm (a0,b0) is the unique primitive solution in range.
    primitive = [(a, b) for (a, b) in solutions if math.gcd(a, b) == 1]
    assert (a0, b0) in primitive
    assert all((a, b) == (a0, b0) or (a, b) == (b0, a0) for (a, b) in primitive)
