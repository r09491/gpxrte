#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os
import string

from cargpx.error import commandError  

from cargpx.overviewcommands import commandAllSegmentsOverview
from cargpx.overviewcommands import commandSingleSegmentDetail
from cargpx.daimlercommands import convertToRoute  

from cargpx.segmentcommands import getCoords
from cargpx.segmentcommands import commandName  
from cargpx.segmentcommands import commandPullAtomic
from cargpx.segmentcommands import commandPullByCoord 
from cargpx.segmentcommands import commandPullByDistance 
from cargpx.segmentcommands import commandPush
from cargpx.segmentcommands import commandPurge
from cargpx.segmentcommands import commandFlat

from cargpx import gpx as gpx

def  runShow(inputs):
    """
    Shows the content of the gpx file. The gpx file shall exist
    with a legal content.

    The output may be restricted to a list of the segment type rte,
    wpt, trk.

    The output may be further restricted to a single segment within
    the list by specifying its index.
    """
    sInfile=os.path.abspath(inputs.infile)
    if not os.path.isfile(sInfile):
        print ("gpxrte :-( Illegal GPX input file %s." % (sInfile))
        return -1

    if (inputs.intype != "rte"):
        print ("gpxrte :-( For RTE segment only!")
        return -2

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


def  runDaimler(inputs):
    """
    Converts an RTE segment to a daimler route compatible format. The gpx file
    shall exist with a legal content. Segment types other than RTE are ignored.

    If the specified file is consistent with the Daimler route naming covention
    then the output is written to this file. Otherwise the file name is generated
    according to the convention and written to this file. 
    """
    result=":-( 'Daimler' command failed )-:"

    eAnysegs = gpx.Garmin(inputs.anygpxfile).oldRtes()
    if len(eAnysegs) > 0:
        anysegnum=inputs.segmentnumber
        if (anysegnum >= 0) and (anysegnum < len(eAnysegs)):
            eAnyseg=eAnysegs[anysegnum]
            result = convertToRoute(eAnyseg,inputs.anygpxfile)
        else:
            result = ":-( %s: %d )-:" % ("Segment number out of range", anysegnum)
    else:
        result = ":-( %s )-:" % ("RTE segment is missing.")
    return result


def  runSegmentName(inputs):
    """
    Sets the name of the RTE segment to the specified name.
    """
    try:
        commandName(inputs.anygpxfile, \
                           inputs.segmentnumber, inputs.segmentname)
    except commandError as e:
        print (e)
    else:
        print ("gpxrte :-) Name completed ok.")


def runSegmentPullByCoord(inputs):
    """
    """
    print ("gpxrte :-, Pull RTE by coords")

    sInfile=os.path.abspath(inputs.infile)
    if not os.path.isfile(sInfile):
        print ("gpxrte :-( Illegal GPX input file %s." % (sInfile))
        return -1

    if (inputs.intype != "rte"):
        print ("gpxrte :-( For RTE segment only!")
        return -2

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
        outfile = commandPullByCoord( \
            inputs.infile,inputs.insegment,inputs.intype,
            inputs.outfile,beglat,beglon,endlat,endlon)
        print ("gpxrte ++  Output to %s" % (outfile))
    except commandError as e:
        print (e)
    else:
        print ("gpxrte :-) Pull by coord ok.")


def runSegmentPullByDistance(inputs):
    """
    """
    meter = inputs.meter if inputs.meter is not None else 22500.0
    meter = -meter if meter < 0.0 else meter

    print ("gpxrte :-, Pull RTE by distance")

    sInfile=os.path.abspath(inputs.infile)
    if not os.path.isfile(sInfile):
        print ("gpxrte :-( Illegal GPX input file %s." % (sInfile))
        return -1

    if (inputs.intype != "rte"):
        print ("gpxrte :-( For RTE segment only!")
        return -2

    try:
        outSegs = commandPullByDistance(sInfile,
                         inputs.insegment, meter, inputs.outfile)
        print ("gpxrte ++  Created %d RTE files." % (outSegs))
    except commandError as e:
        print (e)
    else:
        print ("gpxrte :-) Pull by distance ok.")


def  runSegmentPullAtomic(inputs):
    """
    """
    print ("gpxrte :-, Pull RTE atomic")

    sInfile=os.path.abspath(inputs.infile)
    if not os.path.isfile(sInfile):
        print ("gpxrte :-( Illegal GPX input file %s." % (sInfile))
        return -1

    if (inputs.intype != "rte"):
        print ("gpxrte :-( For RTE segment only!")
        return -2

    try:
        iNumFiles=commandPullAtomic(sInfile, inputs.insegment)
    except commandError as e:
        print (e)
    else:
        print ("gpxrte :-; %d files written." % (iNumFiles))
        print ("gpxrte :-) Pull atomic segment ok.")


def  runPush(inputs):
    """
    """
    print ("gpxrte :-, Push RTE")

    sOutfile=os.path.abspath(inputs.outfile)

    sInfile=os.path.abspath(inputs.infile)
    if not os.path.isfile(sInfile):
        print ("gpxrte :-( Illegal GPX input file %s." % (sInfile))
        return -1

    if (inputs.intype != "rte"):
        print ("gpxrte :-( For RTE segment only!")
        return -2

    try:
        iNumSegs=commandPush(sInfile, inputs.insegment, sOutfile)
    except commandError as e:
        print (e)
    else:
        print ("gpxrte :-; %d segments written." % (iNumSegs))
        print ("gpxrte :-) Push segment ok.")


def  runPurge(inputs):
    """
    """
    print ("gpxrte :-, Purge RTE")

    sInfile=os.path.abspath(inputs.infile)
    if not os.path.isfile(sInfile):
        print ("gpxrte :-( Illegal GPX input file %s." % (sInfile))
        return -1

    if (inputs.intype != "rte"):
        print ("gpxrte :-( For RTE segment only!")
        return -2

    try:
        iNumSegs=commandPurge(sInfile, inputs.insegment)
    except commandError as e:
        print (e)
    else:
        print ("gpxrte :-; %d segments written." % (iNumSegs))
        print ("gpxrte :-) Purge segment ok.")


def  runFlat(inputs):
    """
    """
    print ("gpxrte :-, Flat RTE")

    sInfile=os.path.abspath(inputs.infile)
    if not os.path.isfile(sInfile):
        print ("gpxrte :-( Illegal GPX input file %s." % (sInfile))
        return -1

    if (inputs.intype != "rte"):
        print ("gpxrte :-( For RTE segment only!")
        return -2

    if inputs.outfile is None:
        sOutfile = sInfile
    else:
        sOutfile=os.path.abspath(inputs.outfile)

    try:
        iNumSegs=commandFlat(sInfile, sOutfile)
    except commandError as e:
        print (e)
    else:
        print ("gpxrte :-; %d segments written." % (iNumSegs))
        print ("gpxrte :-) Flat segment ok.")


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
    showParser.add_argument('-t', '--intype', dest='intype', \
                                choices=('trk', 'rte', 'wpt'), \
                                default='rte', help='Segment type to use for input')
    showParser.add_argument('-f', '--infile', dest='infile', required=True, \
                                help='Any GPX file to show')
    showParser.set_defaults(func=runShow)

    daimlerParser = subparsers.add_parser('daimler', \
                            help='Generates a COMAND Online NTG 4.5 route')
    daimlerParser.set_defaults(func=runDaimler)
    daimlerParser.add_argument(dest='segmentnumber', nargs='?', \
                            type=int, default=0, \
                            help='RTE segment number to use')


    nameParser = subparsers.add_parser('name', help='Sets the name of an RTE segment')
    nameParser.add_argument(dest='segmentname', \
                            help='RTE segment name to set')
    nameParser.add_argument(dest='segmentnumber', nargs='?', \
                            type=int, default=0, \
                            help='RTE segment number to use')
    nameParser.set_defaults(func=runSegmentName)
    
    pullParser = subparsers.add_parser('pull', help='Pulls an RTE segment')
    pullSubparser = pullParser.add_subparsers(help='subcommands pull')

    pullSubparserAtomic = pullSubparser.add_parser('atomic', \
                               help='Pulls complete RTE segments')
    pullSubparserAtomic.add_argument('-s', '--insegment',dest='insegment', \
                            type=int, help='Segment number to use for pull')
    pullSubparserAtomic.add_argument('-t', '--intype', dest='intype', \
                            choices=('trk', 'rte', 'wpt'), \
                            default='rte', help='Segment type to use for pull')
    pullSubparserAtomic.add_argument('-f', '--infile', dest='infile', required=True, \
                            help='Any GPX file for pull', )
    pullSubparserAtomic.set_defaults(func=runSegmentPullAtomic)


    pullSubparserByCoord = pullSubparser.add_parser('coord', \
                              help='Pulls an RTE segment closest to the coords or cities')
    pullSubparserByCoord.add_argument('-blat','--beglat', dest='beglat', \
                             type=float, help='New route begin coord (lat)')
    pullSubparserByCoord.add_argument('-blon','--beglon', dest='beglon', \
                            type=float, help='New route begin coord (lon)')
    pullSubparserByCoord.add_argument('-elat','--endlat',dest='endlat',  \
                            type=float, help='New route end coord (lat)')
    pullSubparserByCoord.add_argument('-elon','--endlon',dest='endlon',  \
                            type=float, help='New route end coord (lon)')
    pullSubparserByCoord.add_argument('-bc','--begcity',dest='begcity',  \
                            help='New route begin city name')
    pullSubparserByCoord.add_argument('-bi','--begcityindex',dest='begcityindex',  \
                            type=int, help='New route begin city index')
    pullSubparserByCoord.add_argument('-ec','--endcity',dest='endcity',  \
                            help='New route end city')
    pullSubparserByCoord.add_argument('-ei','--endcityindex',dest='endcityindex',  \
                            type=int, help='New route end city index')

    pullSubparserByCoord.add_argument('-s', '--insegment',dest='insegment', \
                            type=int, default=0, help='Segment number to use for input')
    pullSubparserByCoord.add_argument('-t', '--intype', dest='intype', \
                            choices=('trk', 'rte', 'wpt'), \
                            default='rte', help='Segment type to use for input')
    pullSubparserByCoord.add_argument('-f', '--infile', dest='infile', required=True, \
                            help='Any GPX file for input', )
    pullSubparserByCoord.add_argument('-F', '--outfile', dest='outfile', \
                            required=True, help='Any GPX file for output', )
    pullSubparserByCoord.set_defaults(func=runSegmentPullByCoord)


    pullSubparserByDistance = pullSubparser.add_parser('distance', \
                              help='Pulls RTE segments by distances')
    pullSubparserByDistance.add_argument('-m','--meter', dest='meter', \
                             type=float, help='Desired route distance (m)')
    pullSubparserByDistance.add_argument('-s', '--insegment',dest='insegment', \
                            type=int, default=0, help='Segment number to use for input')
    pullSubparserByDistance.add_argument('-t', '--intype', dest='intype', \
                            choices=('trk', 'rte', 'wpt'), \
                            default='rte', help='Segment type to use for input')
    pullSubparserByDistance.add_argument('-f', '--infile', dest='infile', \
                            required=True, help='Any GPX file for input', )
    pullSubparserByDistance.add_argument('-F', '--outfile', dest='outfile', \
                            required=True, help='Any GPX file for output', )
    pullSubparserByDistance.set_defaults(func=runSegmentPullByDistance)


    pushParser = subparsers.add_parser('push', help='Pushes an RTE segment')
    pushParser.add_argument('-s', '--insegment',dest='insegment', \
                             type=int, help='Segment number to use for input')
    pushParser.add_argument('-t', '--intype', dest='intype', \
                            choices=('trk', 'rte', 'wpt'), \
                            default='rte', help='Segment type to use for input')
    pushParser.add_argument('-f', '--infile', dest='infile', \
                            required=True, help='Any GPX file for input', )
    pushParser.add_argument('-F', '--outfile', dest='outfile', \
                            required=True, help='Any GPX file for output', )
    pushParser.set_defaults(func=runPush)


    purgeParser = subparsers.add_parser('purge', help='Purges an RTE segment')
    purgeParser.add_argument('-s', '--insegment',dest='insegment', type=int, default=0, \
                                required=True, help='Segment number to remove')
    purgeParser.add_argument('-t', '--intype', dest='intype', \
                            choices=('trk', 'rte', 'wpt'), \
                            default='rte', help='Segment type to use for input')
    purgeParser.add_argument('-f', '--infile', dest='infile', \
                            required=True, help='Any GPX file for input', )
    purgeParser.set_defaults(func=runPurge)


    flatParser = subparsers.add_parser('flat', help='Flattens into RTE segment')
    flatParser.add_argument('-t', '--intype', dest='intype', \
                            choices=('trk', 'rte', 'wpt'), \
                            default='rte', help='Segment type to use for input')
    flatParser.add_argument('-f', '--infile', dest='infile', \
                            required=True, help='Any GPX file for input', )
    flatParser.add_argument('-F', '--outfile', dest='outfile', \
                                help='Any GPX file for output', )
    flatParser.set_defaults(func=runFlat)


    try:
        inputs=parser.parse_args(commandline)
    except IOError as msg:
        parser.error(str(msg))
    return inputs

if __name__ == '__main__':
    sys.exit(main(parse(sys.argv[1:])))
