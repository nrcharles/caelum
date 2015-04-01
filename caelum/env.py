"""Enviroment."""
import os

WEATHER_DATA_PATH = os.environ['HOME'] + "/weather_data"
SRC_PATH = os.path.dirname(os.path.abspath(__file__))

try:
    os.listdir(WEATHER_DATA_PATH)
except OSError:
    try:
        os.mkdir(WEATHER_DATA_PATH)
    except IOError:
        pass
