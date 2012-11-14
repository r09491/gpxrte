'''
Created on Sep 18, 2010

@author: kirus
@purpose: Provide a set of primitive conversion routines
'''

import math

def toRad(deg):
    return deg * math.pi / 180.0

def fromRad(rad):
    return rad * 180.0 / math.pi
