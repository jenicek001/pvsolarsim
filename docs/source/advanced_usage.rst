Advanced Usage
==============

This guide covers advanced features and use cases for PVSolarSim.

Custom Weather Data
-------------------

Using CSV Files
~~~~~~~~~~~~~~~

Load weather data from custom CSV files with flexible column mapping:

.. code-block:: python

   from pvsolarsim import simulate_annual, Location, PVSystem

   location = Location(latitude=40.0, longitude=-105.0, altitude=1655)
   system = PVSystem(panel_area=20.0, panel_efficiency=0.20, tilt=35, azimuth=180)

   # Custom CSV with non-standard column names
   results = simulate_annual(
       location=location,
       system=system,
       year=2025,
       weather_source="csv",
       file_path="my_weather_data.csv",
       column_mapping={
           'ghi': 'GlobalHorizontalIrradiance',
           'dni': 'DirectNormalIrradiance',
           'dhi': 'DiffuseHorizontalIrradiance',
           'temp_air': 'AmbientTemperature',
           'wind_speed': 'WindSpeed',
           'cloud_cover': 'CloudCoverage'
       }
   )

Data Interpolation
~~~~~~~~~~~~~~~~~~

Handle missing data with interpolation:

.. code-block:: python

   from pvsolarsim.weather import interpolate_weather_data, detect_gaps
   import pandas as pd

   # Load weather data
   df = pd.read_csv('weather_data.csv', parse_dates=['timestamp'])
   df = df.set_index('timestamp')

   # Detect gaps
   gaps = detect_gaps(df.index, max_gap_minutes=120)
   print(f"Found {len(gaps)} gaps in data")

   # Interpolate missing values
   df_clean = interpolate_weather_data(
       df,
       method='linear',  # or 'spline', 'forward_fill', 'backward_fill'
       max_gap_hours=3   # Don't interpolate gaps larger than 3 hours
   )

Data Quality Checks
~~~~~~~~~~~~~~~~~~~

Validate weather data quality:

.. code-block:: python

   from pvsolarsim.weather import perform_quality_checks, create_quality_report
   from pvsolarsim import Location

   location = Location(latitude=40.0, longitude=-105.0, altitude=1655)

   # Perform quality checks
   quality_results = perform_quality_checks(
       weather_data=df,
       location=location
   )

   # Create report
   report = create_quality_report(quality_results)
   print(report)

   # Filter flagged data
   clean_df = df[~quality_results['has_issues']]

Multiple Model Comparison
--------------------------

Compare different clear-sky models:

.. code-block:: python

   from pvsolarsim.atmosphere import calculate_clearsky_irradiance
   from pvsolarsim.solar import calculate_solar_position
   from datetime import datetime
   import pytz

   timestamp = datetime(2025, 6, 21, 12, 0, tzinfo=pytz.UTC)
   position = calculate_solar_position(timestamp, 40.0, -105.0, 1655)

   # Compare models
   models = ['ineichen', 'simplified_solis']
   for model in models:
       irr = calculate_clearsky_irradiance(
           apparent_elevation=position.elevation,
           latitude=40.0,
           longitude=-105.0,
           altitude=1655,
           model=model
       )
       print(f"{model}: GHI={irr.ghi:.2f} W/m²")

Compare temperature models:

.. code-block:: python

   from pvsolarsim.temperature import calculate_cell_temperature

   models = ['faiman', 'sapm', 'pvsyst', 'generic_linear']
   for model in models:
       temp = calculate_cell_temperature(
           poa_global=800,
           temp_air=25,
           wind_speed=3,
           model=model
       )
       print(f"{model}: T_cell={temp:.2f}°C")

Batch Processing
----------------

Process multiple locations:

.. code-block:: python

   from pvsolarsim import Location, PVSystem, simulate_annual
   import pandas as pd

   # Define locations
   locations = [
       Location(40.0, -105.0, 1655, timezone="America/Denver", name="Boulder"),
       Location(34.0, -118.0, 100, timezone="America/Los_Angeles", name="LA"),
       Location(42.0, -71.0, 20, timezone="America/New_York", name="Boston"),
   ]

   system = PVSystem(panel_area=20.0, panel_efficiency=0.20, tilt=35, azimuth=180)

   # Simulate all locations
   results_dict = {}
   for loc in locations:
       results = simulate_annual(
           location=loc,
           system=system,
           year=2025,
           weather_source='clear_sky'
       )
       results_dict[loc.name] = results.statistics.total_energy_kwh

   # Create comparison dataframe
   comparison = pd.DataFrame.from_dict(results_dict, orient='index', columns=['Energy (kWh)'])
   print(comparison.sort_values('Energy (kWh)', ascending=False))

Process multiple system configurations:

.. code-block:: python

   import numpy as np

   location = Location(40.0, -105.0, 1655, timezone="America/Denver")
   tilts = np.arange(0, 60, 5)  # 0° to 55° in 5° steps

   results = []
   for tilt in tilts:
       system = PVSystem(panel_area=20.0, panel_efficiency=0.20, tilt=tilt, azimuth=180)
       sim = simulate_annual(location, system, 2025, weather_source='clear_sky')
       results.append({
           'tilt': tilt,
           'energy': sim.statistics.total_energy_kwh,
           'capacity_factor': sim.statistics.capacity_factor
       })

   # Find optimal tilt
   df = pd.DataFrame(results)
   optimal = df.loc[df['energy'].idxmax()]
   print(f"Optimal tilt: {optimal['tilt']}° ({optimal['energy']:.2f} kWh)")

Custom Analysis
---------------

Monthly Energy Profile
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   results = simulate_annual(location, system, 2025, weather_source='clear_sky')
   
   # Get monthly summary
   monthly = results.get_monthly_summary()
   print(monthly)

   # Plot monthly energy (requires matplotlib)
   import matplotlib.pyplot as plt
   
   monthly.plot(y='energy_kwh', kind='bar', title='Monthly Energy Production')
   plt.xlabel('Month')
   plt.ylabel('Energy (kWh)')
   plt.tight_layout()
   plt.savefig('monthly_energy.png')

Daily Energy Profile
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Get daily summary
   daily = results.get_daily_summary()
   
   # Summer vs Winter comparison
   summer_avg = daily.loc['2025-06-01':'2025-08-31', 'energy_kwh'].mean()
   winter_avg = daily.loc['2025-12-01':'2025-02-28', 'energy_kwh'].mean()
   print(f"Summer avg: {summer_avg:.2f} kWh/day")
   print(f"Winter avg: {winter_avg:.2f} kWh/day")

Export and Integration
----------------------

Export to CSV
~~~~~~~~~~~~~

.. code-block:: python

   # Export full time series
   results.export_csv('annual_production.csv')

   # Export monthly summary
   monthly = results.get_monthly_summary()
   monthly.to_csv('monthly_summary.csv')

Export to JSON
~~~~~~~~~~~~~~

.. code-block:: python

   import json

   # Create summary dictionary
   summary = {
       'location': {
           'latitude': location.latitude,
           'longitude': location.longitude,
           'altitude': location.altitude
       },
       'system': {
           'panel_area': system.panel_area,
           'efficiency': system.panel_efficiency,
           'tilt': system.tilt,
           'azimuth': system.azimuth
       },
       'results': {
           'annual_energy_kwh': results.statistics.total_energy_kwh,
           'capacity_factor': results.statistics.capacity_factor,
           'peak_power_w': results.statistics.peak_power_w
       }
   }

   with open('simulation_summary.json', 'w') as f:
       json.dump(summary, f, indent=2)

Integration with Databases
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import sqlite3

   # Store results in SQLite
   conn = sqlite3.connect('pv_simulations.db')
   results.time_series.to_sql('simulation_2025', conn, if_exists='replace')
   conn.close()

Performance Optimization
------------------------

Use Coarser Time Intervals
~~~~~~~~~~~~~~~~~~~~~~~~~~~

For quick estimates, use hourly intervals instead of 5-minute:

.. code-block:: python

   # Quick estimate (~30 seconds)
   results_hourly = simulate_annual(
       location, system, 2025,
       interval_minutes=60,  # Hourly
       weather_source='clear_sky'
   )

   # Detailed simulation (~13 minutes)
   results_detailed = simulate_annual(
       location, system, 2025,
       interval_minutes=5,  # 5-minute
       weather_source='clear_sky'
   )

   # Compare results
   print(f"Hourly: {results_hourly.statistics.total_energy_kwh:.2f} kWh")
   print(f"5-min: {results_detailed.statistics.total_energy_kwh:.2f} kWh")
   print(f"Difference: {abs(results_hourly.statistics.total_energy_kwh - results_detailed.statistics.total_energy_kwh):.2f} kWh")

Progress Callbacks
~~~~~~~~~~~~~~~~~~

Monitor long-running simulations:

.. code-block:: python

   def progress_callback(progress):
       print(f"Progress: {progress*100:.1f}%", end='\\r')

   results = simulate_annual(
       location, system, 2025,
       interval_minutes=5,
       weather_source='clear_sky',
       progress_callback=progress_callback
   )

Advanced System Modeling
------------------------

Soiling and Degradation
~~~~~~~~~~~~~~~~~~~~~~~~

Account for panel soiling and age-related degradation:

.. code-block:: python

   result = calculate_power(
       location=location,
       system=system,
       timestamp=timestamp,
       ambient_temp=25,
       wind_speed=3,
       cloud_cover=20,
       soiling_factor=0.95,      # 5% soiling loss
       degradation_factor=0.985,  # 1.5% degradation (old system)
       inverter_efficiency=0.96
   )

Different Panel Orientations
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Simulate East-West split systems:

.. code-block:: python

   # East-facing array
   system_east = PVSystem(panel_area=10.0, panel_efficiency=0.20, tilt=15, azimuth=90)
   results_east = simulate_annual(location, system_east, 2025, weather_source='clear_sky')

   # West-facing array
   system_west = PVSystem(panel_area=10.0, panel_efficiency=0.20, tilt=15, azimuth=270)
   results_west = simulate_annual(location, system_west, 2025, weather_source='clear_sky')

   # Combined output
   total_energy = results_east.statistics.total_energy_kwh + results_west.statistics.total_energy_kwh
   print(f"Total E-W system energy: {total_energy:.2f} kWh")

Next Steps
----------

* Review the :doc:`mathematical_background` for detailed equations
* Check the :doc:`faq` for common questions
* See the :doc:`tutorials` for Jupyter notebook examples
