import os

from copy import deepcopy
import lxml.etree as etree

from .latlon import *
from .error import commandError
from .time import getNowZulu
from .schemes import gpsbabel

        
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
    try:
        NS = '//{'+eGpx.nsmap[None]+'}%s'
    except KeyError:
        NS = '//{'+eGpx.nsmap['gpx']+'}%s'

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
        eTime[0].text=getNowZulu()

    eGpx.set('creator', 'gpxrte - http://www.josef-heid.de')        
    etree.ElementTree(eGpx).write(sOutFile,encoding='utf-8', \
                                      xml_declaration=True,pretty_print=True)


def modifyGpxFile(sFileName, iInSeg, applyModifier, args):
    """
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

    eRte=eRtes[iSegmentNumber]
    applyModifier(eRte, args)
    eGpx.write(sFileName)


def commandName(sFileName, iInSeg, sName):
    """
    """

    def modifyName(eRte, sName):
        """
        Get the old RTE name element. Its content shall become 
        the new segment name.
        """

        NS = '{'+eRte.nsmap[None]+'}%s'
        eRteName = eRte.find(NS % 'name')
        if eRteName is None:
            raise Error("NONAME")
        eName.text=sName

    modifyGpxFile(sFileName, iInSeg, modifyName, sName)


def commandPullAtomic(sInFile, iInSeg, sOutFile):
    """
    Returns GPX file with the selected RTE segment
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


def commandPullCoord(sInFile,iInSeg,iInType,sOutFile, \
                         fBeginLat,fBeginLon,fEndLat,fEndLon):
    """
    Returns a GPX file with a single segment with the start
    point and end point closest to the input requests.
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
    eInSeg=eInSegs[iInSeg]

    eRtePts=eRte.findall(NS % 'rtept' )
    if eInPts is None: 
        raise commandError("NOPTS")
    inLatLons=[getLatLon(ePt) for ePt in eRtePts]

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
    
    if iBegin >= iEnd: raise commandError("ILLWALKING")

    for eRtePt in eRtePts[:iBegin]:eRte.remove(eRtePt) 
    for eRtePt in eRtePts[iEnd+1:]:eRte.remove(eRtePt) 

    writeGpxFile(eGpx,lLatLons[iBegin:iEnd+1],sOutFile)
    return len(eGpx.findall(NS % 'rte'))


def commandPullDistance(sInFile,iInSeg,fMeter,sOutFile):
    """
    Splits a long GPX route into several segments not exceeding the
    requested distance. The segments may be stored in individual files
    or a single file.
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
    for eRte in eRtes[:iInSeg]:eGpx.remove(eRte) 
    for eRte in eRtes[iInSeg+1:]:eGpx.remove(eRte) 
    eRte=eRtes[iInSeg]

    eRtePts=eRte.findall(NS % 'rtept' )
    if eRtePts is None: 
        raise commandError("NOPTS")
    inLatLons=[getLatLon(ePt) for ePt in eRtePts]

    pre, ext = os.path.splitext(os.path.basename(sOutFile))

    iBegin,iCount,fLength = 0, 0, 0.0
    for iEnd in range(1,len(inLatLons)):
        fLength += inLatLons[iEnd].rangeTo(inLatLons[iEnd-1])
        if fLength < fMeter: continue

        eOutGpx=deepcopy(eGpx)
        eOutRte=eOutGpx.findall(NS % 'rte')[iInSeg]
        eOutPts=eOutRte.findall(NS % 'rtept' )
        for ePt in eOutPts[:iBegin]:eOutRte.remove(ePt) 
        for ePt in eOutPts[iEnd:]:eOutRte.remove(ePt) 
        eOutLatLons=[getLatLon(ePt) for ePt in eOutPts[iBegin:iEnd]]
        writeGpxFile(eOutGpx,eOutLatLons,"%s_%03d_distance.gpx" % (pre,iCount))

        iBegin,iCount,fLength = iEnd-1,iCount+1,0.0

    eOutGpx=deepcopy(eGpx)
    eOutRte=eOutGpx.findall(NS % 'rte')[iInSeg]
    eOutPts=eOutRte.findall(NS % 'rtept' )
    for ePt in eOutPts[:iBegin]:eOutRte.remove(ePt) 
    eOutLatLons=[getLatLon(ePt) for ePt in eOutPts[iBegin:]]
    writeGpxFile(eOutGpx,eOutLatLons,"%s_%03d_distance.gpx" % (pre,iCount))
    return iCount


def commandPush(sInFile,iInSeg,sOutFile):
    """
    Appends a GPX file to another GPX file with propably multiple segments
    """

    eInGpx = etree.parse(sInFile).getroot()
    if eInGpx is None:
        raise commandError("NOROOT")
    NS = '{'+eInGpx.nsmap[None]+'}%s'

    eInRtes= eInGpx.findall(NS % 'rte')
    if eInRtes is None: 
        raise commandError("NOSEG")

    eOutGpx = etree.parse(sOutFile).getroot()
    if eOutGpx is None:
        raise commandError("NOROOT")
    NS = '{'+eOutGpx.nsmap[None]+'}%s'
    
    if iInSeg is None:
        eOutGpx.extend(eInRtes)
    elif (iInSeg < 0) or (iInSeg >= len(eInRtes)):
        raise commandError("ILLSEGNUM")
    else:
        eOutGpx.extend(eInRtes[iInSeg])

    eOutRtePts= eOutGpx.findall(NS % 'rte' + '/' + NS % 'rtept' )
    lLatLons=[getLatLon(eRtePt) for eRtePt in eOutRtePts]

    writeGpxFile(eOutGpx,lLatLons,sOutFile)
    return len(eOutGpx.findall(NS % 'rte'))


def commandPurge(sInFile,iInSeg):
    """
    Removes the specified segment from the GPX file
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

    # Remove the complete segment
    eGpx.remove(eRtes[iInSeg])

    eRtePts= eGpx.findall(NS % 'rte' + '/' + NS % 'rtept' )
    lLatLons=[getLatLon(eRtePt) for eRtePt in eRtePts]

    writeGpxFile(eGpx,lLatLons,sInFile)
    return len(eGpx.findall(NS % 'rte'))


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

def commandReverse(sInFile,iInSeg,sOutFile):
    """
    Inverts the route
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

    eRtePts=eRtes[iInSeg].findall(NS % 'rtept' )
    for eRtePt in reversed(eRtePts):eGpx.append(eRtePt)

    writeGpxFile(eGpx,None,sOutFile)
    return len(eRtes)


def commandHead(sInFile,iInSeg,iInPoint,sOutFile):
    """
    Returns the head points of the segment not including the point indexed
    by iInPoint
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
    eRte=eRtes[iInSeg]

    eRtePts=eRte.findall(NS % 'rtept' )
    if (iInPoint < 0) or (iInPoint >= len(eRtePts)):
        raise commandError("ILLPNTNUM")
    for eRtePt in eRtePts[iInPoint:]:eRte.remove(eRtePt) 

    lLatLons=[getLatLon(ePt) for ePt in eRtePts[:iInPoint]]
    writeGpxFile(eGpx,lLatLons,sOutFile)
    return len(eRtes)


def commandTail(sInFile,iInSeg,iInPoint,sOutFile):
    """
    Returns the tail points of the segment including the point indexed
    by iInPoint
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
    eRte=eRtes[iInSeg]

    eRtePts=eRte.findall(NS % 'rtept' )
    if (iInPoint < 0) or (iInPoint >= len(eRtePts)):
        raise commandError("ILLPNTNUM")
    for eRtePt in eRtePts[:iInPoint]:eRte.remove(eRtePt) 

    lLatLons=[getLatLon(ePt) for ePt in eRtePts[iInPoint:]]
    writeGpxFile(eGpx,lLatLons,sOutFile)
    return len(eRtes)


def commandSwap(sInFile,iInSeg,iInPoint,sOutFile):
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


def commandFindClosestCoord(sInFile,iInSeg,lat,lon):
    """
    Returns the index of the closest RTE point to the given coord
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

    lLatLons=[getLatLon(ePt) for ePt in eRtePts]
    index,brg,rng = closestToPoint(lLatLons,LatLon(lat,lon))
    return index,lLatLons[index].lat,lLatLons[index].lon,brg,rng


def commandFindClosestRoute(sInFile1,iInSeg1,sInFile2,iInSeg2):
    """
    Returns the index of the closest RTE point to the given route
    """
    eInGpx = etree.parse(sInFile1).getroot()
    if eInGpx is None:
        raise commandError("NOROOT")
    NS = '{'+eInGpx.nsmap[None]+'}%s'

    eInRtes1= eInGpx.findall(NS % 'rte')
    if eInRtes1 is None: 
        raise commandError("NOSEG")
    if (iInSeg1 < 0) or (iInSeg1 >= len(eInRtes1)):
        raise commandError("ILLSEGNUM")

    eInRtePts1 = eInRtes1[iInSeg1].findall(NS % 'rtept')
    if eInRtePts1 is None: 
        raise commandError("NOPTS")
    lInLatLons1=[getLatLon(ePt) for ePt in eInRtePts1]

    eInGpx2 = etree.parse(sInFile2).getroot()
    if eInGpx2 is None:
        raise commandError("NOROOT")
    NS = '{'+eInGpx2.nsmap[None]+'}%s'

    eInRtes2= eInGpx2.findall(NS % 'rte')
    if eInRtes2 is None: 
        raise commandError("NOSEG")
    if (iInSeg2 < 0) or (iInSeg2 >= len(eInRtes2)):
        raise commandError("ILLSEGNUM")

    eInRtePts2 = eInRtes2[iInSeg2].findall(NS % 'rtept')
    if eInRtePts2 is None: 
        raise commandError("NOPTS")
    lInLatLons2=[getLatLon(ePt) for ePt in eInRtePts2]

    iP1,iP2,brg,rng = closestToRoute(lInLatLons1,lInLatLons2)
    return iP1,iP2,lInLatLons1[iP1].lat,lInLatLons1[iP1].lon, \
        lInLatLons2[iP2].lat,lInLatLons2[iP1].lon,brg,rng 
