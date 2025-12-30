Weather Data
============

.. automodule:: pvsolarsim.weather
   :members:
   :undoc-members:
   :show-inheritance:

File Readers
------------

CSV Reader
~~~~~~~~~~

.. autoclass:: pvsolarsim.weather.readers.CSVWeatherReader
   :members:
   :undoc-members:
   :show-inheritance:

JSON Reader
~~~~~~~~~~~

.. autoclass:: pvsolarsim.weather.readers.JSONWeatherReader
   :members:
   :undoc-members:
   :show-inheritance:

API Clients
-----------

PVGIS Client
~~~~~~~~~~~~

.. autoclass:: pvsolarsim.weather.api_clients.PVGISClient
   :members:
   :undoc-members:
   :show-inheritance:

OpenWeatherMap Client
~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: pvsolarsim.weather.api_clients.OpenWeatherMapClient
   :members:
   :undoc-members:
   :show-inheritance:

Data Quality
------------

Interpolation
~~~~~~~~~~~~~

.. autofunction:: pvsolarsim.weather.interpolation.interpolate_weather_data

.. autofunction:: pvsolarsim.weather.interpolation.detect_gaps

.. autofunction:: pvsolarsim.weather.interpolation.fill_gaps

Quality Checks
~~~~~~~~~~~~~~

.. autofunction:: pvsolarsim.weather.quality.perform_quality_checks

.. autofunction:: pvsolarsim.weather.quality.create_quality_report

Base Classes
------------

.. autoclass:: pvsolarsim.weather.base.WeatherDataSource
   :members:
   :undoc-members:
   :show-inheritance:
