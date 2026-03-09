from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


def test_readme_uses_layered_rigor_language() -> None:
    text = _read("README.md")
    assert "Verified Frontier" in text
    assert "Physics Interpretation (Conjectural)" in text
    assert "Historical Archive" in text
    assert "4/13" in text
    assert "7/13" in text
    assert "2/91" in text
    assert "J_max" in text
    assert "J = J_max sin" in text


def test_pages_source_uses_layered_rigor_language() -> None:
    text = _read("docs/index_source.html")
    assert "Verified Frontier" in text
    assert "Physics Interpretation (Conjectural)" in text
    assert "Historical Archive" in text
    assert "4/13" in text
    assert "7/13" in text
    assert "2/91" in text
    assert "J_max" in text
    assert "J = J_max sin" in text


def test_pages_verified_section_promotes_exact_pmns_route() -> None:
    text = _read("docs/index_source.html")
    start = text.index('<section id="verified">')
    end = text.index('<section id="conjectural">')
    verified = text[start:end]
    assert "PMNS_CYCLOTOMIC.py" in verified
    assert "4/13" in verified
    assert "7/13" in verified
    assert "2/91" in verified
    assert "J_max" in verified
    assert "J = J_max sin" in verified
