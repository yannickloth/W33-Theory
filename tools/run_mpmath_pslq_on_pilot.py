#!/usr/bin/env python3
import json
import math

from mpmath import mp

mp.dps = 80
p = "artifacts/pslq_cyclotomic_pilot.json"
j = json.load(open(p))
res = j["results"]["g1_g1_g2"]["analysis"]
ows = [complex(s) for s in res["overlaps"]]
re_list = [float(c.real) for c in nows]
neg_sqrt3_im_list = [float(-math.sqrt(3) * c.imag) for c in nows]
vec = re_list + neg_sqrt3_im_list
print("vec (len={}):".format(len(vec)), vec)
mp_vec = [mp.mpf(str(v)) for v in vec]
rel = mp.pslq(mp_vec)
print("mpmath.pslq ->", rel)
