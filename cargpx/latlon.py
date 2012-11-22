#!/usr/bin/env python
'''
Created on Sep 18, 2010

@author: kirus
@purpose: Provides utilities to calc bearing and range
'''

import math
from .primitive import toRad, fromRad
    
class LatLon:
    def __init__(self,lat=0.0,lon=0.0):
        """
        """
        self.lat=lat
        self.lon=lon
        
    def __copy__(self):
        """
        """
        clone=LatLon()
        clone.__dict__.update(self.__dict__)
        return clone
              
    def __str__(self):
        """
        """
        return str(self.lat) + '/' + str(self.lon)

    def __get__(self):
        """
        """
        return self.lat, self.lon

    def bearingTo(self,other):
        """
        Calculates the bearing in degree self to other
        """
        
        if type(other)==type(self):
            lat1,lon1=self.lat,self.lon
            lat2,lon2=other.lat,other.lon
        
            coslat1 = math.cos(toRad(lat1))
            coslat2 = math.cos(toRad(lat2))
            sinlat1 = math.sin(toRad(lat1))
            sinlat2 = math.sin(toRad(lat2))
            sindlon = math.sin(toRad(lon2-lon1))
            cosdlon = math.cos(toRad(lon2-lon1))
    
            tc = math.atan2(sindlon*coslat2, 
                  coslat1*sinlat2-sinlat1*coslat2*cosdlon)
            if tc <= 0.0:
                tc = tc + 2*math.pi
                
            return fromRad(tc)
        return 0.0

    def rangeTo(self,other):
        """
        Calculate the distance in Meter between two geographical
        position given by latitude and longitude (Great Circle
        Navigation)

        Formulas takken from:
          http://www.movable-type.co.uk/scripts/gis-faq-5.1.html
        """
        if type(other)==type(self):       
            lat1,lon1=self.lat,self.lon
            lat2,lon2=other.lat,other.lon

            sindlon = math.sin(toRad(lon2 - lon1)/2)
            sindlat = math.sin(toRad(lat2 - lat1)/2)

            coslat1 = math.cos(toRad(lat1))
            coslat2 = math.cos(toRad(lat2))

            a = sindlat*sindlat + coslat1*coslat2 * sindlon*sindlon
            c = 2 * math.asin(min(1,math.sqrt(a)))

            # Radius dependent on latitude only
            R = 6378000.0 - 21000.0 * math.sin(toRad(lat1 +lat2)/2) 

            return R * c
        return 0.0


def lengthOf(lLatlon):
    """
    Returns length of point list in meters
    """
    length = 0.0
    for ll in range(1,len(lLatlon)):
        length += lLatlon[ll].rangeTo(lLatlon[ll-1])
    return length

def eleProfileOf(lEle):
    """
    Returns climb and descend of the elevations in meters
    """
    climb, descend = 0.0, 0.0 
    for e in range(1,len(lEle)):
        if (lEle[e]<0.5): continue
        deltaEle=lEle[e]-lEle[e-1]
        if deltaEle>0.0:
            climb+=deltaEle
        if deltaEle<0.0:    
            descend-=deltaEle

    return climb, descend

NULL_BOUNDS = (90.0,180.0,-90.0,-180.0)
def minmaxOf(lLatlon,bounds=NULL_BOUNDS):
    """
    Returns the min, max bounds for the points 
    """
    minlat,minlon,maxlat,maxlon=bounds
    for ll in lLatlon:
        if ll.lat<minlat:minlat=ll.lat
        if ll.lon<minlon:minlon=ll.lon
        if ll.lat>maxlat:maxlat=ll.lat
        if ll.lon>maxlon:maxlon=ll.lon
    return minlat,minlon,maxlat,maxlon

def isRoundTrip(lLatLon):
    """
    Returns True if the segment is a round trip (2%)
    """
    return lengthOf([lLatLon[0],lLatLon[-1]]) < (lengthOf(lLatLon)/50.0)

def closestToPoint(lLatLon,pLatLon):
    """
    Returns the closest point index with bearing and range in meters
    """
    lRng = [pLatLon.rangeTo(ll) for ll in lLatLon]
    iP = lRng.index(min(lRng))
    return iP,pLatLon.bearingTo(lLatLon[iP]),pLatLon.rangeTo(lLatLon[iP])

def closestToRoute(lLatLon1,lLatLon2):
    """
    Returns the closest point indices with bearing and range in meters
    """
    lClosest = [closestToPoint(lLatLon1,ll) for ll in lLatLon2]
    lRng = [p[2] for p in lClosest]
    iP = lRng.index(min(lRng))
    return iP,lClosest[iP][0],lClosest[iP][1],lClosest[iP][2]
