"""High-level API for PVSolarSim.

This module provides simple, easy-to-use functions for common use cases.
"""

from datetime import datetime
from typing import Any

from pvsolarsim.core.location import Location
from pvsolarsim.core.pvsystem import PVSystem


def calculate_power(
    location: Location,
    system: PVSystem,
    timestamp: datetime,
    weather_source: str = "clear_sky",
    **kwargs: Any,
) -> Any:
    """Calculate instantaneous PV power output.

    Args:
        location: Geographic location
        system: PV system configuration
        timestamp: Time for calculation
        weather_source: Weather data source ("clear_sky", "openweathermap", "csv")
        **kwargs: Additional arguments for weather source

    Returns:
        PowerResult with power, irradiance, and temperature data

    Example:
        >>> result = calculate_power(location, system, datetime(2025, 6, 21, 12, 0))
        >>> print(f"Power: {result.power_w:.2f} W")
    """
    # TODO: Implementation in Phase 2
    raise NotImplementedError("Coming in Phase 2 (Weeks 5-7)")


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
    # TODO: Implementation in Phase 2
    raise NotImplementedError("Coming in Phase 2 (Weeks 5-7)")
