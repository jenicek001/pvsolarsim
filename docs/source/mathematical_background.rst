Mathematical Background
=======================

This page provides detailed mathematical formulations for the models used in PVSolarSim.

Solar Position
--------------

PVSolarSim uses the Solar Position Algorithm (SPA) developed by NREL [Reda2004]_.

The solar position is defined by two angles:

* **Zenith angle** (:math:`\\theta_z`): Angle from vertical (0° = overhead)
* **Azimuth angle** (:math:`\\gamma_s`): Horizontal angle from North (clockwise)

The elevation angle is complementary to zenith:

.. math::

   \\alpha_s = 90° - \\theta_z

The SPA algorithm accounts for:

* Earth's orbit eccentricity
* Axial tilt (obliquity)
* Nutation and aberration
* Atmospheric refraction

**Reference:** [Reda2004]_ Reda, I., & Andreas, A. (2004). Solar position algorithm for solar radiation applications. *Solar Energy*, 76(5), 577-589.

Air Mass
--------

Air mass represents the path length of sunlight through the atmosphere relative to the vertical path.

Relative Air Mass (Kasten-Young)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. math::

   AM_{rel} = \\frac{1}{\\cos(\\theta_z) + 0.50572(96.07995 - \\theta_z)^{-1.6364}}

Absolute Air Mass
~~~~~~~~~~~~~~~~~

.. math::

   AM_{abs} = AM_{rel} \\times \\frac{P}{P_0}

where :math:`P` is atmospheric pressure and :math:`P_0 = 101325` Pa is standard pressure.

Clear-Sky Irradiance
--------------------

Ineichen Clear-Sky Model
~~~~~~~~~~~~~~~~~~~~~~~~~

The Ineichen model uses the Linke turbidity parameter.

Direct Normal Irradiance:

.. math::

   DNI = B \\times e^{-0.09 \\times AM \\times (T_L - 1)}

where:

* :math:`B` = extraterrestrial direct normal irradiance
* :math:`AM` = air mass
* :math:`T_L` = Linke turbidity

Global Horizontal Irradiance:

.. math::

   GHI = DHI + DNI \\times \\cos(\\theta_z)

**Reference:** Ineichen, P., & Perez, R. (2002). A new airmass independent formulation for the Linke turbidity coefficient. *Solar Energy*, 73(3), 151-157.

Simplified Solis Model
~~~~~~~~~~~~~~~~~~~~~~

Uses aerosol optical depth (AOD) instead of Linke turbidity:

.. math::

   DNI = I_0 \\times \\exp\\left(-\\frac{\\tau_{aer}(\\lambda)}{\\sin(\\alpha_s)^{k_a}}\\right)

where :math:`\\tau_{aer}` is aerosol optical depth and :math:`k_a` is the aerosol extinction coefficient.

Cloud Cover Effects
-------------------

Campbell-Norman Model
~~~~~~~~~~~~~~~~~~~~~

.. math::

   I_{cloudy} = I_{clear} \\times (1 - C_{eff})

where:

.. math::

   C_{eff} = a \\times N^b

* :math:`N` = cloud cover fraction (0-1)
* :math:`a, b` = empirical coefficients

Plane-of-Array (POA) Irradiance
--------------------------------

Total POA irradiance:

.. math::

   POA_{total} = POA_{beam} + POA_{diffuse} + POA_{ground}

Beam Component
~~~~~~~~~~~~~~

.. math::

   POA_{beam} = DNI \\times \\cos(AOI) \\times IAM(AOI)

where AOI (Angle of Incidence) is:

.. math::

   \\cos(AOI) = \\sin(\\delta) \\sin(\\phi) \\cos(\\beta) - \\sin(\\delta) \\cos(\\phi) \\sin(\\beta) \\cos(\\gamma)
   + \\cos(\\delta) \\cos(\\phi) \\cos(\\beta) \\cos(\\omega) + \\cos(\\delta) \\sin(\\phi) \\sin(\\beta) \\cos(\\gamma) \\cos(\\omega)
   + \\cos(\\delta) \\sin(\\beta) \\sin(\\gamma) \\sin(\\omega)

where:

* :math:`\\delta` = solar declination
* :math:`\\phi` = latitude
* :math:`\\beta` = surface tilt
* :math:`\\gamma` = surface azimuth
* :math:`\\omega` = hour angle

Diffuse Component (Perez Model)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. math::

   POA_{diffuse} = DHI \\times [(1 - F_1) \\times \\frac{1 + \\cos(\\beta)}{2} + F_1 \\times \\frac{a}{b} + F_2 \\times \\sin(\\beta)]

where :math:`F_1` and :math:`F_2` are circumsolar and horizon brightening coefficients.

**Reference:** Perez, R., et al. (1990). Modeling daylight availability and irradiance components from direct and global irradiance. *Solar Energy*, 44(5), 271-289.

Ground-Reflected Component
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. math::

   POA_{ground} = GHI \\times \\rho \\times \\frac{1 - \\cos(\\beta)}{2}

where :math:`\\rho` is ground albedo (typically 0.2).

Incidence Angle Modifier (IAM)
-------------------------------

Physical Model (Fresnel)
~~~~~~~~~~~~~~~~~~~~~~~~

.. math::

   IAM(AOI) = 1 - \\left[\\frac{1}{2} \\left(\\frac{\\sin^2(AOI - \\theta_r)}{\\sin^2(AOI + \\theta_r)} + \\frac{\\tan^2(AOI - \\theta_r)}{\\tan^2(AOI + \\theta_r)}\\right)\\right]

where :math:`\\theta_r` is the refraction angle from Snell's law:

.. math::

   n_1 \\sin(AOI) = n_2 \\sin(\\theta_r)

ASHRAE Model
~~~~~~~~~~~~

.. math::

   IAM(AOI) = 1 - b_0 \\left(\\frac{1}{\\cos(AOI)} - 1\\right)

where :math:`b_0 \\approx 0.05` for typical glass-covered modules.

Cell Temperature
----------------

Faiman Model
~~~~~~~~~~~~

Energy balance considering radiative and convective heat transfer:

.. math::

   T_{cell} = T_{amb} + \\frac{POA}{U_0 + U_1 \\times v_{wind}}

where:

* :math:`U_0` = constant heat loss coefficient (W/m²/K)
* :math:`U_1` = convective heat loss coefficient (W·s/m³/K)
* :math:`v_{wind}` = wind speed (m/s)

**Reference:** Faiman, D. (2008). Assessing the outdoor operating temperature of photovoltaic modules. *Progress in Photovoltaics*, 16(4), 307-315.

SAPM Model
~~~~~~~~~~

Sandia Array Performance Model:

.. math::

   T_{cell} = T_{amb} + POA \\times e^{a + b \\times v_{wind}}

where :math:`a` and :math:`b` are module-specific parameters.

**Reference:** King, D. L., et al. (2004). Sandia photovoltaic array performance model. *SAND Report*, 2004-3535.

PVsyst Model
~~~~~~~~~~~~

.. math::

   T_{cell} = T_{amb} + \\frac{POA}{U_c + U_v \\times v_{wind}} \\times (1 - \\eta_{stc})

where :math:`\\eta_{stc}` is the efficiency at standard test conditions.

Power Output
------------

DC Power
~~~~~~~~

.. math::

   P_{DC} = POA \\times A_{panel} \\times \\eta_{stc} \\times f_{temp} \\times f_{soil} \\times f_{degrad}

Temperature Correction Factor
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. math::

   f_{temp} = 1 + \\gamma \\times (T_{cell} - 25)

where :math:`\\gamma` is the temperature coefficient (typically -0.004/°C for silicon).

AC Power
~~~~~~~~

.. math::

   P_{AC} = P_{DC} \\times \\eta_{inv}

where :math:`\\eta_{inv}` is the inverter efficiency.

Performance Metrics
-------------------

Capacity Factor
~~~~~~~~~~~~~~~

.. math::

   CF = \\frac{E_{actual}}{P_{rated} \\times 8760}

where :math:`E_{actual}` is annual energy production and :math:`P_{rated}` is rated power.

Performance Ratio
~~~~~~~~~~~~~~~~~

.. math::

   PR = \\frac{Y_f}{Y_r}

where:

* :math:`Y_f` = Final yield (kWh/kWp)
* :math:`Y_r` = Reference yield (hours of equivalent rated power)

Specific Yield
~~~~~~~~~~~~~~

.. math::

   Y_{specific} = \\frac{E_{annual}}{P_{rated}}

measured in kWh/kWp.

References
----------

.. [Reda2004] Reda, I., & Andreas, A. (2004). Solar position algorithm for solar radiation applications. Solar Energy, 76(5), 577-589.

Additional references are provided throughout the text.
