#!/usr/bin/env python3
"""Example: Weather data quality checking and interpolation.

This example demonstrates how to use PVSolarSim's weather data quality
checking and interpolation features to handle real-world data issues.
"""

import numpy as np
import pandas as pd

from pvsolarsim.weather import (
    create_quality_report,
    detect_gaps,
    fill_gaps,
    interpolate_weather_data,
    perform_quality_checks,
)


def create_sample_weather_data():
    """Create sample weather data with some quality issues."""
    # Create hourly data for one day
    timestamps = pd.date_range("2025-06-21", periods=24, freq="h", tz="UTC")

    # Simulate realistic weather pattern with some issues
    hours = timestamps.hour.values

    # Solar irradiance (parabolic pattern, peaks at noon)
    ghi_values = [max(0, 900 * (1 - abs(h - 12) / 12) ** 2) for h in hours]

    # Introduce some data quality issues:
    ghi_values[2] = -50  # Negative value (error)
    ghi_values[14] = 2000  # Out of range (too high)
    ghi_values[22] = 100  # Nighttime irradiance (suspicious)

    # Create temperature data
    temp_values = [15 + 10 * np.sin((h - 6) * np.pi / 12) for h in hours]
    temp_values[10] = np.nan  # Missing value

    # Create DataFrame
    weather_df = pd.DataFrame(
        {
            "ghi": ghi_values,
            "dni": [g * 1.1 if g > 0 else 0 for g in ghi_values],
            "dhi": [g * 0.3 if g > 0 else 0 for g in ghi_values],
            "temp_air": temp_values,
            "wind_speed": [3 + 2 * np.sin(h * np.pi / 12) for h in hours],
        },
        index=timestamps,
    )

    return weather_df


def create_gappy_weather_data():
    """Create weather data with gaps in the time series."""
    # Create data with some timestamps missing
    timestamps = pd.to_datetime(
        [
            "2025-06-21 00:00",
            "2025-06-21 01:00",
            "2025-06-21 02:00",
            # Gap: 03:00 and 04:00 missing
            "2025-06-21 05:00",
            "2025-06-21 06:00",
            # Gap: 07:00 through 09:00 missing
            "2025-06-21 10:00",
            "2025-06-21 11:00",
            "2025-06-21 12:00",
        ],
        utc=True,
    )

    hours = [t.hour for t in timestamps]
    ghi_values = [max(0, 900 * (1 - abs(h - 12) / 12) ** 2) for h in hours]

    weather_df = pd.DataFrame(
        {
            "ghi": ghi_values,
            "temp_air": [15 + 10 * np.sin((h - 6) * np.pi / 12) for h in hours],
        },
        index=timestamps,
    )

    return weather_df


def main():
    """Run weather data quality and interpolation examples."""
    print("=" * 70)
    print("Weather Data Quality Checking and Interpolation Examples")
    print("=" * 70)

    # Example 1: Quality checking
    print("\n1. Quality Checking Example")
    print("-" * 70)

    weather_data = create_sample_weather_data()
    print(f"\nOriginal data shape: {weather_data.shape}")
    print("\nFirst few rows:")
    print(weather_data.head())
    print("\nLast few rows:")
    print(weather_data.tail())

    # Perform quality checks
    print("\nPerforming quality checks...")
    # Location: Boulder, Colorado
    quality_flags = perform_quality_checks(weather_data, latitude=40.0, longitude=-105.0)

    # Print quality summary
    summary = quality_flags.summary()
    print("\nQuality Summary:")
    print(f"  Total data points: {summary['total_points']}")
    print(f"  Quality percentage: {summary['quality_percentage']:.2f}%")
    print("  Issues found:")
    print(f"    - Nighttime GHI > 0: {summary['nighttime_ghi_count']}")
    print(f"    - Negative values: {summary['negative_values_count']}")
    print(f"    - Out of range: {summary['out_of_range_count']}")
    print(f"    - Inconsistent irradiance: {summary['inconsistent_count']}")

    # Create detailed report
    print("\nDetailed Quality Report:")
    print("-" * 70)
    report = create_quality_report(weather_data, quality_flags)
    print(report)

    # Example 2: Interpolation
    print("\n2. Interpolation Example")
    print("-" * 70)

    # Remove some values to demonstrate interpolation
    weather_with_gaps = weather_data.copy()
    weather_with_gaps.loc[weather_with_gaps.index[5:8], "temp_air"] = np.nan
    weather_with_gaps.loc[weather_with_gaps.index[15:17], "ghi"] = np.nan

    print("\nData with gaps:")
    print(weather_with_gaps[["ghi", "temp_air"]].iloc[4:9])

    # Interpolate missing values
    interpolated = interpolate_weather_data(weather_with_gaps, method="linear")

    print("\nAfter linear interpolation:")
    print(interpolated[["ghi", "temp_air"]].iloc[4:9])

    # Example 3: Gap detection
    print("\n3. Gap Detection Example")
    print("-" * 70)

    gappy_data = create_gappy_weather_data()
    print(f"\nData with missing timestamps: {len(gappy_data)} records")
    print(gappy_data[["ghi", "temp_air"]])

    # Detect gaps
    gaps = detect_gaps(gappy_data, expected_freq="1h")
    print(f"\nDetected {len(gaps)} gap(s):")
    print(gaps)

    # Fill gaps
    print("\nFilling gaps with linear interpolation...")
    filled = fill_gaps(gappy_data, method="linear", expected_freq="1h")
    print(f"\nFilled data: {len(filled)} records")
    print(filled[["ghi", "temp_air"]])

    # Example 4: Comparison of interpolation methods
    print("\n4. Comparison of Interpolation Methods")
    print("-" * 70)

    # Create simple data with a gap
    simple_data = pd.DataFrame(
        {"value": [100.0, np.nan, np.nan, np.nan, 500.0]},
        index=pd.date_range("2025-01-01", periods=5, freq="h", tz="UTC"),
    )

    print("\nOriginal data:")
    print(simple_data)

    # Linear interpolation
    linear = interpolate_weather_data(simple_data.copy(), method="linear")
    print("\nLinear interpolation:")
    print(linear)

    # Forward fill
    from pvsolarsim.weather import forward_fill

    ffill = forward_fill(simple_data.copy())
    print("\nForward fill:")
    print(ffill)

    # Backward fill
    from pvsolarsim.weather import backward_fill

    bfill = backward_fill(simple_data.copy())
    print("\nBackward fill:")
    print(bfill)

    print("\n" + "=" * 70)
    print("Examples completed!")
    print("=" * 70)


if __name__ == "__main__":
    main()
