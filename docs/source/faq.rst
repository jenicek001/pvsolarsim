FAQ
===

Frequently Asked Questions about PVSolarSim.

General Questions
-----------------

What is PVSolarSim?
~~~~~~~~~~~~~~~~~~~

PVSolarSim is a Python library for simulating photovoltaic (PV) solar energy production. It provides accurate physics-based models for solar position, atmospheric effects, irradiance on tilted surfaces, temperature effects, and complete system performance simulation.

Who should use PVSolarSim?
~~~~~~~~~~~~~~~~~~~~~~~~~~~

PVSolarSim is designed for:

* Solar energy researchers and engineers
* PV system designers and installers
* Energy analysts and consultants
* Students learning about solar energy
* Anyone needing accurate PV power calculations

How accurate is PVSolarSim?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

PVSolarSim achieves high accuracy through:

* Solar position: <0.01° error (NREL SPA algorithm via pvlib)
* Clear-sky irradiance: <2% error vs. pvlib
* POA irradiance: <1% error vs. pvlib
* Temperature models: <0.1°C error vs. pvlib

All models are validated against pvlib-python and industry standards.

Is PVSolarSim free?
~~~~~~~~~~~~~~~~~~~~

Yes, PVSolarSim is open-source software released under the MIT License. It is free to use, modify, and distribute.

Installation
------------

What are the system requirements?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* Python 3.9 or later
* Operating system: Windows, macOS, or Linux
* At least 100 MB of free disk space

How do I install PVSolarSim?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   pip install pvsolarsim

For development:

.. code-block:: bash

   git clone https://github.com/jenicek001/pvsolarsim.git
   cd pvsolarsim
   pip install -e ".[dev]"

Why am I getting import errors?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Make sure you're using Python 3.9 or later:

.. code-block:: bash

   python --version

If you get "ModuleNotFoundError", ensure PVSolarSim is installed:

.. code-block:: bash

   pip install pvsolarsim

Usage
-----

How do I calculate solar position?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from pvsolarsim.solar import calculate_solar_position
   from datetime import datetime
   import pytz

   position = calculate_solar_position(
       timestamp=datetime(2025, 6, 21, 12, 0, tzinfo=pytz.UTC),
       latitude=49.8,
       longitude=15.5,
       altitude=300
   )

How do I simulate annual energy production?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from pvsolarsim import Location, PVSystem, simulate_annual

   location = Location(latitude=40.0, longitude=-105.0, altitude=1655)
   system = PVSystem(panel_area=20.0, panel_efficiency=0.20, tilt=35, azimuth=180)

   results = simulate_annual(
       location=location,
       system=system,
       year=2025,
       weather_source='clear_sky'
   )

   print(f"Annual energy: {results.statistics.total_energy_kwh:.2f} kWh")

What weather data sources are supported?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

PVSolarSim supports:

* **Clear-sky models**: Theoretical calculations (no weather data needed)
* **CSV files**: Custom weather data
* **JSON files**: Custom weather data
* **PVGIS**: Free TMY data from European Commission
* **OpenWeatherMap**: Real-time and historical API (requires API key)

How do I use my own weather data?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   results = simulate_annual(
       location=location,
       system=system,
       year=2025,
       weather_source="csv",
       file_path="my_weather_data.csv",
       column_mapping={
           'ghi': 'GlobalHorizontalIrradiance',
           'temp_air': 'Temperature'
       }
   )

What time interval should I use for simulations?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Common intervals:

* **1-5 minutes**: Detailed analysis, captures rapid changes (~13 min runtime for 5-min)
* **15 minutes**: Good balance of accuracy and speed
* **1 hour**: Quick estimates, annual simulations (~30 sec runtime)

Accuracy difference between hourly and 5-minute is typically <2%.

Models and Algorithms
----------------------

Which clear-sky model should I use?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* **Ineichen** (default): Industry standard, uses Linke turbidity, validated worldwide
* **Simplified Solis**: More physically based, uses aerosol optical depth (AOD)

For most applications, use Ineichen with default Linke turbidity of 3.0.

Which diffuse model should I use?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* **Perez** (default): Industry standard, anisotropic, most accurate
* **Hay-Davies**: Good balance of accuracy and simplicity
* **Isotropic**: Simplest, less accurate

Perez is recommended for all applications.

Which temperature model should I use?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* **SAPM**: Widely used, validated against field data (recommended)
* **Faiman**: Physically based, good for research
* **PVsyst**: Accounts for efficiency and absorption
* **Generic Linear**: Simplest, uses NOCT parameter

SAPM is recommended for most applications.

Performance
-----------

How long does an annual simulation take?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Typical runtime on modern hardware:

* Hourly intervals: ~30 seconds
* 5-minute intervals: ~13 minutes
* 1-minute intervals: ~60 minutes

How can I speed up simulations?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. Use hourly intervals instead of 5-minute
2. Use clear-sky models instead of API weather data
3. Limit the number of locations in batch processing
4. Use progress callbacks to monitor long-running simulations

Errors and Troubleshooting
---------------------------

ValueError: timestamp must be timezone-aware
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

All timestamps must include timezone information:

.. code-block:: python

   import pytz
   from datetime import datetime

   # ❌ Wrong - naive timestamp
   timestamp = datetime(2025, 6, 21, 12, 0)

   # ✅ Correct - timezone-aware
   timestamp = datetime(2025, 6, 21, 12, 0, tzinfo=pytz.UTC)

Why is my power output zero at night?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This is expected! Solar panels don't produce power when the sun is below the horizon. Check that your timestamps are during daylight hours.

Why are my results different from other tools?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Small differences (<5%) are normal due to:

* Different clear-sky models
* Different temperature models
* Different IAM models
* Rounding and numerical precision

Validate your inputs (location, system parameters, weather data) are correct.

Data and API Issues
-------------------

How do I get an OpenWeatherMap API key?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. Sign up at https://openweathermap.org/api
2. Subscribe to Solar Radiation API
3. Use your API key in the client:

.. code-block:: python

   from pvsolarsim.weather import OpenWeatherMapClient
   
   client = OpenWeatherMapClient(api_key="your_api_key_here")

Where can I get weather data?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Free sources:

* **PVGIS**: https://re.jrc.ec.europa.eu/pvg_tools/en/
* **NSRDB** (USA): https://nsrdb.nrel.gov/
* **Meteonorm**: Commercial, high quality

Or use built-in clear-sky models for theoretical estimates.

How do I handle missing weather data?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from pvsolarsim.weather import interpolate_weather_data

   # Interpolate gaps
   clean_data = interpolate_weather_data(
       weather_data,
       method='linear',
       max_gap_hours=3
   )

Contributing
------------

How can I contribute to PVSolarSim?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

See the :doc:`contributing` guide for details on:

* Reporting bugs
* Suggesting features
* Contributing code
* Improving documentation

Where do I report bugs?
~~~~~~~~~~~~~~~~~~~~~~~~

Report bugs on GitHub: https://github.com/jenicek001/pvsolarsim/issues

Please include:

* Python version
* PVSolarSim version
* Minimal code to reproduce the issue
* Error message and traceback

License
-------

What license does PVSolarSim use?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

PVSolarSim is released under the MIT License, which allows:

* Commercial use
* Modification
* Distribution
* Private use

See the LICENSE file for full details.

Can I use PVSolarSim in commercial projects?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Yes! The MIT License allows commercial use. No attribution is legally required, but we appreciate it!

Further Help
------------

Where can I get help?
~~~~~~~~~~~~~~~~~~~~~

* **Documentation**: https://pvsolarsim.readthedocs.io
* **GitHub Issues**: https://github.com/jenicek001/pvsolarsim/issues
* **Email**: jenicek001@users.noreply.github.com

How do I cite PVSolarSim in publications?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bibtex

   @software{pvsolarsim2025,
     author = {jenicek001},
     title = {PVSolarSim: Python library for photovoltaic solar energy simulation},
     year = {2025},
     url = {https://github.com/jenicek001/pvsolarsim},
     version = {0.1.0}
   }
