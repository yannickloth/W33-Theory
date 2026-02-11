import json
from pathlib import Path

from tools.w33_rootword_uv_parser import W33RootwordParser


def is_rotation(a, b):
    # check if list b is any rotation or reversed rotation of a
    if len(a) != len(b):
        return False
    n = len(a)
    for s in range(n):
        if all(a[(i + s) % n] == b[i] for i in range(n)):
            return True
    rb = list(reversed(b))
    for s in range(n):
        if all(a[(i + s) % n] == rb[i] for i in range(n)):
            return True
    return False


def test_sample_cycle_parses_correctly():
    p = W33RootwordParser()
    data = json.loads(
        Path(
            "analysis/minimal_commutator_cycles/minimal_holonomy_cycles_ordered_rootwords.json"
        ).read_text(encoding="utf-8")
    )
    # find first cycle with edge_roots_present
    entry = next(e for e in data if e.get("edge_roots_present"))
    rootword = entry["edge_roots"]

    out = p.parse(rootword)

    # sample expected values from repo minimal sample
    expected_cycle = [1, 2, 37, 19, 21, 12, 1, 10]
    assert len(out["cycle_vertices"]) == 8
    assert is_rotation(out["cycle_vertices"], expected_cycle)

    # canonical direction vectors should map to (0,1) and (1,0) for this sample
    assert out["u_canonical"] == (0, 1)
    assert out["v_canonical"] == (1, 0)
    assert out["k_canonical"] == entry["k"]

    # basepoint p recovered as the intersection of the two N12 lines
    assert out.get("p") == (0, 0)


def test_parse_all_minimal_root_covered_cycles_no_exceptions():
    p = W33RootwordParser()
    data = json.loads(
        Path(
            "analysis/minimal_commutator_cycles/minimal_holonomy_cycles_ordered_rootwords.json"
        ).read_text(encoding="utf-8")
    )
    for entry in data:
        if not entry.get("edge_roots_present"):
            continue
        rw = entry["edge_roots"]
        out = p.parse(rw)
        assert isinstance(out["k_canonical"], int)
        assert len(out["cycle_vertices"]) == 8
        assert isinstance(out["u_canonical"], tuple)
        assert isinstance(out["v_canonical"], tuple)
