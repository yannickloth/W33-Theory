def test_cclviii_monster_ap_center_smoke():
    k = 12
    carrier = 59
    outer = [47, 71]
    assert outer == [carrier - k, carrier + k]
    assert sum(outer) == 118 == 2 * carrier
    assert outer[0] * carrier * outer[1] == 196883
