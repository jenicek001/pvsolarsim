"""Simulation module for time series and annual PV energy production.

This module provides tools for simulating PV system performance over extended periods,
including time series generation, statistical analysis, and annual energy calculations.
"""

from pvsolarsim.simulation.engine import simulate_annual
from pvsolarsim.simulation.results import AnnualStatistics, SimulationResult
from pvsolarsim.simulation.timeseries import generate_time_series

__all__ = [
    "simulate_annual",
    "SimulationResult",
    "AnnualStatistics",
    "generate_time_series",
]
