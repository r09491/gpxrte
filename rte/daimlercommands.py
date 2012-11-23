STARTER='''<gpx:gpx creator="gpxdaimlercommands.py - http://www.josef-heid.de" version="1.1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:gpx="http://www.topografix.com/GPX/1/1" xsi:schemaLocation="http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd" xmlns:gpxd="http://www.daimler.com/DaimlerGPXExtensions/V2.4"><gpx:rte><gpx:name>DaimlerStarter</gpx:name><gpx:extensions><gpxd:RteExtension><gpxd:RouteIconId IconId="17"></gpxd:RouteIconId><gpxd:RouteDrivingDirection UsedInDirection="true"></gpxd:RouteDrivingDirection><gpxd:RouteLength Unit="kilometer" Value="0.0"></gpxd:RouteLength></gpxd:RteExtension></gpx:extensions></gpx:rte></gpx:gpx>'''

import lxml.etree as etree

from .error import *
from .latlon import *

from segmentcommands import writeGpxFile, getLatLon

def isRouteFileNameOk(sInRouteFileName):
    import os, time
    try:
        sBasename = os.path.basename(sInRouteFileName)
        tTime=time.strptime(sBasename,"Route_%Y%m%d_%H%M%S.gpx")
        return True
    except ValueError:
        return False

def getRouteFileName(sInRouteFileName):
    if isRouteFileNameOk(sInRouteFileName):
        return (sInRouteFileName)
    else:
        import datetime
        return datetime.datetime.now().strftime("Route_%Y%m%d_%H%M%S.gpx")

def convertToRoute(sInFile,iInSeg,sOutFile):
    """
    From the given RTE segment produces an output which the COMAND
    Online may use as a route. This is reverse engineered.

    The current understanding is:
    
    (1) The GPX file may contain only one RTE segment
    (2) All tags are to be qualified with namespace
    (3) Above XML header to be used
    (4) RTEPTs have lat/lon only
    (5) The file name is prefixed with 'Route'. It is extended with the 
        time the reording stopped.
    (7) The length of the route may be specified in the extension part.
        If not provided the screen displays blanks in the route listing.
    """

    # Create the root element of a new GPX structure. This shall be
    # outputed later to the GPX file.
    eOutGpx = etree.fromstring(STARTER)
    if eOutGpx is None:
        raise commandError("NOROOT")
    outNS = '{'+eOutGpx.nsmap['gpx']+'}%s'
    extNS = '{'+eOutGpx.nsmap['gpxd']+'}%s'

    eOutRtes= eOutGpx.findall(outNS % 'rte')
    if eOutRtes is None: 
        raise commandError("NOSEG")

    eInGpx = etree.parse(sInFile).getroot()
    if eInGpx is None:
        raise commandError("NOROOT")
    inNS = '{'+eInGpx.nsmap[None]+'}%s'

    eInRtes= eInGpx.findall(inNS % 'rte')
    if eInRtes is None: 
        raise commandError("NOSEG")
    if (iInSeg < 0) or (iInSeg >= len(eInRtes)):
        raise commandError("ILLSEGNUM")

    eOutRtes= eOutGpx.findall(outNS % 'rte')
    if eOutRtes is None: 
        raise commandError("NOSEG")

    eInRte,eOutRte=eInRtes[iInSeg],eOutRtes[0]

    eInRteName = eInRte.find(inNS % 'name')
    eOutRteName = eOutRte.find(outNS % 'name')
    eOutRteName.text=eInRteName.text

    eInRtePts = eInRte.findall(inNS % 'rtept')
    eOutRtePts = [etree.SubElement(eOutRte, outNS % 'rtept', \
         lat=ePt.get('lat'),lon=ePt.get('lon')) for ePt in eInRtePts] 
    lLatLons=[getLatLon(ePt) for ePt in eOutRtePts]


    sRteLength='%s/%s/%s' % (outNS % 'extensions', \
                       extNS % 'RteExtension',extNS % 'RouteLength')
    eOutRteLength = eOutRtes[0].find(sRteLength)
    eOutRteLength.set('Unit','kilometer')
    eOutRteLength.set('Value', '%.2f' % (lengthOf(lLatLons)/1000.0))

    if sOutFile is None:
        sOutFile =getRouteFileName(sInRouteFileName)

    writeGpxFile(eOutGpx,lLatLons,sOutFile)
    return len(eOutGpx.findall(outNS % 'rte'))
