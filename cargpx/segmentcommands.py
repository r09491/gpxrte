import os

import lxml.etree as etree

from .gpx import Gpx, Rte
from .time import getNowZulu
from .latlon import LatLon, isRoundTrip, minmaxOf, NULL_BOUNDS
from .schemes import gpsbabel
from .error import commandError

        
def getCoords(sCity):
    """
    """
    from geopy import geocoders
    geoNames=geocoders.GeoNames()
    return geoNames.geocode(sCity,exactly_one=False)


def getLatLon(ePt):
    return LatLon(float(ePt.get('lat')),float(ePt.get('lon')))


def writeGpxFile(eGpx,lLatLon,sOutFile):
    """
    """

    if eGpx is None:
        raise commandError("NOROOT")
    NS = '//{'+eGpx.nsmap[None]+'}%s'

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
        eTime[0].text=getNowZulu()

    eGpx.set('creator', 'gpxrte - http://www.josef-heid.de')        
    etree.ElementTree(eGpx).write(sOutFile,encoding='utf-8',xml_declaration=True,pretty_print=True)


def modifyGpxFile(sFileName, iSegmentNumber, applyModifier, args):
    """
    """

    eAnyroot = Gpx(sFileName)
    if eAnyroot is None:
        raise commandError("NOROOT")

    eAnysegs = eAnyroot.oldRtes()
    if eAnysegs is None: 
        raise commandError("NOSEG")

    if (iSegmentNumber < 0) or (iSegmentNumber >= len(eAnysegs)):
        raise commandError("ILLSEGMENT")

    eAnyseg=eAnysegs[iSegmentNumber]
    applyModifier(eAnyseg, args)
    eAnyroot.write(sFileName)


def commandName(sFileName, iSegmentNumber, sName):
    """
    """

    def modifyName(eSeg, sName):
        """
        Get the old RTE name element. Its content shall become 
        the new segment name.
        """

        eName = eSeg.oldName()
        if eName is None: 
            raise Error("NONAME")
        eName.poke(sName)

    modifyGpxFile(sFileName, iSegmentNumber, modifyName, sName)


def writeSegment(eInSeg, iBeg=None, iEnd=None, sName=None, sExt=".gpx"):
    """
    """
    eInPts = eInSeg.oldPts()
    if eInPts is None:
        raise commandError("NOPTS")

    if iBeg is None: iBeg = 0
    if iEnd is None: iEnd = len(eInPts)

    inPts=(ePt.peek() for ePt in eInPts)
    inLatLons=[LatLon(pt[0],pt[1]) for pt in inPts]
 
    from .schemes import gpsbabel
    eOutRoot = gpsbabel()
    eOutSeg = eOutRoot.oldRtes()[0] 
    eOutSeg.clonePts(eInPts[iBeg:iEnd])

    eInName = eInSeg.oldName()
    eOutName = eOutSeg.oldName()
    eOutName.clone(eInName)

    eOutMetadata = eOutRoot.oldMetadata()
    eOutMetadataBounds = eOutMetadata.oldBounds()
    eOutMetadataBounds.poke(minmaxOf(inLatLons[iBeg:iEnd]))
    eOutMetadataTime = eOutMetadata.oldTime()
    eOutMetadataTime.poke(getNowZulu())

    if sName is None:
        sName = eInName.peek()
    eOutRoot.write(sName + sExt)
    

def commandPullAtomic(sInFile, iInSeg, sOutFile):
    """
    Returns GPX file with the complete segment
    """

    eGpx = etree.parse(sInFile).getroot()
    if eGpx is None:
        raise commandError("NOROOT")
    NS = '{'+eGpx.nsmap[None]+'}%s'

    eRtes= eGpx.findall(NS % 'rte')
    if eRtes is None: 
        raise commandError("NOSEG")
    if (iInSeg < 0) or (iInSeg >= len(eRtes)):
        raise commandError("ILLSEGNUM")

    # Keep the pull segemnt only
    for eRte in eRtes[:iInSeg]: eGpx.remove(eRte)
    for eRte in eRtes[iInSeg+1:]: eGpx.remove(eRte)

    eRtePts = eRtes[iInSeg].findall(NS % 'rtept')
    lLatLons=[getLatLon(eRtePt) for eRtePt in eRtePts]

    if sOutFile is None:
        eRteName = eRtes[iInSeg].find(NS % 'name')
        if eRteName is None:
            sOutFile = "%s_%03d_atomic.gpx" % (os.path.splitext(sInFile)[0], iInSeg)
        else:
            eRteName = eRtes[iInSeg].find(NS % 'name')
            sOutFile = "%s.gpx" % (eRteName.text.strip())

    writeGpxFile(eGpx,lLatLons,sOutFile)
    return len(eGpx.findall(NS % 'rte'))


def commandPullByCoord(sInFile,iInSegment,iInType,sOutFile, \
                          fBeginLat,fBeginLon,fEndLat,fEndLon):
    """
    Returns a GPX file with a single segment with the start
    point and end point closest to the input requests.
    """

    eInRoot = Gpx(sInFile)
    if eInRoot is None:
        raise commandError("NOROOT")

    eInSegs = eInRoot.oldRtes()
    if eInSegs is None: 
        raise commandError("NOSEG")
    if (iInSegment < 0) or (iInSegment >= len(eInSegs)):
        raise commandError("ILLSEGMENT")

    eInSeg=eInSegs[iInSegment]
    eInPts = eInSeg.oldPts()
    if eInPts is None: 
        raise commandError("NOPTS")

    inPts=(ePt.peek() for ePt in eInPts)
    inLatLons=[LatLon(pt[0],pt[1]) for pt in inPts]

    iBegin=0
    if (fBeginLat is not None) and (fBeginLon is not None):
        # Associate with closest list item
        beginLatLon=LatLon(fBeginLat,fBeginLon)
        beginRangeTo=[beginLatLon.rangeTo(ll) for ll in inLatLons]
        iBegin=beginRangeTo.index(min(beginRangeTo))
    else:
        # No change for the beginning of the list 
        fBeginLat,fBeginLon= inLatLons[0].lat,inLatLons[0].lon

    iEnd=len(inLatLons)-1
    if (fEndLat is not None) and (fEndLon is not None):
        # Associate with closest list item
        endLatLon=LatLon(fEndLat,fEndLon)
        endRangeTo=[endLatLon.rangeTo(ll) for ll in inLatLons]
        iEnd=endRangeTo.index(min(endRangeTo))
    else:
        # No change for the ending of the list
        fEndLat,fEndLon= inLatLons[-1].lat,inLatLons[-1].lon
    
    if iBegin >= iEnd:
        raise commandError("ILLWALKING")

    pre, ext = os.path.splitext(os.path.basename(sOutFile))

    writeSegment(eInSeg,iBegin,iEnd+1,sName=("%s__%04d_%04d__coord.gpx" % \
                                                 (pre,iBegin,iEnd)),sExt=ext)
    return 1


def commandPullByDistance(sInFile,iSegment,sOutFile,fMeter,):
    """
    Splits a long GPX route into several segments not exceeding the
    requested distance. The segments may be stored in individual files
    or a single file.
    """

    eInRoot = Gpx(sInFile)
    if eInRoot is None:
        raise commandError("NOROOT")

    eInSegs = eInRoot.oldRtes()
    if eInSegs is None: 
        raise commandError("NOSEG")
    if (iSegment < 0) or (iSegment >= len(eInSegs)):
        raise commandError("ILLSEGMENT")

    eInSeg=eInSegs[iSegment]
    eInPts = eInSeg.oldPts()
    if eInPts is None: 
        raise commandError("NOPTS")

    inPts=(ePt.peek() for ePt in eInPts)
    inLatLons=[LatLon(pt[0],pt[1]) for pt in inPts]

    pre, ext = os.path.splitext(os.path.basename(sOutFile))
    
    iBegin,iCount,fLength = 0, 0, 0.0
    for iEnd in range(1,len(inLatLons)):
        fLength += inLatLons[iEnd].rangeTo(inLatLons[iEnd-1])
        if fLength < fMeter: continue
        writeSegment(eInSeg,iBegin,iEnd,sName=("%s__%03d__distance" % \
                                                   (pre,iCount)),sExt=ext)
        iBegin,iCount,fLength = \
            iEnd-1,iCount+1,inLatLons[iEnd].rangeTo(inLatLons[iEnd-1])

    return iCount


def commandPush(sInFile,iInSegment,sOutFile):
    """
    Appends a GPX file to another GPX file with propably multiple segments
    """

    eInRoot = Gpx(sInFile)
    if eInRoot is None:
        raise commandError("NOROOT")

    eInSegs = eInRoot.oldRtes()
    if eInSegs is None: 
        raise commandError("NOSEG")

    eOutRoot = Gpx(sOutFile) if os.path.isfile(sOutFile) else gpsbabel()
    if eOutRoot is None:
        raise commandError("NOROOT")

    if iInSegment is None:
        # Push everything
        eOutRoot.cloneRtes(eInSegs)
    elif (iInSegment >= 0) and (iInSegment < len(eInSegs)):
        # Push only the selected
        eOutRoot.cloneRtes([eInSegs[iInSegment]])
    else:
        raise commandError("ILLSEGNUM")

    return eOutRoot.write(sOutFile)


def commandPurge(sInFile,iInSegment):
    """
    Removes the specified segment from the GPX file
    """

    eInRoot = Gpx(sInFile)
    if eInRoot is None:
        raise commandError("NOROOT")

    eInSegs = eInRoot.oldRtes()
    if eInSegs is None: 
        raise commandError("NOSEG")

    if (iInSegment < 0) or (iInSegment >= len(eInSegs)):
        raise commandError("ILLSEGNUM")

    eOutRoot = gpsbabel()
    if eOutRoot is None:
        raise commandError("NOROOT")

    if (iInSegment < 0) or (iInSegment >= len(eInSegs)):
        raise commandError("ILLSEGNUM")

    # The element to be delted is not cloned
    eOutRoot.cloneRtes(eInSegs[:iInSegment])
    eOutRoot.cloneRtes(eInSegs[iInSegment+1:])
    return eOutRoot.write(sInFile)


def commandFlat(sInFile,sOutFile):
    """
    Flattens all RTE segements into singel segment by appending
    all points to the RTE segment
    """

    eGpx = etree.parse(sInFile).getroot()
    if eGpx is None:
        raise commandError("NOROOT")
    NS = '{'+eGpx.nsmap[None]+'}%s'

    eRtes= eGpx.findall(NS % 'rte')
    if eRtes is None: 
        raise commandError("NOSEG")

    for eRte in eRtes[1:]:
        eRtePts = eRte.findall(NS % 'rtept')
        if eRtePts is not None: eRtes[0].extend(eRtePts)
        eGpx.remove(eRte)

    eRteName = eRtes[0].find(NS % 'name')
    eRteName.text = os.path.splitext(os.path.basename(sOutFile))[0]

    lLatLons=[getLatLon(ePt) for ePt in eRtePts]
    writeGpxFile(eGpx,lLatLons,sOutFile)

    return len(etree.ETXPath(NS % 'rte')(eGpx))


def commandSwapIndex(sInFile,iInSeg,iInPoint,sOutFile):
    """
    Swaps the segement at the indexed point. The point at 
    the index becomes the beginning of the RTE segment.
    """

    eGpx = etree.parse(sInFile).getroot()
    if eGpx is None:
        raise commandError("NOROOT")
    NS = '{'+eGpx.nsmap[None]+'}%s'

    eRtes= eGpx.findall(NS % 'rte')
    if eRtes is None: 
        raise commandError("NOSEG")
    if (iInSeg < 0) or (iInSeg >= len(eRtes)):
        raise commandError("ILLSEGNUM")

    eRtePts = eRtes[iInSeg].findall(NS % 'rtept')
    if eRtePts is None: 
        raise commandError("NOPTS")
    if (iInPoint < 0) or (iInPoint >= len(eRtePts)):
        raise commandError("ILLPNTNUM")

    lLatLons=[getLatLon(ePt) for ePt in eRtePts]
    if not isRoundTrip(lLatLons):
        raise commandError("NORTRIP")

    # Move to tail until the required point is the firrst
    for i in range(iInPoint): eRtes[0].append(eRtePts[i])

    writeGpxFile(eGpx,lLatLons,sOutFile)
    return len(eRtes)
