"""Helper functions."""
import csv
import os
import urllib2
import zipfile
import tempfile
import logging
from . import env
from geopy.distance import great_circle

SRC_PATH = os.path.dirname(os.path.abspath(__file__))

SLON = {'W': -1.0,
        'E': 1.0}
SLAT = {'N': 1.0,
        'S': -1.0}
logger = logging.getLogger(__name__)


def download(url, filename):
    """download and extract file."""
    logger.info("Downloading %s", url)
    request = urllib2.Request(url)
    request.add_header('User-Agent',
                       'caelum/0.1 +https://github.com/nrcharles/caelum')
    opener = urllib2.build_opener()
    local_file = open(filename, 'w')
    local_file.write(opener.open(request).read())
    local_file.close()


def download_extract(url):
    """download and extract file."""
    logger.info("Downloading %s", url)
    request = urllib2.Request(url)
    request.add_header('User-Agent',
                       'caelum/0.1 +https://github.com/nrcharles/caelum')
    opener = urllib2.build_opener()
    with tempfile.TemporaryFile(suffix='.zip', dir=env.WEATHER_DATA_PATH) \
            as local_file:
        logger.debug('Saving to temporary file %s', local_file.name)
        local_file.write(opener.open(request).read())
        compressed_file = zipfile.ZipFile(local_file, 'r')
        logger.debug('Extracting %s', compressed_file)
        compressed_file.extractall(env.WEATHER_DATA_PATH)
        local_file.close()


def _mlat(tlat):
    nlat = SLAT[tlat[-1:]] * float(tlat[0:-2])/10.
    return nlat


def _mlon(tlon):
    nlon = SLON[tlon[-1:]] * float(tlon[0:-2])/10.
    return nlon


def parse_noaa_line(line):
    """Parse NOAA stations.

    This is an old list, the format is:

    NUMBER NAME & STATE/COUNTRY                     LAT   LON     ELEV (meters)

    010250 TROMSO                             NO  6941N 01855E    10
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
    """Find closest station from the old list."""
    with open(env.SRC_PATH + '/inswo-stns.txt') as index:
        index.readline()  # header
        index.readline()  # whitespace
        min_dist = 9999
        station_name = ''
        station_name = ''
        for line in index:
            try:
                i = parse_noaa_line(line)
                new_dist = great_circle((latitude, longitude),
                                        (float(i['LAT']),
                                         float(i['LON']))).miles

            except:
                logger.error(line)
                raise IOError('Inventory Issue')

            if new_dist < min_dist:
                min_dist = new_dist
                station_name = i['station_name']
                station_code = i['station_code']
        index.close()
        return station_code, station_name
    raise KeyError('station not found')


def closest_eere(latitude, longitude):
    """Find closest station from the new(er) list.

    Warning: There may be some errors with smaller non US stations.

    Args:
        latitude (float)
        longitude (float)

    Returns:
        tuple (station_code (str), station_name (str))

    """
    with open(env.SRC_PATH + '/eere_meta.csv') as eere_meta:
        stations = csv.DictReader(eere_meta)
        d = 9999
        station_code = ''
        station_name = ''
        for station in stations:
            new_dist = great_circle((latitude, longitude),
                                    (float(station['latitude']),
                                     float(station['longitude']))).miles
            if new_dist <= d:
                d = new_dist
                station_code = station['station_code']
                station_name = station['weather_station']
        return station_code, station_name
    raise KeyError('station not found')


def eere_station(station_code):
    """Station information.

    Args:
        station_code (str): station code.

    Returns (dict): station information
    """
    with open(env.SRC_PATH + '/eere_meta.csv') as eere_meta:
        stations = csv.DictReader(eere_meta)
        for station in stations:
            if station['station_code'] == station_code:
                return station
    raise KeyError('station not found')

if __name__ == '__main__':
    print(closest_noaa(52.208364, 5.320569))
    print eere_station('163120')
