
from .error import *
from .latlon import *
from .supporters import *

import lxml.etree as etree

def getLatLon(ePt):
    return LatLon(float(ePt.get('lat')),float(ePt.get('lon')))


def summarizeSingleSegment(eRte):
    """
    Traverses all points in a route segments, stores the found
    points and calculates the total distance, climb, and descend 
    to the summary list 
    """
    if not etree.iselement(eRte):
        raise commandError("NOELE")
    NS = getNS(eRte)

    eRteName = eRte.find(NS % 'name')
    if eRteName is None: 
        raise commandError("NONAME")
    rteName = eRteName.text

    eRtePts = eRte.findall(NS % 'rtept')
    if eRtePts is None: 
        raise commandError("NOPTS")
    lLatLons=[getLatLon(eRtePt) for eRtePt in eRtePts]

    eRtePtNames = (eRtePt.find(NS % 'name') for eRtePt in eRtePts)
    if eRtePtNames is None: 
        raise commandError("NONAME")
    lNames =(eName.text for eName in eRtePtNames)

    eRtePtEles = (eRtePt.find(NS % 'ele') for eRtePt in eRtePts)
    lEles =(float(eEle.text) for eEle in eRtePtEles if eEle is not None)

    srcLength=lengthOf(list(lLatLons))
    srcClimb,srcDescend=eleProfileOf(list(lEles))

    return rteName, len(list(lLatLons)), srcLength, srcClimb, srcDescend
 

def summariseAllSegments(eInSegs):
    """
    Traverse all routes in a gpx file and append each result
    to the summary list 
    """
    return [summarizeSingleSegment(seg) for seg in eInSegs]

def showAllSegmentsOverview(summary):
    """
    Displays an high level overview for all segments in the tree  
    """

    print("++ Total number of found segments: %d" % (len(summary)))

    totalSegments=0
    totalNumpts=0
    totalRange=0.0
    totalClimb=0.0
    totalDescend=0.0
    for (name, numpts, length, climb, descend) in summary:            
        print("## "+ "%3d" % totalSegments + \
            ",Points:" + str(int(numpts)) + \
            ",Distance(m):" + str(int(length)) + \
            ",Climb(m):" + str(int(climb)) + \
            ",Descend(m):"+ str(int(descend)) + \
            ",Name:" + name)
                                
        totalSegments+=1
        totalNumpts+=numpts
        totalRange+=length
        totalClimb+=climb
        totalDescend+=descend

    print("++ Total" + ":Points:" + str(int(totalNumpts)) + \
        ",Distance(m):" + str(int(totalRange)) + \
        ",Climb(m):" + str(int(totalClimb)) + \
        ",Descend(m):"+ str(int(totalDescend)))

    return 0


def commandAllSegmentsOverview(sInFile):
    """
    Traverse the provide GPX segments and outputs a summary 
    """
    eGpx = etree.parse(sInFile).getroot()
    if eGpx is None:
        raise commandError("NOROOT")
    NS = getNS(eGpx)

    eRtes= etree.ETXPath(NS % 'rte')(eGpx)
    if eRtes is None: 
        raise commandError("NOSEG")
    return showAllSegmentsOverview(summariseAllSegments(eRtes))


def commandSingleSegmentDetail(sInFile,iInSeg):
    """
    Traverse a single GPX segment and output a detailed report 
    """

    eGpx = etree.parse(sInFile).getroot()
    if eGpx is None:
        raise commandError("NOROOT")
    NS = getNS(eGpx)

    eRtes= eGpx.findall(NS % 'rte')
    if eRtes is None: 
        raise commandError("NOSEG")
    if (iInSeg < 0) or (iInSeg >= len(eRtes)):
        raise commandError("ILLSEGNUM")

    eRte=eRtes[iInSeg]

    eRteName = eRte.find(NS % 'name')
    if eRteName is None: 
        raise commandError("NONAME")
    rteName = eRteName.text

    eRtePts = eRte.findall(NS % 'rtept')
    if eRtePts is None: 
        raise commandError("NOPTS")
    lLatLons=[getLatLon(eRtePt) for eRtePt in eRtePts]

    eRtePtNames = (eRtePt.find(NS % 'name') for eRtePt in eRtePts)
    if eRtePtNames is None: 
        raise commandError("NONAME")
    lNames =(eName.text for eName in eRtePtNames)

    print("++ Showing overview for segment %s, with %d points." % \
        (rteName,len(list(lLatLons))))

    s,e=lLatLons[0],lLatLons[-1]
        
    o=s
    km=0.0
    for (n,p) in zip(lNames,lLatLons):
        km=km+o.rangeTo(p)/1000.0

        print("## %3d,km:%07.3f,fromPrev:%03.0f/%05.3f,FromStart:%03.0f/%06.3f,ToEnd:%03.0f/%06.3f,Name:%s" % \
            (lLatLons.index(p), km, \
                 o.bearingTo(p),o.rangeTo(p)/1000.0, \
                 s.bearingTo(p),s.rangeTo(p)/1000.0, \
                 p.bearingTo(e),p.rangeTo(e)/1000.0,n))
        o=p

    if s.rangeTo(e)/1000.0 < 0.05*km:
        print("++ Segment is rountrip.")
    else:
        print("++ Segment is oneway.")
