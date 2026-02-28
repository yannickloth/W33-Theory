import zipfile, json, os, subprocess, sys

# always recreate tri.zip with required prefix
prefix = 'TOE_E6pair_SRG_triangle_decomp_v01_20260227'
base = os.path.join(prefix + '_bundle', prefix)
if os.path.exists('tri.zip'):
    os.remove('tri.zip')
with zipfile.ZipFile('tri.zip','w',zipfile.ZIP_DEFLATED) as z:
    for root,dirs,files in os.walk(base):
        for f in files:
            path=os.path.join(root,f)
            arcname=os.path.relpath(path, os.path.dirname(base))
            z.write(path, arcname)
print('created tri.zip with prefix')

# create edge zip from artifacts
edge_zip='edge_real.zip'
with zipfile.ZipFile(edge_zip,'w',zipfile.ZIP_DEFLATED) as zf:
    zf.write('artifacts/edge_to_rootpair_triple.json',
             'TOE_edge_to_oriented_rootpairs_v01_20260227/edge_to_oriented_rootpair_triple.json')
print('created', edge_zip)

# run mapping script by importing module (avoids subprocess issues)
out='edge_orient_map_real.json'
import sys
# prepare argv as if called from command line
sys.argv = ['map_edges_to_octonion_orients.py', '--tri_zip', 'tri.zip',
            '--edge_zip', edge_zip, '--out', out]
import importlib
from tools import map_edges_to_octonion_orients as meo
importlib.reload(meo)
try:
    meo.main()
    d = json.load(open(out))
    print('mapped', len(d['edge_to_orient']), 'edges')
    print('first 10', d['edge_to_orient'][:10])
except Exception as e:
    print('mapping failed with', e)
