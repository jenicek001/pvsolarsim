API Reference
=============

This section contains the complete API reference for PVSolarSim.

.. toctree::
   :maxdepth: 2

   solar
   atmosphere
   irradiance
   temperature
   power
   simulation
   weather

Overview
--------

PVSolarSim is organized into the following modules:

Solar Position
~~~~~~~~~~~~~~

.. autosummary::
   :nosignatures:

   pvsolarsim.solar.calculate_solar_position

Atmosphere
~~~~~~~~~~

.. autosummary::
   :nosignatures:

   pvsolarsim.atmosphere.calculate_clearsky_irradiance
   pvsolarsim.atmosphere.calculate_cloud_impact

Irradiance
~~~~~~~~~~

.. autosummary::
   :nosignatures:

   pvsolarsim.irradiance.calculate_poa_irradiance

Temperature
~~~~~~~~~~~

.. autosummary::
   :nosignatures:

   pvsolarsim.temperature.calculate_cell_temperature
   pvsolarsim.temperature.calculate_temperature_correction_factor

Power
~~~~~

.. autosummary::
   :nosignatures:

   pvsolarsim.calculate_power

Simulation
~~~~~~~~~~

.. autosummary::
   :nosignatures:

   pvsolarsim.simulate_annual
   pvsolarsim.simulation.generate_time_series

Weather
~~~~~~~

.. autosummary::
   :nosignatures:

   pvsolarsim.weather.CSVWeatherReader
   pvsolarsim.weather.JSONWeatherReader
   pvsolarsim.weather.PVGISClient
   pvsolarsim.weather.OpenWeatherMapClient
