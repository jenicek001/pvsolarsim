"""Time series generation utilities for PV simulations.

This module provides functions to generate time series for simulation periods,
with support for configurable intervals, timezone awareness, and daylight filtering.
"""

from datetime import datetime
from typing import Optional

import pandas as pd
import pytz


def generate_time_series(
    start: datetime,
    end: datetime,
    interval_minutes: int = 5,
    timezone: Optional[str] = None,
    daylight_only: bool = False,
) -> pd.DatetimeIndex:
    """Generate a time series for simulation.

    Creates a pandas DatetimeIndex spanning from start to end with the specified
    interval. All timestamps are timezone-aware.

    Parameters
    ----------
    start : datetime
        Start time (if naive, timezone parameter is required)
    end : datetime
        End time (if naive, timezone parameter is required)
    interval_minutes : int, default 5
        Time interval in minutes (1-60)
    timezone : str, optional
        Timezone name (e.g., 'UTC', 'America/Denver') if start/end are naive
    daylight_only : bool, default False
        If True, filter to daylight hours only (requires location-based calculation,
        currently returns all times - to be implemented in future version)

    Returns
    -------
    pd.DatetimeIndex
        Timezone-aware datetime index

    Raises
    ------
    ValueError
        If interval is out of valid range or timezone handling is incorrect

    Examples
    --------
    >>> from datetime import datetime
    >>> import pytz
    >>>
    >>> # Using timezone-aware datetimes
    >>> start = datetime(2025, 1, 1, 0, 0, tzinfo=pytz.UTC)
    >>> end = datetime(2025, 1, 2, 0, 0, tzinfo=pytz.UTC)
    >>> times = generate_time_series(start, end, interval_minutes=60)
    >>> len(times)
    25
    >>>
    >>> # Using naive datetimes with timezone parameter
    >>> start = datetime(2025, 1, 1, 0, 0)
    >>> end = datetime(2025, 1, 2, 0, 0)
    >>> times = generate_time_series(start, end, interval_minutes=15, timezone='UTC')
    >>> len(times)
    97
    """
    # Validate interval
    if not 1 <= interval_minutes <= 1440:  # Up to 1 day
        raise ValueError("interval_minutes must be between 1 and 1440")

    # Handle timezone
    if start.tzinfo is None or end.tzinfo is None:
        if timezone is None:
            raise ValueError(
                "Timezone parameter required when start or end is timezone-naive"
            )
        tz = pytz.timezone(timezone)
        if start.tzinfo is None:
            start = tz.localize(start)
        if end.tzinfo is None:
            end = tz.localize(end)

    # Generate time series
    times = pd.date_range(start=start, end=end, freq=f"{interval_minutes}min")

    # Daylight filtering would require solar position calculation
    # for each timestamp - deferred to future version if needed
    if daylight_only:
        # For now, just return all times
        # Future: calculate solar elevation and filter
        pass

    return times
