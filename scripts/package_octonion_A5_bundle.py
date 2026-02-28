import zipfile, os

bundle_name = 'TOE_octonion_A5_search_v01_20260227_bundle.zip'
inner_dir = 'TOE_octonion_A5_search_v01_20260227'

if not os.path.exists('octonion_A5_search_results.json'):
    raise FileNotFoundError('octonion_A5_search_results.json not found; run recompute_line_polarization_A5.py --search-octonion first')

with zipfile.ZipFile(bundle_name, 'w', zipfile.ZIP_DEFLATED) as zf:
    zf.write('octonion_A5_search_results.json', f'{inner_dir}/octonion_A5_search_results.json')
    # include the search script for reproducibility
    zf.write('TOE_line_polarization_A5_v01_20260227_bundle/TOE_line_polarization_A5_v01_20260227/recompute_line_polarization_A5.py',
             f'{inner_dir}/recompute_line_polarization_A5.py')
    readme = f"""Octonion A5 search bundle

Contains the JSON results of the A5 subgroup search in the signed-permutation
group, along with the script used to generate them.
"""
    zf.writestr(f'{inner_dir}/README.md', readme)

print('created bundle', bundle_name)