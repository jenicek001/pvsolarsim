"""Weather data interpolation and gap filling.

This module provides functions to interpolate missing weather data
and fill gaps in time series.
"""

from typing import Optional

import pandas as pd


def interpolate_weather_data(
    data: pd.DataFrame,
    method: str = "linear",
    limit: Optional[int] = None,
    limit_direction: str = "both",
) -> pd.DataFrame:
    """Interpolate missing values in weather data.

    Parameters
    ----------
    data : pd.DataFrame
        Weather data with potential missing values (NaN)
    method : str, default 'linear'
        Interpolation method. Options:
        - 'linear': Linear interpolation
        - 'time': Interpolation based on time index
        - 'nearest': Use nearest valid value
        - 'zero': Fill with zeros
        - 'slinear', 'quadratic', 'cubic': Spline interpolation
    limit : int, optional
        Maximum number of consecutive NaNs to fill. If None, fill all.
    limit_direction : str, default 'both'
        Direction to fill NaNs: 'forward', 'backward', or 'both'

    Returns
    -------
    pd.DataFrame
        Weather data with interpolated values

    Examples
    --------
    >>> import pandas as pd
    >>> from datetime import datetime
    >>> data = pd.DataFrame({
    ...     'ghi': [100, None, None, 400],
    ...     'temp_air': [20, None, 25, None]
    ... }, index=pd.date_range('2025-01-01', periods=4, freq='h', tz='UTC'))
    >>> filled = interpolate_weather_data(data, method='linear')
    >>> filled['ghi'].tolist()
    [100.0, 200.0, 300.0, 400.0]
    """
    # Create a copy to avoid modifying original data
    result = data.copy()

    # Interpolate each column
    for col in result.columns:
        if result[col].isna().any():
            result[col] = result[col].interpolate(
                method=method,
                limit=limit,
                limit_direction=limit_direction,  # type: ignore[call-overload]
            )

    return result


def forward_fill(
    data: pd.DataFrame, limit: Optional[int] = None, columns: Optional[list[str]] = None
) -> pd.DataFrame:
    """Fill missing values by propagating forward the last valid value.

    Parameters
    ----------
    data : pd.DataFrame
        Weather data with potential missing values
    limit : int, optional
        Maximum number of consecutive NaNs to fill forward
    columns : list of str, optional
        Specific columns to fill. If None, fill all columns.

    Returns
    -------
    pd.DataFrame
        Weather data with forward-filled values

    Examples
    --------
    >>> data = pd.DataFrame({
    ...     'ghi': [100, None, None, 400],
    ...     'temp_air': [20, None, None, 25]
    ... })
    >>> filled = forward_fill(data, limit=2)
    """
    result = data.copy()

    cols_to_fill = columns if columns is not None else result.columns
    for col in cols_to_fill:
        if col in result.columns:
            result[col] = result[col].ffill(limit=limit)

    return result


def backward_fill(
    data: pd.DataFrame, limit: Optional[int] = None, columns: Optional[list[str]] = None
) -> pd.DataFrame:
    """Fill missing values by propagating backward the next valid value.

    Parameters
    ----------
    data : pd.DataFrame
        Weather data with potential missing values
    limit : int, optional
        Maximum number of consecutive NaNs to fill backward
    columns : list of str, optional
        Specific columns to fill. If None, fill all columns.

    Returns
    -------
    pd.DataFrame
        Weather data with backward-filled values

    Examples
    --------
    >>> data = pd.DataFrame({
    ...     'ghi': [None, None, 300, 400],
    ...     'temp_air': [None, 22, None, 25]
    ... })
    >>> filled = backward_fill(data, limit=2)
    """
    result = data.copy()

    cols_to_fill = columns if columns is not None else result.columns
    for col in cols_to_fill:
        if col in result.columns:
            result[col] = result[col].bfill(limit=limit)

    return result


def detect_gaps(data: pd.DataFrame, expected_freq: Optional[str] = None) -> pd.DataFrame:
    """Detect gaps in weather data time series.

    Parameters
    ----------
    data : pd.DataFrame
        Weather data with DatetimeIndex
    expected_freq : str, optional
        Expected frequency (e.g., 'h' for hourly, '5min' for 5-minute).
        If None, infer from data.

    Returns
    -------
    pd.DataFrame
        DataFrame with gap information:
        - gap_start: Start time of gap
        - gap_end: End time of gap
        - gap_duration: Duration of gap
        - missing_points: Number of missing data points

    Examples
    --------
    >>> data = pd.DataFrame(
    ...     {'ghi': [100, 200, 300]},
    ...     index=pd.to_datetime(['2025-01-01 00:00', '2025-01-01 01:00',
    ...                           '2025-01-01 05:00'], utc=True)
    ... )
    >>> gaps = detect_gaps(data, expected_freq='h')
    >>> len(gaps)
    1
    """
    if not isinstance(data.index, pd.DatetimeIndex):
        raise ValueError("Data must have a DatetimeIndex")

    # Infer frequency if not provided
    if expected_freq is None:
        inferred_freq = pd.infer_freq(data.index)
        if inferred_freq is None:
            raise ValueError(
                "Could not infer frequency. Please provide expected_freq parameter."
            )
        expected_freq = inferred_freq

    # Normalize frequency format (e.g., 'h' -> '1h')
    if expected_freq and not any(char.isdigit() for char in expected_freq):
        expected_freq = f"1{expected_freq}"

    # Generate complete time range
    full_range = pd.date_range(
        start=data.index.min(), end=data.index.max(), freq=expected_freq, tz=data.index.tz
    )

    # Find missing timestamps
    missing_times = full_range.difference(data.index)

    if len(missing_times) == 0:
        # No gaps found
        return pd.DataFrame(columns=["gap_start", "gap_end", "gap_duration", "missing_points"])

    # Group consecutive missing timestamps into gaps
    gaps = []
    gap_start = missing_times[0]
    gap_end = missing_times[0]

    for i in range(1, len(missing_times)):
        # Check if this timestamp is consecutive
        expected_next = gap_end + pd.Timedelta(expected_freq)
        if missing_times[i] == expected_next:
            gap_end = missing_times[i]
        else:
            # Gap ended, record it
            gaps.append(
                {
                    "gap_start": gap_start,
                    "gap_end": gap_end,
                    "gap_duration": gap_end - gap_start + pd.Timedelta(expected_freq),
                    "missing_points": int((gap_end - gap_start) / pd.Timedelta(expected_freq))
                    + 1,
                }
            )
            gap_start = missing_times[i]
            gap_end = missing_times[i]

    # Record the last gap
    gaps.append(
        {
            "gap_start": gap_start,
            "gap_end": gap_end,
            "gap_duration": gap_end - gap_start + pd.Timedelta(expected_freq),
            "missing_points": int((gap_end - gap_start) / pd.Timedelta(expected_freq)) + 1,
        }
    )

    return pd.DataFrame(gaps)


def fill_gaps(
    data: pd.DataFrame,
    method: str = "linear",
    max_gap_size: Optional[int] = None,
    expected_freq: Optional[str] = None,
) -> pd.DataFrame:
    """Fill gaps in weather data time series.

    This function first detects gaps, then fills them using the specified method.
    Only gaps smaller than max_gap_size are filled.

    Parameters
    ----------
    data : pd.DataFrame
        Weather data with DatetimeIndex and potential gaps
    method : str, default 'linear'
        Interpolation method ('linear', 'forward', 'backward', 'both')
    max_gap_size : int, optional
        Maximum gap size (in number of points) to fill. Larger gaps are left unfilled.
    expected_freq : str, optional
        Expected frequency of data (e.g., 'h', '5min'). If None, infer from data.

    Returns
    -------
    pd.DataFrame
        Weather data with filled gaps (up to max_gap_size)

    Examples
    --------
    >>> data = pd.DataFrame(
    ...     {'ghi': [100, 200]},
    ...     index=pd.to_datetime(['2025-01-01 00:00', '2025-01-01 05:00'], utc=True)
    ... )
    >>> filled = fill_gaps(data, method='linear', expected_freq='h')
    >>> len(filled)
    6
    """
    if not isinstance(data.index, pd.DatetimeIndex):
        raise ValueError("Data must have a DatetimeIndex")

    # Infer frequency if not provided
    if expected_freq is None:
        expected_freq = pd.infer_freq(data.index)
        if expected_freq is None:
            raise ValueError(
                "Could not infer frequency. Please provide expected_freq parameter."
            )

    # Normalize frequency format (e.g., 'h' -> '1h')
    if expected_freq and not any(char.isdigit() for char in expected_freq):
        expected_freq = f"1{expected_freq}"

    # Generate complete time range
    full_range = pd.date_range(
        start=data.index.min(), end=data.index.max(), freq=expected_freq, tz=data.index.tz
    )

    # Reindex to include all timestamps (creates NaN for missing data)
    result = data.reindex(full_range)

    # Apply interpolation based on method
    if method == "linear":
        result = interpolate_weather_data(result, method="linear", limit=max_gap_size)
    elif method == "forward":
        result = forward_fill(result, limit=max_gap_size)
    elif method == "backward":
        result = backward_fill(result, limit=max_gap_size)
    elif method == "both":
        # Fill forward first, then backward
        result = forward_fill(result, limit=max_gap_size)
        result = backward_fill(result, limit=max_gap_size)
    else:
        raise ValueError(
            f"Unknown method: {method}. Use 'linear', 'forward', 'backward', or 'both'."
        )

    return result
