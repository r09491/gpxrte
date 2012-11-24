from .error import *
from .latlon import *
from .time import *

import lxml.etree as etree

def getNS(e):
    if not etree.iselement(e):
        raise commandError("NOELE")
    try:
        return '{'+e.nsmap[None]+'}%s'
    except KeyError:
        return '{'+e.nsmap['gpx']+'}%s'
    

def getLatLon(ePt):
    if not etree.iselement(ePt):
        raise commandError("NOELE")
    return LatLon(float(ePt.get('lat')),float(ePt.get('lon')))


def writeGpxFile(eGpx,lLatLon,sOutFile):
    """
    """

    if not etree.iselement(eGpx):
        raise commandError("NOELE")
    NS = getNS(eGpx)

    if not lLatLon is None:
        eBounds= etree.ETXPath(NS % 'bounds')(eGpx)
        if eBounds:
            minlat,minlon,maxlat,maxlon = \
                minmaxOf(lLatLon,NULL_BOUNDS)
            eBounds[0].set('minlat',str(minlat))
            eBounds[0].set('minlon',str(minlon))
            eBounds[0].set('maxlat',str(maxlat))
            eBounds[0].set('maxlon',str(maxlon))

    eTime= etree.ETXPath(NS % 'time')(eGpx)
    if eTime: 
        eTime[0].text=getNowUtc()

    eGpx.set('creator', 'gpxrte - http://www.josef-heid.de')        
    etree.ElementTree(eGpx).write(sOutFile,encoding='utf-8', \
                                      xml_declaration=True,pretty_print=True)
