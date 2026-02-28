#!/usr/bin/env python3
"""Package the core triality-bridge artifacts into a zip bundle."""
import zipfile, os

files=[
    'data/w33_triality_bridge.json',
    'block_heis_coords.json',
    'block_heis_assign.json',
    'heis6_translation_pairs.json',
    'spa_triality_summary.json',
]
name='TOE_triality_bridge_bundle_v01.zip'
with zipfile.ZipFile(name,'w',compression=zipfile.ZIP_DEFLATED) as zf:
    for f in files:
        if os.path.exists(f):
            zf.write(f)
            print('added',f)
        else:
            print('missing',f)
print('bundle created',name)
