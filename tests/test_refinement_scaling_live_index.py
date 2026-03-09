from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_live_index_states_the_refinement_scaling_firewall() -> None:
    text = (ROOT / "docs" / "index.html").read_text(encoding="utf-8")
    assert "Bridge firewall" in text
    assert "genuine 4D Weyl law" in text
    assert "genuine zeta pole" in text
    assert "almost-commutative product with a 4D continuum geometry" in text
