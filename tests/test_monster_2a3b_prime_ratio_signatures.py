from __future__ import annotations


def _leading_int(s: str) -> int | None:
    out = ""
    for ch in s:
        if "0" <= ch <= "9":
            out += ch
        else:
            break
    if not out:
        return None
    try:
        return int(out)
    except Exception:
        return None


def test_monster_2a3b_prime_ratio_signatures_match_toe_invariants() -> None:
    """Regression: the 2A×3B prime-order structure constants factor cleanly."""
    from scripts.w33_leech_monster import (
        analyze_monster_2a3b_class_algebra_partial_distribution,
    )
    from scripts.w33_padic_ads_cft import analyze_conformal_dimensions

    dist = analyze_monster_2a3b_class_algebra_partial_distribution()
    assert dist.get("available") is True
    classes = dist.get("classes", {})
    assert isinstance(classes, dict)

    gap = analyze_conformal_dimensions()
    dims = gap.get("conformal_dimensions", {})
    assert isinstance(dims, dict)
    delta = min(int(lam) for lam in dims.keys() if int(lam) > 0)
    assert int(delta) == 4

    targets = {
        "11A": 144,
        "13A": 156,
        "17A": 14,
        "19A": 48,
        "23A": 4,
        "29A": 3,
        "31A": 15,
        "41A": 2,
        "71A": 1,
    }

    for cls, expected_ratio in targets.items():
        info = classes.get(cls, {})
        assert isinstance(info, dict)
        n = int(info.get("structure_constant_per_element", 0) or 0)
        p = _leading_int(cls)
        assert p is not None and p > 1
        assert n % p == 0
        ratio = n // p
        assert ratio == int(expected_ratio)
