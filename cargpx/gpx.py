#!/usr/bin/env python
'''
Created on Sep 18, 2010

@author: kirus
@purpose: Traverse a gpx file and provide its content
'''

import sys, os
import string
from copy import deepcopy
import lxml.etree as etree


class GPX:
    TAG="gpx"

class METADATA:
    TAG,TIME,BOUNDS,NAME="metadata","time","bounds","name"

class RTE:
    TAG,PT,ELE,NAME,EXTENSIONS="rte","rtept","ele","name","extensions"

class WPT:
    TAG,PT,ELE,NAME="wpt","wptpt","ele","name"

class TRK:
    TAG,PT,ELE,NAME="trk","trkpt","ele","name"

class Error(Exception):
    pass

class Name(object):
    def __init__(self,eName):
        self.eName=eName

    def peek(self):
        if self.eName is None:
            return ""
        else:
            return self.eName.text

    def poke(self,name):
        if self.eName is not None:
            self.eName.text = name

    def clone(self,fromother):
        if not isinstance(self, Name):
            raise Error
        self.poke(fromother.peek())


class Time(object):
    def __init__(self,eTime):
        self.eTime=eTime

    def peek(self):
        if self.eTime is None:
            return ""
        else:
            return self.eTime.text

    def poke(self,time):
        self.eTime.text = time

    def clone(self,fromother):
        if not isinstance(self, Time):
            raise Error
        self.poke(fromother.peek())


class Bounds(object):
    def __init__(self,eBounds):
        self.eBounds=eBounds

    def peek(self):
        if self.eBounds is None:
            return 90.0, 180.0, -90.0, -180.0
        else:
            minlat=float(self.eBounds.get('minlat'))
            minlon=float(self.eBounds.get('minlon'))
            maxlat=float(self.eBounds.get('maxlat'))
            maxlon=float(self.eBounds.get('maxlon'))
            return minlat, minlon, maxlat, maxlon

    def poke(self, bounds):
        minlat, minlon, maxlat, maxlon = bounds
        self.eBounds.set('minlat', str(minlat))
        self.eBounds.set('minlon', str(minlon))
        self.eBounds.set('maxlat', str(maxlat))
        self.eBounds.set('maxlon', str(maxlon))

    def clone(self,fromother):
        if not isinstance(self, Bounds):
            raise Error
        print (self[0])
        self.poke(fromother.peek())


class Point(object):
    def __init__(self,ePoint):
        self.ePoint=ePoint

    def peek(self):
        return float(self.ePoint.get('lat')), float(self.ePoint.get('lon'))

    def poke(self, latlon):
        if self.ePoint is None:
            raise Error
        self.ePoint.set('lat', str(latlon[0]));
        self.ePoint.set('lon', str(latlon[1]));

    def clone(self,fromother):
        if not isinstance(fromother, Point):
            raise Error
        self.poke(fromother.peek())


class Ele(object):
    def __init__(self,eEle):
        self.eEle=eEle

    def peek(self):
        if self.eEle is None:
            return 0.0
        else:
            return float(self.eEle.text)

    def poke(self, ele):
        if self.eEle is None:
            raise Error
        self.eEle.text = str(ele)

    def clone(self,fromother):
        if not isinstance(fromother, ele):
            raise Error
        self.poke(fromother.peek())

        
class Rtept(Point):
    def __init__(self,ePoint):
        Point.__init__(self, ePoint)

        self.tRteName=ePoint.tag.replace(RTE.PT,RTE.NAME)
        self.tRteEle=ePoint.tag.replace(RTE.PT,RTE.ELE)

    def oldName(self):
        """
        Copies and returns the name element of the RTE point.
        """
        return Name(self.ePoint.find(self.tRteName))

    def oldEle(self):
        """
        Copies and returns the elevation element of the RTE point.
        """
        return Ele(self.ePoint.find(self.tRteEle))


class Wptpt(Point):
    def __init__(self,ePoint):
        Point.__init__(self, ePoint)

        self.tWptName=ePoint.tag.replace(WPT.PT,WPT.NAME)
        self.tWptEle=ePoint.tag.replace(WPT.PT,WPT.ELE)

    def oldName(self):
        """
        Copies and returns the name element of the WPT point.
        """
        return Name(self.ePoint.find(self.tWptName))

    def oldEle(self):
        """
        Copies and returns the elevation element of the WPT point.
        """
        return Ele(self.ePoint.find(self.tWptEle))


class Trkpt(Point):
    def __init__(self,ePoint):
        Point.__init__(self, ePoint)

        self.tTrkName=ePoint.tag.replace(TRK.PT,TRK.NAME)
        self.tTrkEle=ePoint.tag.replace(TRK.PT,TRK.ELE)

    def oldName(self):
        """
        Copies and returns the name element of the TRK point.
        """
        return Name(self.ePoint.find(self.tTrkName))

    def oldEle(self):
        """
        Copies and returns the elevation element of the TRK point.
        """
        return Ele(self.ePoint.find(self.tTrkEle))


class Rte(object):
    def __init__(self,eSegment):
        self.eSegment=eSegment

        # Generate all required fully qualified tags
        self.tRteName=eSegment.tag.replace(RTE.TAG,RTE.NAME)
        self.tRtePt=eSegment.tag.replace(RTE.TAG,RTE.PT)

    def oldName(self):
        """
        Copies and returns the name element of the parent RTE segment.
        """
        return Name(self.eSegment.find(self.tRteName))

    def oldPts(self):
        """
        Copies and returns all existing point elements of the parent RTE segment
        """
        return [Rtept(pt) for pt in self.eSegment.findall(self.tRtePt)]

    def newPts(self,num):
        """
        Creates and returns new point elements for the parent RTE segment
        """
        return [Rtept(etree.SubElement(self.eSegment, \
                     self.tRtePt, lat="0.0", lon="0.0")) for e in range(num)]

    def clonePts(self, eFromPoints):
        """
        Appends the points to the RTE segment
        """
        for ePt in eFromPoints: self.eSegment.append(deepcopy(ePt.ePoint)) 

class Wpt(object):
    def __init__(self,eSegment):
        self.eSegment=eSegment

        # Generate all required fully qualified tags
        self.tWptName=eSegment.tag.replace(WPT.TAG,WPT.NAME)
        self.tWptPt=eSegment.tag.replace(WPT.TAG,WPT.PT)

    def oldName(self):
        """
        Copies and returns the name element of the parent WPT segment.
        """
        return Name(self.eSegment.find(self.tWptName))

    def oldPts(self):
        """
        Copies and returns all existing point elements of the parent WPT segment
        """
        return [Wptpt(pt) for pt in self.eSegment.findall(self.tWptPt)]

    def newPts(self,num):
        """
        Creates and returns new point elements for the parent WPT segment
        """
        return [Wptpt(etree.SubElement(self.eSegment, \
                     self.tWptPt, lat="0.0", lon="0.0")) for e in range(num)]

class Trk(object):
    def __init__(self,eSegment):
        self.eSegment=eSegment

        # Generate all required fully qualified tags
        self.tTrkName=eSegment.tag.replace(TRK.TAG,TRK.NAME)
        self.tTrkPt=eSegment.tag.replace(TRK.TAG,TRK.PT)

    def oldName(self):
        """
        Copies and returns the name element of the parent TRK segment.
        """
        return Name(self.eSegment.find(self.tTrkName))

    def oldPts(self):
        """
        Copies and returns all existing point elements of the parent TRK segment
        """
        return [Trkpt(pt) for pt in self.eSegment.findall(self.tTrkPt)]

    def netrks(self,num):
        """
        Creates and returns new point elements for the parent TRK segment
        """
        return [Trkpt(etree.SubElement(self.eSegment, \
                     self.tTrkPt, lat="0.0", lon="0.0")) for e in range(num)]

class Metadata(object):
    def __init__(self,eMetadata):
        self.eMetadata=eMetadata

        # Generate all required fully qualified tags
        self.tMetadataName=eMetadata.tag.replace(METADATA.TAG,METADATA.NAME)
        self.tMetadataTime=eMetadata.tag.replace(METADATA.TAG,METADATA.TIME)
        self.tMetadataBounds=eMetadata.tag.replace(METADATA.TAG,METADATA.BOUNDS)

    def oldName(self):
        """
        Copies and returns the name element of the parent RTE segment.
        """
        return Name(self.eMetadata.find(self.tMetadataName))

    def oldTime(self):
        """
        Copies and returns the time element of the parent RTE segment.
        """
        return Time(self.eMetadata.find(self.tMetadataTime))

    def oldBounds(self):
        """
        Copies and returns the time element of the parent RTE segment.
        """
        return Bounds(self.eMetadata.find(self.tMetadataBounds))


class Gpx(object):
    """
    """

    def __init__(self,gpxfile="",gpxstring=""):
        # Create the element root
        if (gpxfile == "") and (gpxstring != ""):
            self.root = etree.fromstring(gpxstring)
        else:
            self.root = etree.parse(gpxfile).getroot()

        # Generate all required fully qualified tags
        self.tMetadata=self.root.tag.replace(GPX.TAG,METADATA.TAG)

        self.tRte=self.root.tag.replace(GPX.TAG,RTE.TAG)
        self.tWpt=self.root.tag.replace(GPX.TAG,WPT.TAG)
        self.tTrk=self.root.tag.replace(GPX.TAG,TRK.TAG)

    def write(self, gpxfile, encoding='utf-8', standalone="no",xml_declaration='True'):
        self.root.set('creator', 'gpxrte.py - http://www.josef-heid.de')        
        etree.ElementTree(self.root).write(gpxfile, encoding=encoding, \
               standalone=standalone, xml_declaration=xml_declaration, \
                                               pretty_print=True)

    def oldMetadata(self):
        """
        Copies and returns a list of all METADATA segment elements.
        """
        return Metadata(self.root.find(self.tMetadata))

    def newMetadata(self):
        """
        Creates and returns a list of all METADATA segment elements.
        """
        return Metadata(etree.SubElement(self.root, self.tMetadata))

    def oldRtes(self):
        """
        Copies and returns a list of all RTE segment elements.
        """
        return [Rte(s) for s in self.root.findall(self.tRte)] 

    def newRtes(self,num):
        """
        Creates and returns a list of all RTE segment elements.
        """
        return [Rte(etree.SubElement(self.root, self.tRte)) \
                    for e in range(num)]

    def cloneRtes(self, eFromSegs):
        """
        Appends the RTE segments to the GPX root
        """
        for eSeg in eFromSegs: self.root.append(deepcopy(eSeg.eSegment))
 

    def oldWpts(self):
        """
        Copies and returns a list of all WPT segment elements.
        """
        return [Wpt(s) for s in self.root.findall(self.tWpt)] 

    def newWpts(self,num):
        """
        Creates and returns a list of all WPT segment elements.
        """
        return [Wpt(etree.SubElement(self.root, self.tWpt)) \
                    for e in range(num)]

    def oldTrks(self):
        """
        Copies and returns a list of all TRK segment elements.
        """
        return [Trk(s) for s in self.root.findall(self.tTrk)] 

    def newTrks(self,num):
        """
        Creates and returns a list of all TRK segment elements.
        """
        return [Trk(etree.SubElement(self.root, self.tTrk)) \
                    for e in range(num)]

class DAIMLER:
    NS={"gpxd":"http://www.daimler.com/DaimlerGPXExtensions/V2.4"}
    RTEEXTENSION = "gpxd:RteExtension"
    RTELENGTH = "gpxd:RouteLength"

class DaimlerRteLength(object):
    def __init__(self,eRteLength):
        self.eRteLength = eRteLength 

    def peek(self):
        return self.eRteLength.get('Unit'), self.eRteLength.get('Value') 

    def poke(self, unitkm):
        self.eRteLength.set('Unit', unitkm[0])
        self.eRteLength.set('Value', unitkm[1])
                
    def clone(self,fromOther):
        self.eRteLength.poke(self.e.peek())


class DaimlerRteExtension(object):
    def __init__(self,eRteExtension):
        self.eRteExtension = eRteExtension
                
    def oldRteLength(self):
        """
        Copies and returns the Daimler Route Length element.
        """
        ele=self.eRteExtension.find(DAIMLER.RTELENGTH,namespaces=DAIMLER.NS)
        return DaimlerRteLength(ele)

    def newRouteLength(self,num):
        """
        Creates and returns the Daimler Route Length element.
        """
        ele=etree.SubElement(self.eRteExtension,DAIMLER.RTELENGTH,namespaces=DAIMLER.NS)
        return DaimlerRteLength(ele)


class DaimlerExtensions(object):
    def __init__(self,eExtensions):
        self.eExtensions = eExtensions

    def oldRteExtension(self):
        """
        Copies and returns the RTE extension element.
        """
        ele=self.eExtensions.find(DAIMLER.RTEEXTENSION,namespaces=DAIMLER.NS)
        return DaimlerRteExtension(ele)

    def newRteExtension(self,num):
        """
        Creates and returns the RTE  extension element.
        """
        ele=etree.SubElement(self.eExtensions,DAIMLER.RTEEXTENSION,namespaces=DAIMLER.NS)
        return DaimlerRteExtension(ele)


class DaimlerRte(Rte):
    def __init__(self,eSegment):
        Rte.__init__(self, eSegment)

        self.rteExtensionsTag=eSegment.tag.replace(RTE.TAG,RTE.EXTENSIONS)

    def oldExtensions(self):
        """
        Copies and returns the RTE segment extension element.
        """
        return DaimlerExtensions(self.eSegment.find(self.rteExtensionsTag))

    def newExtensions(self,num):
        """
        Creates and returns the RTE segment extension element.
        """
        return DaimlerExtensions(etree.SubElement(self.eSegment, self.rteExtensionsTag))


class Daimler(Gpx):
    def __init__(self,gpxfile="",gpxstring=""):
        Gpx.__init__(self, gpxfile, gpxstring)

    def oldRtes(self):
        """
        Copies and returns a list of all Daimler RTE segment elements.
        """
        return [DaimlerRte(ele) for ele in self.root.findall(self.tRte)] 

    def newRtes(self,num):
        """
        Creates and returns a list of new Daimler RTE segment elements.
        """
        return [Daimler.Rte(etree.SubElement(self.root, self.tRte)) \
                    for e in range(num)]

class Gpsbabel(Gpx):
    def __init__(self,gpxfile="",gpxstring=""):
        Gpx.__init__(self, gpxfile, gpxstring)

class Garmin(Gpx):
    def __init__(self,gpxfile="",gpxstring=""):
        Gpx.__init__(self, gpxfile, gpxstring)

