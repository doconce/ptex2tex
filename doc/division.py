#!/usr/bin/env python
import sys

def division(a, b):
    try:
        return a/float(b)
    except ZeroDivisionError:
        print 'cannot divide by zero'
        return None

if __name__ == '__main__':
    print division(2, 0)
