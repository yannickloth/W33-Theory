from scripts.ce2_growth_rule import (
    canonical_tag,
    canonical_pattern,
    next_state,
    _PATTERNS,
    _TAGS,
)


def test_growth_rule_advances_pattern():
    # obtain tables from the underlying kernel-action module
    from scripts.ce2_kernel_action import build_kernel_tables
    _, _, action1, _ = build_kernel_tables()
    # find a valid tag/pattern pair
    tag = None
    pattern = None
    for ti, row in enumerate(action1):
        for pi, val in enumerate(row):
            if val >= 0:
                tag = ti
                pattern = pi
                break
        if tag is not None:
            break
    assert tag is not None and pattern is not None

    newtag, newpat = next_state(tag, pattern, swap_id=1)
    assert isinstance(newtag, int) and isinstance(newpat, int)
    assert 0 <= newpat < len(_PATTERNS)


def test_invalid_swap_id_raises():
    tag = canonical_tag(1, 0, 0)
    pat = canonical_pattern((1, 1, 1))
    try:
        next_state(tag, pat, swap_id=3)
        assert False, "expected ValueError"
    except ValueError:
        pass


def test_pattern_conversion_roundtrip():
    for pat in _PATTERNS:
        idx = canonical_pattern(pat)
        assert _PATTERNS[idx] == pat


def test_tag_conversion_roundtrip():
    for t in _TAGS:
        idx = canonical_tag(*t)
        assert _TAGS[idx] == t
