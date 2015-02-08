"""Helper functions"""
import os
import math

SRC_PATH = os.path.dirname(os.path.abspath(__file__))

SLON = {'W':-1.0,
        'E':1.0}
SLAT = {'N':1.0,
        'S':-1.0}

def _mlat(tlat):
    nlat = SLAT[tlat[-1:]] * float(tlat[0:-2])/10.
    return nlat

def _mlon(tlon):
    nlon = SLON[tlon[-1:]] * float(tlon[0:-2])/10.
    return nlon

def parse_noaa_line(line):
    """
    NUMBER NAME & STATE/COUNTRY                                LAT   LON     ELEV (meters)

    010250 TROMSO                                          NO  6941N 01855E    10
    """
    station = {}
    station['station_name'] = line[7:51].strip()
    station['station_code'] = line[0:6]
    station['CC'] = line[55:57]
    station['ELEV(m)'] = int(line[73:78])
    station['LAT'] = _mlat(line[58:64])
    station['LON'] = _mlon(line[65:71])
    station['ST'] = line[52:54]
    return station

def closest_noaa(latitude, longitude):
    """Find closest station code of a given station class"""
    with open(SRC_PATH + '/inswo-stns.txt') as index:
        index.readline() #header
        index.readline() #whitespace
        min_dist = 9999
        station_name = ''
        station_name = ''
        for line in index:
            try:
                i = parse_noaa_line(line)
                new_dist = math.sqrt(math.pow((float(i['LAT']) - latitude), 2) \
                        + math.pow((float(i['LON']) - longitude), 2))
            except:
                print 'error'
                print line
                raise IOError('Inventory Issue')

            if new_dist < min_dist:
                min_dist = new_dist
                station_name = i['station_name']
                station_code = i['station_code']
        index.close()
        return station_code, station_name
    raise KeyError('station not found')

if __name__ == '__main__':
    print closest_noaa(52.208364, 5.320569)
