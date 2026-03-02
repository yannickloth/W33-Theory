import subprocess, zipfile, tempfile, os
from pathlib import Path

repo = Path('C:/Repos/Theory of Everything')
with tempfile.TemporaryDirectory() as tmp:
    tmp = Path(tmp)
    tri_folder = repo / 'TOE_E6pair_SRG_triangle_decomp_v01_20260227_bundle'
    tri_zip = tmp / 'tri.zip'
    with zipfile.ZipFile(tri_zip, 'w', zipfile.ZIP_DEFLATED) as zf:
        for p in tri_folder.rglob('*'):
            if p.is_file():
                zf.write(p, p.relative_to(tri_folder))
    edge_zip = tmp / 'edge.zip'
    with zipfile.ZipFile(edge_zip, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.write(repo / 'artifacts' / 'edge_to_rootpair_triple.json',
                 'TOE_edge_to_oriented_rootpairs_v01_20260227/edge_to_oriented_rootpair_triple.json')
    outdir = tmp / 'out'
    proc = subprocess.run([str(repo / '.venv' / 'Scripts' / 'python.exe'),
                           str(repo / 'tools' / 'derive_7pocket_derivations.py'),
                           '--tri_zip', str(tri_zip),
                           '--edge_zip', str(edge_zip),
                           '--out_dir', str(outdir)], cwd=repo,
                          capture_output=True, text=True)
    print('return code', proc.returncode)
    print('stdout:\n', proc.stdout)
    print('stderr:\n', proc.stderr)
    print('outdir exists', outdir.exists())
    if outdir.exists():
        print('contents', list(outdir.iterdir()))
