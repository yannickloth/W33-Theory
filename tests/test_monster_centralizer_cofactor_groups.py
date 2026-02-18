from __future__ import annotations


def test_monster_centralizer_cofactor_recognition_and_perm_hits() -> None:
    from scripts.w33_monster_centralizer_cofactor_groups import analyze

    rep = analyze()
    assert rep.get("available") is True

    classes = rep.get("classes", {})
    assert isinstance(classes, dict)

    # Lie/symmetric/cyclic cofactor recognitions by order.
    assert classes["13A"]["cofactor_order"] == 5616
    assert classes["13A"]["cofactor_group_recognized"] == "PSL3(3)"

    assert classes["17A"]["cofactor_order"] == 168
    assert classes["17A"]["cofactor_group_recognized"] == "PSL2(7)"

    assert classes["19A"]["cofactor_order"] == 60
    assert classes["19A"]["cofactor_group_recognized"] == "A5"

    assert classes["23A"]["cofactor_order"] == 24
    assert classes["23A"]["cofactor_group_recognized"] == "S4"

    assert classes["29A"]["cofactor_order"] == 3
    assert classes["29A"]["cofactor_group_recognized"] == "C3"

    # Prime-ratio permutation-degree hits.
    hits_23 = classes["23A"]["perm_hits"]
    assert isinstance(hits_23, list)
    assert any(
        h.get("pair") == "2A×3B" and int(h.get("r", 0) or 0) == 4 for h in hits_23
    )

    hits_29 = classes["29A"]["perm_hits"]
    assert isinstance(hits_29, list)
    assert any(
        h.get("pair") == "2A×3B" and int(h.get("r", 0) or 0) == 3 for h in hits_29
    )
