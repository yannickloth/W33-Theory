import csv
from pathlib import Path


def load_recorded(path: Path):
    d = {}
    with path.open('r', encoding='utf-8') as f:
        rdr = csv.DictReader(f)
        for r in rdr:
            if r.get('triad'):
                parts = [int(x) for x in r['triad'].split()]
                tri = tuple(sorted(parts))
            else:
                tri = tuple(sorted((int(r['a']), int(r['b']), int(r['c']))))
            if r.get('hol_mod12'):
                hol = int(r['hol_mod12'])
            elif r.get('holonomy_z12'):
                hol = int(r['holonomy_z12'])
            else:
                hol = None
            d[tri] = hol
    return d


def test_recomputed_triads_match_recorded():
    recorded = load_recorded(Path('bundles/phase_aware_v3/W33_N12_58_phase_aware_loop_v3/w33_four_center_triads_with_ray_holonomy.csv'))
    recomputed = load_recorded(Path('analysis/triad_recompute_20260209/w33_four_center_triads_with_ray_holonomy.csv'))
    # ensure counts match
    assert len(recorded) == len(recomputed)
    # ensure exact match of triad -> hol value
    assert recorded == recomputed
