"""PVSolarSim - Python library for photovoltaic solar energy simulation.

This library provides comprehensive tools for simulating PV solar energy production,
including solar position calculations, atmospheric modeling, irradiance computations,
temperature modeling, and annual energy simulations.

Example:
    >>> import pvsolarsim
    >>> location = pvsolarsim.Location(latitude=49.8, longitude=15.5, altitude=300)
    >>> system = pvsolarsim.PVSystem(panel_area=20.0, panel_efficiency=0.20, tilt=35.0, azimuth=180.0)
    >>> result = pvsolarsim.calculate_power(location, system, timestamp)
    >>> print(f"Power: {result.power_w:.2f} W")
"""

__version__ = "0.1.0"
__author__ = "jenicek001"
__license__ = "MIT"

from pvsolarsim.api.highlevel import calculate_power, simulate_annual
from pvsolarsim.core.location import Location
from pvsolarsim.core.pvsystem import PVSystem

__all__ = [
    "Location",
    "PVSystem",
    "calculate_power",
    "simulate_annual",
    "__version__",
]
