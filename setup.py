"""install"""
import os
from setuptools import setup, find_packages
import datetime

NOW = datetime.datetime.now()
MAJOR = 0

def read(fname):
    """README helper fuction"""
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name="caelum",
    version="%s.%s.%s.%s" % (MAJOR, NOW.month, NOW.day, NOW.hour),
    author="Nathan Charles",
    author_email="ncharles@gmail.com",
    description=("Python library for typical historical weather sources"),
    license="LGPL",
    keywords="climate weather data TMY EPW EERE",
    url="https://github.com/nrcharles/caelum",
    packages=find_packages(),
    long_description=read('README.md'),
    install_requires=['geopy'],
    package_data={'': ['*.csv','*.txt']},
    test_suite='tests.unit',
    classifiers=[
        "Development Status :: 4 - Beta",
        ("License :: OSI Approved ::" \
            " GNU Library or Lesser General Public License (LGPL)"),
    ],
)
