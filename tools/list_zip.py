import zipfile
import sys

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage: python list_zip.py <zipfile>')
        sys.exit(1)
    zname = sys.argv[1]
    with zipfile.ZipFile(zname) as z:
        for name in z.namelist():
            print(name)
