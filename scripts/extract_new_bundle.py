import zipfile
zf=zipfile.ZipFile('TOE_K27_HEISENBERG_S3_v01_20260228_bundle.zip')
zf.extractall('TOE_K27_HEISENBERG_S3')
print('extracted new bundle')