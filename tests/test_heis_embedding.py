#!/usr/bin/env python3
"""Tests for the Heisenberg embedding of N."""

from __future__ import annotations

from THEORY_PART_CXCVI_HEISENBERG_EMBEDDING import verify_homomorphism, build_map


def test_embedding_file_created():
    # running main writes the summary file
    from THEORY_PART_CXCVI_HEISENBERG_EMBEDDING import main
    main()
    from pathlib import Path
    assert (Path(__file__).resolve().parent / "heis_embedding_summary.json").exists()


def test_homomorphism_on_random_pairs():
    assert verify_homomorphism(sample=200) is True


def test_mapping_structure():
    mapping = build_map()
    # check at least one nontrivial image
    assert any(v.u != (0,0) or v.v != (0,0) for v in mapping.values())
    assert len(mapping) == 192
