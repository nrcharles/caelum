"""TMY3 data set library: thin wrapper around TMY csv files.

Examples:
    >>> sum([int(i['GHI (W/m^2)']) for i in data('724666')])/365./1000.
    4.438213698630137

    >>> round(total('724666', 'DNI (W/m^2)')/365.,2)
    5.11

"""
import csv
# Copyright (C) 2015 Nathan Charles
#
# This program is free software. See terms in LICENSE file.

import datetime
import os
import logging
logger = logging.getLogger(__name__)
from .tools import download
from . import env

# path to tmy3 data
# default = ~/tmp3/

try:
    os.listdir(os.environ['HOME'] + '/tmy3')
except OSError:
    try:
        os.mkdir(os.environ['HOME'] + '/tmy3')
    except IOError:
        pass


def tmybasename(usaf):
    """Basename for USAF base.

    Args:
        usaf (str): USAF code

    Returns:
        (str)
    """
    url_file = open(env.SRC_PATH + '/tmy3.csv')
    for line in url_file.readlines():
        if line.find(usaf) is not -1:
            return line.rstrip().partition(',')[0]


def _tmy_url(usaf):
    """tmy3 url."""
    tmybase = tmybasename(usaf)
    url = "http://rredc.nrel.gov/solar/old_data/nsrdb/1991-2005/data/tmy3/"
    # url = "http://rredc.nrel.gov/solar/old_data/nsrdb/1991-2005/data/tmy3.20080820/"
    return url + tmybase


def strptime(string, timezone=0):
    """custom strptime - necessary because of 24:00 end of day labeling."""
    year = int(string[6:10])
    month = int(string[0:2])
    day = int(string[3:5])
    hour = int(string[11:13])
    minute = int(string[14:16])
    return datetime.datetime(year, month, day) + \
        datetime.timedelta(hours=hour, minutes=minute) - \
        datetime.timedelta(hours=timezone)


def normalize_date(tmy_date, year):
    """change TMY3 date to an arbitrary year.

    Args:
        tmy_date (datetime): date to mangle.
        year (int): desired year.

    Returns:
        (None)
    """
    month = tmy_date.month
    day = tmy_date.day - 1
    hour = tmy_date.hour
    # hack to get around 24:00 notation
    if month is 1 and day is 0 and hour is 0:
        year = year + 1
    return datetime.datetime(year, month, 1) + \
        datetime.timedelta(days=day, hours=hour, minutes=0)


class data(object):

    """TMY3 iterator object.

    Atributes:
        latiude (float)
        longitude (float)
        tz (float)
    """

    def __init__(self, usaf):
        """initialize.

        Args:
            usaf (str)

        Returns:
            (object)
        """
        filename = env.WEATHER_DATA_PATH + '/' + usaf + 'TYA.csv'
        self.csvfile = None
        try:
            self.csvfile = open(filename)
        except IOError:
            logger.info("%s not found", filename)
            download(_tmy_url(usaf), filename)
            self.csvfile = open(filename)
        logging.debug('opened %s', self.csvfile.name)
        header = self.csvfile.readline().split(',')
        self.tmy_data = csv.DictReader(self.csvfile)
        self.latitude = float(header[4])
        self.longitude = float(header[5])
        self.tz = float(header[3])

    def __iter__(self):
        """iterate."""
        return self

    def next(self):
        """iterate."""
        record = self.tmy_data.next()
        _sd = record['Date (MM/DD/YYYY)'] + ' ' + record['Time (HH:MM)']
        record['utc_datetime'] = strptime(_sd, self.tz)
        record['datetime'] = strptime(_sd)
        return record

    def __del__(self):
        """del."""
        self.csvfile.close()


def total(usaf, field='GHI (W/m^2)'):
    """total annual insolation, defaults to GHI."""
    running_total = 0
    usafdata = data(usaf)
    for record in usafdata:
        running_total += float(record[field])
    return running_total/1000.

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    import doctest
    doctest.testmod()
