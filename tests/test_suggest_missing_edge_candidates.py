from pathlib import Path
import pytest

from tools.suggest_missing_edge_candidates import generate_report


MISSING_JSON = Path('analysis/minimal_commutator_cycles/w33_uv_parser_det1_missing_edges.json')
OUT_JSON = Path('analysis/minimal_commutator_cycles/w33_uv_parser_det1_missing_edges_candidates.json')
OUT_CSV = Path('analysis/minimal_commutator_cycles/w33_uv_parser_det1_missing_edges_candidates.csv')


def test_generate_candidates_smoke():
    if not MISSING_JSON.exists():
        pytest.skip('Missing edges file not present; skipping smoke test')
    # run generator for a small number of edges
    report = generate_report(MISSING_JSON, top_n=8, candidates_per_edge=3, out_dir=Path('analysis/minimal_commutator_cycles'))
    assert isinstance(report, dict)
    assert 'edges' in report
    # ensure files were written
    assert OUT_JSON.exists()
    assert OUT_CSV.exists()
    # ensure at least one edge has candidates
    assert any(len(e.get('candidates', [])) > 0 for e in report['edges'])
