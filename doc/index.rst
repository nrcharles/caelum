.. caelum documentation master file, created by
   sphinx-quickstart on Thu Feb  5 17:56:36 2015.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to caelum!
==================

caelum is a python interface to various weather sources including NOAA GFS and EREE.

Quickstart
""""""""""

Install caelum via pip.

.. code-block:: shell

    pip install caelum

Calculate total annual GHI in kWh.

.. code-block:: python

    from caelum import eere
    weather_station = '418830'
    sum([int(i['GHI (W/m^2)']) for i in eere.EPWdata(weather_station)])/1000.


Source code for caelum is on `github <https://github.com/nrcharles/caelum>`_

Contents:

.. toctree::
   eere
   gfs
   :maxdepth: 2



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
