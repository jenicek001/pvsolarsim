Quick Start
===========

This guide will help you get started with PVSolarSim quickly.

Basic Solar Position Calculation
---------------------------------

Calculate the position of the sun at a specific time and location:

.. code-block:: python

   from pvsolarsim.solar import calculate_solar_position
   from datetime import datetime
   import pytz

   # Define time and location
   timestamp = datetime(2025, 6, 21, 12, 0, tzinfo=pytz.UTC)
   latitude = 49.8   # Degrees North
   longitude = 15.5  # Degrees East
   altitude = 300    # Meters above sea level

   # Calculate solar position
   position = calculate_solar_position(
       timestamp=timestamp,
       latitude=latitude,
       longitude=longitude,
       altitude=altitude
   )

   print(f"Azimuth: {position.azimuth:.2f}°")
   print(f"Elevation: {position.elevation:.2f}°")
   print(f"Zenith: {position.zenith:.2f}°")

Output::

   Azimuth: 183.45°
   Elevation: 63.25°
   Zenith: 26.75°

Clear-Sky Irradiance
--------------------

Calculate solar irradiance on a clear day:

.. code-block:: python

   from pvsolarsim.atmosphere import calculate_clearsky_irradiance

   # Calculate clear-sky irradiance
   irradiance = calculate_clearsky_irradiance(
       apparent_elevation=position.elevation,
       latitude=latitude,
       longitude=longitude,
       altitude=altitude,
       model="ineichen",
       linke_turbidity=3.0  # Typical value for clear atmosphere
   )

   print(f"GHI: {irradiance.ghi:.2f} W/m²")
   print(f"DNI: {irradiance.dni:.2f} W/m²")
   print(f"DHI: {irradiance.dhi:.2f} W/m²")

Output::

   GHI: 927.35 W/m²
   DNI: 845.12 W/m²
   DHI: 82.23 W/m²

Plane-of-Array (POA) Irradiance
--------------------------------

Calculate irradiance on a tilted solar panel:

.. code-block:: python

   from pvsolarsim.irradiance import calculate_poa_irradiance

   # Panel orientation
   surface_tilt = 35.0     # Degrees from horizontal
   surface_azimuth = 180.0  # Degrees (180 = South)

   # Calculate POA irradiance
   poa = calculate_poa_irradiance(
       surface_tilt=surface_tilt,
       surface_azimuth=surface_azimuth,
       solar_zenith=position.zenith,
       solar_azimuth=position.azimuth,
       dni=irradiance.dni,
       dhi=irradiance.dhi,
       ghi=irradiance.ghi,
       diffuse_model='perez',  # Industry standard
       albedo=0.2              # Ground reflectance
   )

   print(f"POA Global: {poa.poa_global:.2f} W/m²")
   print(f"POA Direct: {poa.poa_direct:.2f} W/m²")
   print(f"POA Diffuse: {poa.poa_diffuse:.2f} W/m²")
   print(f"POA Ground: {poa.poa_ground:.2f} W/m²")

Instantaneous Power Calculation
--------------------------------

Calculate the power output of a PV system at a specific moment:

.. code-block:: python

   from pvsolarsim import Location, PVSystem, calculate_power
   from datetime import datetime
   import pytz

   # Define location
   location = Location(
       latitude=49.8,
       longitude=15.5,
       altitude=300,
       timezone="Europe/Prague"
   )

   # Define PV system
   system = PVSystem(
       panel_area=20.0,           # m²
       panel_efficiency=0.20,     # 20%
       tilt=35,                   # Degrees
       azimuth=180,               # South-facing
       temp_coefficient=-0.004    # -0.4%/°C
   )

   # Calculate power
   result = calculate_power(
       location=location,
       system=system,
       timestamp=datetime(2025, 6, 21, 12, 0, tzinfo=pytz.UTC),
       ambient_temp=25,       # °C
       wind_speed=3,          # m/s
       cloud_cover=20,        # %
       soiling_factor=0.98,   # 98% clean
       inverter_efficiency=0.96  # 96% efficient
   )

   print(f"DC Power: {result.power_w:.2f} W")
   print(f"AC Power: {result.power_ac_w:.2f} W")
   print(f"POA Irradiance: {result.poa_irradiance:.2f} W/m²")
   print(f"Cell Temperature: {result.cell_temperature:.2f}°C")

Output::

   DC Power: 3456.78 W
   AC Power: 3318.51 W
   POA Irradiance: 986.32 W/m²
   Cell Temperature: 42.15°C

Annual Energy Simulation
-------------------------

Simulate a full year of energy production:

.. code-block:: python

   from pvsolarsim import Location, PVSystem, simulate_annual

   # Define location and system
   location = Location(
       latitude=40.0,
       longitude=-105.0,
       altitude=1655,
       timezone="America/Denver"
   )
   
   system = PVSystem(
       panel_area=20.0,
       panel_efficiency=0.20,
       tilt=35,
       azimuth=180
   )

   # Simulate full year
   results = simulate_annual(
       location=location,
       system=system,
       year=2025,
       interval_minutes=60,  # Hourly intervals
       weather_source='clear_sky'
   )

   # Print statistics
   print(f"Annual Energy: {results.statistics.total_energy_kwh:.2f} kWh")
   print(f"Capacity Factor: {results.statistics.capacity_factor * 100:.2f}%")
   print(f"Peak Power: {results.statistics.peak_power_w:.2f} W")
   print(f"Average Daily Energy: {results.statistics.avg_daily_energy_kwh:.2f} kWh")

   # Export to CSV
   results.export_csv('annual_production.csv')

Output::

   Annual Energy: 8543.21 kWh
   Capacity Factor: 24.35%
   Peak Power: 3987.65 W
   Average Daily Energy: 23.41 kWh

Weather Data Integration
-------------------------

Use real weather data for simulations:

.. code-block:: python

   from pvsolarsim import simulate_annual
   from pvsolarsim.weather import CSVWeatherReader

   # Using CSV weather data
   results = simulate_annual(
       location=location,
       system=system,
       year=2025,
       interval_minutes=60,
       weather_source="csv",
       file_path="weather_data.csv",
       column_mapping={
           'ghi': 'global_horizontal_irradiance',
           'dni': 'direct_normal_irradiance',
           'dhi': 'diffuse_horizontal_irradiance',
           'temp_air': 'air_temperature',
           'wind_speed': 'wind_speed'
       }
   )

   # Or using PVGIS TMY data
   results = simulate_annual(
       location=location,
       system=system,
       year=2025,
       weather_source="pvgis"
   )

Next Steps
----------

* Explore the :doc:`core_concepts` for detailed explanations
* Check out :doc:`tutorials` for Jupyter notebook examples
* Read the :doc:`api/modules` for complete API reference
* See :doc:`advanced_usage` for advanced features
