"""Simulation engine for PV annual energy production.

This module provides the core simulation engine for calculating PV system
performance over extended periods using vectorized operations for efficiency.
"""

from datetime import datetime
from typing import Any, Callable, Optional

import pandas as pd
import pytz

from pvsolarsim.core.location import Location
from pvsolarsim.core.pvsystem import PVSystem
from pvsolarsim.power import calculate_power
from pvsolarsim.simulation.results import AnnualStatistics, SimulationResult
from pvsolarsim.simulation.timeseries import generate_time_series


def simulate_annual(
    location: Location,
    system: PVSystem,
    year: int = 2025,
    interval_minutes: int = 5,
    weather_source: str = "clear_sky",
    ambient_temp: float = 25.0,
    wind_speed: float = 1.0,
    cloud_cover: float = 0.0,
    soiling_factor: float = 1.0,
    degradation_factor: float = 1.0,
    inverter_efficiency: Optional[float] = None,
    progress_callback: Optional[Callable[[float], None]] = None,
    **kwargs: Any,
) -> SimulationResult:
    """Simulate annual PV energy production.

    Runs a full year simulation with the specified time interval, calculating
    power output at each timestamp and aggregating results into comprehensive
    statistics.

    Parameters
    ----------
    location : Location
        Geographic location of PV system
    system : PVSystem
        PV system configuration
    year : int, default 2025
        Year to simulate
    interval_minutes : int, default 5
        Time interval in minutes (1-60 recommended)
    weather_source : str, default 'clear_sky'
        Weather data source ('clear_sky' only in this version)
    ambient_temp : float, default 25.0
        Ambient temperature in °C (used for clear_sky)
    wind_speed : float, default 1.0
        Wind speed in m/s (used for clear_sky)
    cloud_cover : float, default 0.0
        Cloud cover 0-100% or 0-1 (used for clear_sky)
    soiling_factor : float, default 1.0
        Soiling losses (0-1, 1=clean)
    degradation_factor : float, default 1.0
        Degradation factor (0-1)
    inverter_efficiency : float, optional
        Inverter efficiency (0-1), if provided calculates AC power
    progress_callback : callable, optional
        Function called with progress (0.0 to 1.0)
    **kwargs : dict
        Additional parameters for future weather sources

    Returns
    -------
    SimulationResult
        Complete simulation results with time series and statistics

    Raises
    ------
    ValueError
        If parameters are invalid
    NotImplementedError
        If weather_source is not 'clear_sky'

    Examples
    --------
    >>> from pvsolarsim import Location, PVSystem, simulate_annual
    >>>
    >>> location = Location(latitude=49.8, longitude=15.5, altitude=300)
    >>> system = PVSystem(panel_area=20.0, panel_efficiency=0.20, tilt=35, azimuth=180)
    >>>
    >>> # Basic annual simulation with clear sky
    >>> results = simulate_annual(location, system, year=2025, interval_minutes=5)
    >>> print(f"Annual energy: {results.statistics.total_energy_kwh:.2f} kWh")
    >>> print(f"Capacity factor: {results.statistics.capacity_factor * 100:.2f}%")
    >>>
    >>> # With cloud cover and soiling
    >>> results = simulate_annual(
    ...     location, system, year=2025,
    ...     cloud_cover=20, soiling_factor=0.98
    ... )
    >>>
    >>> # Export to CSV
    >>> results.export_csv('annual_production.csv')
    """
    # Validate parameters
    if weather_source != "clear_sky":
        raise NotImplementedError(
            f"Weather source '{weather_source}' not yet implemented. "
            "Only 'clear_sky' is currently supported."
        )

    if not 1 <= interval_minutes <= 60:
        raise ValueError("interval_minutes must be between 1 and 60")

    # Generate time series for the year
    tz = pytz.timezone(location.timezone)
    start = tz.localize(datetime(year, 1, 1, 0, 0, 0))
    end = tz.localize(datetime(year, 12, 31, 23, 59, 59))

    times = generate_time_series(
        start=start, end=end, interval_minutes=interval_minutes, timezone=location.timezone
    )

    # Calculate power for each timestamp
    power_results = []
    total_steps = len(times)

    for i, timestamp in enumerate(times):
        # Calculate instantaneous power
        result = calculate_power(
            location=location,
            system=system,
            timestamp=timestamp,
            ambient_temp=ambient_temp,
            wind_speed=wind_speed,
            cloud_cover=cloud_cover,
            soiling_factor=soiling_factor,
            degradation_factor=degradation_factor,
            inverter_efficiency=inverter_efficiency,
            **kwargs,
        )

        power_results.append(
            {
                "timestamp": timestamp,
                "power_w": result.power_w,
                "power_ac_w": result.power_ac_w if result.power_ac_w is not None else result.power_w,
                "poa_irradiance": result.poa_irradiance,
                "cell_temperature": result.cell_temperature,
                "ghi": result.ghi,
                "dni": result.dni,
                "dhi": result.dhi,
                "solar_elevation": result.solar_elevation,
            }
        )

        # Report progress
        if progress_callback and i % 1000 == 0:
            progress = (i + 1) / total_steps
            progress_callback(progress)

    # Final progress callback
    if progress_callback:
        progress_callback(1.0)

    # Create time series DataFrame
    df = pd.DataFrame(power_results)
    df.set_index("timestamp", inplace=True)

    # Calculate statistics
    statistics = _calculate_statistics(df, system, interval_minutes)

    return SimulationResult(
        time_series=df,
        statistics=statistics,
        location=location,
        system=system,
        interval_minutes=interval_minutes,
    )


def _calculate_statistics(
    df: pd.DataFrame, system: PVSystem, interval_minutes: int
) -> AnnualStatistics:
    """Calculate annual statistics from time series data.

    Parameters
    ----------
    df : pd.DataFrame
        Time series DataFrame with power and irradiance data
    system : PVSystem
        PV system configuration
    interval_minutes : int
        Time interval in minutes

    Returns
    -------
    AnnualStatistics
        Aggregated performance metrics
    """
    # Energy calculation (power * time interval)
    interval_hours = interval_minutes / 60.0
    energy_kwh_per_step = df["power_w"] * interval_hours / 1000.0

    # Total energy
    total_energy_kwh = energy_kwh_per_step.sum()

    # Peak power
    peak_power_w = df["power_w"].max()

    # Daylight hours (where solar elevation > 0)
    daylight_mask = df["solar_elevation"] > 0
    total_daylight_hours = daylight_mask.sum() * interval_hours
    average_power_w = df.loc[daylight_mask, "power_w"].mean() if daylight_mask.any() else 0.0

    # Capacity factor
    # CF = Actual Energy / (Rated Power * Hours in Year)
    hours_in_year = 8760
    rated_power_w = system.panel_area * system.panel_efficiency * 1000  # 1000 W/m² STC
    capacity_factor = total_energy_kwh / (rated_power_w * hours_in_year / 1000.0)

    # Performance ratio (simplified)
    # PR = Actual Energy / Ideal Energy (at STC irradiance)
    # For clear sky, use total POA irradiance as reference
    total_poa_energy = (df["poa_irradiance"] * interval_hours).sum()
    ideal_energy_kwh = (
        total_poa_energy * system.panel_area * system.panel_efficiency / 1000.0
    )
    performance_ratio = total_energy_kwh / ideal_energy_kwh if ideal_energy_kwh > 0 else 0.0

    # Monthly aggregation
    df_monthly = df.copy()
    df_monthly["energy_kwh"] = energy_kwh_per_step
    monthly_energy = df_monthly.groupby(df_monthly.index.to_period("M"))["energy_kwh"].sum()

    # Daily aggregation
    daily_energy = df_monthly.groupby(df_monthly.index.to_period("D"))["energy_kwh"].sum()

    return AnnualStatistics(
        total_energy_kwh=total_energy_kwh,
        capacity_factor=capacity_factor,
        peak_power_w=peak_power_w,
        average_power_w=average_power_w,
        total_daylight_hours=total_daylight_hours,
        performance_ratio=performance_ratio,
        monthly_energy_kwh=monthly_energy,
        daily_energy_kwh=daily_energy,
    )
