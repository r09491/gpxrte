__ERRORS__= { \
    "NOROOT": "GPX root segment is missing.", \
        "NOSEGMENTS": "Segments are missing.", \
        "NOPTS": "Points are missing.", \
        "NONAME": "Name is missing.", \
        "NORTRIP": "No round trip segment .", \
        "ILLSEGNUM": "Segment number is illegal.", \
        "ILLPNTNUM": "Point number is illegal.", \
        "ILLSEGTYP": "Segment type is illegal.", \
        "ILLWALKING": "Walking direction mismatch.", \
        "ILLBEGCITY": "City not found.", \
        "ILLENDCITY": "End city not found." }

class commandError(Exception):

    def __init__(self,code):
        self.code=code

    def __str__(self):
        return "gpxrte /:-( " + self.code + ': ' +  __ERRORS__[self.code]
