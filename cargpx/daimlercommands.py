STARTER='''<gpx:gpx creator="gpxdaimlercommands.py - http://www.josef-heid.de" version="1.1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:gpx="http://www.topografix.com/GPX/1/1" xsi:schemaLocation="http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd" xmlns:gpxd="http://www.daimler.com/DaimlerGPXExtensions/V2.4"><gpx:rte><gpx:name>DaimlerStarter</gpx:name><gpx:extensions><gpxd:RteExtension><gpxd:RouteIconId IconId="17"></gpxd:RouteIconId><gpxd:RouteDrivingDirection UsedInDirection="true"></gpxd:RouteDrivingDirection><gpxd:RouteLength Unit="kilometer" Value="0.0"></gpxd:RouteLength></gpxd:RteExtension></gpx:extensions></gpx:rte></gpx:gpx>'''

from . import gpx
from . import latlon

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

def convertToRoute(eInSeg,sInRouteFileName):
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
    eOutRoot = gpx.Daimler(gpxstring=STARTER)
    # Get the old RTE segment element as parsed from STARTER.
    eOutSeg = eOutRoot.oldRtes()[0]

    # Get the old RTE segment name elementfrom the source. Its content 
    # shall become the new segment name.
    eSrcName = eInSeg.oldName()
    # Get the default RTE segment name element as pared from STARTER. 
    # Its content shall be overridden.
    eOutName = eOutSeg.oldName()
    # Keep the segment name
    eOutName.clone(eSrcName)

    # Get the point elements from the provided route segment
    eSrcPts = eInSeg.oldPts()
    # The output segment does not contain any point elements yet.
    # Generate the point elements to receive the points later. They
    # are subelements of the segment element
    eOutPts = eOutSeg.newPts(len(eSrcPts))
    # The source element content is cloned to the point elements
    # of the output segment.
    for o, s in zip(eOutPts, eSrcPts): o.clone(s)

    #Calculate the length of the route
    outPts=(ePt.peek() for ePt in eOutPts)
    outLatLons=(latlon.LatLon(pt[0],pt[1]) for pt in outPts)
    rteLength=latlon.lengthOf(list(outLatLons))

    # Get the daimler extension from the STARTER and store the length
    eOutExtensions = eOutSeg.oldExtensions()
    eOutRteExtension = eOutExtensions.oldRteExtension()
    eOutRteLength = eOutRteExtension.oldRteLength()
    eOutRteLength.poke(('kilometer', "%.2f" % (rteLength/1000.0)))

    # Write the tree to the file (Daimler naming conventions)
    eOutRoot.write(getRouteFileName(sInRouteFileName))
 
    return 0
