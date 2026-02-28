import zipfile, os

bundle_name = 'TOE_edge_orient_map_v01_20260227_bundle.zip'
inner_dir = 'TOE_edge_orient_map_v01_20260227'

if not os.path.exists('edge_orient_map_real.json'):
    raise FileNotFoundError('edge_orient_map_real.json not found; run mapping first')

with zipfile.ZipFile(bundle_name, 'w', zipfile.ZIP_DEFLATED) as zf:
    zf.write('edge_orient_map_real.json', f'{inner_dir}/edge_orient_map_real.json')
    # add a minimal README
    readme = f"""Edge orientation mapping bundle

Contains real orientation mapping produced on 2026-02-27.
"""
    zf.writestr(f'{inner_dir}/README.md', readme)

print('created bundle', bundle_name)
