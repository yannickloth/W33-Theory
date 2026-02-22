#!/usr/bin/env python3
import sys

import numpy as np

p = sys.argv[1]
arr = np.load(p)
print("files:", arr.files)
for k in arr.files:
    a = arr[k]
    print(k, a.shape, a.dtype)
