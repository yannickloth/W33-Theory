import zipfile, sys
zip_path = sys.argv[1]
with zipfile.ZipFile(zip_path) as z:
    for name in z.namelist():
        if 'edge_to_oriented_rootpair' in name:
            print(name)
            data = z.read(name).decode()
            print('---begin---')
            print(data[:1000])
            print('---end---')
