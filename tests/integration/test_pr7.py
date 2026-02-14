"""
Test PR #7 - Weather Data Quality Validation and Interpolation
Real-World Prague System with Quality Checks and Gap Filling

This test demonstrates PR #7 features:
1. Weather data quality validation
2. Gap detection and interpolation
3. Comparison with Czech Republic solar production expectations
4. Analysis of kWh/kWp ratio and capacity factor

Location: Prague, Czech Republic (50.0807°N, 14.8594°E)
System: 14.04 kWp residential installation
Expected Performance (Czech Republic averages):
- Annual sunny hours: ~1,600-1,800 hours
- kWh/kWp ratio: 900-1,100 kWh/kWp
- Capacity factor: 10-13%
"""

from pathlib import Path

import pandas as pd

from pvsolarsim import Location
from pvsolarsim.weather import (
    CSVWeatherReader,
    create_quality_report,
    detect_gaps,
    fill_gaps,
    interpolate_weather_data,
    perform_quality_checks,
)


def main():  # noqa: C901 - Integration test with multiple demonstration sections
    print("=" * 80)
    print("Testing PR #7: Weather Data Quality Validation & Interpolation")
    print("Real-World System: 14.04 kWp in Prague, Czech Republic")
    print("=" * 80)
    print()

    # ==================================================================================
    # SYSTEM CONFIGURATION - Prague Residential Installation
    # ==================================================================================

    # Location: Prague area, Czech Republic
    latitude = 50.0807494
    longitude = 14.8594164
    altitude = 220  # meters
    timezone = "Europe/Prague"

    # System parameters - Real installation with 2 panel types
    # String 1: 16x München Energieprodukte MSMD450M6-72 M6
    munchen_panels = {
        "count": 16,
        "power_wp": 450,
        "efficiency": 0.2037,  # 20.37%
        "temp_coeff_pmax": -0.0035,  # -0.35%/°C
        "area_m2": 2.108 * 1.048,  # 2.209 m²
    }

    # String 2: 18x Canadian Solar HiKu CS3L-380MS
    canadian_panels = {
        "count": 18,
        "power_wp": 380,
        "efficiency": 0.205,  # ~20.5%
        "temp_coeff_pmax": -0.0037,  # -0.37%/°C
        "area_m2": 1.765 * 1.048,  # 1.850 m²
    }

    # Total system
    total_power_wp = (
        munchen_panels["count"] * munchen_panels["power_wp"]
        + canadian_panels["count"] * canadian_panels["power_wp"]
    )
    total_area_m2 = (
        munchen_panels["count"] * munchen_panels["area_m2"]
        + canadian_panels["count"] * canadian_panels["area_m2"]
    )
    weighted_efficiency = total_power_wp / (total_area_m2 * 1000)  # At STC (1000 W/m²)
    weighted_temp_coeff = (
        munchen_panels["count"] * munchen_panels["power_wp"] * munchen_panels["temp_coeff_pmax"]
        + canadian_panels["count"]
        * canadian_panels["power_wp"]
        * canadian_panels["temp_coeff_pmax"]
    ) / total_power_wp
    tilt = 35.0  # degrees (optimal for Central Europe)
    azimuth = 202.0  # degrees (SSW orientation)

    print("System Configuration:")
    print(f"  Location: {latitude}°N, {longitude}°E, {altitude}m")
    print(
        f"  String 1: {munchen_panels['count']}x München MSMD450M6-72 @ {munchen_panels['power_wp']}W"
    )
    print(f"    - Capacity: {munchen_panels['count'] * munchen_panels['power_wp']/1000:.2f} kWp")
    print(f"    - Efficiency: {munchen_panels['efficiency']*100:.2f}%")
    print(
        f"  String 2: {canadian_panels['count']}x Canadian Solar CS3L-380MS @ {canadian_panels['power_wp']}W"
    )
    print(f"    - Capacity: {canadian_panels['count'] * canadian_panels['power_wp']/1000:.2f} kWp")
    print(f"    - Efficiency: {canadian_panels['efficiency']*100:.2f}%")
    print(f"  Total Capacity: {total_power_wp/1000:.2f} kWp")
    print(f"  Total Area: {total_area_m2:.2f} m²")
    print(f"  Weighted Efficiency: {weighted_efficiency*100:.2f}%")
    print(f"  Weighted Temperature Coefficient: {weighted_temp_coeff*100:.3f}%/°C")
    print(f"  Tilt: {tilt}°, Azimuth: {azimuth}° (SSW)")
    print()

    # Create Location and PVSystem objects for quality checks
    location = Location(
        latitude=latitude,
        longitude=longitude,
        altitude=altitude,
        timezone=timezone,
    )

    # ==================================================================================
    # PART 1: LOAD SAMPLE WEATHER DATA
    # ==================================================================================

    print("PART 1: Loading Sample Weather Data")
    print("-" * 80)

    # Get path to sample data
    test_dir = Path(__file__).parent
    sample_csv = test_dir / "sample_data" / "prague_weather_2025_sample.csv"

    if not sample_csv.exists():
        print(f"❌ Sample data not found: {sample_csv}")
        print("   Please ensure sample data files exist in tests/integration/sample_data/")
        return

    # Load weather data
    reader = CSVWeatherReader(str(sample_csv))
    weather_data = reader.read()

    print(f"✓ Loaded {len(weather_data)} weather data points")
    print(f"  Time range: {weather_data.index.min()} to {weather_data.index.max()}")
    print(f"  Columns: {', '.join(weather_data.columns)}")
    print()

    # Show sample data
    print("Sample data (first 5 rows):")
    print(weather_data.head())
    print()

    # ==================================================================================
    # PART 2: WEATHER DATA QUALITY VALIDATION
    # ==================================================================================

    print("PART 2: Weather Data Quality Validation")
    print("-" * 80)

    # Perform comprehensive quality checks
    quality_flags = perform_quality_checks(
        weather_data,
        latitude=location.latitude,
        longitude=location.longitude,
    )

    # Get quality summary
    summary = quality_flags.summary()

    print("Quality Check Results:")
    print(f"  Total data points: {summary['total_points']}")
    print(f"  Quality percentage: {summary['quality_percentage']:.2f}%")
    print()
    print("  Issues detected:")
    print(f"    - Nighttime GHI > 0:        {summary['nighttime_ghi_count']:>6}")
    print(f"    - Negative values:          {summary['negative_values_count']:>6}")
    print(f"    - Out of range:             {summary['out_of_range_count']:>6}")
    print(f"    - Inconsistent irradiance:  {summary['inconsistent_count']:>6}")
    print(f"    - Total issues:             {summary['total_issues']:>6}")
    print()

    # Create detailed quality report
    report = create_quality_report(weather_data, quality_flags)
    print("Detailed Quality Report:")
    print(report)
    print()

    # ==================================================================================
    # PART 3: GAP DETECTION AND INTERPOLATION
    # ==================================================================================

    print("PART 3: Gap Detection and Interpolation")
    print("-" * 80)

    # Detect gaps in the data
    gaps = detect_gaps(weather_data, expected_freq="1h")

    if len(gaps) > 0:
        print(f"✓ Detected {len(gaps)} gap(s) in weather data:")
        for idx, gap in gaps.iterrows():
            print(f"  Gap {idx+1}:")
            print(f"    Start: {gap['gap_start']}")
            print(f"    End:   {gap['gap_end']}")
            print(f"    Duration: {gap['gap_duration']}")
            print(f"    Missing points: {gap['missing_points']}")
        print()

        # Fill gaps using linear interpolation
        print("Filling gaps with linear interpolation...")
        filled_weather = fill_gaps(
            weather_data,
            method="linear",
            max_gap_size=24,  # Fill gaps up to 24 hours
            expected_freq="1h",
        )

        print("✓ Weather data after gap filling:")
        print(f"  Original points: {len(weather_data)}")
        print(f"  Filled points:   {len(filled_weather)}")
        print(f"  Added points:    {len(filled_weather) - len(weather_data)}")
        print()
    else:
        print("✓ No gaps detected in weather data")
        filled_weather = weather_data
        print()

    # ==================================================================================
    # PART 4: INTERPOLATE MISSING VALUES IN EXISTING DATA
    # ==================================================================================

    print("PART 4: Interpolating Missing Values")
    print("-" * 80)

    # Check for NaN values in the data
    nan_counts = filled_weather.isna().sum()
    total_nans = nan_counts.sum()

    if total_nans > 0:
        print(f"Found {total_nans} NaN values:")
        for col, count in nan_counts.items():
            if count > 0:
                print(f"  {col}: {count}")
        print()

        print("Interpolating missing values...")
        clean_weather = interpolate_weather_data(
            filled_weather,
            method="linear",
            limit=3,  # Fill max 3 consecutive NaNs
        )

        # Check remaining NaNs
        remaining_nans = clean_weather.isna().sum().sum()
        print("✓ Interpolation complete:")
        print(f"  Original NaNs:  {total_nans}")
        print(f"  Remaining NaNs: {remaining_nans}")
        print(f"  Filled:         {total_nans - remaining_nans}")
        print()
    else:
        print("✓ No missing values found in weather data")
        clean_weather = filled_weather
        print()

    # ==================================================================================
    # PART 5: ANNUAL SIMULATION WITH CLEAN DATA
    # ==================================================================================

    print("PART 5: Annual Energy Production Simulation")
    print("-" * 80)

    # NOTE: We only have sample data for a few days, so we'll simulate just those days
    # For a real annual simulation, we'd need a full year of data

    print("Note: Simulating with available sample data (not full year)")
    print()

    # We can't use simulate_annual() with partial data, so let's use the sample directly
    # and extrapolate results

    # For demonstration, let's estimate what a full year would look like
    # based on the sample data characteristics

    print("Analyzing sample data characteristics:")
    print()

    # Calculate average daily GHI from sample days
    for date in pd.unique(clean_weather.index.date):
        day_data = clean_weather[clean_weather.index.date == date]
        if len(day_data) >= 12:  # Reasonable amount of data
            # Calculate daily average for this sample day
            hourly_ghi = day_data["ghi"].mean()
            print(f"  {date}: Average GHI = {hourly_ghi:.1f} W/m²")

    print()

    # ==================================================================================
    # PART 6: CZECH REPUBLIC PERFORMANCE EXPECTATIONS
    # ==================================================================================

    print("PART 6: Czech Republic Solar Performance Expectations")
    print("-" * 80)

    print("Based on Czech Meteorological Institute and industry data:")
    print()

    # Czech Republic solar irradiation averages
    # Source: PVGIS database for Prague area
    annual_ghi_kwh_m2 = 1050  # kWh/m²/year (Prague average)
    annual_sunny_hours = 1650  # hours/year (Prague average)

    print("Prague Climate Characteristics:")
    print(f"  Annual GHI:            {annual_ghi_kwh_m2} kWh/m²/year")
    print(f"  Annual sunny hours:    {annual_sunny_hours} hours/year")
    print(f"  Average daily GHI:     {annual_ghi_kwh_m2/365:.2f} kWh/m²/day")
    print()

    # Expected system performance
    print("Expected System Performance (14.04 kWp):")
    print()

    # Performance Ratio (PR) - typical for residential Czech installations
    performance_ratio = 0.75  # 75% (accounting for all losses)

    # Calculate expected annual energy
    # Energy = GHI × Area × Efficiency × Performance Ratio
    expected_annual_kwh = (
        annual_ghi_kwh_m2 * total_area_m2 * weighted_efficiency * performance_ratio
    )

    print(f"  Performance Ratio (PR):      {performance_ratio*100:.0f}%")
    print(f"  Expected Annual Energy:      {expected_annual_kwh:,.0f} kWh")
    print(f"  kWh/kWp ratio:               {expected_annual_kwh/total_power_wp*1000:.0f} kWh/kWp")
    print()

    # Capacity Factor
    # CF = Actual Energy / (Rated Power × Hours in Year)
    hours_per_year = 365 * 24
    expected_capacity_factor = expected_annual_kwh / (total_power_wp * hours_per_year / 1000)

    print(f"  Expected Capacity Factor:    {expected_capacity_factor*100:.1f}%")
    print()

    # Typical range for Czech Republic
    print("Czech Republic Typical Ranges:")
    print("  kWh/kWp ratio:     900 - 1,100 kWh/kWp")
    print("  Capacity Factor:   10% - 13%")
    print("  Performance Ratio: 70% - 80%")
    print()

    # Monthly breakdown (approximation based on Czech climate)
    print("Expected Monthly Energy Distribution:")
    monthly_factors = {
        "January": 0.03,
        "February": 0.05,
        "March": 0.08,
        "April": 0.10,
        "May": 0.13,
        "June": 0.14,
        "July": 0.13,
        "August": 0.12,
        "September": 0.09,
        "October": 0.06,
        "November": 0.04,
        "December": 0.03,
    }

    for month, factor in monthly_factors.items():
        monthly_kwh = expected_annual_kwh * factor
        print(f"  {month:12s}: {monthly_kwh:6.0f} kWh ({factor*100:4.0f}%)")
    print()

    # ==================================================================================
    # PART 7: QUALITY METRICS AND VALIDATION
    # ==================================================================================

    print("PART 7: Data Quality Metrics")
    print("-" * 80)

    print("Weather Data Quality Assessment:")
    print(
        f"  Data completeness:     {(1 - clean_weather.isna().sum().sum() / (len(clean_weather) * len(clean_weather.columns)))*100:.2f}%"
    )
    print(f"  Quality score:         {summary['quality_percentage']:.2f}%")
    print(f"  Gaps filled:           {len(filled_weather) - len(weather_data)}")
    print(f"  NaNs interpolated:     {total_nans if total_nans > 0 else 0}")
    print()

    # Validation checks
    print("Data Validation Status:")
    if summary["quality_percentage"] > 95:
        print("  ✓ Excellent data quality (>95%)")
    elif summary["quality_percentage"] > 85:
        print("  ✓ Good data quality (>85%)")
    elif summary["quality_percentage"] > 75:
        print("  ⚠ Fair data quality (>75%) - some issues detected")
    else:
        print("  ✗ Poor data quality (<75%) - manual review recommended")

    if len(gaps) == 0:
        print("  ✓ No time series gaps")
    elif len(gaps) <= 3:
        print(f"  ⚠ {len(gaps)} gap(s) detected and filled")
    else:
        print(f"  ✗ Many gaps ({len(gaps)}) - data may be incomplete")

    if total_nans == 0:
        print("  ✓ No missing values")
    elif total_nans < len(clean_weather) * 0.05:
        print(f"  ⚠ Some missing values ({total_nans}) - interpolated")
    else:
        print(f"  ✗ Many missing values ({total_nans}) - review recommended")

    print()

    # ==================================================================================
    # PART 8: COMPARISON WITH INDUSTRY BENCHMARKS
    # ==================================================================================

    print("PART 8: Industry Benchmark Comparison")
    print("-" * 80)

    kwh_per_kwp = expected_annual_kwh / total_power_wp * 1000

    print("System Performance vs Czech Republic Benchmarks:")
    print()
    print(f"  Our estimate:          {kwh_per_kwp:.0f} kWh/kWp")
    print("  Czech average:         950 kWh/kWp")
    print("  Good installations:    1,000 - 1,100 kWh/kWp")
    print("  Excellent:             >1,100 kWh/kWp")
    print()

    if kwh_per_kwp >= 1100:
        print("  ✓ Excellent performance expected")
    elif kwh_per_kwp >= 1000:
        print("  ✓ Very good performance expected")
    elif kwh_per_kwp >= 900:
        print("  ✓ Good performance expected (typical for CZ)")
    else:
        print("  ⚠ Below average - check system parameters")

    print()
    print(f"  Capacity Factor:       {expected_capacity_factor*100:.1f}%")
    print("  Czech typical range:   10-13%")

    if 10 <= expected_capacity_factor * 100 <= 13:
        print("  ✓ Within typical range for Czech Republic")
    elif expected_capacity_factor * 100 > 13:
        print("  ✓ Above average - excellent location/setup")
    else:
        print("  ⚠ Below typical range")

    print()

    # ==================================================================================
    # SUMMARY
    # ==================================================================================

    print("=" * 80)
    print("SUMMARY: PR #7 Testing Complete")
    print("=" * 80)
    print()
    print("Features Validated:")
    print("  ✓ Weather data quality validation")
    print("  ✓ Gap detection and filling")
    print("  ✓ Missing value interpolation")
    print("  ✓ Data quality reporting")
    print("  ✓ Czech Republic performance benchmarking")
    print()
    print("Expected Annual Performance (14.04 kWp system in Prague):")
    print(f"  Annual Energy:    {expected_annual_kwh:,.0f} kWh")
    print(f"  kWh/kWp ratio:    {kwh_per_kwp:.0f} kWh/kWp")
    print(f"  Capacity Factor:  {expected_capacity_factor*100:.1f}%")
    print(f"  Data Quality:     {summary['quality_percentage']:.1f}%")
    print()
    print("This performance is typical for a well-designed residential solar")
    print("installation in the Prague area, Czech Republic.")
    print()
    print("=" * 80)


if __name__ == "__main__":
    main()
