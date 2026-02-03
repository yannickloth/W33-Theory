import json
from pathlib import Path


def _load(path: str):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def test_toe_sm_decomposition_27_basic_counts():
    data = _load("artifacts/toe_sm_decomposition_27.json")
    assert data["status"] == "ok"
    tri = data["triads"]
    assert tri["total"] == 45
    assert tri["forbidden"] == 9
    assert tri["forbidden_partitions_vertices"] is True
    # Two Qψ patterns: 16·16·10 and 10·10·1 (scaled by 3)
    pats = {
        (tuple(x["qpsi3"]), x["count"], x["forbidden"])
        for x in tri["qpsi3_pattern_counts"]
    }
    assert (tuple([-2, 1, 1]), 40, 8) in pats
    assert (tuple([-2, -2, 4]), 5, 1) in pats


def test_toe_affine_plane_duality_counts():
    data = _load("artifacts/toe_affine_plane_duality.json")
    assert data["status"] == "ok"
    counts = data["counts"]
    assert counts["bad_triads"] == 9
    assert counts["triads_total"] == 45
    assert counts["triads_allowed"] == 36
    assert counts["double_sixes"] == 36
    assert counts["affine_points"] == 9
    assert counts["affine_lines"] == 12
    assert counts["z3_lifts_per_line"] == 3
    lines = data["duality_by_line"]
    assert len(lines) == 12
    for row in lines:
        assert len(row["allowed_triads_cycle"]) == 3
        assert len(row["double_sixes_cycle"]) == 3
        assert len(row["z3_equivariant_pairing"]) == 3


def test_toe_three_generation_coupling_atlas_counts():
    data = _load("artifacts/toe_three_generation_coupling_atlas.json")
    assert data["status"] == "ok"
    counts = data["counts"]
    assert counts["couplings_total"] == 1620
    assert counts["couplings_forbidden"] == 324
    assert counts["couplings_allowed"] == 1296
    pairs = counts["orbit_pairs"]
    assert len(pairs) == 6
    for row in pairs:
        assert row["total"] == 270
        assert row["forbidden"] == 54
        assert row["allowed"] == 216

    # Sanity spot-check: up-Yukawa-type triads are more suppressed (2/6 triads forbidden => 1/3)
    triad_types = {tuple(t["fields"]): t for t in data["triad_types"]}
    assert triad_types[("H_u", "Q", "u^c")]["forbidden_frac"] == 72 / 216


def test_toe_yukawa_textures_has_up_yukawa_texture():
    data = _load("artifacts/toe_yukawa_textures.json")
    assert data["status"] == "ok"
    blocks = {tuple(b["type"]): b for b in data["textures"]}
    up = blocks[("H_u", "Q", "u^c")]
    assert up["total"] == 6
    assert up["forbidden"] == 2


def test_toe_phase_diagram_charge_alignment_basic():
    data = _load("artifacts/toe_phase_diagram_charge_alignment.json")
    assert data["status"] == "ok"
    grid = data["grid"]
    fw = grid["firewall_strength"]
    sig = grid["phase_noise_sigma"]
    assert len(fw) >= 2 and len(sig) >= 2
    cells = data["cells"]
    assert len(cells) == len(fw)
    assert all(len(row) == len(sig) for row in cells)

    allowed = {"Y", "Qpsi", "Qchi", "T3"}
    for row in cells:
        for cell in row:
            assert cell["best"]["label"] in allowed
            sim = float(cell["best"]["sim"])
            assert 0.0 <= sim <= 1.0


def test_toe_affine_plane_interaction_dictionary_invariants():
    data = _load("artifacts/toe_affine_plane_interaction_dictionary.json")
    assert data["status"] == "ok"
    counts = data["counts"]
    assert counts["blocks"] == 9
    assert counts["affine_lines"] == 12
    assert counts["triads_total"] == 45
    assert counts["triads_forbidden"] == 9
    assert counts["triads_allowed"] == 36
    assert counts["couplings_total"] == 1620
    assert counts["couplings_per_triad"] == 36
    assert counts["couplings_per_allowed_line"] == 108

    blocks = data["blocks"]
    assert len(blocks) == 9
    for b in blocks:
        assert b["couplings_total"] == 36
        assert b["couplings_forbidden"] == 36

    lines = data["lines"]
    assert len(lines) == 12
    for row in lines:
        assert row["couplings_total"] == 108
        assert len(row["allowed_triads_cycle"]) == 3
        assert len(row["double_sixes_cycle"]) == 3
