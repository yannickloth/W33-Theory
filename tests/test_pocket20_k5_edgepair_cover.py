import json
import pandas as pd

def test_pocket20_summary():
    data = json.load(open('summary.json'))
    assert data['num_pockets20'] == 105
    assert data['num_edgepair_pockets'] == 90
    assert data['num_edges'] == 45
    assert data['expect_each'] == 2

def test_orbit10_structure():
    data = json.load(open('orbit10_lines_k5_structure.json'))
    # expect a list of ten records
    assert isinstance(data, list)
    assert len(data) == 10
    for rec in data:
        assert 'line' in rec and 'k5_edge' in rec

def test_vertex_edge_mapping():
    data = json.load(open('srg_vertices20_to_k5edge.json'))
    assert len(data) == 20
    for rec in data:
        assert len(rec['edges']) >= 1

def test_pocket_cover_csv():
    df = pd.read_csv('pocket20_edgepair_cover.csv')
    # there are 90 records
    assert len(df) == 90
    # each edgepair appears twice
    counts = df['edgepair'].value_counts()
    assert all(c == 2 for c in counts)
