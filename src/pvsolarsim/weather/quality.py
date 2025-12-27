"""Weather data quality checks and validation.

This module provides functions to check data quality, flag suspicious values,
and validate consistency of weather data.
"""

from dataclasses import dataclass
from typing import Optional

import numpy as np
import pandas as pd


@dataclass
class QualityFlags:
    """Quality flags for weather data.

    Attributes
    ----------
    nighttime_ghi : pd.Series
        Boolean series indicating nighttime GHI > 0
    negative_values : pd.Series
        Boolean series indicating any negative values
    out_of_range : pd.Series
        Boolean series indicating values outside acceptable ranges
    inconsistent : pd.Series
        Boolean series indicating inconsistent irradiance components
    """

    nighttime_ghi: pd.Series
    negative_values: pd.Series
    out_of_range: pd.Series
    inconsistent: pd.Series

    @property
    def any_issues(self) -> pd.Series:
        """Return True where any quality issue exists."""
        return (
            self.nighttime_ghi | self.negative_values | self.out_of_range | self.inconsistent
        )

    def summary(self) -> dict:
        """Return summary of quality issues."""
        return {
            "nighttime_ghi_count": self.nighttime_ghi.sum(),
            "negative_values_count": self.negative_values.sum(),
            "out_of_range_count": self.out_of_range.sum(),
            "inconsistent_count": self.inconsistent.sum(),
            "total_issues": self.any_issues.sum(),
            "total_points": len(self.nighttime_ghi),
            "quality_percentage": 100 * (1 - self.any_issues.sum() / len(self.nighttime_ghi)),
        }


def check_nighttime_irradiance(
    data: pd.DataFrame, latitude: float, longitude: float, threshold: float = 10.0
) -> pd.Series:
    """Check for suspicious nighttime irradiance values.

    Parameters
    ----------
    data : pd.DataFrame
        Weather data with 'ghi' column and DatetimeIndex
    latitude : float
        Latitude in degrees
    longitude : float
        Longitude in degrees
    threshold : float, default 10.0
        GHI threshold (W/m²) below which should be considered zero at night

    Returns
    -------
    pd.Series
        Boolean series indicating suspicious nighttime values (True = suspicious)

    Notes
    -----
    This function calculates solar elevation for each timestamp and flags
    any GHI values > threshold when the sun is below the horizon (elevation < 0).
    """
    if "ghi" not in data.columns:
        return pd.Series(False, index=data.index)

    # Import solar position calculation
    from pvsolarsim.solar.position import calculate_solar_position

    # Calculate solar elevation for each timestamp
    elevations = []
    for timestamp in data.index:
        try:
            pos = calculate_solar_position(timestamp.to_pydatetime(), latitude, longitude)
            elevations.append(pos.elevation)
        except Exception:
            # If calculation fails, assume day (conservative)
            elevations.append(10.0)

    elevations_series = pd.Series(elevations, index=data.index)

    # Flag nighttime (elevation < 0) with GHI > threshold
    is_night = elevations_series < 0
    has_irradiance = data["ghi"] > threshold

    return is_night & has_irradiance


def check_value_ranges(data: pd.DataFrame) -> pd.Series:
    """Check if values are within physically realistic ranges.

    Parameters
    ----------
    data : pd.DataFrame
        Weather data to check

    Returns
    -------
    pd.Series
        Boolean series indicating out-of-range values (True = out of range)

    Notes
    -----
    Checks the following ranges:
    - ghi: 0-1500 W/m²
    - dni: 0-1500 W/m²
    - dhi: 0-1000 W/m²
    - temp_air: -60 to 60 °C
    - wind_speed: 0-50 m/s
    - cloud_cover: 0-100 %
    """
    out_of_range = pd.Series(False, index=data.index)

    # Define ranges
    ranges = {
        "ghi": (0, 1500),
        "dni": (0, 1500),
        "dhi": (0, 1000),
        "temp_air": (-60, 60),
        "wind_speed": (0, 50),
        "cloud_cover": (0, 100),
    }

    for col, (min_val, max_val) in ranges.items():
        if col in data.columns:
            out_of_range |= (data[col] < min_val) | (data[col] > max_val)

    return out_of_range


def check_negative_values(data: pd.DataFrame) -> pd.Series:
    """Check for negative values in columns that should be non-negative.

    Parameters
    ----------
    data : pd.DataFrame
        Weather data to check

    Returns
    -------
    pd.Series
        Boolean series indicating negative values (True = has negative)
    """
    negative = pd.Series(False, index=data.index)

    # Columns that must be non-negative
    non_negative_cols = ["ghi", "dni", "dhi", "wind_speed", "cloud_cover"]

    for col in non_negative_cols:
        if col in data.columns:
            negative |= data[col] < 0

    return negative


def check_irradiance_consistency(
    data: pd.DataFrame, latitude: float, longitude: float, tolerance: float = 50.0
) -> pd.Series:
    """Check consistency of irradiance components.

    Verifies that GHI ≈ DHI + DNI * cos(zenith), allowing for measurement
    errors and atmospheric effects.

    Parameters
    ----------
    data : pd.DataFrame
        Weather data with 'ghi', 'dni', 'dhi' columns
    latitude : float
        Latitude in degrees
    longitude : float
        Longitude in degrees
    tolerance : float, default 50.0
        Maximum acceptable difference (W/m²) between measured and calculated GHI

    Returns
    -------
    pd.Series
        Boolean series indicating inconsistent values (True = inconsistent)

    Notes
    -----
    The check is only performed when all three irradiance components are present.
    """
    # Only check if all components are present
    if not all(col in data.columns for col in ["ghi", "dni", "dhi"]):
        return pd.Series(False, index=data.index)

    # Import solar position calculation
    from pvsolarsim.solar.position import calculate_solar_position

    # Calculate solar zenith for each timestamp
    zeniths = []
    for timestamp in data.index:
        try:
            pos = calculate_solar_position(timestamp.to_pydatetime(), latitude, longitude)
            zeniths.append(pos.zenith)
        except Exception:
            # If calculation fails, skip consistency check for this point
            zeniths.append(np.nan)

    zeniths_series = pd.Series(zeniths, index=data.index)

    # Calculate expected GHI from components
    cos_zenith = np.cos(np.radians(zeniths_series))
    cos_zenith = np.maximum(cos_zenith, 0)  # Clip to non-negative

    expected_ghi = data["dhi"] + data["dni"] * cos_zenith

    # Check if difference exceeds tolerance
    # Only check during daytime (zenith < 90)
    is_daytime = zeniths_series < 90
    difference = np.abs(data["ghi"] - expected_ghi)

    return is_daytime & (difference > tolerance)


def perform_quality_checks(
    data: pd.DataFrame, latitude: float, longitude: float
) -> QualityFlags:
    """Perform comprehensive quality checks on weather data.

    Parameters
    ----------
    data : pd.DataFrame
        Weather data to check
    latitude : float
        Latitude in degrees
    longitude : float
        Longitude in degrees

    Returns
    -------
    QualityFlags
        Object containing all quality flags

    Examples
    --------
    >>> import pandas as pd
    >>> data = pd.DataFrame({
    ...     'ghi': [0, 100, -10, 2000],
    ...     'temp_air': [20, 25, 30, 100]
    ... }, index=pd.date_range('2025-01-01', periods=4, freq='h', tz='UTC'))
    >>> flags = perform_quality_checks(data, latitude=40.0, longitude=-105.0)
    >>> flags.summary()
    {...}
    """
    flags = QualityFlags(
        nighttime_ghi=check_nighttime_irradiance(data, latitude, longitude),
        negative_values=check_negative_values(data),
        out_of_range=check_value_ranges(data),
        inconsistent=check_irradiance_consistency(data, latitude, longitude),
    )

    return flags


def create_quality_report(
    data: pd.DataFrame, flags: QualityFlags, output_file: Optional[str] = None
) -> str:
    """Create a detailed quality report.

    Parameters
    ----------
    data : pd.DataFrame
        Original weather data
    flags : QualityFlags
        Quality flags from perform_quality_checks()
    output_file : str, optional
        If provided, save report to this file

    Returns
    -------
    str
        Quality report as formatted string

    Examples
    --------
    >>> data = pd.DataFrame(...)
    >>> flags = perform_quality_checks(data, 40.0, -105.0)
    >>> report = create_quality_report(data, flags)
    >>> print(report)
    """
    summary = flags.summary()

    report_lines = [
        "=" * 60,
        "WEATHER DATA QUALITY REPORT",
        "=" * 60,
        "",
        f"Total data points: {summary['total_points']}",
        f"Quality percentage: {summary['quality_percentage']:.2f}%",
        "",
        "Issue Summary:",
        f"  Nighttime GHI > 0:        {summary['nighttime_ghi_count']:>6}",
        f"  Negative values:          {summary['negative_values_count']:>6}",
        f"  Out of range:             {summary['out_of_range_count']:>6}",
        f"  Inconsistent irradiance:  {summary['inconsistent_count']:>6}",
        f"  Total issues:             {summary['total_issues']:>6}",
        "",
    ]

    if summary["total_issues"] > 0:
        report_lines.extend(
            [
                "Problematic timestamps (first 10):",
                "-" * 60,
            ]
        )

        # Show first 10 problematic timestamps
        problematic = data[flags.any_issues].head(10)
        for idx, _row in problematic.iterrows():
            issues = []
            if flags.nighttime_ghi[idx]:
                issues.append("nighttime_ghi")
            if flags.negative_values[idx]:
                issues.append("negative")
            if flags.out_of_range[idx]:
                issues.append("out_of_range")
            if flags.inconsistent[idx]:
                issues.append("inconsistent")

            report_lines.append(f"{idx}: {', '.join(issues)}")

    report_lines.append("=" * 60)

    report = "\n".join(report_lines)

    if output_file:
        with open(output_file, "w") as f:
            f.write(report)

    return report
