import json
from pathlib import Path

import pytest


def test_translation_commutator_is_central_on_h27():
    bundle = Path.cwd() / "artifacts" / "bundles" / "W33_Heisenberg_action_bundle_20260209_v1" / "analysis"
    jpath = bundle / "W33_Heisenberg_generators_Tx_Ty_Z.json"
    if not jpath.exists():
        pytest.skip("Heisenberg bundle not present in artifacts/ (integration-only test)")
    assert jpath.exists(), "Translation lifts JSON missing"
    j = json.loads(jpath.read_text(encoding="utf-8"))

    # Load H27 coords
    h27_csv = Path.cwd() / "artifacts" / "bundles" / "W33_Heisenberg_action_bundle_20260209_v1" / "H27_vertices_as_F3_cube_xy_t.csv"
    if not h27_csv.exists():
        pytest.skip("Heisenberg bundle not present in artifacts/ (integration-only test)")
    assert h27_csv.exists(), "H27 coords CSV missing"
    coords = {}
    with h27_csv.open("r", encoding="utf-8") as f:
        f.readline()
        for line in f:
            parts = [s.strip() for s in line.split(",")]
            vid = int(parts[0])
            x, y, t = int(parts[1]), int(parts[2]), int(parts[3])
            coords[vid] = (x, y, t)

    Z = {int(k): int(v) for k, v in j["Z"]["perm_40"].items()}

    # Determine delta t = t2 - t (mod 3) for all H27 vertices; it should be constant and nonzero
    deltas = set()
    mismatches = []
    for vid, (x, y, t) in coords.items():
        zvid = Z.get(vid)
        if zvid is None:
            mismatches.append((vid, "missing in Z"))
            continue
        x2, y2, t2 = coords[zvid]
        if (x2, y2) != (x, y):
            mismatches.append((vid, (x, y, t), (x2, y2, t2)))
            continue
        delta = (t2 - t) % 3
        deltas.add(delta)

    assert not mismatches, f"Z moves some H27 vertices between phase points: {mismatches}"
    assert len(deltas) == 1 and next(iter(deltas)) in (1, 2), f"Z acts with inconsistent delta t values: {deltas}"
