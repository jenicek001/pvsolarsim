# Weather Data Handling in PVSolarSim

This guide explains how to work with weather data in PVSolarSim, including data quality checks, interpolation, and gap filling.

## Table of Contents
- [Weather Data Format](#weather-data-format)
- [Data Quality Checking](#data-quality-checking)
- [Interpolation and Gap Filling](#interpolation-and-gap-filling)
- [Examples](#examples)

## Weather Data Format

PVSolarSim expects weather data as a pandas DataFrame with a timezone-aware DatetimeIndex and the following columns:

### Required Columns
- `temp_air`: Ambient air temperature (°C)
- At least one irradiance component: `ghi`, `dni`, or `dhi`

### Optional Columns
- `ghi`: Global Horizontal Irradiance (W/m²)
- `dni`: Direct Normal Irradiance (W/m²)
- `dhi`: Diffuse Horizontal Irradiance (W/m²)
- `wind_speed`: Wind speed (m/s)
- `cloud_cover`: Cloud cover (0-100%)

### Value Ranges
The following ranges are considered physically realistic:
- `ghi`: 0-1500 W/m²
- `dni`: 0-1500 W/m²
- `dhi`: 0-1000 W/m²
- `temp_air`: -60 to 60 °C
- `wind_speed`: 0-50 m/s
- `cloud_cover`: 0-100 %

## Data Quality Checking

PVSolarSim provides comprehensive data quality checking to identify issues in weather data.

### Basic Quality Checks

```python
from pvsolarsim.weather import perform_quality_checks

# Perform all quality checks
quality_flags = perform_quality_checks(
    weather_data,
    latitude=40.0,
    longitude=-105.0
)

# Get summary
summary = quality_flags.summary()
print(f"Quality: {summary['quality_percentage']:.1f}%")
print(f"Issues: {summary['total_issues']}")
```

### Quality Flag Types

The quality checking system flags four types of issues:

1. **Nighttime GHI**: Detects suspicious irradiance values when the sun is below the horizon
2. **Negative Values**: Flags negative values in columns that should be non-negative (GHI, DNI, DHI, wind speed)
3. **Out of Range**: Identifies values outside physically realistic ranges
4. **Inconsistent Irradiance**: Checks consistency between GHI, DNI, and DHI components using the relationship: GHI ≈ DHI + DNI × cos(zenith)

### Individual Quality Checks

You can also run individual quality checks:

```python
from pvsolarsim.weather import (
    check_nighttime_irradiance,
    check_negative_values,
    check_value_ranges,
    check_irradiance_consistency,
)

# Check for nighttime irradiance
nighttime_flags = check_nighttime_irradiance(
    weather_data,
    latitude=40.0,
    longitude=-105.0,
    threshold=10.0  # W/m²
)

# Check value ranges
range_flags = check_value_ranges(weather_data)

# Check irradiance consistency
consistency_flags = check_irradiance_consistency(
    weather_data,
    latitude=40.0,
    longitude=-105.0,
    tolerance=50.0  # W/m²
)
```

### Quality Reports

Generate detailed quality reports for debugging:

```python
from pvsolarsim.weather import create_quality_report

report = create_quality_report(
    weather_data,
    quality_flags,
    output_file="quality_report.txt"  # Optional
)
print(report)
```

Example output:
```
============================================================
WEATHER DATA QUALITY REPORT
============================================================

Total data points: 8760
Quality percentage: 95.23%

Issue Summary:
  Nighttime GHI > 0:             12
  Negative values:                3
  Out of range:                   8
  Inconsistent irradiance:       95
  Total issues:                 418

Problematic timestamps (first 10):
------------------------------------------------------------
2025-01-15 23:45:00+00:00: nighttime_ghi
2025-02-03 14:30:00+00:00: inconsistent
...
============================================================
```

## Interpolation and Gap Filling

PVSolarSim provides tools to handle missing data through interpolation and gap filling.

### Gap Detection

Detect gaps in time series data:

```python
from pvsolarsim.weather import detect_gaps

# Detect gaps
gaps = detect_gaps(weather_data, expected_freq="1h")

print(f"Found {len(gaps)} gaps:")
for _, gap in gaps.iterrows():
    print(f"  {gap['gap_start']} to {gap['gap_end']}")
    print(f"    Duration: {gap['gap_duration']}")
    print(f"    Missing points: {gap['missing_points']}")
```

### Interpolation Methods

Fill missing values using various interpolation methods:

```python
from pvsolarsim.weather import interpolate_weather_data

# Linear interpolation (default)
filled = interpolate_weather_data(weather_data, method="linear")

# Time-based interpolation
filled = interpolate_weather_data(weather_data, method="time")

# Spline interpolation
filled = interpolate_weather_data(weather_data, method="cubic")

# With limit on consecutive fills
filled = interpolate_weather_data(
    weather_data,
    method="linear",
    limit=3,  # Fill max 3 consecutive NaNs
    limit_direction="forward"  # Fill forward from valid values
)
```

### Forward/Backward Fill

Propagate valid values forward or backward:

```python
from pvsolarsim.weather import forward_fill, backward_fill

# Forward fill
filled = forward_fill(weather_data, limit=2)

# Backward fill
filled = backward_fill(weather_data, limit=2)

# Specific columns only
filled = forward_fill(weather_data, columns=["temp_air"])
```

### Automated Gap Filling

Automatically detect and fill gaps in the time series:

```python
from pvsolarsim.weather import fill_gaps

# Fill all gaps with linear interpolation
filled = fill_gaps(
    weather_data,
    method="linear",
    expected_freq="1h"
)

# Limit gap size to fill
filled = fill_gaps(
    weather_data,
    method="linear",
    max_gap_size=3,  # Only fill gaps ≤ 3 points
    expected_freq="1h"
)

# Use forward fill for large datasets
filled = fill_gaps(
    weather_data,
    method="forward",
    expected_freq="1h"
)
```

## Examples

### Complete Workflow

```python
import pandas as pd
from pvsolarsim.weather import (
    CSVWeatherReader,
    perform_quality_checks,
    create_quality_report,
    fill_gaps,
)

# 1. Read weather data
reader = CSVWeatherReader(
    "weather_data.csv",
    column_mapping={
        "timestamp": "datetime",
        "ghi": "irradiance_ghi",
        "temp_air": "temperature",
    },
)
weather_data = reader.read()

# 2. Check data quality
quality_flags = perform_quality_checks(
    weather_data,
    latitude=40.0,
    longitude=-105.0,
)

# 3. Generate report
report = create_quality_report(weather_data, quality_flags)
print(report)

# 4. Fill gaps if quality is acceptable
summary = quality_flags.summary()
if summary["quality_percentage"] > 85:
    # Fill gaps
    clean_data = fill_gaps(
        weather_data,
        method="linear",
        max_gap_size=5,
        expected_freq="1h",
    )
    print(f"Filled {len(clean_data) - len(weather_data)} gaps")
else:
    print("Data quality too low - manual review required")
```

### Custom Quality Thresholds

```python
from pvsolarsim.weather import (
    check_nighttime_irradiance,
    check_value_ranges,
)

# Custom nighttime threshold
nighttime_flags = check_nighttime_irradiance(
    weather_data,
    latitude=40.0,
    longitude=-105.0,
    threshold=5.0,  # More strict (default: 10.0)
)

# Custom irradiance consistency tolerance
from pvsolarsim.weather import check_irradiance_consistency

consistency_flags = check_irradiance_consistency(
    weather_data,
    latitude=40.0,
    longitude=-105.0,
    tolerance=100.0,  # More lenient (default: 50.0)
)

# Combine flags
has_issues = nighttime_flags | consistency_flags
print(f"Flagged {has_issues.sum()} timestamps")
```

### Handling Different Time Frequencies

```python
from pvsolarsim.weather import fill_gaps

# Hourly data
hourly_filled = fill_gaps(weather_data_hourly, expected_freq="1h")

# 5-minute data
fine_filled = fill_gaps(weather_data_5min, expected_freq="5min")

# 15-minute data
medium_filled = fill_gaps(weather_data_15min, expected_freq="15min")
```

## Best Practices

1. **Always Check Quality First**: Run quality checks before using weather data for simulations
2. **Set Appropriate Thresholds**: Adjust thresholds based on your data source and application
3. **Limit Gap Filling**: Don't fill large gaps (>6 hours) with interpolation - use alternative data sources
4. **Document Issues**: Save quality reports for reproducibility
5. **Validate Results**: Compare filled data with original to ensure reasonableness
6. **Use Time-Appropriate Methods**: Linear interpolation works well for temperature; forward fill may be better for cloud cover

## API Reference

For complete API documentation, see:
- `pvsolarsim.weather.quality` module
- `pvsolarsim.weather.interpolation` module
- Example: `examples/weather_quality_example.py`
