Core Concepts
=============

This page explains the fundamental concepts behind PVSolarSim.

Solar Position
--------------

The position of the sun in the sky is critical for PV simulations. PVSolarSim uses the **Solar Position Algorithm (SPA)** 
developed by NREL, which provides accuracy better than 0.01° between years 2000 and 6000.

Solar position is defined by two angles:

* **Azimuth**: Horizontal angle measured clockwise from North (0° = North, 90° = East, 180° = South, 270° = West)
* **Elevation** (or altitude): Vertical angle from the horizon (0° = horizon, 90° = directly overhead)
* **Zenith**: Complementary to elevation (zenith = 90° - elevation)

The solar position depends on:

1. **Time**: Date and time (must be timezone-aware)
2. **Location**: Latitude, longitude, and altitude
3. **Atmospheric refraction**: Bending of light through the atmosphere

Example
~~~~~~~

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

Atmospheric Modeling
--------------------

Solar radiation is affected by the atmosphere through:

* **Scattering**: Rayleigh (molecular) and Mie (aerosol) scattering
* **Absorption**: By water vapor, ozone, and other gases
* **Air mass**: Path length through the atmosphere

Clear-Sky Models
~~~~~~~~~~~~~~~~

PVSolarSim supports multiple clear-sky models:

1. **Ineichen Model** (default)
   
   * Uses Linke turbidity parameter
   * Industry standard, widely validated
   * Best for European conditions

2. **Simplified Solis Model**
   
   * Uses aerosol optical depth (AOD)
   * More physically based
   * Requires more detailed atmospheric data

Output Components
~~~~~~~~~~~~~~~~~

All clear-sky models return three irradiance components:

* **GHI** (Global Horizontal Irradiance): Total irradiance on a horizontal surface
* **DNI** (Direct Normal Irradiance): Direct beam irradiance perpendicular to sun rays
* **DHI** (Diffuse Horizontal Irradiance): Scattered irradiance on a horizontal surface

Relationship: ``GHI ≈ DNI × cos(zenith) + DHI``

Cloud Cover Effects
-------------------

Clouds reduce solar irradiance. PVSolarSim provides three cloud cover models:

1. **Campbell-Norman**: Physics-based model accounting for cloud thickness
2. **Simple Linear**: Fast approximation (good for quick estimates)
3. **Kasten-Czeplak**: Validated for European conditions

Cloud cover can be specified as:

* Percentage (0-100%)
* Fraction (0-1)
* Oktas (0-8)

Plane-of-Array (POA) Irradiance
--------------------------------

Solar panels are typically tilted, not horizontal. POA irradiance is the total irradiance on the tilted panel surface.

Components of POA Irradiance
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. math::

   POA_{total} = POA_{beam} + POA_{diffuse} + POA_{ground}

1. **Beam Component**: Direct sunlight projected onto the panel

   .. math::

      POA_{beam} = DNI \\times \\cos(AOI) \\times IAM(AOI)

   where:
   
   * AOI = Angle of Incidence (angle between sun rays and panel normal)
   * IAM = Incidence Angle Modifier (accounts for reflection losses)

2. **Diffuse Component**: Scattered light from the sky
   
   * Depends on the diffuse model (Isotropic, Perez, Hay-Davies)
   * Perez model is the industry standard

3. **Ground-Reflected Component**: Light reflected from the ground

   .. math::

      POA_{ground} = GHI \\times albedo \\times \\frac{1 - \\cos(tilt)}{2}

Diffuse Models
~~~~~~~~~~~~~~

* **Isotropic**: Assumes uniform sky brightness (simple, less accurate)
* **Perez**: Anisotropic model with circumsolar and horizon brightening (industry standard)
* **Hay-Davies**: Weighted average of isotropic and circumsolar components

Incidence Angle Modifiers (IAM)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

IAM accounts for increased reflection at high angles of incidence:

* **ASHRAE**: Simple polynomial model
* **Physical**: Based on Fresnel equations (most accurate)
* **Martin-Ruiz**: Good balance of accuracy and simplicity

Temperature Effects
-------------------

PV panel efficiency decreases with increasing cell temperature.

Temperature Coefficient
~~~~~~~~~~~~~~~~~~~~~~~

Most silicon panels have a temperature coefficient around -0.4%/°C to -0.5%/°C.

.. math::

   P_{corrected} = P_{STC} \\times [1 + \\gamma \\times (T_{cell} - 25)]

where:

* :math:`P_{STC}` = Power at Standard Test Conditions (25°C)
* :math:`\\gamma` = Temperature coefficient (e.g., -0.004 for -0.4%/°C)
* :math:`T_{cell}` = Cell temperature (°C)

Cell Temperature Models
~~~~~~~~~~~~~~~~~~~~~~~

PVSolarSim supports four models:

1. **Faiman**: Radiative and convective heat transfer
2. **SAPM** (Sandia): Widely used, validated against field data
3. **PVsyst**: Accounts for efficiency and absorption
4. **Generic Linear**: Simple model using NOCT

Factors affecting cell temperature:

* POA irradiance (higher → hotter)
* Ambient temperature (higher → hotter)
* Wind speed (higher → cooler)
* Panel mounting (roof-integrated → hotter)

Power Calculation
-----------------

Instantaneous DC power is calculated as:

.. math::

   P_{DC} = POA_{global} \\times A_{panel} \\times \\eta_{panel} \\times f_{temp} \\times f_{soiling} \\times f_{degradation}

where:

* :math:`A_{panel}` = Panel area (m²)
* :math:`\\eta_{panel}` = Panel efficiency at STC
* :math:`f_{temp}` = Temperature correction factor
* :math:`f_{soiling}` = Soiling factor (0-1)
* :math:`f_{degradation}` = Degradation factor (0-1)

AC power includes inverter efficiency:

.. math::

   P_{AC} = P_{DC} \\times \\eta_{inverter}

Annual Simulation
-----------------

An annual simulation calculates power at regular intervals throughout the year.

Time Series Generation
~~~~~~~~~~~~~~~~~~~~~~

PVSolarSim generates timezone-aware timestamps at configurable intervals:

* Common intervals: 1 min, 5 min, 15 min, 60 min (hourly)
* Finer intervals → more accurate energy estimate, longer computation time

Performance Metrics
~~~~~~~~~~~~~~~~~~~

1. **Total Energy** (kWh): Sum of energy over the year

   .. math::

      E_{total} = \\sum_{i=1}^{N} P_i \\times \\Delta t

2. **Capacity Factor**: Ratio of actual to theoretical maximum energy

   .. math::

      CF = \\frac{E_{actual}}{P_{rated} \\times 8760}

3. **Performance Ratio**: Actual vs. ideal energy accounting for irradiance

   .. math::

      PR = \\frac{E_{actual}}{E_{ideal}}

4. **Specific Yield** (kWh/kWp): Energy per installed capacity

Weather Data Integration
-------------------------

Real-world simulations require weather data including:

* Irradiance components (GHI, DNI, DHI)
* Ambient temperature
* Wind speed
* Cloud cover (optional if irradiance is provided)

Data Sources
~~~~~~~~~~~~

1. **Clear-Sky**: Theoretical clear-sky calculations (no weather data needed)
2. **CSV/JSON**: Custom weather data files
3. **PVGIS**: Free TMY data from European Commission
4. **OpenWeatherMap**: Real-time and historical weather API

Data Quality
~~~~~~~~~~~~

PVSolarSim includes data quality checks:

* Range validation (GHI 0-1500 W/m², temp -60 to 60°C, etc.)
* Consistency checks (GHI ≈ DNI×cos(zenith) + DHI)
* Nighttime irradiance detection
* Gap detection and interpolation

Next Steps
----------

* Try the :doc:`tutorials` for hands-on examples
* Check the :doc:`advanced_usage` guide for complex scenarios
* Review the :doc:`mathematical_background` for detailed equations
* Explore the :doc:`api/modules` for complete API documentation
