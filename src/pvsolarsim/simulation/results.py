"""Result classes for PV simulations.

This module defines dataclasses for storing and analyzing simulation results,
including time series data and aggregated statistics.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import pandas as pd

if TYPE_CHECKING:
    from pvsolarsim.core.location import Location
    from pvsolarsim.core.pvsystem import PVSystem


@dataclass
class AnnualStatistics:
    """Annual performance statistics from PV simulation.

    Attributes
    ----------
    total_energy_kwh : float
        Total energy production in kWh
    capacity_factor : float
        Capacity factor (0-1)
    peak_power_w : float
        Peak instantaneous power in Watts
    average_power_w : float
        Average power during daylight hours in Watts
    total_daylight_hours : float
        Total hours with solar elevation > 0
    performance_ratio : float
        Performance ratio (0-1), ratio of actual to ideal energy
    monthly_energy_kwh : pd.Series
        Monthly energy production in kWh
    daily_energy_kwh : pd.Series
        Daily energy production in kWh
    """

    total_energy_kwh: float
    capacity_factor: float
    peak_power_w: float
    average_power_w: float
    total_daylight_hours: float
    performance_ratio: float
    monthly_energy_kwh: pd.Series
    daily_energy_kwh: pd.Series


@dataclass
class SimulationResult:
    """Results from PV simulation.

    Contains both time series data and aggregated statistics.

    Attributes
    ----------
    time_series : pd.DataFrame
        Time series with power and irradiance data
    statistics : AnnualStatistics
        Aggregated performance metrics
    location : Location
        Geographic location used in simulation
    system : PVSystem
        PV system configuration used
    interval_minutes : int
        Time interval used in simulation
    """

    time_series: pd.DataFrame
    statistics: AnnualStatistics
    location: Location  # Forward reference
    system: PVSystem  # Forward reference
    interval_minutes: int

    def export_csv(self, filepath: str) -> None:
        """Export time series data to CSV file.

        Parameters
        ----------
        filepath : str
            Path to output CSV file

        Examples
        --------
        >>> result.export_csv('annual_production.csv')
        """
        self.time_series.to_csv(filepath, index=True)

    def get_monthly_summary(self) -> pd.DataFrame:
        """Get monthly summary statistics.

        Returns
        -------
        pd.DataFrame
            Monthly statistics with columns: energy_kwh, avg_power_w, peak_power_w

        Examples
        --------
        >>> monthly = result.get_monthly_summary()
        >>> print(monthly)
        """
        monthly = pd.DataFrame(
            {
                "energy_kwh": self.statistics.monthly_energy_kwh,
                "avg_power_w": self.time_series.groupby(
                    self.time_series.index.to_period("M")
                )["power_w"].mean(),
                "peak_power_w": self.time_series.groupby(
                    self.time_series.index.to_period("M")
                )["power_w"].max(),
            }
        )
        return monthly

    def get_daily_summary(self) -> pd.DataFrame:
        """Get daily summary statistics.

        Returns
        -------
        pd.DataFrame
            Daily statistics with columns: energy_kwh, avg_power_w, peak_power_w

        Examples
        --------
        >>> daily = result.get_daily_summary()
        >>> print(daily.head())
        """
        daily = pd.DataFrame(
            {
                "energy_kwh": self.statistics.daily_energy_kwh,
                "avg_power_w": self.time_series.groupby(
                    self.time_series.index.to_period("D")
                )["power_w"].mean(),
                "peak_power_w": self.time_series.groupby(
                    self.time_series.index.to_period("D")
                )["power_w"].max(),
            }
        )
        return daily
