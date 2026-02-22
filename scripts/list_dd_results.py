import datetime
import glob
import os

files = glob.glob("checks/PART_CVII_dd_shrink_result_*.json")
for f in sorted(files):
    st = os.stat(f)
    print(f, "mtime=", datetime.datetime.fromtimestamp(st.st_mtime))
