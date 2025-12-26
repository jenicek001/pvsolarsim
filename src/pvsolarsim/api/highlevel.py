"""High-level API for PVSolarSim.

This module provides simple, easy-to-use functions for common use cases.
"""

from datetime import datetime
from typing import Any, Optional

from pvsolarsim.atmosphere import ClearSkyModel
from pvsolarsim.core.location import Location
from pvsolarsim.core.pvsystem import PVSystem
from pvsolarsim.power import PowerResult, calculate_power as _calculate_power


def calculate_power(
    location: Location,
    system: PVSystem,
    timestamp: datetime,
    ambient_temp: float = 25.0,
    wind_speed: float = 1.0,
    cloud_cover: float = 0,
    ghi: Optional[float] = None,
    dni: Optional[float] = None,
    dhi: Optional[float] = None,
    soiling_factor: float = 1.0,
    degradation_factor: float = 1.0,
    inverter_efficiency: Optional[float] = None,
    **kwargs: Any,
) -> PowerResult:
    """Calculate instantaneous PV power output.

    Args:
        location: Geographic location
        system: PV system configuration
        timestamp: Time for calculation (timezone-aware)
        ambient_temp: Ambient air temperature (°C), default 25
        wind_speed: Wind speed (m/s), default 1.0
        cloud_cover: Cloud cover (0-100% or 0-1), default 0
        ghi: Global horizontal irradiance (W/m²), optional
        dni: Direct normal irradiance (W/m²), optional
        dhi: Diffuse horizontal irradiance (W/m²), optional
        soiling_factor: Soiling losses (0-1, 1=clean), default 1.0
        degradation_factor: Degradation factor (0-1), default 1.0
        inverter_efficiency: Inverter efficiency (0-1), optional
        **kwargs: Additional arguments (clearsky_model, diffuse_model, etc.)

    Returns:
        PowerResult with power, irradiance, and temperature data

    Example:
        >>> from pvsolarsim import Location, PVSystem, calculate_power
        >>> from datetime import datetime
        >>> import pytz
        >>>
        >>> location = Location(latitude=49.8, longitude=15.5, altitude=300)
        >>> system = PVSystem(panel_area=20.0, panel_efficiency=0.20, tilt=35, azimuth=180)
        >>> timestamp = datetime(2025, 6, 21, 12, 0, tzinfo=pytz.UTC)
        >>> result = calculate_power(location, system, timestamp, ambient_temp=25)
        >>> print(f"Power: {result.power_w:.2f} W")
    """
    return _calculate_power(
        location=location,
        system=system,
        timestamp=timestamp,
        ambient_temp=ambient_temp,
        wind_speed=wind_speed,
        cloud_cover=cloud_cover,
        ghi=ghi,
        dni=dni,
        dhi=dhi,
        soiling_factor=soiling_factor,
        degradation_factor=degradation_factor,
        inverter_efficiency=inverter_efficiency,
        **kwargs,
    )


def simulate_annual(
    location: Location,
    system: PVSystem,
    year: int = 2025,
    interval: int = 5,
    weather_source: str = "clear_sky",
    **kwargs: Any,
) -> Any:
    """Run annual PV energy simulation.

    Args:
        location: Geographic location
        system: PV system configuration
        year: Year for simulation
        interval: Time interval in minutes (1-60)
        weather_source: Weather data source
        **kwargs: Additional arguments for weather source

    Returns:
        AnnualResults with time series data and summary statistics

    Example:
        >>> results = simulate_annual(location, system, year=2025, interval=5)
        >>> print(f"Total: {results.total_energy_kwh:.2f} kWh/year")
    """
    # TODO: Implementation in Week 7
    raise NotImplementedError("Coming in Week 7 (Time Series & Annual Simulation)")
