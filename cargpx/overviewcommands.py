from .gpx import Gpx
from .latlon import LatLon, lengthOf, eleProfileOf
from .error import commandError

def summarizeSingleSegment(eInSeg):
    """
    Traverses all points in a route segments, stores the found
    points and calculates the total distance, climb, and descend 
    to the summary list 
    """

    name = eInSeg.oldName().peek()

    eSrcPts = eInSeg.oldPts()

    srcPts=(ePt.peek() for ePt in eSrcPts)
    srcLatLons=(LatLon(pt[0],pt[1]) for pt in srcPts)
    srcLength=lengthOf(list(srcLatLons))

    eSrcEles=(ePt.oldEle() for ePt in eSrcPts)
    srcEles=(eEle.peek() for eEle in eSrcEles if eEle is not None)
    srcClimb,srcDescend=eleProfileOf(list(srcEles))

    return name, len(list(eSrcPts)), srcLength, srcClimb, srcDescend
 
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
        print("## "+ str(totalSegments) + \
            ",Name:" + name + \
            ",Points:" + str(int(numpts)) + \
            ",Distance(m):" + str(int(length)) + \
            ",Climb(m):" + str(int(climb)) + \
            ",Descend(m):"+ str(int(descend)))
                                
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
    eInRoot = Gpx(sInFile)
    if eInRoot is None:
        raise commandError("NOROOT")

    eInSegs = eInRoot.oldRtes()
    return showAllSegmentsOverview(summariseAllSegments(eInSegs))

def commandSingleSegmentDetail(sInFile,iInSeg):
    """
    Traverse a single GPX segment and output a detailed report 
    """

    eInRoot = Gpx(sInFile)
    if eInRoot is None:
        raise commandError("NOROOT")

    eInSegs = eInRoot.oldRtes()
    if (iInSeg>=len(eInSegs)) or (0>iInSeg):
        raise commandError("ILLSEGNUM")

    eInSeg=eInSegs[iInSeg]

    name = eInSeg.oldName().peek()

    eInPts = eInSeg.oldPts()
    if (eInPts is None) or (len(eInPts) == 0): 
        raise commandError("NOPTS")

    inPts=(ePt.peek() for ePt in eInPts)
    inLatLons=[LatLon(pt[0],pt[1]) for pt in inPts]

    eInNames = (ePt.oldName() for ePt in eInPts)
    inNames =(eName.peek() for eName in eInNames)

    print("++ Showing overview for segment %s, with %d points." % \
        (name,len(list(inLatLons))))

    s,e=inLatLons[0],inLatLons[-1]
        
    o=s
    km=0.0
    for (n,p) in zip(inNames,inLatLons):
        km=km+o.rangeTo(p)/1000.0

        print("## %3d,km:%07.3f,fromPrev:%03.0f/%05.3f,FromStart:%03.0f/%06.3f,ToEnd:%03.0f/%06.3f,Name:%s" % \
            (inLatLons.index(p), km, \
                 o.bearingTo(p),o.rangeTo(p)/1000.0, \
                 s.bearingTo(p),s.rangeTo(p)/1000.0, \
                 p.bearingTo(e),p.rangeTo(e)/1000.0,n))
        o=p

    if s.rangeTo(e) < 500:
        print("++ Segment is rountrip.")
    else:
        print("++ Segment is oneway.")
