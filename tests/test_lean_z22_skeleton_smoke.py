from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEAN_FILE = ROOT / "proofs" / "lean" / "z22_exclusion.lean"


def test_lean_z22_file_ascii_clean() -> None:
    text = LEAN_FILE.read_text(encoding="utf-8")
    assert all(ord(ch) < 128 for ch in text)
    assert "â" not in text
    assert "Â" not in text


def test_lean_z22_contains_key_lemmas() -> None:
    text = LEAN_FILE.read_text(encoding="utf-8")
    assert "theorem zMap_one" in text
    assert "theorem z22_contradiction_via_zMap" in text
