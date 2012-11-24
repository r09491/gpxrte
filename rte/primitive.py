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

def nDeg(deg):
    while deg>360.0:deg-=360.0
    while deg<0.0:deg+=360.0
    return deg

def iDeg(deg):
    return nDeg(deg+180.0)
