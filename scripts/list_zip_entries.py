import sys, zipfile
zip_path = sys.argv[1]
for e in zipfile.ZipFile(zip_path).namelist():
    if 'edge_to_oriented_rootpair' in e:
        print(e)
