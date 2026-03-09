from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


def test_readme_tracks_current_frontier_and_exact_pmns() -> None:
    text = _read("README.md")
    assert "Current Frontier" in text
    assert "continuum bridge" in text
    assert "4/13" in text
    assert "7/13" in text
    assert "2/91" in text
    assert "TQFT invariants" in text
    assert "Continuum Limit & Spectral Action Convergence" in text
    assert "Information-Theoretic Closure & Holographic Bound" in text


def test_pages_live_index_uses_current_top_level_language() -> None:
    text = _read("docs/index.html")
    assert "Verified Results" in text
    assert "Physics Interpretation (Conjectural)" in text
    assert "Historical Archive" in text
    assert "4/13" in text
    assert "7/13" in text
    assert "2/91" in text
    assert "J_max" in text
    assert "J = J_max sin" in text
    assert "residual gaps on top of that structure" in text


def test_pages_verified_section_promotes_exact_pmns_route_and_spectral_bridge() -> None:
    text = _read("docs/index.html")
    start = text.index('<section id="verified">')
    end = text.index('<section id="conjectural">')
    verified = text[start:end]
    assert "PMNS_CYCLOTOMIC.py" in verified
    assert "4/13" in verified
    assert "7/13" in verified
    assert "2/91" in verified
    assert "J_max" in verified
    assert "J = J_max sin" in verified
    assert "tests/test_exact_spectral_bridge.py" in verified
    assert "Str(e^-tD^2)=-80" in verified
