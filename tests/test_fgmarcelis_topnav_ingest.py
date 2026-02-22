import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_pg32_artifact_exists_and_valid():
    p = ROOT / "artifacts" / "pg32_lines_from_remaining15.json"
    assert p.exists(), "pg32 lines artifact missing"
    data = json.loads(p.read_text(encoding="utf-8"))
    summary = data.get("summary", {})
    assert summary.get("n_lines") == 35
    assert summary.get("line_size") == 3
    # each listed line must have exactly 3 point indices
    for L in data.get("lines", []):
        pts = L.get("points", [])
        assert len(pts) == 3


def test_ckm_27_lines_summary():
    p = ROOT / "CKM_27_LINES.json"
    assert p.exists(), "CKM 27-lines summary missing"
    d = json.loads(p.read_text(encoding="utf-8"))
    isec = d.get("intersection_structure", {})
    assert isec.get("lines") == 27
    # repo summary uses 11 intersections per line and 156 total (Schläfli meet counts)
    assert isec.get("intersections_per_line") == 11
    assert isec.get("total_intersections") == 156


def test_mog_map_builds():
    # THE_EXACT_MAP provides build_mog_map()
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "THE_EXACT_MAP", ROOT / "THE_EXACT_MAP.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mog = mod.build_mog_map()
    assert isinstance(mog, dict)
    assert len(mog) == 12
