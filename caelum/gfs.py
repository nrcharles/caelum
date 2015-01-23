"""Download GFS grib2 files."""

import urllib2
import datetime
import csv
import os

DATA_PATH = os.environ['HOME'] + "/gfs"


def _verify_path(path):
    """look for path and create it if doesn't exist"""
    try:
        os.listdir(path)
    except OSError:
        os.mkdir(path)

_verify_path(DATA_PATH)


def _baseurl(gfs_timestamp, filename):
    """build url url"""
    url = 'http://nomads.ncep.noaa.gov/pub/data/nccf/com/gfs/prod/gfs.%s/'\
          '%s' % (gfs_timestamp, filename)
    return url


def _join(segments):
    """simply list by joining adjacent segments"""
    new = []
    start = segments[0][0]
    end = segments[0][1]
    for i in range(len(segments)-1):
        if segments[i+1][0] != segments[i][1]:
            new.append((start, end))
            start = segments[i+1][0]
        end = segments[i+1][1]
    new.append((start, end))
    return new


def _filter_messages(messages, products=None, levels=None):
    """filter messages for desired products and levels"""
    if products is None:
        products = []
    if levels is None:
        levels = []
    segments = []
    bounds = len(messages)
    for i, message in enumerate(messages):
        if (message[3] in products or len(products) == 0) and \
                (message[4] in levels or len(levels) == 0):
            start = int(message[1])
            if i == (bounds - 1):
                end = None
            else:
                end = int(messages[i+1][1])
            segments.append((start, end))
    return _join(segments)


def _download_segments(filename, url, segments):
    """download segments into a single file"""
    gribfile = open(filename, 'w')
    for start, end in segments:
        req = urllib2.Request(url)
        req.add_header('User-Agent',
                       'caelum/0.1 +https://github.com/nrcharles/caelum')
        if end:
            req.headers['Range'] = 'bytes=%s-%s' % (start, end)
        else:
            req.headers['Range'] = 'bytes=%s' % (start)
        opener = urllib2.build_opener()
        gribfile.write(opener.open(req).read())
    gribfile.close()


def _sflux(closest, offset):
    """sflux dataset naming convention"""
    return 'gfs.t%02dz.sfluxgrbf%02d.grib2' % (closest, offset)


def get(timestamp, dataset, products=None, levels=None, offset=0):
    """saves GFS grib file to DATA_PATH

    Args:
        dataset(function): naming convention function.  eg. _sflux
        timestamp(datetime): ???
        offset(int): multiple of 3

    """
    closest = timestamp.hour//6*6
    filename = dataset(closest, offset)
    gfs_timestamp = '%s%02d' % (timestamp.strftime('%Y%m%d'), closest)

    url = _baseurl(gfs_timestamp, filename)
    index = url + '.idx'
    messages = message_index(index)
    segments = _filter_messages(messages, products, levels)
    path = DATA_PATH + '/%s/' % gfs_timestamp
    _verify_path(path)
    _download_segments(path + filename, url, segments)


def message_index(index_url):
    """get message index of components for urllib2
    Args:
        url(string):

    Returns:
        list: messages
    """
    idx = csv.reader(urllib2.urlopen(index_url), delimiter=':')
    messages = []
    for line in idx:
        messages.append(line)
    return messages

if __name__ == '__main__':
    START = datetime.datetime.now()
    PRODUCTS = ['TCDC', 'SNOWC', 'TMP', 'ALBDO', 'UGRD', 'VGRD']
    LEVELS = ['surface', 'entire atmosphere (considered as a single layer)',
              'low cloud layer', '1 hybrid level']

    for j in range(5):
        get(START, _sflux, PRODUCTS, LEVELS, j*3)
