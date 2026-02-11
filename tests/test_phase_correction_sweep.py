from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MODULE_PATH = ROOT / "tools" / "sweep_phase_correction_bundles.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("phase_sweep", MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load module from {MODULE_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _write(path: Path, content: str = "x") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_discover_bundle_dirs_and_compatibility(tmp_path: Path):
    sweep = _load_module()
    root = tmp_path / "bundles"

    good = root / "good_bundle"
    bad = root / "bad_bundle"

    _write(good / "qutrit_MUB_state_vectors_for_N12_vertices.csv")
    _write(good / "H27_vertices_as_F3_cube_xy_t.csv")
    _write(good / "missing_planes_as_phase_space_points.csv")
    _write(good / "N12_vertices_as_affine_lines.csv")

    _write(bad / "qutrit_MUB_state_vectors_for_N12_vertices.csv")

    discovered = sweep.discover_bundle_dirs([root])
    assert good.resolve() in discovered
    assert bad.resolve() in discovered

    ok, missing = sweep.is_compatible_bundle(good)
    assert ok is True
    assert missing == []

    ok, missing = sweep.is_compatible_bundle(bad)
    assert ok is False
    assert "H27_vertices_as_F3_cube_xy_t.csv" in missing
    assert "N12_vertices_as_affine_lines.csv" in missing
    assert "missing_planes_as_phase_space_points.csv" in missing


def test_build_markdown_summary_includes_rows():
    sweep = _load_module()
    summary = {
        "generated_at_utc": "2026-02-10T00:00:00+00:00",
        "python_executable": "py -3",
        "bundles_total": 2,
        "bundles_succeeded": 1,
        "bundles_failed_or_skipped": 1,
        "results": [
            {
                "bundle_dir": "A",
                "status": "ok",
                "matches": 54,
                "total": 54,
                "notes": [],
            },
            {
                "bundle_dir": "B",
                "status": "skipped_incompatible",
                "matches": None,
                "total": None,
                "notes": ["Missing required files"],
            },
        ],
    }
    out = sweep.build_markdown_summary(summary)
    assert "Phase correction bundle sweep" in out
    assert "`A`" in out
    assert "`ok`" in out
    assert "54" in out
    assert "Missing required files" in out
