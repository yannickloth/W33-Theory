import json
from pathlib import Path


def load_json(p):
    return json.loads(Path(p).read_text(encoding="utf-8"))


def test_agl23_count_and_commutator():
    base = Path("analysis/w33_bundle_temp/analysis")
    agl = load_json(base / "AGL23_lifts.json")
    assert agl["count"] == 216

    txj = load_json(base / "W33_Heisenberg_generators_Tx_Ty_Z.json")
    Z_perm = txj["Z"]["perm_40"]
    Tx = (
        [int(txj["Tx"]["perm_40"][str(i)]) for i in range(40)]
        if isinstance(txj["Tx"]["perm_40"], dict)
        else txj["Tx"]["perm_40"]
    )
    Ty = (
        [int(txj["Ty"]["perm_40"][str(i)]) for i in range(40)]
        if isinstance(txj["Ty"]["perm_40"], dict)
        else txj["Ty"]["perm_40"]
    )

    def compose(pA, pB):
        return [pA[pB[i]] for i in range(len(pA))]

    def invert(p):
        inv = [0] * len(p)
        for i, v in enumerate(p):
            inv[v] = i
        return inv

    Tx_inv = invert(Tx)
    Ty_inv = invert(Ty)
    # commutator = Tx Ty Tx^{-1} Ty^{-1}
    c1 = compose(Tx, Ty)
    c2 = compose(c1, Tx_inv)
    comm = compose(c2, Ty_inv)
    # compare to Z_perm (may be dict in file)
    expected = (
        [int(Z_perm[str(i)]) for i in range(40)] if isinstance(Z_perm, dict) else Z_perm
    )
    # allow either orientation (Z or Z^{-1}) since generator orientation may differ
    expected_inv = [0] * len(expected)
    for i, v in enumerate(expected):
        expected_inv[v] = i
    assert comm == expected or comm == expected_inv


def test_parallelogram_match_fraction():
    base = Path("analysis/w33_bundle_temp/analysis")
    cmp = load_json(base / "parallelogram_holonomy_vs_bargmann.json")
    assert cmp["total_parallelograms"] == 54
    assert cmp["matches"] == 54
