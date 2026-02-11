from tools.vogel_rational_cubic_search import find_rational_m_for_dim
from tools.vogel_rational_cubic_sweep import hit_dims, sweep_dims


def test_sweep_small_range_and_s12_dims_no_hits():
    # run a small sweep and ensure it returns a mapping
    results = sweep_dims(200, 1000, step=1, denom_cap=500)
    assert isinstance(results, dict)
    assert hit_dims(results) == [248, 287, 336, 484, 603, 782]
    # check the s12 dims still have no rational hits up to a larger denom cap
    r486 = find_rational_m_for_dim(486, denom_cap=1000)
    r242 = find_rational_m_for_dim(242, denom_cap=1000)
    r728 = find_rational_m_for_dim(728, denom_cap=1000)
    assert r486["hits"] == []
    assert r242["hits"] == []
    assert r728["hits"] == []
