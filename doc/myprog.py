#!/usr/bin/env python

import math, sys

"""
This is a small script containing a simple function.
"""

def myfunc(x):
    result = None
    if isinstance(x, (list, tuple)):
        result = []
        for i in x:
            result.append(math.fabs(i))
    elif isinstance(x, (int, float)):
        result = math.fabs(x)
    return result

print myfunc(-1.0)
print myfunc((2, -3.))
try:
    result = myfunc([eval(x) for x in (sys.argv[1:])])
    if result: print result
except:
    pass
                
