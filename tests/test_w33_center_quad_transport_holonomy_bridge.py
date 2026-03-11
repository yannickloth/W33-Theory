from __future__ import annotations

import json
from pathlib import Path

from w33_center_quad_transport_holonomy_bridge import (
    build_center_quad_transport_holonomy_summary,
    write_summary,
)


def test_transport_triangle_count_and_archived_parity_match() -> None:
    summary = build_center_quad_transport_holonomy_summary()
    assert summary["status"] == "ok"
    assert summary["transport_triangles"] == 5280
    assert summary["archived_v14_triangle_parity"] == {
        "parity0": 3120,
        "parity1": 2160,
    }


def test_holonomy_cycle_types_split_exactly_by_z2_parity() -> None:
    holonomy = build_center_quad_transport_holonomy_summary()["triangle_holonomy"]
    assert holonomy["cycle_type_counts"] == {
        "identity": 240,
        "three_cycle": 2880,
        "transposition": 2160,
    }
    assert holonomy["by_z2_parity"] == {
        "0": {"identity": 240, "three_cycle": 2880},
        "1": {"transposition": 2160},
    }


def test_z2_triangle_parity_equals_holonomy_sign_exactly() -> None:
    holonomy = build_center_quad_transport_holonomy_summary()["triangle_holonomy"]
    assert holonomy["z2_parity_equals_holonomy_sign_exactly"] is True


def test_summary_write_emits_json(tmp_path: Path) -> None:
    out = write_summary(tmp_path / "w33_center_quad_transport_holonomy_bridge_summary.json")
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["status"] == "ok"
    assert "sign character of an exact local S3 holonomy" in data["bridge_verdict"]
