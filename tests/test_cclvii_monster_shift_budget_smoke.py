def test_cclvii_monster_shift_budget_smoke():
    center = 64
    shifts = [17, 5, -7]
    factors = [center - 17, center - 5, center + 7]
    assert factors == [47, 59, 71]
    assert shifts[0] + shifts[1] + shifts[2] == 15
    assert sum(factors) == 3 * center - 15 == 177
