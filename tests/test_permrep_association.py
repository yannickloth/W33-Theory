import json
from pathlib import Path

import numpy as np


def test_he_2058_association_scheme_matches_atlas():
    import importlib

    import scripts.w33_permrep_association as permassoc
    from scripts.w33_permrep_association import parse_gap_permrep

    importlib.reload(permassoc)

    gap = Path("data/HeG1-p2058B0.g1")
    assert gap.exists()

    # parser should find one generator per .g file
    assert len(parse_gap_permrep(gap)) == 1
    assert len(parse_gap_permrep(Path("data/HeG1-p2058B0.g2"))) == 1

    # analyze should auto-collect companion .g2 and produce the full scheme
    report = permassoc.analyze_gap_permrep_association(gap, base=1)
    assert report["degree"] == 2058
    assert report["rank"] == 5
    # match ATLAS suborbit lengths for He(2058)
    expected = [1, 136, 136, 425, 1360]
    assert sorted(report["suborbit_lengths"]) == sorted(expected)

    # M0 (identity relation) -> should be identity matrix in M-basis
    M0 = np.array(report["Ms"][0], dtype=int)
    # check M0 is identity
    assert np.array_equal(M0, np.eye(M0.shape[0], dtype=int))

    # eigenvalues: each M_i should have exactly r eigenvalues
    for eigs in report["eigs"]:
        assert len(eigs) == report["rank"]
        # eigenvalues should be real (association scheme)
        assert all(abs(np.imag(ev)) < 1e-9 for ev in eigs)

    # quick consistency: sum of suborbit lengths == degree
    assert sum(report["suborbit_lengths"]) == report["degree"]


def test_analyze_auto_loads_companion_g_files():
    import importlib

    import scripts.w33_permrep_association as permassoc

    importlib.reload(permassoc)

    # calling analyze on .g1 should implicitly load .g2
    report = permassoc.analyze_gap_permrep_association(
        Path("data/HeG1-p2058B0.g1"), base=1
    )
    assert report["degree"] == 2058
    assert report["rank"] == 5
