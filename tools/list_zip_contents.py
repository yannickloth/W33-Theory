import zipfile

for zname in ['INFINITY_NEIGHBOR_CHARGE_TABLE_BUNDLE_v01.zip','W33_DIRECTION_DECOMPOSITION_BUNDLE_v01.zip']:
    print('---', zname)
    with zipfile.ZipFile(zname) as z:
        for name in z.namelist():
            print('   ', name)
