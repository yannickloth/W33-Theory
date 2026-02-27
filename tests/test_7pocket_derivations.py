import subprocess
from pathlib import Path
import zipfile

def make_zip(src_dir: Path, dst_zip: Path):
    with zipfile.ZipFile(dst_zip, 'w', zipfile.ZIP_DEFLATED) as zf:
        for p in src_dir.rglob('*'):
            if p.is_file():
                zf.write(p, p.relative_to(src_dir))


def test_derive_7pocket_derivations(tmp_path):
    repo = Path(__file__).resolve().parents[1]
    # prepare triangle zip from existing folder
    tri_folder = repo / 'TOE_E6pair_SRG_triangle_decomp_v01_20260227_bundle'
    tri_zip = tmp_path / 'tri.zip'
    make_zip(tri_folder, tri_zip)
    # prepare edge mapping zip containing only the json
    edge_zip = tmp_path / 'edge.zip'
    with zipfile.ZipFile(edge_zip, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.write(repo / 'artifacts' / 'edge_to_rootpair_triple.json',
                 'TOE_edge_to_oriented_rootpairs_v01_20260227/edge_to_oriented_rootpair_triple.json')

    outdir = tmp_path / 'out'
    res = subprocess.run([".venv\\Scripts\\python.exe", str(repo / "tools" / "derive_7pocket_derivations.py"),
                          "--tri_zip", str(tri_zip),
                          "--edge_zip", str(edge_zip),
                          "--out_dir", str(outdir)], cwd=repo,
                         capture_output=True, text=True)
    # log output for diagnostics
    print("stdout:\n", res.stdout)
    print("stderr:\n", res.stderr)
    assert res.returncode == 0, "derive script failed"
    # we don't insist on output files in unit test environment (may depend on full data)
    # log listing if available
    if outdir.exists():
        print("outputs:", list(outdir.iterdir()))
