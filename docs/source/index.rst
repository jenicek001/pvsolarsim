PVSolarSim Documentation
========================

.. image:: https://badge.fury.io/py/pvsolarsim.svg
   :target: https://badge.fury.io/py/pvsolarsim
   :alt: PyPI version

.. image:: https://img.shields.io/badge/python-3.9+-blue.svg
   :target: https://www.python.org/downloads/
   :alt: Python 3.9+

.. image:: https://img.shields.io/badge/License-MIT-yellow.svg
   :target: https://opensource.org/licenses/MIT
   :alt: License: MIT

**PVSolarSim** is a comprehensive Python library for simulating photovoltaic solar energy production. 
It provides accurate physics-based modeling of solar irradiance, atmospheric effects, and PV system performance.

.. toctree::
   :maxdepth: 2
   :caption: User Guide

   installation
   quickstart
   core_concepts
   advanced_usage
   tutorials

.. toctree::
   :maxdepth: 2
   :caption: API Reference

   api/modules
   api/solar
   api/atmosphere
   api/irradiance
   api/temperature
   api/power
   api/simulation
   api/weather

.. toctree::
   :maxdepth: 1
   :caption: Additional Resources

   mathematical_background
   faq
   contributing
   changelog

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

Key Features
============

* **High Accuracy**: Solar position accuracy <0.01° using NREL SPA algorithm
* **Multiple Models**: Support for various clear-sky, diffuse, and temperature models
* **Weather Integration**: CSV, JSON, OpenWeatherMap, and PVGIS support
* **Type-Safe**: Full type hints with mypy validation
* **Well-Tested**: 81%+ code coverage with 270+ comprehensive tests
* **Easy to Use**: Clean API with comprehensive documentation

Quick Example
=============

.. code-block:: python

   from pvsolarsim import Location, PVSystem, calculate_power
   from datetime import datetime
   import pytz

   # Define location and system
   location = Location(latitude=49.8, longitude=15.5, altitude=300)
   system = PVSystem(
       panel_area=20.0,
       panel_efficiency=0.20,
       tilt=35,
       azimuth=180
   )

   # Calculate instantaneous power
   result = calculate_power(
       location=location,
       system=system,
       timestamp=datetime(2025, 6, 21, 12, 0, tzinfo=pytz.UTC),
       ambient_temp=25,
       wind_speed=3,
       cloud_cover=20
   )

   print(f"Power: {result.power_w:.2f} W")
