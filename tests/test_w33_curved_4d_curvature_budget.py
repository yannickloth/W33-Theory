from __future__ import annotations

import json
from math import pi
from pathlib import Path

from w33_curved_4d_curvature_budget import (
    build_curved_4d_curvature_budget_summary,
    cp2_curvature_seed,
    k3_curvature_seed,
    refinement_invariance_checks,
    torus4_seed,
    weyl_l2_floor,
    write_summary,
)


def test_torus_has_no_topological_curvature_floor() -> None:
    torus = torus4_seed()
    assert torus.euler_characteristic == 0
    assert torus.signature == 0
    assert torus.nonflat_topologically_forced is False
    assert torus.nonconformally_flat_topologically_forced is False
    assert torus.weyl_l2_floor == 0.0


def test_cp2_has_exact_nonzero_weyl_floor() -> None:
    cp2 = cp2_curvature_seed()
    assert cp2.euler_characteristic == 3
    assert cp2.signature == 1
    assert cp2.nonflat_topologically_forced is True
    assert cp2.nonconformally_flat_topologically_forced is True
    assert cp2.hitchin_thorpe_plus == 9
    assert cp2.hitchin_thorpe_minus == 3
    assert abs(cp2.weyl_l2_floor - 12 * pi**2) < 1e-12


def test_k3_has_larger_exact_weyl_floor() -> None:
    k3 = k3_curvature_seed()
    assert k3.euler_characteristic == 24
    assert k3.signature == -16
    assert k3.nonflat_topologically_forced is True
    assert k3.nonconformally_flat_topologically_forced is True
    assert sorted((k3.hitchin_thorpe_plus, k3.hitchin_thorpe_minus)) == [0, 96]
    assert abs(k3.weyl_l2_floor - 192 * pi**2) < 1e-10


def test_refinement_preserves_seed_euler_characteristics() -> None:
    checks = refinement_invariance_checks()
    assert checks["cp2_euler_characteristics"] == [3, 3, 3]
    assert checks["k3_euler_characteristics"] == [24, 24, 24]
    assert checks["signature_is_topological_invariant"] is True


def test_weyl_floor_scales_with_absolute_signature() -> None:
    assert weyl_l2_floor(0) == 0.0
    assert abs(weyl_l2_floor(1) - 12 * pi**2) < 1e-12
    assert abs(weyl_l2_floor(-16) - 16 * weyl_l2_floor(1)) < 1e-10


def test_summary_records_refinement_invariant_curvature_budget() -> None:
    summary = build_curved_4d_curvature_budget_summary()
    assert summary["status"] == "ok"
    assert summary["comparison_seed"]["name"] == "T4"
    assert summary["curved_seeds"][0]["name"] == "CP2"
    assert summary["curved_seeds"][1]["name"] == "K3"
    assert summary["curved_seeds"][0]["signature"] == 1
    assert summary["curved_seeds"][1]["signature"] == -16
    assert "nonzero Weyl-curvature channel" in summary["bridge_verdict"]


def test_write_summary_emits_json(tmp_path: Path) -> None:
    out = write_summary(tmp_path / "w33_curved_4d_curvature_budget_summary.json")
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["status"] == "ok"
    assert data["comparison_seed"]["weyl_l2_floor"] == 0.0
    assert data["curved_seeds"][0]["nonconformally_flat_topologically_forced"] is True
