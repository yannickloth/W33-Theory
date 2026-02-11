from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEAN_FILE = ROOT / "proofs" / "lean" / "gl2_enumeration.lean"


def test_gl2_enumeration_contains_conjugacy() -> None:
    text = LEAN_FILE.read_text(encoding="utf-8")
    assert "theorem candidates_conjugate" in text
    assert "def inv2x2" in text
    assert "def adj2x2" in text
