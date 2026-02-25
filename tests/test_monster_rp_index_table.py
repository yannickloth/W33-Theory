from __future__ import annotations


def _find_hit(hits: list[dict], *, pair: str, r: int) -> dict:
    for h in hits:
        if not isinstance(h, dict):
            continue
        if str(h.get("pair")) == pair and int(h.get("r", 0) or 0) == int(r):
            return h
    raise AssertionError(f"missing perm-hit {pair} r={r}")


def test_monster_rp_index_table_cross_checks() -> None:
    """Regression: r_p=n/p matches a transitive perm-degree index [H:K]."""
    from scripts.w33_monster_rp_index_table import analyze

    rep = analyze(include_mass_ranking=False)
    assert rep.get("available") is True

    ogg_primes = rep.get("ogg_primes", [])
    assert isinstance(ogg_primes, list)
    for p in (5, 7, 11, 13, 17, 19, 23, 29, 31, 41, 47, 59, 71):
        assert p in ogg_primes

    summary = rep.get("summary", {})
    assert isinstance(summary, dict)
    assert int(summary.get("n_classes", 0) or 0) >= 21
    assert int(summary.get("n_classes_with_perm_hit", 0) or 0) >= 11

    per_prime = rep.get("per_prime", [])
    assert isinstance(per_prime, list)
    prime_map = {int(rec.get("p", 0) or 0): rec for rec in per_prime if isinstance(rec, dict)}

    assert prime_map[5]["best_pair_by_perm_index"] == "2A×3A"
    assert int(prime_map[5]["best_perm_index_r"]) == 1140000

    assert prime_map[11]["best_pair_by_perm_index"] == "2A×3B"
    assert int(prime_map[11]["best_perm_index_r"]) == 144

    assert prime_map[13]["best_pair_by_perm_index"] == "2A×3B"
    assert int(prime_map[13]["best_perm_index_r"]) == 156

    per_class = rep.get("per_class", {})
    assert isinstance(per_class, dict)

    hit_11 = _find_hit(per_class["11A"]["perm_hits"], pair="2A×3B", r=144)
    assert hit_11["index_equals_r"] is True
    assert hit_11["cofactor_group"] == "M12"
    assert int(hit_11["stabilizer_order"]) == 660
    assert int(hit_11["n"]) == 11 * 144

    hit_5 = _find_hit(per_class["5A"]["perm_hits"], pair="2A×3A", r=1140000)
    assert hit_5["cofactor_group"] == "HN"
    assert int(hit_5["stabilizer_order"]) == 239500800
    assert int(hit_5["n"]) == 5 * 1140000

    hit_13a = _find_hit(per_class["13A"]["perm_hits"], pair="2A×3B", r=156)
    assert hit_13a["cofactor_group"] == "PSL3(3)"
    assert int(hit_13a["stabilizer_order"]) == 36
    assert int(hit_13a["n"]) == 13 * 156

    hit_13b = _find_hit(per_class["13B"]["perm_hits"], pair="2A×3C", r=104)
    assert hit_13b["cofactor_group"] == "13^2:2A4"
    assert int(hit_13b["stabilizer_order"]) == 39
    assert int(hit_13b["n"]) == 13 * 104

