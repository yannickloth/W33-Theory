import json

from tools.vogel_rational_cubic_search import find_rational_m_for_dim


def test_vogel_rational_search_no_hits_for_486_242():
    r486 = find_rational_m_for_dim(486, denom_cap=500)
    r242 = find_rational_m_for_dim(242, denom_cap=500)
    assert r486["hits"] == []
    assert r242["hits"] == []
