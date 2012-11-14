_GPSBABEL='''<gpx xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://www.topografix.com/GPX/1/1" version="1.1" creator="gpxrte - http://www.josef-heid.de" xsi:schemaLocation="http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd"><metadata><time>2013-01-01T00:00:00Z</time><bounds minlat="-90.0" minlon="-180.0" maxlat="90.0" maxlon="180.0"/></metadata></gpx>'''

from .gpx import Gpx;

def gpsbabel():
    return Gpx(gpxstring=_GPSBABEL)
