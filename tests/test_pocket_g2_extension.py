import subprocess
from pathlib import Path
import zipfile
import json

def make_zip(src_dir: Path, dst_zip: Path):
    with zipfile.ZipFile(dst_zip, 'w', zipfile.ZIP_DEFLATED) as zf:
        for p in src_dir.rglob('*'):
            if p.is_file():
                zf.write(p, p.relative_to(src_dir))


def test_pocket_g2_extension_geometry(tmp_path):
    repo = Path(__file__).resolve().parents[1]
    tri_folder = repo / 'TOE_E6pair_SRG_triangle_decomp_v01_20260227_bundle'
    tri_zip = tmp_path / 'tri.zip'
    make_zip(tri_folder, tri_zip)
    edge_zip = tmp_path / 'edge.zip'
    with zipfile.ZipFile(edge_zip, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.write(repo / 'artifacts' / 'edge_to_rootpair_triple.json',
                 'TOE_edge_to_oriented_rootpairs_v01_20260227/edge_to_oriented_rootpair_triple.json')

    out = tmp_path / 'out'
    res = subprocess.run([
        ".venv\Scripts\python.exe",
        str(repo / 'tools' / 'pocket_g2_extension.py'),
        '--tri_zip', str(tri_zip),
        '--edge_zip', str(edge_zip)
    ], cwd=repo)
    assert res.returncode == 0, res.stderr
    geom_file = Path('pocket_geometry.json')
    assert geom_file.exists(), "geometry output missing"
    geom = json.loads(geom_file.read_text())
    assert geom['total_pockets'] == 540
    assert len(geom['by_silent_counts']) == 36
    assert geom['twin_pairs_count'] == 270
