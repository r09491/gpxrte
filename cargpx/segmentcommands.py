import os

from .gpx import Gpx, Rte
from .latlon import LatLon, minmaxOf, NULL_BOUNDS
from .schemes import gpsbabel
from .error import commandError

        
def getCoords(sCity):
    """
    """
    from geopy import geocoders
    geoNames=geocoders.GeoNames()
    return geoNames.geocode(sCity,exactly_one=False)


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
    

def commandPullAtomic(sInfile, iSegment):
    """
    Returns GPX file with the complete RTE segment
    """

    eInRoot = Gpx(sInfile)
    if eInRoot is None:
        raise commandError("NOROOT")

    eInSegs = eInRoot.oldRtes()
    if eInSegs is None: 
        raise commandError("NOSEG")

    if iSegment is None:
        for eSeg in eInSegs: writeSegment (eSeg, sExt="__atomic.gpx")
        iSegWritten = len(eInSegs)
    else:
        if (iSegment < 0) or (iSegment >= len(eInSegs)):
            raise commandError("ILLSEGNUM")
        writeSegment (eInSegs[iSegment], sExt="__atomic.gpx")
        iSegWritten = 1

    return iSegWritten


def commandPullByCoord(sInFile,iInSegment,iInType,sOutFile, \
                          fBeginLat,fBeginLon,fEndLat,fEndLon):
    """
    Returns a GPX file with a single RTE segment with the
    start point and end point closest to the input requests.
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
    Splits a long GPX route into several RTEs segments not exceeding the
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


def commandPush(sInfile,iInSegment,sOutfile):
    """
    Appends a GPX file to another GPX file with propably multiple segments
    """

    eInRoot = Gpx(sInfile)
    if eInRoot is None:
        raise commandError("NOROOT")

    eInSegs = eInRoot.oldRtes()
    if eInSegs is None: 
        raise commandError("NOSEG")

    eOutRoot = Gpx(sOutfile) if os.path.isfile(sOutfile) else gpsbabel()
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

    return eOutRoot.write(sOutfile)


def commandPurge(sInfile,iInSegment):
    """
    Removes the specified segment from the GPX file
    """

    eInRoot = Gpx(sInfile)
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
    return eOutRoot.write(sInfile)


def commandFlat(sInfile,sOutfile):
    """
    Flats all RTE segement into one only segement 
    """

    eInRoot = Gpx(sInfile)
    if eInRoot is None:
        raise commandError("NOROOT")

    eInSegs = eInRoot.oldRtes()
    if eInSegs is None: 
        raise commandError("NOSEG")

    eOutRoot = gpsbabel()
    if eOutRoot is None:
        raise commandError("NOROOT")

    eOutSeg = eInSegs[0]
    for eInSeg in eInSegs[1:]:
        eInPts = eInSeg.oldPts()
        if eInPts is None: continue 
        eOutSeg.clonePts(eInPts)

    eName = eOutSeg.oldName()
    if eName is None: 
        raise Error("NONAME")
    eName.poke(os.path.splitext(os.path.basename(sOutfile))[0])

    eOutRoot.cloneRtes([eOutSeg])
    return eOutRoot.write(sOutfile)
