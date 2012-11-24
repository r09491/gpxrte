import pytz
from datetime import datetime
from dateutil.parser import parse

DATEFORMAT='%a %d.%m,%H:%M %Z,'
TZ='Europe/Berlin'

def local2utc(dt, tzname=TZ):
    """ The UTC time from local time
    """
    if not isinstance(dt, datetime):
        dt = parse(dt)
 
    dt = pytz.timezone(tzname).localize(dt)
    utc_dt = pytz.utc.normalize(dt.astimezone(pytz.utc))
    return utc_dt.isoformat()
 
def utc2local(dt, tzname=TZ):
    """ The local time from the UTC time
    """
    if not isinstance(dt, datetime):
        dt = parse(dt)
 
    localtz = pytz.timezone(tzname)
    dt = localtz.normalize(dt.astimezone(localtz))
    return dt

def getNowUtc():
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

if __name__ == '__main__':
    print(getNowUtc())
