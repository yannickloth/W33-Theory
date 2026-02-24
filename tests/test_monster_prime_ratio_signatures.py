from __future__ import annotations

import json
from pathlib import Path


def _load_degree_payload(path: str) -> tuple[int, int, list[int]]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    order = int(payload.get("order", 0) or 0)
    n_cls = int(payload.get("n_conjugacy_classes", 0) or 0)
    degs = payload.get("degrees", [])
    assert isinstance(degs, list)
    degs_int = [int(x) for x in degs]
    return order, n_cls, degs_int


def test_he_hn_irrep_degrees_sum_of_squares_matches_group_order() -> None:
    # Deterministic offline degree multisets: sum_{chi} chi(1)^2 = |G|.
    he_order, he_ncls, he_degs = _load_degree_payload("data/he_irrep_degrees.json")
    assert he_order == 4030387200
    assert he_ncls == 33
    assert len(he_degs) == 33
    assert sum(d * d for d in he_degs) == he_order

    hn_order, hn_ncls, hn_degs = _load_degree_payload("data/hn_irrep_degrees.json")
    assert hn_order == 273030912000000
    assert hn_ncls == 54
    assert len(hn_degs) == 54
    assert sum(d * d for d in hn_degs) == hn_order


def test_prime_ratio_signature_irrep_and_perm_hits_on_sporadic_rungs() -> None:
    from scripts.w33_monster_prime_ratio_signatures import analyze

    rep = analyze()
    assert rep.get("available") is True

    rungs = rep.get("rungs", {})
    assert isinstance(rungs, dict)

    # 11A: has a nontrivial hit r_11=144 in deg(M12).
    info_11 = rungs.get("11A", {})
    assert isinstance(info_11, dict)
    assert info_11.get("cofactor_group") == "M12"
    hits_11_ir = info_11.get("ratio_hits_in_irrep_degree_set", [])
    assert isinstance(hits_11_ir, list)
    assert any(int(h.get("r", 0) or 0) == 144 for h in hits_11_ir)

    hits_11_perm = info_11.get("ratio_hits_in_perm_degree_set", [])
    assert isinstance(hits_11_perm, list)
    assert any(int(h.get("r", 0) or 0) == 144 for h in hits_11_perm)

    # 5A/7A: no r_p hits any irrep degree of HN/He (for any of the 6 (2X,3Y) pairs).
    info_5 = rungs.get("5A", {})
    assert isinstance(info_5, dict)
    assert info_5.get("cofactor_group") == "HN"
    hits_5_ir = info_5.get("ratio_hits_in_irrep_degree_set", [])
    assert isinstance(hits_5_ir, list)
    assert hits_5_ir == []

    hits_5_perm = info_5.get("ratio_hits_in_perm_degree_set", [])
    assert isinstance(hits_5_perm, list)
    assert any(int(h.get("r", 0) or 0) == 1140000 for h in hits_5_perm)

    info_7 = rungs.get("7A", {})
    assert isinstance(info_7, dict)
    assert info_7.get("cofactor_group") == "He"
    hits_7_ir = info_7.get("ratio_hits_in_irrep_degree_set", [])
    assert isinstance(hits_7_ir, list)
    assert hits_7_ir == []

    hits_7_perm = info_7.get("ratio_hits_in_perm_degree_set", [])
    assert isinstance(hits_7_perm, list)
    assert any(int(h.get("r", 0) or 0) == 2058 for h in hits_7_perm)

    # Pipeline check: Δ(2,3,11) support -> best (2X,3Y) by mass -> replicability.
    from scripts.w33_monster_ogg_pipeline import analyze as analyze_ogg_pipeline

    pipe = analyze_ogg_pipeline(max_q_exp=5, scan_primes=[11])
    assert pipe.get("available") is True
    assert pipe.get("scan_primes") == [11]
    summary = pipe.get("summary", {})
    assert isinstance(summary, dict)
    assert summary.get("n_primes") == 1
    assert summary.get("n_structure_best_differs_from_mass_best") == 1
    assert summary.get("best_pair_by_mass_counts") == {"2Ax3A": 1}
    assert summary.get("best_pair_by_structure_counts") == {"2Ax3B": 1}
    assert summary.get("best_pair_by_structure_reason_counts") == {"perm_hit": 1}
    assert summary.get("recommended_pair_perm_hit_counts") == {"2Ax3B": 1}
    assert summary.get("recommended_pair_nontrivial_irrep_hit_counts") == {"2Ax3B": 1}
    results = pipe.get("results", [])
    assert isinstance(results, list)
    assert len(results) == 1
    rec = results[0]
    assert isinstance(rec, dict)
    assert rec.get("p") == 11
    assert rec.get("best_pair") == "2Ax3A"
    assert rec.get("classes") == ["11A"]
    repl = rec.get("replicability", [])
    assert isinstance(repl, list)
    assert repl and repl[0].get("class_name") == "11A"
    assert repl[0].get("verified") is True

    # The "best by mass" pair differs from the "best by cofactor-spectrum hit":
    # 11A has C_M(11A) = 11·M12 and r_11=144 occurs for 2A×3B, landing in deg(M12).
    assert rec.get("best_pair_by_structure") == "2Ax3B"
    assert rec.get("best_pair_by_structure_reason") == "perm_hit"
    assert rec.get("recommended_pair_perm_hit") == "2Ax3B"
    assert rec.get("recommended_pair_nontrivial_irrep_hit") == "2Ax3B"

    ranked_mass = rec.get("ranked_pairs_by_mass", [])
    assert isinstance(ranked_mass, list)
    assert len(ranked_mass) == 6
    assert ranked_mass[0].get("pair") == "2Ax3A"
    assert {str(x.get("pair")) for x in ranked_mass} == {
        "2Ax3A",
        "2Ax3B",
        "2Ax3C",
        "2Bx3A",
        "2Bx3B",
        "2Bx3C",
    }

    ranked_struct = rec.get("ranked_pairs_by_structure", [])
    assert isinstance(ranked_struct, list)
    assert len(ranked_struct) == 6
    assert ranked_struct[0].get("pair") == "2Ax3B"

    # Quantify the mismatch: the signature pair carries tiny probability mass.
    masses = rec.get("mass_by_pair", {})
    assert isinstance(masses, dict)
    m_mass = float(masses["2Ax3A"]["float"])
    m_sig = float(masses["2Ax3B"]["float"])
    assert m_mass > 1e-2
    assert m_sig < 1e-3
