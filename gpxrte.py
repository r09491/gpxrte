#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os
import string

from rte.error import *  
from rte.primitive import *  
from rte.overviewcommands import *
from rte.daimlercommands import *
from rte.segmentcommands import *

def  runShow(inputs):
    """
    Shows the content of the gpx file. The gpx file shall exist
    with a legal content.

    The output may be restricted to a list of the segment type rte,
    wpt, trk.

    The output may be further restricted to a single segment within
    the list by specifying its index.
    """
    sInFile=os.path.abspath(inputs.infile)
    if not os.path.isfile(sInFile):
        print ("gpxrte :-( Illegal GPX input file %s." % (sInFile))
        return -1

    if inputs.insegment is None:
        try:
            commandAllSegmentsOverview(inputs.infile)
        except commandError as e:
            print (e)
    else:
        try:
            commandSingleSegmentDetail(inputs.infile,inputs.insegment)
        except commandError as e:
            print (e)
    return 0


def  runName(inputs):
    """
    Sets the name of the RTE segment to the specified or derived name.
    """

    sInFile=os.path.abspath(inputs.infile)
    if not os.path.isfile(sInFile):
        print ("gpxrte :-( Illegal GPX input file %s." % (sInFile))
        return -1

    if inputs.outfile is None:
        sOutFile = sInFile
    else:
        sOutFile=os.path.abspath(inputs.outfile)

    if inputs.name is None:
        sInName = os.path.splitext(os.path.basename(sOutFile))[0]
    else:
        sInName=inputs.name

    try:
        iNumSegs=commandName(sInFile,inputs.insegment,sInName,sOutFile)
    except commandError as e:
        print (e)
    else:
        print ("gpxrte :-; %d segment(s) written." % (iNumSegs))
        print ("gpxrte :-) Name RTEs ok.")


def runSegmentPullCoord(inputs):
    """
    """

    sInFile=os.path.abspath(inputs.infile)
    if not os.path.isfile(sInFile):
        print ("gpxrte :-( Illegal GPX input file %s." % (sInFile))
        return -1

    if inputs.outfile is None:
        print ("gpxrte :-( Out file name is missing!")
        return -3

    if ((inputs.beglat is None) and  (inputs.beglon is not None)) or \
            ((inputs.beglon is None) and  (inputs.beglat is not None)):
        print( "gpxrte :-( Begin coordinates are inconsistent." )
        return -4

    if ((inputs.endlat is None) and  (inputs.endlon is not None)) or \
            ((inputs.endlon is None) and  (inputs.endlat is not None)):
        print ("gpxrte :-( End coordinates are inconsistent.")
        return -5
    
    beglat, beglon = inputs.beglat, inputs.beglon
    endlat, endlon = inputs.endlat, inputs.endlon
    if inputs.begcity is not None:
        lCoords= getCoords(inputs.begcity)
        if lCoords is None:
            print( "gpxrte :-( No begin city coordinates available." )
            return -6
        if inputs.begcityindex is None:
            print ("gpxrte :-| Begin city is ambiguous.")
            for i, (place,(lat,lon)) in enumerate(lCoords):
                print("%d: %s (%.4f, %.4f)" % (i, place, lat, lon))
            return -7
        if inputs.begcityindex in range(len(lCoords)):
            place, (beglat,beglon) = lCoords[inputs.begcityindex]
            print(" From: %s (%.4f, %.4f)" % (place, beglat, beglon))
        else:
            print( "gpxrte :-( Illegal city begin index." )
            return -8

    if inputs.endcity is not None:
        lCoords= getCoords(inputs.endcity)
        if lCoords is None:
            print( "gpxrte :-( No end city coordinates available." )
            return -9
        if inputs.endcityindex is None:
            print ("gpxrte :-| End city is ambiguous.")
            for i, (place,(lat,lon)) in enumerate(lCoords):
                print("%d: %s (%.4f, %.4f)" % (i, place, lat, lon))
            return -10
        if inputs.endcityindex in range(len(lCoords)):
            place,(endlat,endlon) = lCoords[inputs.endcityindex]
            print(" To  : %s (%.4f, %.4f)" % (place, endlat, endlon))
        else:
            print( "gpxrte :-( Illegal city begin index." )
            return -11

    try:
        outfile = commandPullCoord( \
            inputs.infile,inputs.insegment,inputs.intype,
            inputs.outfile,beglat,beglon,endlat,endlon)
        print ("gpxrte ++  Output to %s" % (outfile))
    except commandError as e:
        print (e)
    else:
        print ("gpxrte :-) Pull by coord ok.")


def runSegmentPullDistance(inputs):
    """
    """
    meter = inputs.meter if inputs.meter is not None else 22500.0
    meter = -meter if meter < 0.0 else meter

    sInFile=os.path.abspath(inputs.infile)
    if not os.path.isfile(sInFile):
        print ("gpxrte :-( Illegal GPX input file %s." % (sInFile))
        return -1

    try:
        outSegs = commandPullDistance(sInFile,
                         inputs.insegment, meter, inputs.outfile)
        print ("gpxrte ++  Created %d RTE files." % (outSegs))
    except commandError as e:
        print (e)
    else:
        print ("gpxrte :-) Pull by distance ok.")


def  runSegmentPullAtomic(inputs):
    """
    """

    sInFile=os.path.abspath(inputs.infile)
    if not os.path.isfile(sInFile):
        print ("gpxrte :-( Illegal GPX input file %s." % (sInFile))
        return -1

    try:
        iNumFiles=commandPullAtomic(sInFile, inputs.insegment,inputs.outfile)
    except commandError as e:
        print (e)
    else:
        print ("gpxrte :-; %d file(s) written." % (iNumFiles))
        print ("gpxrte :-) Pull atomic segment ok.")


def  runPush(inputs):
    """
    """

    sInFile=os.path.abspath(inputs.infile)
    if not os.path.isfile(sInFile):
        print ("gpxrte :-( Illegal GPX input file %s." % (sInFile))
        return -1

    sOutFile=os.path.abspath(inputs.outfile)
    if not os.path.isfile(sOutFile):
        print ("gpxrte :-( Illegal GPX input file %s." % (sOutFile))
        return -3

    try:
        iNumSegs=commandPush(sInFile,inputs.insegment,sOutFile)
    except commandError as e:
        print (e)
    else:
        print ("gpxrte :-; %d segments written." % (iNumSegs))
        print ("gpxrte :-) Push segment ok.")


def  runPurge(inputs):
    """
    """

    sInFile=os.path.abspath(inputs.infile)
    if not os.path.isfile(sInFile):
        print ("gpxrte :-( Illegal GPX input file %s." % (sInFile))
        return -1

    try:
        iNumSegs=commandPurge(sInFile, inputs.insegment)
    except commandError as e:
        print (e)
    else:
        print ("gpxrte :-; %d segments written." % (iNumSegs))
        print ("gpxrte :-) Purge segment ok.")


def  runFlat(inputs):
    """
    """

    sInFile=os.path.abspath(inputs.infile)
    if not os.path.isfile(sInFile):
        print ("gpxrte :-( Illegal GPX input file %s." % (sInFile))
        return -1

    if inputs.outfile is None:
        sOutFile = sInFile
    else:
        sOutFile=os.path.abspath(inputs.outfile)

    try:
        iNumSegs=commandFlat(sInFile, sOutFile)
    except commandError as e:
        print (e)
    else:
        print ("gpxrte :-; %d segment(s) written." % (iNumSegs))
        print ("gpxrte :-) Flat RTEs ok.")


def  runReverse(inputs):
    """
    """

    sInFile=os.path.abspath(inputs.infile)
    if not os.path.isfile(sInFile):
        print ("gpxrte :-( Illegal GPX input file %s." % (sInFile))
        return -1

    if inputs.outfile is None:
        sOutFile = sInFile
    else:
        sOutFile=os.path.abspath(inputs.outfile)

    try:
        iNumSegs=commandReverse(sInFile,inputs.insegment,sOutFile)
    except commandError as e:
        print (e)
    else:
        print ("gpxrte :-; %d segment(s) written." % (iNumSegs))
        print ("gpxrte :-) Reverse RTEs ok.")


def  runHead(inputs):
    """
    """

    sInFile=os.path.abspath(inputs.infile)
    if not os.path.isfile(sInFile):
        print ("gpxrte :-( Illegal GPX input file %s." % (sInFile))
        return -1

    if inputs.outfile is None:
        sOutFile = sInFile
    else:
        sOutFile=os.path.abspath(inputs.outfile)

    try:
        iNumSegs=commandHead(sInFile,inputs.insegment,inputs.inpoint,sOutFile)
    except commandError as e:
        print (e)
    else:
        print ("gpxrte :-; %d segment(s) written." % (iNumSegs))
        print ("gpxrte :-) Head RTEs ok.")


def  runTail(inputs):
    """
    """

    sInFile=os.path.abspath(inputs.infile)
    if not os.path.isfile(sInFile):
        print ("gpxrte :-( Illegal GPX input file %s." % (sInFile))
        return -1

    if inputs.outfile is None:
        sOutFile = sInFile
    else:
        sOutFile=os.path.abspath(inputs.outfile)

    try:
        iNumSegs=commandTail(sInFile,inputs.insegment,inputs.inpoint,sOutFile)
    except commandError as e:
        print (e)
    else:
        print ("gpxrte :-; %d segment(s) written." % (iNumSegs))
        print ("gpxrte :-) Tail RTEs ok.")


def  runSwap(inputs):
    """
    """

    sInFile=os.path.abspath(inputs.infile)
    if not os.path.isfile(sInFile):
        print ("gpxrte :-( Illegal GPX input file %s." % (sInFile))
        return -1

    if inputs.outfile is None:
        sOutFile = sInFile
    else:
        sOutFile=os.path.abspath(inputs.outfile)

    try:
        iNumSegs=commandSwap(sInFile, inputs.insegment, inputs.inpoint, sOutFile)
    except commandError as e:
        print (e)
    else:
        print ("gpxrte :-; %d segment(s) written." % (iNumSegs))
        print ("gpxrte :-) Swap RTE at index ok.")


def runFindClosestCoord(inputs):
    """
    """

    sInFile=os.path.abspath(inputs.infile)
    if not os.path.isfile(sInFile):
        print ("gpxrte :-( Illegal GPX input file %s." % (sInFile))
        return -1

    if (inputs.lat is not None) and (inputs.lon is not None) and (inputs.city is None):
        lat, lon = inputs.lat, inputs.lon
    
    elif (inputs.lat is None) and (inputs.lon is None) and (inputs.city is not None):
        lCoords= getCoords(inputs.city)
        if lCoords is None:
            print( "gpxrte :-( No in city coordinates available." )
            return -6
        elif len(lCoords) == 1:
            place, (lat,lon) = lCoords[0]
        elif (inputs.cityindex is None):
            print ("gpxrte ;-) The city is ambiguous.")
            for i, (place,(lat,lon)) in enumerate(lCoords):
                print("%d: %s (%.4f, %.4f)" % (i, place, lat, lon))
            return -7
        elif inputs.cityindex in range(len(lCoords)):
            place, (lat,lon) = lCoords[inputs.cityindex]
        else:
            print( "gpxrte :-( Illegal city index." )
            return -8
    else:
        print( "gpxrte :-( No coordinates" )
        return -3
 
    try:
        index,rLat,rLon,brg,rng = commandFindClosestCoord( \
            inputs.infile,inputs.insegment,lat,lon)
    except commandError as e:
        print (e)
    else:
        print ("gpxrte :-) FROM #%d (%.4f:%.4f) TO %s (%.4f:%.4f) > %03.0f/%03.0f/%03.0f" % \
                   (index,rLat,rLon,place.split(',')[0].strip(),lat,lon,brg,rng,iDeg(brg)))


def runFindClosestRoute(inputs):
    """
    """

    sInFile1=os.path.abspath(inputs.infile1)
    if not os.path.isfile(sInFile1):
        print ("gpxrte :-( Illegal GPX input file %s." % (sInFile1))
        return -1

    sInFile2=os.path.abspath(inputs.infile2)
    if not os.path.isfile(sInFile2):
        print ("gpxrte :-( Illegal GPX input file %s." % (sInFile2))
        return -2

    try:
        i1,i2,lat1,lon1,lat2,lon2,brg,rng = commandFindClosestRoute( \
            sInFile1,inputs.insegment1,sInFile2,inputs.insegment2)
    except commandError as e:
        print (e)
    else:
        print ("gpxrte :-) FROM #%d(%.4f:%.4f) TO #%d(%.4f:%.4f) > %03.0f/%03.0f/%03.0f" % \
                   (i1,lat1,lon1,i2,lat2,lon2,brg,rng,iDeg(brg)))


def  runDaimler(inputs):
    """
    Converts an RTE segment to a daimler route compatible format. The gpx file
    shall exist with a legal content. Segment types other than RTE are ignored.

    If the specified file is consistent with the Daimler route naming covention
    then the output is written to this file. Otherwise the file name is generated
    according to the convention and written to this file. 
    """

    sInFile=os.path.abspath(inputs.infile)
    if not os.path.isfile(sInFile):
        print ("gpxrte :-( Illegal GPX input file %s." % (sInFile))
        return -1

    if inputs.outfile is not None:
        sOutFile=os.path.abspath(inputs.outfile)
    else:
        sOutFile = None

    try:
        iNumSegs=convertToRoute(sInFile,inputs.insegment,sOutFile)
    except commandError as e:
        print (e)
    else:
        print ("gpxrte :-; %d segment(s) written." % (iNumSegs))
        print ("gpxrte :-) Daimler RTEs ok.")


def main(inputs):
    """
    """
    try:
        return inputs.func(inputs)
    except IOError as msg:
        return inputs.error(str(msg))


def parse(commandline):
    """
    Parses the provided commandline
    """

    import argparse
    parser = argparse.ArgumentParser(version='0.0', \
            description='Tools to manage the content of a GPX file')

    subparsers = parser.add_subparsers(help='commands')

    showParser = subparsers.add_parser('show', help='Shows the content of a GPX file')
    showParser.add_argument('-s', '--insegment',dest='insegment', \
                                type=int, help='Segment number to show')
    showParser.add_argument('-f', '--infile', dest='infile', required=True, \
                                help='Any GPX file to show')
    showParser.set_defaults(func=runShow)


    nameParser = subparsers.add_parser('name', help='Sets the name of a segment')
    nameParser.add_argument('-s', '--insegment',dest='insegment',required=True, \
                             type=int, help='Segment number to use for the name')
    nameParser.add_argument('-f', '--infile', dest='infile', required=True, \
                            help='Any GPX file for input', )
    nameParser.add_argument('-F', '--outfile', dest='outfile', \
                            help='Any GPX file for output. If not provided overrides the input file')
    nameParser.add_argument('-n', '--name', dest='name', \
                            help='The name to set. If not provided derives from the nominal output file')
    nameParser.set_defaults(func=runName)

    
    pullParser = subparsers.add_parser('pull', help='Pulls a segment')
    pullSubparser = pullParser.add_subparsers(help='subcommands pull')
    pullSubparserAtomic = pullSubparser.add_parser('atomic', \
                               help='Pulls complete segments')
    pullSubparserAtomic.add_argument('-s', '--insegment',dest='insegment', type=int, \
                            required=True, help='Segment number to use for pull')
    pullSubparserAtomic.add_argument('-f', '--infile', dest='infile', required=True, \
                            help='Any GPX file for pull', )
    pullSubparserAtomic.add_argument('-F', '--outfile', dest='outfile', \
                            help='Any GPX file for output', )
    pullSubparserAtomic.set_defaults(func=runSegmentPullAtomic)


    pullSubparserCoord = pullSubparser.add_parser('coord', \
                              help='Pulls a segment closest to the coords or cities')
    pullSubparserCoord.add_argument('-blat','--beglat', dest='beglat', \
                             type=float, help='New route begin coord (lat)')
    pullSubparserCoord.add_argument('-blon','--beglon', dest='beglon', \
                            type=float, help='New route begin coord (lon)')
    pullSubparserCoord.add_argument('-elat','--endlat',dest='endlat',  \
                            type=float, help='New route end coord (lat)')
    pullSubparserCoord.add_argument('-elon','--endlon',dest='endlon',  \
                            type=float, help='New route end coord (lon)')
    pullSubparserCoord.add_argument('-bc','--begcity',dest='begcity',  \
                            help='New route begin city name')
    pullSubparserCoord.add_argument('-bi','--begcityindex',dest='begcityindex',  \
                            type=int, help='New route begin city index')
    pullSubparserCoord.add_argument('-ec','--endcity',dest='endcity',  \
                            help='New route end city')
    pullSubparserCoord.add_argument('-ei','--endcityindex',dest='endcityindex',  \
                            type=int, help='New route end city index')

    pullSubparserCoord.add_argument('-s', '--insegment',dest='insegment', \
                            type=int, default=0, help='Segment number to use for input')
    pullSubparserCoord.add_argument('-f', '--infile', dest='infile', required=True, \
                            help='Any GPX file for input', )
    pullSubparserCoord.add_argument('-F', '--outfile', dest='outfile', \
                            required=True, help='Any GPX file for output', )
    pullSubparserCoord.set_defaults(func=runSegmentPullCoord)


    pullSubparserDistance = pullSubparser.add_parser('distance', \
                              help='Pulls segments by distances')
    pullSubparserDistance.add_argument('-m','--meter', dest='meter', \
                             type=float, help='Desired route distance (m)')
    pullSubparserDistance.add_argument('-s', '--insegment',dest='insegment',type=int, \
                            required=True, help='Segment number to use for input')
    pullSubparserDistance.add_argument('-f', '--infile', dest='infile', \
                            required=True, help='Any GPX file for input', )
    pullSubparserDistance.add_argument('-F', '--outfile', dest='outfile', \
                            required=True, help='Any GPX file for output', )
    pullSubparserDistance.set_defaults(func=runSegmentPullDistance)


    pushParser = subparsers.add_parser('push', help='Pushes a segment')
    pushParser.add_argument('-s', '--insegment',dest='insegment', \
                             type=int, help='Segment number to use for input')
    pushParser.add_argument('-f', '--infile', dest='infile', \
                            required=True, help='Any GPX file for input', )
    pushParser.add_argument('-F', '--outfile', dest='outfile', \
                            required=True, help='Any GPX file for output', )
    pushParser.set_defaults(func=runPush)


    purgeParser = subparsers.add_parser('purge', help='Purges a segment')
    purgeParser.add_argument('-s', '--insegment',dest='insegment', type=int, default=0, \
                                required=True, help='Segment number to remove')
    purgeParser.add_argument('-f', '--infile', dest='infile', \
                            required=True, help='Any GPX file for input', )
    purgeParser.set_defaults(func=runPurge)


    flatParser = subparsers.add_parser('flat', help='Flattens into segment')
    flatParser.add_argument('-f', '--infile', dest='infile', \
                            required=True, help='Any GPX file for input', )
    flatParser.add_argument('-F', '--outfile', dest='outfile', \
                            required=True,help='Any GPX file for output', )
    flatParser.set_defaults(func=runFlat)


    reverseParser = subparsers.add_parser('reverse', help='Reverses the segment')
    reverseParser.add_argument('-s', '--insegment',dest='insegment',required=True, \
                                   type=int, help='Segment number to use for reverse')
    reverseParser.add_argument('-f', '--infile', dest='infile', \
                            required=True, help='Any GPX file for input', )
    reverseParser.add_argument('-F', '--outfile', dest='outfile', \
                            required=True, help='Any GPX file for output', )
    reverseParser.set_defaults(func=runReverse)


    headParser = subparsers.add_parser('head', help='Heads the segment')
    headParser.add_argument('-s', '--insegment',dest='insegment',required=True, \
                                   type=int, help='Segment number to use for head')
    headParser.add_argument('-p', '--inpoint',dest='inpoint',required=True, \
                            type=int, help='Point number of fist not inclueded')
    headParser.add_argument('-f', '--infile', dest='infile', \
                            required=True, help='Any GPX file for input', )
    headParser.add_argument('-F', '--outfile', dest='outfile', \
                            required=True, help='Any GPX file for output', )
    headParser.set_defaults(func=runHead)


    tailParser = subparsers.add_parser('tail', help='Tails the segment')
    tailParser.add_argument('-s', '--insegment',dest='insegment',required=True, \
                                   type=int, help='Segment number to use for tail')
    tailParser.add_argument('-p', '--inpoint',dest='inpoint',required=True, \
                            type=int, help='Point number of first tail point')
    tailParser.add_argument('-f', '--infile', dest='infile', \
                            required=True, help='Any GPX file for input', )
    tailParser.add_argument('-F', '--outfile', dest='outfile', \
                            required=True, help='Any GPX file for output', )
    tailParser.set_defaults(func=runTail)


    swapParser = subparsers.add_parser('swap', help='Swaps a round trip segment')
    swapParser.add_argument('-s', '--insegment',dest='insegment',required=True, \
                            type=int, help='Segment number to use for swap')
    swapParser.add_argument('-p', '--inpoint',dest='inpoint',required=True, \
                            type=int, help='Point number to swap at')
    swapParser.add_argument('-f', '--infile', dest='infile', required=True, \
                            help='Any GPX file for input', )
    swapParser.add_argument('-F', '--outfile', dest='outfile', \
                            help='Any GPX file for output', )
    swapParser.set_defaults(func=runSwap)


    findClosestParser = subparsers.add_parser('find', help='Finds a segment')
    findClosestSubparser = findClosestParser.add_subparsers(help='subcommands find')

    findClosestSubparserCoord = findClosestSubparser.add_parser('coord', \
                              help='Finds a route point closest to the coords or cities')
    findClosestSubparserCoord.add_argument('-lat','--lat', dest='lat', \
                             type=float, help='Coord (lat)')
    findClosestSubparserCoord.add_argument('-lon','--lon', dest='lon', \
                            type=float, help='Coord (lon)')
    findClosestSubparserCoord.add_argument('-c','--city',dest='city',  \
                            help='City name')
    findClosestSubparserCoord.add_argument('-i','--cityindex',dest='cityindex',  \
                            type=int, help='City index')
    findClosestSubparserCoord.add_argument('-s','--insegment',dest='insegment', \
                   type=int, required=True, help='Segment number to use for find')
    findClosestSubparserCoord.add_argument('-f', '--infile', dest='infile', \
                            required=True, help='Any GPX file for find', )
    findClosestSubparserCoord.set_defaults(func=runFindClosestCoord)


    findClosestSubparserRoute = findClosestSubparser.add_parser('route', \
                               help='Finds the points closest from two routes')
    findClosestSubparserRoute.add_argument('-s1', '--insegment1',dest='insegment1', \
                          type=int,required=True,help='Segment number to use for find')
    findClosestSubparserRoute.add_argument('-s2', '--insegment2',dest='insegment2', \
                          type=int,required=True,help='Segment number to use for find')
    findClosestSubparserRoute.add_argument('-f1', '--infile1', dest='infile1', \
                            required=True, help='Any GPX file for find', )
    findClosestSubparserRoute.add_argument('-f2', '--infile2', dest='infile2', \
                            required=True, help='Any GPX file for find', )
    findClosestSubparserRoute.set_defaults(func=runFindClosestRoute)


    daimlerParser = subparsers.add_parser('daimler', \
                            help='Generates a COMAND Online NTG 4.5 compatible route')
    daimlerParser.add_argument('-s','--insegment',dest='insegment', \
                   type=int, required=True, help='Segment number to use for daimlerisation')
    daimlerParser.add_argument('-f', '--infile', dest='infile', \
                            required=True, help='Any GPX file for input', )
    daimlerParser.add_argument('-F', '--outfile', dest='outfile', \
                            help='Any GPX file for output', )
    daimlerParser.set_defaults(func=runDaimler)


    try:
        inputs=parser.parse_args(commandline)
    except IOError as msg:
        parser.error(str(msg))
    return inputs

if __name__ == '__main__':
    sys.exit(main(parse(sys.argv[1:])))
