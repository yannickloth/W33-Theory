import zipfile, os

bundle_name = 'TOE_pocket20_K5_edgepair_cover_v01_20260227_bundle.zip'
inner_dir = 'TOE_pocket20_K5_edgepair_cover_v01_20260227'

files = [
    'orbit10_lines_k5_structure.json',
    'srg_vertices20_to_k5edge.json',
    'pocket20_edgepair_cover.csv',
    'edgepair_to_pockets.json',
    'summary.json',
]

for f in files:
    if not os.path.exists(f):
        raise FileNotFoundError(f"missing output file {f}; run compute_pocket20_k5_edgepair_cover.py first")

with zipfile.ZipFile(bundle_name, 'w', zipfile.ZIP_DEFLATED) as zf:
    for f in files:
        zf.write(f, f'{inner_dir}/{f}')
    readme = """Pocket20 K5 edgepair cover bundle

Contains analysis of W33 orbit10 lines as K5 edges and 20-centered pocket
deck structure.
"""
    zf.writestr(f'{inner_dir}/README.md', readme)

print('created bundle', bundle_name)