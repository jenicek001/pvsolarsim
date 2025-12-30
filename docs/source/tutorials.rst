Tutorials
=========

This section contains Jupyter notebook tutorials for PVSolarSim.

Tutorial Notebooks
------------------

The following Jupyter notebooks are available in the ``examples/`` directory:

1. **Basic Calculations**
   
   - Solar position calculation
   - Clear-sky irradiance
   - POA irradiance for tilted panels
   - File: ``01_basic_calculations.ipynb``

2. **Power and Temperature**
   
   - Cell temperature modeling
   - Instantaneous power calculation
   - Comparison of temperature models
   - File: ``02_power_and_temperature.ipynb``

3. **Annual Simulation with Clear Sky**
   
   - Full year simulation
   - Statistical analysis
   - Monthly and daily summaries
   - File: ``03_annual_simulation_clear_sky.ipynb``

4. **Weather Data Integration**
   
   - Loading CSV weather data
   - Using PVGIS TMY data
   - Data quality checks
   - Interpolation and gap filling
   - File: ``04_weather_integration.ipynb``

5. **Multi-Location Comparison**
   
   - Comparing multiple locations
   - Optimal tilt angle analysis
   - Performance ratio analysis
   - File: ``05_multi_location_comparison.ipynb``

Running the Tutorials
----------------------

To run the tutorials, you need to install Jupyter:

.. code-block:: bash

   pip install jupyter matplotlib

Then launch Jupyter:

.. code-block:: bash

   cd pvsolarsim/examples
   jupyter notebook

The tutorials will open in your web browser.

Tutorial Examples
-----------------

Here are quick code snippets from the tutorials:

Example 1: Solar Position Time Series
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from pvsolarsim.solar import calculate_solar_position
   import pandas as pd
   import matplotlib.pyplot as plt

   # Generate timestamps for a day
   times = pd.date_range('2025-06-21', periods=24*60, freq='1min', tz='UTC')
   
   # Calculate solar position for each timestamp
   positions = [
       calculate_solar_position(t, latitude=40.0, longitude=-105.0, altitude=1655)
       for t in times
   ]
   
   # Extract elevations
   elevations = [p.elevation for p in positions]
   
   # Plot sun path
   plt.figure(figsize=(12, 6))
   plt.plot(times, elevations)
   plt.xlabel('Time')
   plt.ylabel('Solar Elevation (°)')
   plt.title('Solar Elevation on Summer Solstice')
   plt.grid(True)
   plt.tight_layout()
   plt.show()

Example 2: Tilt Angle Optimization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from pvsolarsim import Location, PVSystem, simulate_annual
   import numpy as np
   import matplotlib.pyplot as plt

   location = Location(40.0, -105.0, 1655, timezone="America/Denver")
   tilts = np.arange(0, 61, 5)  # 0° to 60° in 5° steps
   
   energies = []
   for tilt in tilts:
       system = PVSystem(panel_area=20.0, panel_efficiency=0.20, tilt=tilt, azimuth=180)
       results = simulate_annual(location, system, 2025, weather_source='clear_sky')
       energies.append(results.statistics.total_energy_kwh)
   
   # Plot results
   plt.figure(figsize=(10, 6))
   plt.plot(tilts, energies, 'o-')
   plt.xlabel('Tilt Angle (°)')
   plt.ylabel('Annual Energy (kWh)')
   plt.title('Energy Production vs Tilt Angle')
   plt.grid(True)
   plt.tight_layout()
   plt.show()
   
   # Find optimal
   optimal_idx = np.argmax(energies)
   print(f"Optimal tilt: {tilts[optimal_idx]}°")
   print(f"Max energy: {energies[optimal_idx]:.2f} kWh")

Example 3: Seasonal Variation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from pvsolarsim import Location, PVSystem, simulate_annual

   location = Location(40.0, -105.0, 1655, timezone="America/Denver")
   system = PVSystem(panel_area=20.0, panel_efficiency=0.20, tilt=35, azimuth=180)
   
   results = simulate_annual(location, system, 2025, weather_source='clear_sky')
   monthly = results.get_monthly_summary()
   
   # Plot seasonal variation
   monthly.plot(kind='bar', y='energy_kwh', figsize=(12, 6))
   plt.xlabel('Month')
   plt.ylabel('Energy (kWh)')
   plt.title('Monthly Energy Production')
   plt.xticks(rotation=45)
   plt.tight_layout()
   plt.show()

Example 4: Weather Data Quality Analysis
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from pvsolarsim.weather import perform_quality_checks, create_quality_report
   from pvsolarsim import Location
   import pandas as pd

   # Load weather data
   df = pd.read_csv('weather_data.csv', parse_dates=['timestamp'])
   df = df.set_index('timestamp')
   
   location = Location(40.0, -105.0, 1655)
   
   # Perform quality checks
   quality_results = perform_quality_checks(df, location)
   
   # Create and print report
   report = create_quality_report(quality_results)
   print(report)
   
   # Visualize issues
   issues_by_type = quality_results.groupby('issue_type').size()
   issues_by_type.plot(kind='bar', title='Data Quality Issues by Type')
   plt.ylabel('Count')
   plt.tight_layout()
   plt.show()

Additional Resources
--------------------

For more examples, see:

* :doc:`quickstart` - Simple examples to get started
* :doc:`advanced_usage` - Advanced techniques and patterns
* ``examples/`` directory in the repository - Complete example scripts
