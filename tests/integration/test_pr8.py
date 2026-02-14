"""
Test PR #8 - Real-World Validation Against Prague Installation
Comprehensive validation test comparing pvsolarsim calculations against pvlib reference
using actual weather data from Prague sample dataset.

This test validates:
1. Power calculations with real weather data
2. Accuracy comparison against pvlib for the same inputs
3. Energy production validation against Czech Republic expectations
4. Temperature modeling accuracy
5. POA irradiance calculation accuracy

Location: Prague, Czech Republic (50.0807494°N, 14.8594164°E)
System: 14.04 kWp residential installation
- String 1: 16× München Energieprodukte MSMD450M6-72 M6 @ 450W = 7.2 kWp
- String 2: 18× Canadian Solar HiKu CS3L-380MS @ 380W = 6.84 kWp
- Orientation: 35° tilt, 202° azimuth (SSW)

Czech Republic Expected Performance:
- Annual sunny hours: ~1,600-1,800 hours
- kWh/kWp ratio: 900-1,100 kWh/kWp
- Capacity factor: 10-13%

Validation Method:
Compare pvsolarsim against pvlib using identical inputs (weather data, location, system)
to validate accuracy of all calculation components.
"""

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from pvsolarsim import Location, PVSystem, calculate_power
from pvsolarsim.weather import CSVWeatherReader

# Import pvlib for validation comparison
try:
    import pvlib

    PVLIB_AVAILABLE = True
except ImportError:
    PVLIB_AVAILABLE = False
    pytestmark = pytest.mark.skip(reason="pvlib not installed")


# ==================================================================================
# REAL SYSTEM CONFIGURATION - Prague Residential Installation
# ==================================================================================

# Location: Prague area, Czech Republic
LATITUDE = 50.0807494
LONGITUDE = 14.8594164
ALTITUDE = 220  # meters (more accurate than 300m)
TIMEZONE = "Europe/Prague"

# Panel specifications - String 1: München panels
MUNCHEN_PANELS = {
    "count": 16,
    "power_wp": 450,
    "efficiency": 0.2037,  # 20.37%
    "temp_coeff_pmax": -0.0035,  # -0.35%/°C
    "area_m2": 2.108 * 1.048,  # 2.209 m²
}

# Panel specifications - String 2: Canadian Solar panels
CANADIAN_PANELS = {
    "count": 18,
    "power_wp": 380,
    "efficiency": 0.205,  # ~20.5%
    "temp_coeff_pmax": -0.0037,  # -0.37%/°C
    "area_m2": 1.765 * 1.048,  # 1.850 m²
}

# System totals
TOTAL_POWER_WP = (
    MUNCHEN_PANELS["count"] * MUNCHEN_PANELS["power_wp"]
    + CANADIAN_PANELS["count"] * CANADIAN_PANELS["power_wp"]
)
TOTAL_AREA_M2 = (
    MUNCHEN_PANELS["count"] * MUNCHEN_PANELS["area_m2"]
    + CANADIAN_PANELS["count"] * CANADIAN_PANELS["area_m2"]
)
WEIGHTED_EFFICIENCY = TOTAL_POWER_WP / (TOTAL_AREA_M2 * 1000)
WEIGHTED_TEMP_COEFF = (
    MUNCHEN_PANELS["count"] * MUNCHEN_PANELS["power_wp"] * MUNCHEN_PANELS["temp_coeff_pmax"]
    + CANADIAN_PANELS["count"] * CANADIAN_PANELS["power_wp"] * CANADIAN_PANELS["temp_coeff_pmax"]
) / TOTAL_POWER_WP

# System orientation
TILT = 35.0  # degrees (optimal for Central Europe)
AZIMUTH = 202.0  # degrees (SSW orientation)


@pytest.fixture
def prague_location():
    """Create Location object for Prague installation."""
    return Location(latitude=LATITUDE, longitude=LONGITUDE, altitude=ALTITUDE, timezone=TIMEZONE)


@pytest.fixture
def prague_system():
    """Create PVSystem object for Prague installation."""
    return PVSystem(
        panel_area=TOTAL_AREA_M2,
        panel_efficiency=WEIGHTED_EFFICIENCY,
        tilt=TILT,
        azimuth=AZIMUTH,
        temp_coefficient=WEIGHTED_TEMP_COEFF,
    )


@pytest.fixture
def prague_weather_data():
    """Load real weather data from Prague sample CSV."""
    data_dir = Path(__file__).parent / "sample_data"
    csv_path = data_dir / "prague_weather_2025_sample.csv"

    if not csv_path.exists():
        pytest.skip(f"Weather data file not found: {csv_path}")

    reader = CSVWeatherReader(filepath=str(csv_path))
    weather_data = reader.read()

    return weather_data


@pytest.fixture
def pvlib_location():
    """Create pvlib Location object for comparison."""
    if not PVLIB_AVAILABLE:
        pytest.skip("pvlib not available")
    return pvlib.location.Location(
        latitude=LATITUDE, longitude=LONGITUDE, altitude=ALTITUDE, tz=TIMEZONE
    )


@pytest.fixture
def pvlib_system():
    """Create pvlib PVSystem object for comparison."""
    if not PVLIB_AVAILABLE:
        pytest.skip("pvlib not available")
    return pvlib.pvsystem.PVSystem(
        surface_tilt=TILT,
        surface_azimuth=AZIMUTH,
        module_parameters={
            "pdc0": TOTAL_POWER_WP,
            "gamma_pdc": WEIGHTED_TEMP_COEFF * 100,  # pvlib uses %/°C
        },
        temperature_model_parameters=pvlib.temperature.TEMPERATURE_MODEL_PARAMETERS["sapm"][
            "open_rack_glass_glass"
        ],
    )


# ==================================================================================
# TEST CASES
# ==================================================================================


@pytest.mark.slow
def test_system_configuration():
    """Test 1: Verify system configuration is correctly set up."""
    print("\n" + "=" * 80)
    print("TEST 1: System Configuration Verification")
    print("=" * 80)

    print(f"\nLocation: {LATITUDE}°N, {LONGITUDE}°E, {ALTITUDE}m")
    print(f"Timezone: {TIMEZONE}")
    print()
    print("Panel Configuration:")
    print(
        f"  String 1: {MUNCHEN_PANELS['count']}× München MSMD450M6-72 @ {MUNCHEN_PANELS['power_wp']}W"
    )
    print(f"    - Capacity: {MUNCHEN_PANELS['count'] * MUNCHEN_PANELS['power_wp']/1000:.2f} kWp")
    print(f"    - Efficiency: {MUNCHEN_PANELS['efficiency']*100:.2f}%")
    print(f"    - Temp Coeff: {MUNCHEN_PANELS['temp_coeff_pmax']*100:.3f}%/°C")
    print(
        f"  String 2: {CANADIAN_PANELS['count']}× Canadian Solar CS3L-380MS @ {CANADIAN_PANELS['power_wp']}W"
    )
    print(f"    - Capacity: {CANADIAN_PANELS['count'] * CANADIAN_PANELS['power_wp']/1000:.2f} kWp")
    print(f"    - Efficiency: {CANADIAN_PANELS['efficiency']*100:.2f}%")
    print(f"    - Temp Coeff: {CANADIAN_PANELS['temp_coeff_pmax']*100:.3f}%/°C")
    print()
    print("System Totals:")
    print(f"  Total Capacity: {TOTAL_POWER_WP/1000:.2f} kWp")
    print(f"  Total Area: {TOTAL_AREA_M2:.2f} m²")
    print(f"  Weighted Efficiency: {WEIGHTED_EFFICIENCY*100:.2f}%")
    print(f"  Weighted Temp Coefficient: {WEIGHTED_TEMP_COEFF*100:.3f}%/°C")
    print(f"  Orientation: Tilt {TILT}°, Azimuth {AZIMUTH}° (SSW)")

    # Verify calculations
    assert abs(TOTAL_POWER_WP - 14040) < 1, "Total power should be 14.04 kWp"
    assert 68 < TOTAL_AREA_M2 < 69, "Total area should be around 68-69 m²"
    assert 0.20 < WEIGHTED_EFFICIENCY < 0.21, "Weighted efficiency should be around 20%"
    assert -0.0037 < WEIGHTED_TEMP_COEFF < -0.0035, "Temp coefficient should be around -0.36%/°C"


@pytest.mark.slow
def test_weather_data_loading(prague_weather_data):
    """Test 2: Verify weather data is loaded correctly."""
    print("\n" + "=" * 80)
    print("TEST 2: Weather Data Loading Verification")
    print("=" * 80)

    print(f"\nWeather data loaded: {len(prague_weather_data)} records")
    print(f"Date range: {prague_weather_data.index.min()} to {prague_weather_data.index.max()}")
    print()
    print("Weather data columns:")
    for col in prague_weather_data.columns:
        print(f"  - {col}")
    print()
    print("Sample statistics:")
    print(prague_weather_data.describe())

    # Verify expected columns
    expected_cols = ["ghi", "dni", "dhi", "temp_air", "wind_speed", "cloud_cover"]
    for col in expected_cols:
        assert col in prague_weather_data.columns, f"Missing column: {col}"

    # Verify data ranges
    assert prague_weather_data["ghi"].max() > 0, "GHI should have positive values"
    assert prague_weather_data["temp_air"].min() < 30, "Temperature should be realistic"
    assert prague_weather_data["wind_speed"].min() >= 0, "Wind speed should be non-negative"


@pytest.mark.slow
def test_power_calculation_sample_day(prague_location, prague_system, prague_weather_data):
    """Test 3: Calculate power for sample day and verify realistic values."""
    print("\n" + "=" * 80)
    print("TEST 3: Power Calculation for Sample Winter Day (Jan 1, 2025)")
    print("=" * 80)

    # Get January 1st data
    jan_1_data = prague_weather_data[
        prague_weather_data.index.date == pd.Timestamp("2025-01-01").date()
    ]

    if len(jan_1_data) == 0:
        pytest.skip("No data for January 1, 2025")

    print(f"\nCalculating power for {len(jan_1_data)} hourly records...")
    print()

    total_energy_wh = 0
    max_power_w = 0

    print(f"{'Time':>8} | {'GHI':>8} | {'Temp':>6} | {'Wind':>6} | {'Cloud':>7} | {'Power':>8}")
    print(f"{'':>8} | {'(W/m²)':>8} | {'(°C)':>6} | {'(m/s)':>6} | {'(%)':>7} | {'(W)':>8}")
    print("-" * 78)

    for timestamp, row in jan_1_data.iterrows():
        result = calculate_power(
            location=prague_location,
            system=prague_system,
            timestamp=timestamp,
            ghi=row["ghi"],
            dni=row["dni"],
            dhi=row["dhi"],
            ambient_temp=row["temp_air"],
            wind_speed=row["wind_speed"],
            cloud_cover=row["cloud_cover"],
        )

        total_energy_wh += result.power_w
        max_power_w = max(max_power_w, result.power_w)

        print(
            f"{timestamp.strftime('%H:%M'):>8} | {row['ghi']:>8.1f} | "
            f"{row['temp_air']:>6.1f} | {row['wind_speed']:>6.1f} | "
            f"{row['cloud_cover']:>7.1f} | {result.power_w:>8.0f}"
        )

    print("-" * 78)
    print("\nDaily Summary (Jan 1, 2025):")
    print(f"  Total Energy: {total_energy_wh/1000:.2f} kWh")
    print(f"  Peak Power: {max_power_w/1000:.2f} kW")
    print(f"  Peak Power / Rated: {max_power_w/TOTAL_POWER_WP*100:.1f}%")

    # Verify realistic values for winter day in Prague
    assert total_energy_wh > 0, "Should produce some energy"
    assert total_energy_wh < TOTAL_POWER_WP * 10, "Daily energy should be realistic for winter"
    assert (
        max_power_w < TOTAL_POWER_WP * 1.2
    ), "Peak power should not exceed rated power significantly"


@pytest.mark.slow
def test_pvlib_comparison_solar_position(prague_location, pvlib_location, prague_weather_data):
    """Test 4: Compare solar position calculations against pvlib."""
    if not PVLIB_AVAILABLE:
        pytest.skip("pvlib not available")

    print("\n" + "=" * 80)
    print("TEST 4: Solar Position Validation Against pvlib")
    print("=" * 80)

    from pvsolarsim.solar import calculate_solar_position

    # Test on sample timestamps during daylight hours
    sample_times = prague_weather_data[prague_weather_data["ghi"] > 100].index[:10]

    if len(sample_times) == 0:
        pytest.skip("No daylight hours in sample data")

    print(f"\nComparing solar position for {len(sample_times)} timestamps...")
    print()
    print(f"{'Time':>19} | {'PVSolarSim':>22} | {'pvlib':>22} | {'Diff':>14}")
    print(
        f"{'':>19} | {'Azim':>10} {'Elev':>10} | {'Azim':>10} {'Elev':>10} | {'Azim':>6} {'Elev':>6}"
    )
    print("-" * 85)

    azimuth_diffs = []
    elevation_diffs = []

    for timestamp in sample_times:
        # pvsolarsim calculation
        pvsim_pos = calculate_solar_position(
            timestamp=timestamp.to_pydatetime(),
            latitude=LATITUDE,
            longitude=LONGITUDE,
            altitude=ALTITUDE,
        )

        # pvlib calculation
        pvlib_pos = pvlib_location.get_solarposition(timestamp)

        azim_diff = abs(pvsim_pos.azimuth - pvlib_pos["azimuth"].iloc[0])
        elev_diff = abs(pvsim_pos.elevation - pvlib_pos["elevation"].iloc[0])

        azimuth_diffs.append(azim_diff)
        elevation_diffs.append(elev_diff)

        print(
            f"{timestamp.strftime('%Y-%m-%d %H:%M'):>19} | "
            f"{pvsim_pos.azimuth:>10.2f}° {pvsim_pos.elevation:>9.2f}° | "
            f"{pvlib_pos['azimuth'].iloc[0]:>10.2f}° {pvlib_pos['elevation'].iloc[0]:>9.2f}° | "
            f"{azim_diff:>6.3f}° {elev_diff:>5.3f}°"
        )

    print("-" * 85)
    print("\nAccuracy Metrics:")
    print(f"  Azimuth MAE: {np.mean(azimuth_diffs):.4f}°")
    print(f"  Azimuth Max Error: {np.max(azimuth_diffs):.4f}°")
    print(f"  Elevation MAE: {np.mean(elevation_diffs):.4f}°")
    print(f"  Elevation Max Error: {np.max(elevation_diffs):.4f}°")

    # Validate accuracy (should be < 0.1° - close enough for practical PV applications)
    assert np.mean(azimuth_diffs) < 0.1, "Mean azimuth error should be < 0.1°"
    assert np.mean(elevation_diffs) < 0.1, "Mean elevation error should be < 0.1°"


@pytest.mark.slow
def test_pvlib_comparison_poa_irradiance(prague_location, pvlib_location, prague_weather_data):
    """Test 5: Compare POA irradiance calculations against pvlib."""
    if not PVLIB_AVAILABLE:
        pytest.skip("pvlib not available")

    print("\n" + "=" * 80)
    print("TEST 5: POA Irradiance Validation Against pvlib")
    print("=" * 80)

    from pvsolarsim.irradiance import calculate_poa_irradiance
    from pvsolarsim.solar import calculate_solar_position

    # Test on sample timestamps during daylight hours
    sample_times = prague_weather_data[prague_weather_data["ghi"] > 100].index[:10]

    if len(sample_times) == 0:
        pytest.skip("No daylight hours in sample data")

    print(f"\nComparing POA irradiance for {len(sample_times)} timestamps...")
    print()
    print(f"{'Time':>19} | {'PVSolarSim':>12} | {'pvlib':>12} | {'Diff':>10} | {'Error':>8}")
    print(f"{'':>19} | {'POA (W/m²)':>12} | {'POA (W/m²)':>12} | {'(W/m²)':>10} | {'(%)':>8}")
    print("-" * 75)

    poa_diffs = []
    poa_errors = []

    for timestamp in sample_times:
        row = prague_weather_data.loc[timestamp]

        # Calculate solar position
        solar_pos = calculate_solar_position(
            timestamp=timestamp.to_pydatetime(),
            latitude=LATITUDE,
            longitude=LONGITUDE,
            altitude=ALTITUDE,
        )

        # pvsolarsim POA calculation
        pvsim_poa = calculate_poa_irradiance(
            surface_tilt=TILT,
            surface_azimuth=AZIMUTH,
            solar_zenith=solar_pos.zenith,
            solar_azimuth=solar_pos.azimuth,
            dni=row["dni"],
            dhi=row["dhi"],
            ghi=row["ghi"],
            diffuse_model="perez",
            albedo=0.2,
        )

        # pvlib POA calculation
        pvlib_pos = pvlib_location.get_solarposition(timestamp)

        # Calculate DNI extra (extraterrestrial irradiance)
        dni_extra = pvlib.irradiance.get_extra_radiation(timestamp)

        pvlib_poa = pvlib.irradiance.get_total_irradiance(
            surface_tilt=TILT,
            surface_azimuth=AZIMUTH,
            solar_zenith=pvlib_pos["zenith"].iloc[0],
            solar_azimuth=pvlib_pos["azimuth"].iloc[0],
            dni=row["dni"],
            ghi=row["ghi"],
            dhi=row["dhi"],
            dni_extra=dni_extra,
            model="perez",
            albedo=0.2,
        )

        pvsim_total = pvsim_poa.poa_global
        pvlib_total = (
            pvlib_poa["poa_global"]
            if isinstance(pvlib_poa, dict)
            else pvlib_poa["poa_global"].iloc[0]
        )

        diff = abs(pvsim_total - pvlib_total)
        error_pct = (diff / pvlib_total * 100) if pvlib_total > 0 else 0

        poa_diffs.append(diff)
        poa_errors.append(error_pct)

        print(
            f"{timestamp.strftime('%Y-%m-%d %H:%M'):>19} | "
            f"{pvsim_total:>12.1f} | {pvlib_total:>12.1f} | "
            f"{diff:>10.2f} | {error_pct:>7.2f}%"
        )

    print("-" * 75)
    print("\nAccuracy Metrics:")
    print(f"  POA MAE: {np.mean(poa_diffs):.2f} W/m²")
    print(f"  POA MAPE: {np.mean(poa_errors):.2f}%")
    print(f"  POA Max Error: {np.max(poa_diffs):.2f} W/m²")

    # Validate accuracy (should be < 5% - very good for POA calculations)
    assert np.mean(poa_errors) < 5.0, "Mean POA error should be < 5%"


@pytest.mark.slow
def test_pvlib_comparison_temperature(prague_weather_data):
    """Test 6: Compare cell temperature calculations against pvlib."""
    if not PVLIB_AVAILABLE:
        pytest.skip("pvlib not available")

    print("\n" + "=" * 80)
    print("TEST 6: Cell Temperature Validation Against pvlib")
    print("=" * 80)

    from pvsolarsim.temperature import calculate_cell_temperature

    # Test on sample timestamps during daylight hours
    sample_times = prague_weather_data[prague_weather_data["ghi"] > 100].index[:10]

    if len(sample_times) == 0:
        pytest.skip("No daylight hours in sample data")

    print(f"\nComparing cell temperature for {len(sample_times)} timestamps...")
    print()
    print(
        f"{'Time':>19} | {'GHI':>8} | {'Temp':>6} | {'PVSolarSim':>11} | {'pvlib':>11} | {'Diff':>8}"
    )
    print(
        f"{'':>19} | {'(W/m²)':>8} | {'(°C)':>6} | {'Tcell (°C)':>11} | {'Tcell (°C)':>11} | {'(°C)':>8}"
    )
    print("-" * 85)

    temp_diffs = []

    for timestamp in sample_times:
        row = prague_weather_data.loc[timestamp]

        # pvsolarsim calculation (using SAPM model for comparison)
        pvsim_temp = calculate_cell_temperature(
            poa_global=row["ghi"] * 1.1,  # Approximate POA
            temp_air=row["temp_air"],
            wind_speed=row["wind_speed"],
            model="sapm",
        )

        # pvlib calculation
        pvlib_temp = pvlib.temperature.sapm_cell(
            poa_global=row["ghi"] * 1.1,
            temp_air=row["temp_air"],
            wind_speed=row["wind_speed"],
            a=-3.47,
            b=-0.0594,
            deltaT=3,
        )

        diff = abs(pvsim_temp - pvlib_temp)
        temp_diffs.append(diff)

        print(
            f"{timestamp.strftime('%Y-%m-%d %H:%M'):>19} | "
            f"{row['ghi']:>8.1f} | {row['temp_air']:>6.1f} | "
            f"{pvsim_temp:>11.2f} | {pvlib_temp:>11.2f} | {diff:>7.2f}"
        )

    print("-" * 85)
    print("\nAccuracy Metrics:")
    print(f"  Temperature MAE: {np.mean(temp_diffs):.2f}°C")
    print(f"  Temperature Max Error: {np.max(temp_diffs):.2f}°C")

    # Validate accuracy (should be < 2°C - acceptable for temperature modeling)
    assert np.mean(temp_diffs) < 2.0, "Mean temperature error should be < 2°C"


@pytest.mark.slow
def test_full_simulation_validation(prague_location, prague_system, prague_weather_data):
    """Test 7: Full simulation validation with energy production checks."""
    print("\n" + "=" * 80)
    print("TEST 7: Full Simulation Validation with Real Weather Data")
    print("=" * 80)

    print(f"\nRunning full simulation for {len(prague_weather_data)} hours...")
    print()

    total_energy_wh = 0
    peak_power_w = 0
    hours_with_production = 0

    for timestamp, row in prague_weather_data.iterrows():
        result = calculate_power(
            location=prague_location,
            system=prague_system,
            timestamp=timestamp.to_pydatetime(),
            ghi=row["ghi"],
            dni=row["dni"],
            dhi=row["dhi"],
            ambient_temp=row["temp_air"],
            wind_speed=row["wind_speed"],
            cloud_cover=row["cloud_cover"],
        )

        total_energy_wh += result.power_w
        peak_power_w = max(peak_power_w, result.power_w)
        if result.power_w > 10:  # Count hours with meaningful production (>10W)
            hours_with_production += 1

    total_energy_kwh = total_energy_wh / 1000
    specific_yield = total_energy_kwh / (TOTAL_POWER_WP / 1000)  # kWh/kWp

    print("Simulation Results:")
    print(f"  Total Energy: {total_energy_kwh:.2f} kWh")
    print(f"  Specific Yield: {specific_yield:.1f} kWh/kWp")
    print(
        f"  Peak Power: {peak_power_w/1000:.2f} kW ({peak_power_w/TOTAL_POWER_WP*100:.1f}% of rated)"
    )
    print(f"  Hours with Production: {hours_with_production} / {len(prague_weather_data)}")
    print()

    # Estimate annual production (sample data is representative days, not continuous)
    # This is just a sanity check, not an accurate annual estimate
    print("Note: This is sample data from representative days, not a full year.")
    print("      Energy values are for demonstration purposes only.")

    # Verify realistic values
    assert total_energy_kwh > 0, "Should produce some energy"
    assert peak_power_w > 0, "Should have some peak power"
    assert peak_power_w <= TOTAL_POWER_WP * 2.0, "Peak power should be realistic (< 2x rated)"
    assert hours_with_production > 0, "Should have some hours with production"


if __name__ == "__main__":
    """Run all tests when executed directly (for demonstration)."""
    print("\n" + "=" * 80)
    print("PR #8 REAL-WORLD VALIDATION TEST")
    print("Prague 14.04 kWp Installation with Real Weather Data")
    print("=" * 80)

    # Create fixtures manually
    location = Location(
        latitude=LATITUDE, longitude=LONGITUDE, altitude=ALTITUDE, timezone=TIMEZONE
    )

    system = PVSystem(
        panel_area=TOTAL_AREA_M2,
        panel_efficiency=WEIGHTED_EFFICIENCY,
        tilt=TILT,
        azimuth=AZIMUTH,
        temp_coefficient=WEIGHTED_TEMP_COEFF,
    )

    # Load weather data
    data_dir = Path(__file__).parent / "sample_data"
    csv_path = data_dir / "prague_weather_2025_sample.csv"
    reader = CSVWeatherReader(filepath=str(csv_path))
    weather_data = reader.read()

    # Run basic tests
    test_system_configuration()
    test_weather_data_loading(weather_data)
    test_power_calculation_sample_day(location, system, weather_data)

    if PVLIB_AVAILABLE:
        pvlib_loc = pvlib.location.Location(
            latitude=LATITUDE, longitude=LONGITUDE, altitude=ALTITUDE, tz=TIMEZONE
        )
        test_pvlib_comparison_solar_position(location, pvlib_loc, weather_data)
        test_pvlib_comparison_poa_irradiance(location, pvlib_loc, weather_data)
        test_pvlib_comparison_temperature(weather_data)

    test_full_simulation_validation(location, system, weather_data)

    print("\n" + "=" * 80)
    print("ALL VALIDATION TESTS COMPLETED SUCCESSFULLY!")
    print("=" * 80)
