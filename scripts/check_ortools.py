#!/usr/bin/env python3
import time
print('start')
import ortools
print('ortools module loaded', getattr(ortools, '__version__', 'no-version'))
from ortools.sat.python import cp_model
print('cp_model imported')
print('done')
