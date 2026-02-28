import zipfile, sys
zf=zipfile.ZipFile(sys.argv[1])
for e in zf.namelist():
    print(e)