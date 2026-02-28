import subprocess, os, sys

def test_pack_binary_bundle(tmp_path):
    # remove existing bundle if any
    bundle = 'TOE_binary_icosahedral_2A5_v01_20260227_bundle.zip'
    if os.path.exists(bundle):
        os.remove(bundle)
    # ensure required inputs exist by running recompute script (it will recreate them)
    subprocess.run([sys.executable, os.path.join('scripts','recompute_binary_icosahedral_2A5.py')], check=True)
    # run packaging script
    subprocess.run([sys.executable, os.path.join('scripts','package_binary_icosahedral_2A5_bundle.py')], check=True)
    assert os.path.isfile(bundle)
