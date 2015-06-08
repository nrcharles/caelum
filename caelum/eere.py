#!/usr/bin/env python
# Copyright (C) 2015 Nathan Charles
#
# This program is free software. See terms in LICENSE file.
"""Global EERE Weather Data Sources wrapper.

Examples:
    Annual GHI for STATION_CODE in Watts
    >>> sum([int(i['GHI (W/m^2)']) for i in EPWdata('418830')])
    1741512

    Minimum Design Temperature
    >>> minimum('418830')
    8.8

    2% Max Design Temperature
    >>> twopercent('418830')
    34.3

"""

from __future__ import absolute_import
from __future__ import print_function
import csv
import datetime
import pytz
import re
from geopy import geocoders
from .tools import download_extract
from . import env
import logging
logger = logging.getLogger(__name__)

DATA_EXTENTIONS = {'SWERA': 'epw',
                   'CSWD': 'epw',
                   'CWEC': 'epw',
                   'ETMY': 'epw',
                   'IGDG': 'epw',
                   'IMGW': 'epw',
                   'INETI': 'epw',
                   'ISHRAE': 'epw',
                   'ITMY': 'epw',
                   'IWEC': 'epw',
                   'KISR': 'epw',
                   'MSI': 'epw',
                   'NIWA': 'epw',
                   'RMY': 'epw',
                   'SWEC': 'epw',
                   'TMY': 'epw',
                   'TMY2': 'epw',
                   'TMY3': 'epw',
                   'IWEC': 'epw',
                   'stat': 'stat',
                   'ddy': 'ddy'}


def _muck_w_date(record):
    """muck with the date because EPW starts counting from 1 and goes to 24."""
    # minute 60 is actually minute 0?
    temp_d = datetime.datetime(int(record['Year']), int(record['Month']),
                               int(record['Day']), int(record['Hour']) % 24,
                               int(record['Minute']) % 60)
    d_off = int(record['Hour'])//24   # hour 24 is actually hour 0
    if d_off > 0:
        temp_d += datetime.timedelta(days=d_off)
    return temp_d


def _eere_url(station_code):
    """build EERE EPW url for station code."""
    baseurl = 'http://apps1.eere.energy.gov/buildings/energyplus/weatherdata/'
    return baseurl + _station_info(station_code)['url']


def _station_info(station_code):
    """filename based meta data for a station code."""
    url_file = open(env.SRC_PATH + '/eere.csv')
    for line in csv.DictReader(url_file):
        if line['station_code'] == station_code:
            return line
    raise KeyError('Station not found')


def _basename(station_code, fmt=None):
    """region, country, weather_station, station_code, data_format, url."""
    info = _station_info(station_code)
    if not fmt:
        fmt = info['data_format']
    basename = '%s.%s' % (info['url'].rsplit('/', 1)[1].rsplit('.', 1)[0],
                          DATA_EXTENTIONS[fmt])
    return basename


def twopercent(station_code):
    """Two percent high design temperature for a location.

    Degrees in Celcius

    Args:
        station_code (str): Weather Station Code

    Returns:
        float degrees Celcius
    """
    # (DB=>MWB) 2%, MaxDB=
    temp = None
    try:
        fin = open('%s/%s' % (env.WEATHER_DATA_PATH,
                              _basename(station_code, 'ddy')))
        for line in fin:
            value = re.search("""2%, MaxDB=(\\d+\\.\\d*)""", line)
            if value:
                temp = float(value.groups()[0])
    except IOError:
        pass

    if not temp:
        # (DB=>MWB) 2%, MaxDB=
        try:
            fin = open('%s/%s' % (env.WEATHER_DATA_PATH,
                                  _basename(station_code, 'stat')))
            flag = 0
            tdata = []
            for line in fin:
                if line.find('2%') is not -1:
                    flag = 3
                if flag > 0:
                    tdata.append(line.split('\t'))
                    flag -= 1
            temp = float(tdata[2][5].strip())
        except IOError:
            pass
    if temp:
        return temp
    else:
        raise Exception("Error: 2% High Temperature not found")


def minimum(station_code):
    """Extreme Minimum Design Temperature for a location.

    Degrees in Celcius

    Args:
        station_code (str): Weather Station Code

    Returns:
        float degrees Celcius
    """
    temp = None
    fin = None
    try:
        fin = open('%s/%s' % (env.WEATHER_DATA_PATH,
                              _basename(station_code, 'ddy')))
    except IOError:
        logger.info("File not found")
        download_extract(_eere_url(station_code))
        fin = open('%s/%s' % (env.WEATHER_DATA_PATH,
                              _basename(station_code, 'ddy')))
    for line in fin:
        value = re.search('Max Drybulb=(-?\\d+\\.\\d*)', line)
        if value:
            temp = float(value.groups()[0])
    if not temp:
        try:
            fin = open('%s/%s' % (env.WEATHER_DATA_PATH,
                                  _basename(station_code, 'stat')))
            for line in fin:
                if line.find('Minimum Dry Bulb') is not -1:
                    return float(line[37:-1].split('\xb0')[0])
        except IOError:
            pass
    if temp:
        return temp
    else:
        raise Exception("Error: Minimum Temperature not found")


class EPWdata(object):

    """EPW weather generator.

    Attributes:
        lat (float): latitude in degrees
        lon (float): lonitude in degrees

    """

    def __init__(self, station_code, DST=False):
        """Data for a weather station.

        Args:
            station_code (str): Station code of weather station
            DST (bool): Weather timestands in daylight savings. Default False
        """
        filename = env.WEATHER_DATA_PATH + '/' + _basename(station_code)
        self.csvfile = None
        try:
            self.csvfile = open(filename)
        except IOError:
            logger.info("File not found")
            download_extract(_eere_url(station_code))
            self.csvfile = open(filename)
        logging.debug('opened %s', self.csvfile.name)
        fieldnames = ["Year", "Month", "Day", "Hour", "Minute", "DS",
                      "Dry-bulb (C)", "Dewpoint (C)", "Relative Humidity",
                      "Pressure (Pa)", "ETR (W/m^2)", "ETRN (W/m^2)",
                      "HIR (W/m^2)", "GHI (W/m^2)", "DNI (W/m^2)",
                      "DHI (W/m^2)", "GHIL (lux)", "DNIL (lux)", "DFIL (lux)",
                      "Zlum (Cd/m2)", "Wdir (degrees)", "Wspd (m/s)",
                      "Ts cover", "O sky cover", "CeilHgt (m)",
                      "Present Weather", "Pw codes", "Pwat (cm)",
                      "AOD (unitless)", "Snow Depth (cm)",
                      "Days since snowfall"]
        station_meta = self.csvfile.readline().split(',')
        self.station_name = station_meta[1]
        self.CC = station_meta[3]
        self.station_fmt = station_meta[4]
        self.station_code = station_meta[5]
        self.lat = station_meta[6]
        self.lon = station_meta[7]
        self.TZ = float(station_meta[8])
        self.ELEV = station_meta[9]
        self.DST = DST

        if self.DST:
            geocoder = geocoders.GoogleV3()
            self.local_tz = pytz.timezone(geocoder.timezone((self.lat,
                                                             self.lon)).zone)
        dummy = ""
        for _ in range(7):
            dummy += self.csvfile.readline()
        self.epw_data = csv.DictReader(self.csvfile, fieldnames=fieldnames)

    def __iter__(self):
        """iterate."""
        return self

    def next(self):
        """Weather data record.

        Yields:
            dict
        """
        record = self.epw_data.next()
        local_time = _muck_w_date(record)
        record['datetime'] = local_time
        # does this fix a specific data set or a general issue?
        if self.DST:
            localdt = self.local_tz.localize(record['datetime'])
            record['utc_datetime'] = localdt.astimezone(pytz.UTC)
        else:
            record['utc_datetime'] = local_time - \
                datetime.timedelta(hours=self.TZ)

        return record
        # 'LOCATION,BEEK,-,NLD,IWEC Data,063800,50.92,5.78,1.0,116.0'

    def __del__(self):
        """clean up open files."""
        self.csvfile.close()

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    import doctest
    doctest.testmod()
